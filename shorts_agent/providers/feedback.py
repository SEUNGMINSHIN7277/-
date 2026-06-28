"""성과 수집 & 피드백 루프 (모듈 H).

- LocalFeedbackProvider: output/performance.json 을 읽어 후킹포맷·카테고리별 '가중치'를 산출.
  · 파일에 format_weights/category_weights 가 있으면 그대로 사용
  · 또는 samples=[{format,category,score}] 가 있으면 평균 정규화로 가중치 계산
- YouTubeAnalyticsFeedback: 자기 채널 Analytics(조회수·시청지속률)를 끌어와
  state.json 의 (영상→포맷/카테고리) 매핑으로 집계 → performance.json 갱신.

가중치 의미: 1.0=평균, >1=평균 이상 성과 → 다음 배치에서 해당 포맷/카테고리 우대.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

from ..config import Settings
from .base import FeedbackProvider

logger = logging.getLogger("shorts_agent")

_EMPTY = {"format_weights": {}, "category_weights": {}}
_ANALYTICS_SCOPES = ["https://www.googleapis.com/auth/yt-analytics.readonly"]


def compute_weights(samples: list[dict]) -> dict:
    """samples → 포맷/카테고리 가중치(전체 평균=1.0 기준 정규화)."""
    def agg(key: str) -> dict:
        buckets: dict[str, list[float]] = {}
        for s in samples:
            k = s.get(key)
            if k is None:
                continue
            buckets.setdefault(k, []).append(float(s.get("score", 0.0)))
        means = {k: (sum(v) / len(v)) for k, v in buckets.items() if v}
        overall = (sum(means.values()) / len(means)) if means else 0.0
        if overall <= 0:
            return {k: 1.0 for k in means}
        return {k: round(max(0.3, m / overall), 3) for k, m in means.items()}

    return {"format_weights": agg("format"), "category_weights": agg("category")}


class LocalFeedbackProvider(FeedbackProvider):
    def __init__(self, settings: Settings):
        self.s = settings
        self.perf_file = Path(settings.output_dir) / "performance.json"

    def collect(self, youtube_ids: list[str]) -> dict:
        if not self.perf_file.exists():
            return dict(_EMPTY)
        try:
            data = json.loads(self.perf_file.read_text(encoding="utf-8"))
        except Exception as e:
            logger.warning("performance.json 로드 실패: %s", e)
            return dict(_EMPTY)
        if data.get("format_weights") or data.get("category_weights"):
            return {"format_weights": data.get("format_weights", {}),
                    "category_weights": data.get("category_weights", {})}
        if data.get("samples"):
            w = compute_weights(data["samples"])
            logger.info("피드백 가중치 계산: %s", w)
            return w
        return dict(_EMPTY)


class YouTubeAnalyticsFeedback(FeedbackProvider):
    """자기 채널 Analytics 로 영상별 성과를 끌어와 가중치 산출(실모드)."""

    def __init__(self, settings: Settings, token_file: str):
        self.s = settings
        self.token_file = token_file
        self.perf_file = Path(settings.output_dir) / "performance.json"
        self.state_file = Path(settings.output_dir) / "state.json"

    def _id_map(self) -> dict[str, tuple[str, str]]:
        """youtube_id → (format_type, category)."""
        if not self.state_file.exists():
            return {}
        jobs = json.loads(self.state_file.read_text(encoding="utf-8")).get("jobs", {})
        out = {}
        for j in jobs.values():
            yid = j.get("youtube_id")
            sc = j.get("script") or {}
            if yid and sc:
                out[yid] = (sc.get("format_type", ""), j.get("product", {}).get("category", ""))
        return out

    def collect(self, youtube_ids: list[str]) -> dict:
        idmap = self._id_map()
        ids = youtube_ids or list(idmap)
        if not ids:
            return dict(_EMPTY)
        try:
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build
            creds = Credentials.from_authorized_user_file(self.token_file, _ANALYTICS_SCOPES)
            yta = build("youtubeAnalytics", "v2", credentials=creds, cache_discovery=False)
        except Exception as e:
            logger.warning("Analytics 초기화 실패 → 로컬 폴백: %s", e)
            return LocalFeedbackProvider(self.s).collect(youtube_ids)

        samples = []
        for yid in ids:
            try:
                resp = yta.reports().query(
                    ids="channel==MINE", startDate="2020-01-01", endDate="2100-01-01",
                    metrics="views,averageViewPercentage,estimatedMinutesWatched",
                    filters=f"video=={yid}",
                ).execute()
                rows = resp.get("rows") or [[0, 0, 0]]
                views, avp, _ = rows[0]
                fmt, cat = idmap.get(yid, ("", ""))
                # 성과 점수 = 조회수 × 시청지속률(리텐션 가중 도달)
                samples.append({"format": fmt, "category": cat,
                                "score": float(views) * (float(avp) / 100.0)})
            except Exception as e:
                logger.warning("Analytics 조회 실패(%s): %s", yid, e)
        weights = compute_weights(samples)
        try:
            self.perf_file.write_text(
                json.dumps({"samples": samples, **weights}, ensure_ascii=False, indent=2),
                encoding="utf-8")
        except Exception:
            pass
        return weights
