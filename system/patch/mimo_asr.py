"""云端 ASR：地址、模型和 Key 都在同一份 JSON（system/cloud-asr.json，不进 git）。

换厂商只改这一文件。模板见 cloud-asr.json.example。
"""

from __future__ import annotations

import io
import json
import logging
import os
import urllib.error
import urllib.request
import wave
from pathlib import Path
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)

CONFIG_ENV = "MIMO_ASR_CONFIG"
_REPO_DEFAULT = Path(__file__).resolve().parents[1] / "cloud-asr.json"


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
        detail = exc.read().decode("utf-8", errors="replace")[:300]
        raise RuntimeError(f"云端 ASR HTTP {exc.code}: {detail}") from exc

    data = json.loads(raw)
    if data.get("error"):
        raise RuntimeError(str(data["error"]))
    choices = data.get("choices") or []
    if not choices:
        raise RuntimeError("云端 ASR 无 choices")
    text = str((choices[0].get("message") or {}).get("content") or "").strip()
    if not text:
        raise RuntimeError("云端 ASR 空文本")
    logger.info("云端 ASR 转写结果: %s", text)
    return text
