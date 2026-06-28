"""한국어 특화 TTS 어댑터 (모듈 D 대안). Naver CLOVA Voice / Typecast.

ElevenLabs 대비 한국어 억양이 자연스러운 경우가 많아 A/B 비교용으로 둔다.
이 엔진들은 단어 타임스탬프를 주지 않으므로, 합성 후 실제 오디오 길이를 측정해
단어를 균등 분배한다(자막 카라오케 동기화는 근사).
"""
from __future__ import annotations

import json
import logging
import time
import urllib.parse
import urllib.request
from pathlib import Path

from ..errors import StageError
from ..models import Stage
from ..utils import media_duration
from .base import VoiceProvider

logger = logging.getLogger("shorts_agent")


def _even_timestamps(text: str, duration: float) -> list[dict]:
    words = text.split()
    if not words or duration <= 0:
        return []
    per = duration / len(words)
    return [{"word": w, "start": round(i * per, 2), "end": round((i + 1) * per, 2)}
            for i, w in enumerate(words)]


class CLOVAVoiceProvider(VoiceProvider):
    """Naver Cloud Platform CLOVA Voice Premium."""

    URL = "https://naveropenapi.apigw.ntruss.com/tts-premium/v1/tts"

    def __init__(self, client_id: str, client_secret: str, speaker: str = "nara"):
        self.client_id = client_id
        self.client_secret = client_secret
        self.speaker = speaker

    def synthesize(self, text: str, out_path) -> tuple[str, list[dict], float]:
        out_path = Path(out_path).with_suffix(".mp3")
        body = urllib.parse.urlencode({
            "speaker": self.speaker, "text": text,
            "volume": "0", "speed": "0", "pitch": "0", "format": "mp3",
        }).encode("utf-8")
        req = urllib.request.Request(self.URL, data=body, method="POST")
        req.add_header("X-NCP-APIGW-API-KEY-ID", self.client_id)
        req.add_header("X-NCP-APIGW-API-KEY", self.client_secret)
        req.add_header("Content-Type", "application/x-www-form-urlencoded")
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                out_path.write_bytes(r.read())
        except Exception as e:
            raise StageError(Stage.VOICED, f"CLOVA TTS 실패: {e}", retryable=True) from e
        dur = media_duration(out_path)
        return str(out_path), _even_timestamps(text, dur), dur


class TypecastVoiceProvider(VoiceProvider):
    """Typecast TTS (actor 기반). 엔드포인트/필드는 계정 문서에 맞게 조정 가능."""

    SPEAK = "https://typecast.ai/api/speak"

    def __init__(self, api_key: str, actor_id: str):
        self.api_key = api_key
        self.actor_id = actor_id

    def _post(self, url, payload=None, method="GET"):
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("Authorization", f"Bearer {self.api_key}")
        req.add_header("Content-Type", "application/json")
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode("utf-8"))

    def synthesize(self, text: str, out_path) -> tuple[str, list[dict], float]:
        out_path = Path(out_path).with_suffix(".wav")
        try:
            res = self._post(self.SPEAK, {
                "actor_id": self.actor_id, "text": text, "lang": "auto",
                "xapi_hd": True, "model_version": "latest",
            }, method="POST")
            poll_url = res["result"]["speak_v2_url"]
            audio_url = None
            for _ in range(30):
                st = self._post(poll_url)
                status = st["result"].get("status")
                if status == "done":
                    audio_url = st["result"]["audio_download_url"]
                    break
                if status in ("failed", "error"):
                    raise RuntimeError(st["result"])
                time.sleep(1.0)
            if not audio_url:
                raise RuntimeError("Typecast 합성 타임아웃")
            with urllib.request.urlopen(audio_url, timeout=60) as r:
                out_path.write_bytes(r.read())
        except Exception as e:
            raise StageError(Stage.VOICED, f"Typecast TTS 실패: {e}", retryable=True) from e
        dur = media_duration(out_path)
        return str(out_path), _even_timestamps(text, dur), dur
