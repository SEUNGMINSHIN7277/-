"""오케스트레이터 (명세 6). 큐/게이트/컴플라이언스/양산방지 통합."""
from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from .config import Settings
from .errors import StageError, with_retry
from .models import FORMAT_TYPES, ProductCandidate, Stage, VideoJob
from .providers.base import (
    AssetProvider,
    CaptionProvider,
    FeedbackProvider,
    RenderProvider,
    ResearchProvider,
    ScriptProvider,
    UploadProvider,
    VoiceProvider,
)
from .similarity import too_similar
from .store import Store

logger = logging.getLogger("shorts_agent")

# 모호·조건부 표시문구 금칙어(공정위 2024.12.1 개정)
_BANNED_DISCLOSURE = ["수수료를 지급받을 수 있", "소정의 수수료", "받을 수도 있"]


@dataclass
class Providers:
    research: ResearchProvider
    script: ScriptProvider
    asset: AssetProvider
    voice: VoiceProvider
    render: RenderProvider
    caption: CaptionProvider
    upload: UploadProvider
    feedback: FeedbackProvider


class ShortsAgent:
    def __init__(self, settings: Settings, providers: Providers, store: Store):
        self.s = settings
        self.p = providers
        self.store = store
        self._weights: dict = {"format_weights": {}, "category_weights": {}}

    # ---------------- 배치 ----------------
    def run_batch(self, seeds: list[str], count: int) -> list[VideoJob]:
        count = min(count, self.s.daily_cap)
        recent_ids = [j.youtube_id for j in self.store.all_jobs() if j.youtube_id]
        self._weights = self.p.feedback.collect(recent_ids) or self._weights
        cat_w = self._weights.get("category_weights", {})
        fmt_w = self._weights.get("format_weights", {})
        if cat_w or fmt_w:
            logger.info("승자 패턴 가중치 적용 — 카테고리:%s 포맷:%s", cat_w, fmt_w)

        candidates = with_retry(
            lambda: self.p.research.find_products(seeds, n=count * 2),
            stage=Stage.SELECTED,
        )
        if not candidates:
            logger.warning("상품 후보가 없습니다.")
            return []

        # 성과 좋은 카테고리 가산 → 재정렬
        candidates.sort(
            key=lambda c: c.total_score * cat_w.get(c.category, 1.0), reverse=True)

        jobs: list[VideoJob] = []
        for cand in candidates[:count]:
            job = self._script_stage(cand)
            jobs.append(job)
            if job.stage == Stage.GATE_A and self.s.auto:
                self.advance_after_gate_a(job)
        return jobs

    # ---------------- 1) 대본(+양산 방지) ----------------
    def _script_stage(self, product: ProductCandidate) -> VideoJob:
        job = VideoJob(job_id=_new_id(), product=product, stage=Stage.SELECTED)
        try:
            script = self._write_unique_script(product)
            job.script = script
            job.stage = Stage.GATE_A
            job.note(f"대본 생성: 포맷={script.format_type}, 후킹='{script.chosen_hook}'")
        except StageError as e:
            job.stage, job.error = Stage.FAILED, str(e)
            logger.error("Job %s 대본 실패: %s", job.job_id, e)
        self.store.put(job)
        return job

    def _write_unique_script(self, product: ProductCandidate):
        """포맷 로테이션 + 유사도 검사로 직전 영상과 겹치지 않는 대본 확보."""
        recent = self.store.recent_hooks
        start = self.store.next_format_index()
        # 성과 가중치로 포맷 우선순위 정렬(동률은 로테이션 커서로 변주 → 양산 방지)
        fmt_w = self._weights.get("format_weights", {})
        order = sorted(
            range(len(FORMAT_TYPES)),
            key=lambda i: (-fmt_w.get(FORMAT_TYPES[i], 1.0), (i - start) % len(FORMAT_TYPES)),
        )
        last_err: Exception | None = None
        for k in order:
            fmt = FORMAT_TYPES[k]
            try:
                script = with_retry(
                    lambda f=fmt: self.p.script.write(
                        product, recent, f, self.s.target_audience, self.s.disclosure_text
                    ),
                    stage=Stage.SCRIPTED,
                )
            except StageError as e:
                last_err = e
                continue
            if not too_similar(script.chosen_hook, recent):
                return script
            logger.info("후킹 유사도 초과 → 포맷 변경 재생성 (%s)", fmt)
        if last_err:
            raise last_err
        # 전부 유사하면 마지막 것이라도 사용(이력이 비어가며 자연 해소)
        return script

    # ---------------- GATE A 승인 → 제작 ----------------
    def advance_after_gate_a(self, job: VideoJob) -> VideoJob:
        if job.stage != Stage.GATE_A:
            logger.warning("Job %s 는 GATE_A 상태가 아님(%s)", job.job_id, job.stage.value)
            return job
        try:
            wd = self.s.output_dir / job.job_id
            wd.mkdir(parents=True, exist_ok=True)
            s, p = job.script, job.product

            job.assets = with_retry(
                lambda: self.p.asset.gather(s, p, wd / "assets"), stage=Stage.ASSETS)
            job.stage = Stage.ASSETS

            job.voice_path, job.voice_timestamps, job.voice_duration = with_retry(
                lambda: self.p.voice.synthesize(s.body, wd / "voice.m4a"), stage=Stage.VOICED)
            job.stage = Stage.VOICED

            job.raw_video_path = with_retry(
                lambda: self.p.render.render(job, wd / "render"), stage=Stage.RENDERED)
            job.stage = Stage.RENDERED

            job.final_video_path = with_retry(
                lambda: self.p.caption.stylize(job, wd / "render"), stage=Stage.CAPTIONED)
            job.stage = Stage.CAPTIONED

            self._make_thumbnail(job, wd)
            self._compliance_check(job)
            job.stage = Stage.GATE_B
            job.note("컴플라이언스 통과 → GATE_B 대기")
        except StageError as e:
            job.stage, job.error = Stage.FAILED, str(e)
            logger.error("Job %s 제작 실패: %s", job.job_id, e)
        self.store.put(job)

        if job.stage == Stage.GATE_B and self.s.auto:
            self.publish(job)
        return job

    def _make_thumbnail(self, job: VideoJob, wd) -> None:
        """후킹 썸네일 생성(실패해도 파이프라인 진행)."""
        try:
            from .utils import make_thumbnail
            bg = None
            if job.assets and job.assets.product_clips:
                imgs = [c for c in job.assets.product_clips if not c.lower().endswith(
                    (".mp4", ".mov", ".webm", ".mkv", ".m4v"))]
                bg = imgs[0] if imgs else None
            out = Path(self.s.output_dir) / f"{job.job_id}.thumb.jpg"
            job.thumbnail_path = str(
                make_thumbnail(out, bg, job.script.chosen_hook, self.s.font_path))
            job.note(f"썸네일 생성: {out.name}")
        except Exception as e:
            logger.warning("썸네일 생성 실패(무시): %s", e)

    # ---------------- 발행 전 자동 검증 ----------------
    def _compliance_check(self, job: VideoJob) -> None:
        sc = job.script
        if not sc or not sc.disclosure_text.strip():
            raise StageError(Stage.GATE_B, "공정위 표시문구 누락", retryable=False)
        if any(b in sc.disclosure_text for b in _BANNED_DISCLOSURE):
            raise StageError(Stage.GATE_B, "모호·조건부 표시문구(공정위 위반)", retryable=False)
        if too_similar(sc.chosen_hook, self.store.recent_hooks):
            raise StageError(Stage.GATE_B, "직전 영상과 후킹 과유사(양산 위험)", retryable=False)
        if not job.final_video_path:
            raise StageError(Stage.GATE_B, "최종 영상 없음", retryable=False)

    # ---------------- GATE B 승인 → 업로드 ----------------
    def publish(self, job: VideoJob) -> VideoJob:
        if job.stage != Stage.GATE_B:
            logger.warning("Job %s 는 GATE_B 상태가 아님(%s)", job.job_id, job.stage.value)
            return job
        today = date.today().isoformat()
        if self.store.uploaded_today(today) >= self.s.daily_cap:
            job.note("일일 발행 캡 도달 — 대기")
            self.store.put(job)
            logger.warning("일일 캡(%d) 도달: %s 보류", self.s.daily_cap, job.job_id)
            return job
        try:
            job.youtube_id = with_retry(lambda: self.p.upload.upload(job), stage=Stage.UPLOADED)
            job.stage = Stage.UPLOADED
            self.store.add_hook(job.script.chosen_hook)
            self.store.inc_uploaded(today)
            logger.info("발행 완료 %s → %s (오늘 %d/%d)",
                        job.job_id, job.youtube_id,
                        self.store.uploaded_today(today), self.s.daily_cap)
        except StageError as e:
            job.stage, job.error = Stage.FAILED, str(e)
            logger.error("Job %s 업로드 실패: %s", job.job_id, e)
        self.store.put(job)
        return job

    # ---------------- 수동 게이트 헬퍼 ----------------
    def approve_a(self, job_id: str, approved: bool) -> VideoJob | None:
        job = self.store.get(job_id)
        if not job:
            return None
        if not approved:
            job.stage, job.error = Stage.FAILED, "GATE_A 반려"
            self.store.put(job)
            return job
        return self.advance_after_gate_a(job)

    def approve_b(self, job_id: str, approved: bool) -> VideoJob | None:
        job = self.store.get(job_id)
        if not job:
            return None
        if not approved:
            job.stage, job.error = Stage.FAILED, "GATE_B 반려"
            self.store.put(job)
            return job
        return self.publish(job)


def _new_id() -> str:
    return uuid.uuid4().hex[:10]
