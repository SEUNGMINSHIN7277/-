"""자막 스타일링 (모듈 F). ASS(libass) 로 모바일 가독성 + 안전영역 + 공정위 표시.

- 본문 자막: 화면 약 60% 높이(하단 UI/링크 영역 회피), 굵은 외곽선+그림자.
- 공정위 표시문구: 인트로 0~2.5s 상단 고정(명세 2-1 위치 강제).
"""
from __future__ import annotations

import logging
from pathlib import Path

from ..config import Settings
from ..models import VideoJob
from ..utils import HEIGHT, WIDTH, run_ffmpeg
from .base import CaptionProvider

logger = logging.getLogger("shorts_agent")

_HEADER = """[Script Info]
ScriptType: v4.00+
PlayResX: {w}
PlayResY: {h}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Main,{font},76,&H00FFFFFF,&H000000FF,&H00101010,&H96000000,1,0,0,0,100,100,0,0,1,6,3,2,90,90,60,1
Style: Disc,{font},38,&H00FFFFFF,&H000000FF,&H00202020,&HB4000000,1,0,0,0,100,100,0,0,1,4,2,8,40,40,40,1

[Events]
Format: Layer, Start, End, Style, MarginL, MarginR, MarginV, Effect, Text
"""

# 하단(Alignment=2) 기준 MarginV: 클수록 위로 올라감. 안전영역(하단 UI/링크) 회피.
_MAIN_MARGINV = int(HEIGHT * 0.40)   # 화면 약 60% 지점
_CTA_MARGINV = int(HEIGHT * 0.28)    # 화면 약 72% 지점
_FONT_NAME = "NanumGothic"


def _ts(t: float) -> str:
    t = max(0.0, t)
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def _esc(text: str) -> str:
    return text.replace("\n", " ").replace("{", "(").replace("}", ")").strip()


class ASSCaptionProvider(CaptionProvider):
    def __init__(self, settings: Settings):
        self.s = settings

    def _build_ass(self, job: VideoJob, dest: Path) -> Path:
        script = job.script
        assert script
        total = job.voice_duration or 30.0
        lines = [l for l in (script.caption_lines or []) if l.strip()] or [script.chosen_hook]

        events: list[str] = []

        # 공정위 표시문구(상단, 0~2.5s) — 위치/문구 강제
        disc = _esc(script.disclosure_text)
        events.append(
            f"Dialogue: 0,{_ts(0)},{_ts(2.5)},Disc,,,,,"
            f"{{\\fad(150,150)}}{disc}"
        )

        # 본문 자막: 글자수 비례 타이밍, 60% 높이 고정
        weights = [max(1, len(l)) for l in lines]
        wsum = sum(weights)
        acc = 0.0
        for line, w in zip(lines, weights):
            start = total * (acc / wsum)
            acc += w
            end = total * (acc / wsum)
            txt = _esc(line)
            events.append(
                f"Dialogue: 0,{_ts(start)},{_ts(end)},Main,90,90,{_MAIN_MARGINV},,"
                f"{{\\fad(80,80)}}{txt}"
            )

        # CTA 강조(마지막 1.8s, 노란 키컬러)
        if script.cta:
            events.append(
                f"Dialogue: 1,{_ts(max(0, total - 1.8))},{_ts(total)},Main,90,90,{_CTA_MARGINV},,"
                f"{{\\c&H0033FFFF&\\fad(80,0)}}{_esc(script.cta)}"
            )

        dest.write_text(
            _HEADER.format(w=WIDTH, h=HEIGHT, font=_FONT_NAME) + "\n".join(events) + "\n",
            encoding="utf-8",
        )
        return dest

    def stylize(self, job: VideoJob, workdir) -> str:
        workdir = Path(workdir)
        ass = self._build_ass(job, workdir / "captions.ass")
        out = Path(self.s.output_dir) / f"{job.job_id}.mp4"
        fontsdir = str(self.s.font_path.parent)
        # ass 필터 인자: 경로 내 특수문자 이스케이프
        ass_arg = str(ass).replace("\\", "/").replace(":", r"\:")
        fonts_arg = fontsdir.replace("\\", "/").replace(":", r"\:")
        vf = f"ass={ass_arg}:fontsdir={fonts_arg}"
        run_ffmpeg(
            ["-i", job.raw_video_path, "-vf", vf,
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
             "-c:a", "copy", str(out)],
            desc="burn_captions",
        )
        job.note(f"자막/표시문구 합성 완료: {out.name}")
        return str(out)
