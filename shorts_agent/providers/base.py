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
    ) -> Script:
        """recent_hooks: 직전 인트로들 — 유사도 검사로 양산 방지."""


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
