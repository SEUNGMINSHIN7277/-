"""모듈 추상 인터페이스 (명세 6 — 교체 가능 설계)."""
from __future__ import annotations

from abc import ABC, abstractmethod

from ..models import AssetBundle, ProductCandidate, Script, VideoJob


class ResearchProvider(ABC):
    @abstractmethod
    def find_products(self, seeds: list[str], n: int) -> list[ProductCandidate]:
        ...


class ScriptProvider(ABC):
    @abstractmethod
    def write(
        self,
        product: ProductCandidate,
        recent_hooks: list[str],
        format_type: str,
        target_audience: str,
        disclosure_text: str,
        trend_hints: dict | None = None,
        style_profile: dict | None = None,
    ) -> Script:
        """recent_hooks: 직전 인트로들 — 유사도 검사로 양산 방지.
        trend_hints: 바이럴 학습 결과(승자 후킹/앵글 등).
        style_profile: 사람 말투/레퍼런스 스타일 가이드(자연스러움 조건)."""


class TrendMiner(ABC):
    @abstractmethod
    def mine(self, seeds: list[str]) -> dict:
        """경쟁 쇼츠 분석 → 승자 패턴(dict) 반환 및 저장."""


class AssetProvider(ABC):
    @abstractmethod
    def gather(self, script: Script, product: ProductCandidate, workdir) -> AssetBundle:
        ...


class VoiceProvider(ABC):
    @abstractmethod
    def synthesize(self, text: str, out_path) -> tuple[str, list[dict], float]:
        """returns (audio_path, word_timestamps, duration_sec)."""


class RenderProvider(ABC):
    @abstractmethod
    def render(self, job: VideoJob, workdir) -> str:
        """returns raw video path (자막 전)."""


class CaptionProvider(ABC):
    @abstractmethod
    def stylize(self, job: VideoJob, workdir) -> str:
        """returns final video path (자막 + 표시문구, 안전영역)."""


class UploadProvider(ABC):
    @abstractmethod
    def upload(self, job: VideoJob) -> str:
        """returns video id."""


class FeedbackProvider(ABC):
    @abstractmethod
    def collect(self, youtube_ids: list[str]) -> dict:
        """KPI 수집 → 다음 배치 가중치."""
