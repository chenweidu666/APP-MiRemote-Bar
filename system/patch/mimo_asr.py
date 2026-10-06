"""云端 ASR：地址、模型和 Key 都在同一份 JSON（system/cloud-asr.json，不进 git）。

换厂商只改这一文件。模板见 cloud-asr.json.example。
"""

from __future__ import annotations

import io
import json
import logging
import os
import subprocess
import time
import urllib.error
import urllib.request
import wave
from pathlib import Path
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)

CONFIG_ENV = "MIMO_ASR_CONFIG"
_REPO_DEFAULT = Path(__file__).resolve().parents[1] / "cloud-asr.json"
_last_down_notify = 0.0
NOTIFY_COOLDOWN_SECONDS = 60.0


def config_path() -> Path:
    override = os.environ.get(CONFIG_ENV, "").strip()
    if override:
        return Path(override).expanduser()
    home = Path.home() / ".config/mi-remote-linux/cloud-asr.json"
    if home.is_file():
        return home
    return _REPO_DEFAULT


def load_asr_config() -> dict[str, Any]:
    path = config_path()
    if not path.is_file():
        raise RuntimeError(f"找不到 ASR 配置: {path}（设 {CONFIG_ENV} 或放 system/cloud-asr.json）")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError(f"ASR 配置不是对象: {path}")
    data["_config_path"] = str(path)
    return data


def _resolve_key_file(cfg: dict[str, Any]) -> Path | None:
    raw = str(cfg.get("key_file") or "").strip()
    env_file = os.environ.get("MIMO_ENV_FILE", "").strip()
    if env_file:
        return Path(env_file).expanduser()
    if not raw:
        return None
    path = Path(raw).expanduser()
    if not path.is_absolute():
        path = (Path(cfg["_config_path"]).parent / path).resolve()
    return path


def load_api_key(cfg: dict[str, Any] | None = None) -> str | None:
    for name in ("MIMO_API_KEY", "MIMO_ASR_API_KEY"):
        value = os.environ.get(name, "").strip()
        if value:
            return value
    if cfg is None:
        try:
            cfg = load_asr_config()
        except RuntimeError:
            cfg = {}
    embedded = str(cfg.get("api_key") or cfg.get("apiKey") or "").strip()
    if embedded:
        return embedded
    key_path = _resolve_key_file(cfg) if cfg else None
    if key_path and key_path.is_file():
        return _read_env_file(key_path)
    return None


def _read_env_file(path: Path) -> str | None:
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return None
    first = text.splitlines()[0].strip()
    if first.startswith("sk-") or first.startswith("tp-") or first.startswith("ttp-"):
        return first
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, _, value = line.partition("=")
        if name.strip() in {"MIMO_API_KEY", "MIMO_ASR_API_KEY", "API_KEY"}:
            return value.strip().strip('"').strip("'")
    return None


def pcm_to_wav_bytes(samples: np.ndarray, sample_rate: int) -> bytes:
    audio = np.ascontiguousarray(samples.astype("<i2", copy=False))
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio.tobytes())
    return buf.getvalue()


def transcribe_pcm(
    samples: np.ndarray,
    sample_rate: int = 16000,
    language: str | None = None,
    timeout: float | None = None,
) -> str:
    cfg = load_asr_config()
    key = load_api_key(cfg)
    if not key:
        notify_asr_down("缺少 api_key")
        raise RuntimeError("未配置 api_key（写在 cloud-asr.json 里，该文件不进 git）")

    import base64

    wav = pcm_to_wav_bytes(samples, sample_rate)
    asr_language = language or str(cfg.get("language") or "zh")
    if asr_language.lower().startswith("zh"):
        asr_language = "zh"
    model = str(cfg.get("model") or "").strip()
    base = str(cfg.get("base_url") or "").rstrip("/")
    if not model or not base:
        raise RuntimeError("cloud-asr.json 需要 base_url 和 model")
    wait = float(timeout if timeout is not None else cfg.get("timeout_seconds") or 20)
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_audio",
                        "input_audio": {
                            "data": "data:audio/wav;base64," + base64.b64encode(wav).decode("ascii")
                        },
                    }
                ],
            }
        ],
        "asr_options": {"language": asr_language},
    }
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        f"{base}/chat/completions",
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {key}",
            "api-key": key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    logger.info(
        "云端 ASR %s / %s（%d 字节 wav）",
        cfg.get("provider") or base,
        model,
        len(wav),
    )
    try:
        with urllib.request.urlopen(request, timeout=wait) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:200]
        reason = f"HTTP {exc.code}"
        notify_asr_down(reason)
        raise RuntimeError(f"云端 ASR {reason}: {detail}") from exc
    except urllib.error.URLError as exc:
        reason = "网络超时或连不上"
        notify_asr_down(reason)
        raise RuntimeError(f"云端 ASR {reason}: {exc}") from exc

    data = json.loads(raw)
    if data.get("error"):
        reason = "接口返回错误"
        notify_asr_down(reason)
        raise RuntimeError(str(data["error"]))
    choices = data.get("choices") or []
    if not choices:
        notify_asr_down("无识别结果")
        raise RuntimeError("云端 ASR 无 choices")
    text = str((choices[0].get("message") or {}).get("content") or "").strip()
    if not text:
        notify_asr_down("空文本")
        raise RuntimeError("云端 ASR 空文本")
    logger.info("云端 ASR 转写结果: %s", text)
    return text


def notify_asr_down(reason: str) -> None:
    """桌面通知：云端挂了。60 秒内最多一条，避免刷屏。"""
    global _last_down_notify
    now = time.monotonic()
    if now - _last_down_notify < NOTIFY_COOLDOWN_SECONDS:
        return
    _last_down_notify = now
    logger.error("云端 ASR 不可用: %s", reason)
    try:
        subprocess.run(
            [
                "notify-send",
                "-a",
                "Baton",
                "-u",
                "critical",
                "-t",
                "8000",
                "小米语音识别挂了",
                reason[:160],
            ],
            check=False,
            timeout=3,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except OSError:
        pass


def probe_health(*, notify: bool = False) -> bool:
    """探测 GET {base_url}/models，确认配置的 model 在列表里。不打印 Key。"""
    try:
        cfg = load_asr_config()
        key = load_api_key(cfg)
        base = str(cfg.get("base_url") or "").rstrip("/")
        model = str(cfg.get("model") or "").strip()
        if not key or not base:
            if notify:
                notify_asr_down("缺少 api_key 或 base_url")
            print("FAIL: 配置不完整", flush=True)
            return False
        request = urllib.request.Request(
            f"{base}/models",
            headers={
                "Authorization": f"Bearer {key}",
                "api-key": key,
                "Accept": "application/json",
            },
        )
        with urllib.request.urlopen(request, timeout=15) as response:
            body = response.read().decode("utf-8")
            status = response.status
        data = json.loads(body)
        ids = [item.get("id") for item in data.get("data") or []]
        ok = status == 200 and (not model or model in ids)
        print(
            f"{'OK' if ok else 'FAIL'} HTTP {status} provider={cfg.get('provider')} "
            f"model={model} listed={model in ids}",
            flush=True,
        )
        if not ok and notify:
            notify_asr_down(f"探测失败 HTTP {status}")
        return ok
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL: {exc}", flush=True)
        if notify:
            notify_asr_down("探测失败（连不上）")
        return False
