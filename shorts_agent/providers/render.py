"""편집 & 렌더링 (모듈 E). FFmpeg 동적 비주얼 합성.

- 이미지 소스 → 켄번스(줌인), 제품 이미지 → 블러배경 카드 쇼케이스
- 소스 없으면 → 움직이는 그라데이션 배경(플레이스홀더도 '모션' 있게)
- 컷 사이 xfade 트랜지션, 비네팅/채도 보정
- 후킹 컷은 짧고 임팩트 있게, 제품 컷을 앞·중앙에 배치 → 영상마다 구성 변주
"""
from __future__ import annotations

import hashlib
import logging
from pathlib import Path

from ..config import Settings
from ..models import VideoJob
from ..utils import (
    GRADIENT_PAIRS,
    gradient_motion_clip,
    is_video,
    ken_burns_clip,
    mux_audio,
    product_card_clip,
    silent_audio,
    video_motion_clip,
    xfade_concat,
)
from .base import RenderProvider

logger = logging.getLogger("shorts_agent")

_TD = 0.35  # 트랜지션 길이


class FFmpegRenderProvider(RenderProvider):
    def __init__(self, settings: Settings):
        self.s = settings

    def _pick_music(self, job_id: str) -> str | None:
        d = self.s.music_dir
        if not d.exists():
            return None
        tracks = sorted(
            p for p in d.iterdir()
            if p.suffix.lower() in {".mp3", ".m4a", ".wav", ".aac", ".ogg"}
        )
        if not tracks:
            return None
        idx = int(hashlib.md5(job_id.encode()).hexdigest(), 16) % len(tracks)
        return str(tracks[idx])

    def render(self, job: VideoJob, workdir) -> str:
        workdir = Path(workdir)
        workdir.mkdir(parents=True, exist_ok=True)
        script, assets = job.script, job.assets
        assert script and assets

        shots = script.shot_directions or ["제품 소개"]
        n = max(5, min(len(shots), 8))

        # 소스 분류
        prod_imgs = [s for s in assets.product_clips if not is_video(s)]
        prod_vids = [s for s in assets.product_clips if is_video(s)]
        broll_vids = [s for s in assets.b_roll_clips if is_video(s)]
        broll_imgs = [s for s in assets.b_roll_clips if not is_video(s)]

        # 컷 길이: 초반 3컷 '빠른 전환'(후킹 retention) 후 안정. xfade 겹침분 보정.
        total = job.voice_duration or 30.0
        budget = total + _TD * (n - 1)
        quick = [2.0, 1.2, 1.2][: min(3, n)]
        rest_cuts = n - len(quick)
        rest_each = (budget - sum(quick)) / rest_cuts if rest_cuts > 0 else 0.0
        durations = quick + [rest_each] * rest_cuts
        durations = [max(_TD + 0.6, d) for d in durations]

        clips: list[Path] = []
        for i in range(n):
            out = workdir / f"cut_{i:02d}.mp4"
            d = durations[i]
            use_card = (i == 0 or i == n // 2) and prod_imgs
            if use_card:
                product_card_clip(prod_imgs[0], out, d)
            elif prod_vids and i == 0:
                video_motion_clip(prod_vids[0], out, d)
            elif broll_vids:
                video_motion_clip(broll_vids[i % len(broll_vids)], out, d)
            elif broll_imgs:
                ken_burns_clip(broll_imgs[i % len(broll_imgs)], out, d, idx=i)
            elif prod_imgs:
                ken_burns_clip(prod_imgs[0], out, d, idx=i)
            else:
                c0, c1 = GRADIENT_PAIRS[i % len(GRADIENT_PAIRS)]
                gtype = "radial" if i % 2 == 0 else "linear"
                gradient_motion_clip(out, c0, c1, d, gtype=gtype, speed=0.010 + 0.004 * (i % 3))
            clips.append(out)

        silent_video = xfade_concat(clips, durations, workdir / "silent.mp4", td=_TD)

        audio = job.voice_path or str(silent_audio(workdir / "silence.m4a", total))
        music = self._pick_music(job.job_id)
        raw = workdir / "raw.mp4"
        mux_audio(silent_video, audio, raw, music=music)

        job.note(f"렌더: {n}컷 모션+트랜지션, {total:.1f}s" + (" +BGM" if music else ""))
        return str(raw)
