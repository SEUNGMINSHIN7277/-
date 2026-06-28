"""보이스오버 (모듈 D). ElevenLabs with-timestamps 로 단어 타이밍까지 확보.

채널 페르소나(voice_id) 고정 권장(명세 D-주의).
"""
from __future__ import annotations

import base64
import json
import logging
import urllib.request
from pathlib import Path

from ..errors import StageError
from ..models import Stage
from .base import VoiceProvider

logger = logging.getLogger("shorts_agent")


class ElevenLabsVoiceProvider(VoiceProvider):
    def __init__(self, api_key: str, voice_id: str, model: str = "eleven_multilingual_v2"):
        self.api_key = api_key
        self.voice_id = voice_id
        self.model = model

    def synthesize(self, text: str, out_path) -> tuple[str, list[dict], float]:
        out_path = Path(out_path)
        url = (
            f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}/with-timestamps"
        )
        body = json.dumps(
            {
                "text": text,
                "model_id": self.model,
                "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
            }
        ).encode("utf-8")
        req = urllib.request.Request(url, data=body, method="POST")
        req.add_header("xi-api-key", self.api_key)
        req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                payload = json.loads(r.read().decode("utf-8"))
        except Exception as e:
            raise StageError(Stage.VOICED, f"ElevenLabs 실패: {e}", retryable=True) from e

        audio_b64 = payload.get("audio_base64")
        if not audio_b64:
            raise StageError(Stage.VOICED, "TTS 오디오 누락", retryable=True)
        out_path.write_bytes(base64.b64decode(audio_b64))

        words = _chars_to_words(payload.get("alignment") or {})
        duration = words[-1]["end"] if words else 0.0
        return str(out_path), words, duration


def _chars_to_words(alignment: dict) -> list[dict]:
    """문자 단위 alignment → 단어 단위 타임스탬프."""
    chars = alignment.get("characters") or []
    starts = alignment.get("character_start_times_seconds") or []
    ends = alignment.get("character_end_times_seconds") or []
    words: list[dict] = []
    cur, w_start = "", None
    for i, ch in enumerate(chars):
        if w_start is None:
            w_start = starts[i] if i < len(starts) else 0.0
        if ch.isspace():
            if cur:
                words.append({"word": cur, "start": w_start, "end": ends[i - 1] if i else w_start})
                cur, w_start = "", None
        else:
            cur += ch
    if cur:
        words.append({"word": cur, "start": w_start or 0.0, "end": ends[-1] if ends else 0.0})
    return words
