"""성과 수집 & 피드백 루프 (모듈 H).

YouTube Analytics(자기 채널) + 쿠팡파트너스 실적을 합쳐 후킹/카테고리별
'승자 패턴' 가중치를 만든다. 키가 없으면 빈 가중치를 반환(루프 비활성).
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

from ..config import Settings
from .base import FeedbackProvider

logger = logging.getLogger("shorts_agent")


class LocalFeedbackProvider(FeedbackProvider):
    """발행 이력(state)에서 포맷/카테고리별 성과를 집계하는 경량 구현.

    실제 운영에서는 collect() 안에서 YouTube Analytics API + 쿠팡 실적 리포트를
    호출해 CTR·전환·수수료를 채운다(아래 TODO).
    """

    def __init__(self, settings: Settings):
        self.s = settings
        self.perf_file = Path(settings.output_dir) / "performance.json"

    def collect(self, youtube_ids: list[str]) -> dict:
        # TODO(실연동): YouTube Analytics API 로 영상별 시청지속률/CTR,
        #   쿠팡파트너스 리포트로 클릭/전환/수수료를 영상에 매핑.
        if not self.perf_file.exists():
            return {"format_weights": {}, "category_weights": {}}
        try:
            return json.loads(self.perf_file.read_text(encoding="utf-8"))
        except Exception as e:
            logger.warning("성과 파일 로드 실패: %s", e)
            return {"format_weights": {}, "category_weights": {}}
