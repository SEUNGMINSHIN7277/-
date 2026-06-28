"""편집 & 렌더링 (모듈 E). FFmpeg 로 9:16 무자막 영상 합성.

real/mock 공통: 파일 경로(에셋)만 소비하므로 동일 구현을 쓴다.
컷 구성을 영상마다 동적으로(후킹 컷 짧게, 제품 컷 분산) → 양산 신호 완화.
"""
from __future__ import annotations

import logging
from pathlib import Path

from ..config import Settings
from ..models import VideoJob
from ..utils import (
    concat_clips,
    make_solid_clip,
    mux_audio,
    normalize_clip,
    silent_audio,
)
from .base import RenderProvider

logger = logging.getLogger("shorts_agent")

_PALETTE = ["0x1e293b", "0x334155", "0x7c2d12", "0x4c1d95", "0x0f766e", "0x9d174d"]


class FFmpegRenderProvider(RenderProvider):
    def __init__(self, settings: Settings):
        self.s = settings

    def render(self, job: VideoJob, workdir) -> str:
        workdir = Path(workdir)
        workdir.mkdir(parents=True, exist_ok=True)
        font = self.s.font_path
        script = job.script
        assets = job.assets
        assert script and assets

        shots = script.shot_directions or ["제품 소개"]
        n = max(len(shots), 4)

        # 소스 배치: 제품 컷을 앞·중간에 배치하고 사이를 b-roll 로 채움
        sources: list[str | None] = []
        prod = list(assets.product_clips)
        broll = list(assets.b_roll_clips)
        for i in range(n):
            if prod and (i == 0 or i == n // 2):
                sources.append(prod.pop(0))
            elif broll:
                sources.append(broll[i % len(broll)])
            elif prod:
                sources.append(prod.pop(0))
            else:
                sources.append(None)

        total = job.voice_duration or 30.0
        hook = min(3.0, total * 0.2)
        rest = (total - hook) / max(1, n - 1)
        durations = [hook] + [rest] * (n - 1)

        clips: list[Path] = []
        for i, (src, dur, shot) in enumerate(zip(sources, durations, shots + [""] * n)):
            out = workdir / f"cut_{i:02d}.mp4"
            if src:
                normalize_clip(src, out, dur, font)
            else:
                make_solid_clip(
                    out, text=(shot or job.product.name)[:24],
                    color=_PALETTE[i % len(_PALETTE)], duration=dur, font=font,
                    sub="(소스 컷 자리)",
                )
            clips.append(out)

        silent_video = concat_clips(clips, workdir / "silent.mp4")

        # 오디오: 나레이션(없으면 무음 폴백) + 선택 배경음악
        audio = job.voice_path
        if not audio:
            audio = str(silent_audio(workdir / "silence.m4a", total))
        raw = workdir / "raw.mp4"
        mux_audio(silent_video, audio, raw, music=assets.music_path)

        job.note(f"렌더 완료: {n}컷, {total:.1f}s")
        return str(raw)
