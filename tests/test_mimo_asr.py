"""MiMo ASR 辅助：WAV 封装与 Key 读取（不打真实网络、不打印 Key）。"""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "system/patch"))

from mimo_asr import _read_env_file, load_api_key, load_asr_config, pcm_to_wav_bytes  # noqa: E402


class MimoAsrHelpersTest(unittest.TestCase):
    def test_pcm_to_wav_header(self) -> None:
        samples = np.array([0, 1000, -1000, 0], dtype=np.int16)
        blob = pcm_to_wav_bytes(samples, 16000)
        with tempfile.NamedTemporaryFile(suffix=".wav") as handle:
            handle.write(blob)
            handle.flush()
            with wave.open(handle.name, "rb") as wav:
                self.assertEqual(wav.getnchannels(), 1)
                self.assertEqual(wav.getsampwidth(), 2)
                self.assertEqual(wav.getframerate(), 16000)
                self.assertEqual(wav.getnframes(), 4)

    def test_read_bare_key(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / ".env"
            path.write_text("sk-unittest-not-real\n", encoding="utf-8")
            self.assertEqual(_read_env_file(path), "sk-unittest-not-real")

    def test_read_named_key(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "mimo.env"
            path.write_text("MIMO_API_KEY=sk-named\n", encoding="utf-8")
            self.assertEqual(_read_env_file(path), "sk-named")

    def test_accept_token_plan(self) -> None:
        os.environ["MIMO_API_KEY"] = "tp-unittest-not-real"
        try:
            self.assertEqual(load_api_key(), "tp-unittest-not-real")
        finally:
            os.environ.pop("MIMO_API_KEY", None)

    def test_load_asr_config_and_key_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            cfg_path = tmp_path / "cloud-asr.json"
            cfg_path.write_text(
                '{"provider":"test","base_url":"https://example.invalid/v1",'
                '"model":"demo-asr","api_key":"tp-from-json"}',
                encoding="utf-8",
            )
            os.environ.pop("MIMO_API_KEY", None)
            os.environ.pop("MIMO_ASR_API_KEY", None)
            os.environ.pop("MIMO_ENV_FILE", None)
            os.environ["MIMO_ASR_CONFIG"] = str(cfg_path)
            try:
                cfg = load_asr_config()
                self.assertEqual(cfg["model"], "demo-asr")
                self.assertEqual(load_api_key(cfg), "tp-from-json")
            finally:
                os.environ.pop("MIMO_ASR_CONFIG", None)


if __name__ == "__main__":
    unittest.main()
