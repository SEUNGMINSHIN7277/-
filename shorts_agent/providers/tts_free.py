"""무료 TTS (edge-tts). API 키 불필요 · 한국어 뉴럴 보이스 · 단어 타임스탬프 제공.

Microsoft Edge 읽어주기 엔진의 공개 엔드포인트를 사용한다(무자본 핵심 부품).
WordBoundary 이벤트로 실제 단어 타이밍을 받아 카라오케 자막을 정확히 동기화.
설치: pip install edge-tts
추천 한국어 보이스: ko-KR-SunHiNeural(여), ko-KR-HyunsuNeural / ko-KR-InJoonNeural(남)
"""
from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from ..errors import StageError
from ..models import Stage
from ..utils import media_duration
from .base import VoiceProvider

logger = logging.getLogger("shorts_agent")


class EdgeTTSVoiceProvider(VoiceProvider):
    def __init__(self, voice: str = "ko-KR-SunHiNeural", rate: str = "+0%", pitch: str = "+0Hz"):
        self.voice = voice
        self.rate = rate
        self.pitch = pitch

    def synthesize(self, text: str, out_path) -> tuple[str, list[dict], float]:
        try:
            import edge_tts
        except ImportError as e:
            raise StageError(Stage.VOICED, "edge-tts 미설치: pip install edge-tts", False) from e
        out = Path(out_path).with_suffix(".mp3")

        async def _run() -> list[dict]:
            comm = edge_tts.Communicate(text, self.voice, rate=self.rate, pitch=self.pitch)
            words: list[dict] = []
            with open(out, "wb") as f:
                async for ch in comm.stream():
                    if ch["type"] == "audio":
                        f.write(ch["data"])
                    elif ch["type"] == "WordBoundary":
                        s = ch["offset"] / 1e7           # 100ns → s
                        d = ch["duration"] / 1e7
                        words.append({"word": ch["text"], "start": round(s, 3),
                                      "end": round(s + d, 3)})
            return words

        try:
            words = asyncio.run(_run())
        except Exception as e:
            raise StageError(Stage.VOICED, f"edge-tts 합성 실패: {e}", retryable=True) from e

        if not words:
            dur = media_duration(out)
            toks = text.split()
            per = dur / max(1, len(toks))
            words = [{"word": w, "start": round(i * per, 2), "end": round((i + 1) * per, 2)}
                     for i, w in enumerate(toks)]
        else:
            dur = words[-1]["end"]
        return str(out), words, dur
