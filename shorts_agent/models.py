"""파이프라인 데이터 모델 (영상 1개 = 1 Job)."""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any


class Stage(str, Enum):
    SELECTED = "selected"
    SCRIPTED = "scripted"
    GATE_A = "gate_a"        # 사람: 상품·후킹 승인
    ASSETS = "assets"
    VOICED = "voiced"
    RENDERED = "rendered"
    CAPTIONED = "captioned"
    GATE_B = "gate_b"        # 사람: 최종 검수 + 컴플라이언스 자동검증
    UPLOADED = "uploaded"
    FAILED = "failed"


# 양산 방지를 위한 후킹 포맷 풀 (모듈 B 에서 로테이션)
FORMAT_TYPES = [
    "question",    # 질문형: "이거 모르고 OO 쓰셨어요?"
    "measure",     # 실측형: 숫자·비교 데이터로 증명
    "compare",     # 비교형: A vs B
    "fail_story",  # 실패담형: "저 이거 사고 후회했는데…"
    "secret",      # 정보형: "아는 사람만 쓰는…"
    "reaction",    # 리액션형: 사용 순간의 반응
]


@dataclass
class ProductCandidate:
    name: str
    category: str
    coupang_url: str = ""           # 원본 상품 URL
    coupang_deeplink: str = ""      # 파트너스 추적 딥링크
    product_id: str = ""
    image_url: str = ""
    price: int = 0
    est_commission_rate: float = 0.03
    hook_score: float = 0.0         # 후킹 가능성
    conversion_score: float = 0.0   # 전환 가능성
    source_availability: str = "stock_only"  # manufacturer|self_shot|stock_only
    rationale: str = ""             # 선정 이유(고유 통찰 시드)

    @property
    def total_score(self) -> float:
        return round(self.hook_score * 0.5 + self.conversion_score * 0.5, 3)


@dataclass
class Script:
    hook_variants: list[str]        # 3초 후킹 후보 5개
    chosen_hook: str                # 선택된 후킹(인트로 자막/유사도 검사 대상)
    body: str                       # 구어체 기승전결 나레이션 전문
    caption_lines: list[str]        # 화면 자막용 짧은 청크(가독성)
    shot_directions: list[str]      # 컷별 비주얼 지시
    cta: str
    disclosure_text: str            # 공정위 표시문구 (필수)
    format_type: str                # 로테이션용
    title: str = ""                 # 업로드 제목(표시문구 prefix 전)
    hashtags: list[str] = field(default_factory=list)
    target_audience: str = ""       # 타깃 시청자(예: 20-30대 여성)


@dataclass
class AssetBundle:
    product_clips: list[str]        # 고유(제조사/직접촬영/상품 이미지)
    b_roll_clips: list[str]         # 스톡/AI 보조
    music_path: str | None = None


@dataclass
class VideoJob:
    job_id: str
    product: ProductCandidate
    script: Script | None = None
    assets: AssetBundle | None = None
    voice_path: str | None = None
    voice_timestamps: list[dict] = field(default_factory=list)
    voice_duration: float = 0.0
    raw_video_path: str | None = None
    final_video_path: str | None = None
    thumbnail_path: str | None = None
    youtube_id: str | None = None
    stage: Stage = Stage.SELECTED
    error: str | None = None
    log: list[str] = field(default_factory=list)

    def note(self, msg: str) -> None:
        self.log.append(msg)

    # ---- 직렬화 (상태 저장용) ----
    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["stage"] = self.stage.value
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "VideoJob":
        d = dict(d)
        prod = ProductCandidate(**d.pop("product"))
        scr = d.pop("script")
        asb = d.pop("assets")
        job = cls(
            job_id=d["job_id"],
            product=prod,
            script=Script(**scr) if scr else None,
            assets=AssetBundle(**asb) if asb else None,
            voice_path=d.get("voice_path"),
            voice_timestamps=d.get("voice_timestamps", []),
            voice_duration=d.get("voice_duration", 0.0),
            raw_video_path=d.get("raw_video_path"),
            final_video_path=d.get("final_video_path"),
            thumbnail_path=d.get("thumbnail_path"),
            youtube_id=d.get("youtube_id"),
            stage=Stage(d.get("stage", "selected")),
            error=d.get("error"),
            log=d.get("log", []),
        )
        return job
