"""자막 스타일링 (모듈 F). libass 로 'CapCut 풍' 동적 자막 + 공정위 표시.

- 나레이션 단어 타임스탬프(voice_timestamps)에 맞춘 **카라오케 단어 하이라이트**
  (현재 발화 단어가 노란색으로 채워짐) + 등장 시 팝(scale) 애니메이션.
- 후킹(첫 구절)은 더 크게/강하게. CTA 는 마지막에 컬러 팝.
- 모바일 안전영역(하단 UI/링크 회피) + 굵은 외곽선/그림자/블러로 가독성 확보.
- 인트로 0~2.5초 상단에 공정위 표시문구 고정(위치 강제).
"""
from __future__ import annotations

import logging
import re
from pathlib import Path

from ..config import Settings
from ..models import VideoJob
from ..utils import HEIGHT, WIDTH, _ass_filter_path, run_ffmpeg
from .base import CaptionProvider

logger = logging.getLogger("shorts_agent")

# 폰트 미지원 글자(이모지 등) → tofu 방지 위해 제거
_EMOJI = re.compile(
    "[\U0001F000-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF"
    "\U00002190-\U000021FF\U00002B00-\U00002BFF️⃣]"
)

_HEADER = """[Script Info]
ScriptType: v4.00+
PlayResX: {w}
PlayResY: {h}
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Hook,{font},94,&H0000F0FF,&H00FFFFFF,&H00101010,&HA0000000,1,0,0,0,100,100,1,0,1,7,4,5,70,70,0,1
Style: Body,{font},78,&H0000F0FF,&H00FFFFFF,&H00141414,&H96000000,1,0,0,0,100,100,0.5,0,1,6,3,5,90,90,0,1
Style: Cta,{font},82,&H00F5FF00,&H00FFFFFF,&H00101010,&HA0000000,1,0,0,0,100,100,1,0,1,7,4,5,80,80,0,1
Style: Disc,{font},34,&H00E8E8E8,&H000000FF,&H00202020,&HB4000000,0,0,0,0,100,100,0,0,1,3,2,8,40,40,46,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

_FONT_NAME = "NanumGothic"
_CX = WIDTH // 2
_Y_MAIN = int(HEIGHT * 0.60)   # 본문 자막 세로 위치(안전영역)
_Y_CTA = int(HEIGHT * 0.74)


def _ts(t: float) -> str:
    t = max(0.0, t)
    return f"{int(t // 3600)}:{int((t % 3600) // 60):02d}:{t % 60:05.2f}"


def _esc(text: str) -> str:
    text = _EMOJI.sub("", text)
    return text.replace("\n", " ").replace("{", "(").replace("}", ")").strip()


def _group_words(words: list[dict], max_chars: int = 11, max_words: int = 4) -> list[list[dict]]:
    """단어들을 짧은 구절(2~4단어)로 묶음. 문장부호에서 끊음."""
    phrases: list[list[dict]] = []
    cur: list[dict] = []
    clen = 0
    for w in words:
        token = str(w.get("word", ""))
        cur.append(w)
        clen += len(token)
        ends = token[-1:] in {".", "!", "?", "…", ",", "。"}
        if clen >= max_chars or len(cur) >= max_words or ends:
            phrases.append(cur)
            cur, clen = [], 0
    if cur:
        phrases.append(cur)
    return phrases


def _karaoke_line(words: list[dict], style: str, *, pop: str, layer: int = 0,
                  y: int = _Y_MAIN) -> str:
    start = float(words[0].get("start", 0.0))
    end = float(words[-1].get("end", start + 1.0))
    parts = []
    for i, w in enumerate(words):
        ws = float(w.get("start", start))
        if i + 1 < len(words):
            dur = float(words[i + 1].get("start", ws)) - ws
        else:
            dur = float(w.get("end", ws)) - ws
        cs = max(6, round(dur * 100))
        parts.append(f"{{\\kf{cs}}}{_esc(str(w.get('word', '')))} ")
    text = "".join(parts).strip()
    override = f"{{\\an5\\pos({_CX},{y})\\fad(70,40){pop}\\blur1}}"
    return (f"Dialogue: {layer},{_ts(start)},{_ts(end)},{style},,0,0,0,,{override}{text}")


class ASSCaptionProvider(CaptionProvider):
    def __init__(self, settings: Settings):
        self.s = settings

    def _build_ass(self, job: VideoJob, dest: Path) -> Path:
        script = job.script
        assert script
        total = job.voice_duration or 30.0
        events: list[str] = []

        # 1) 공정위 표시문구(상단, 0~2.5s) — 위치/문구 강제
        events.append(
            f"Dialogue: 0,{_ts(0)},{_ts(min(2.6, total))},Disc,,0,0,0,,"
            f"{{\\fad(150,150)}}{_esc(script.disclosure_text)}"
        )

        # 2) 본문 자막: 단어 타임스탬프 → 카라오케 / 없으면 caption_lines 폴백
        words = job.voice_timestamps or []
        if words:
            phrases = _group_words(words)
            for idx, ph in enumerate(phrases):
                if idx == 0:
                    pop = "\\fscx72\\fscy72\\t(0,200,\\fscx100\\fscy100)"
                    events.append(_karaoke_line(ph, "Hook", pop=pop, layer=0))
                else:
                    pop = "\\fscx88\\fscy88\\t(0,140,\\fscx100\\fscy100)"
                    events.append(_karaoke_line(ph, "Body", pop=pop, layer=0))
        else:
            events += self._fallback_lines(script, total)

        # 3) CTA(마지막 ~2.2s, 컬러 팝)
        if script.cta:
            cstart = max(0.0, total - 2.2)
            pop = "\\fscx70\\fscy70\\t(0,180,\\fscx106\\fscy106)\\t(180,260,\\fscx100\\fscy100)"
            events.append(
                f"Dialogue: 2,{_ts(cstart)},{_ts(total)},Cta,,0,0,0,,"
                f"{{\\an5\\pos({_CX},{_Y_CTA})\\fad(80,0){pop}\\blur1}}{_esc(script.cta)}"
            )

        dest.write_text(
            _HEADER.format(w=WIDTH, h=HEIGHT, font=_FONT_NAME) + "\n".join(events) + "\n",
            encoding="utf-8",
        )
        return dest

    def _fallback_lines(self, script, total: float) -> list[str]:
        lines = [l for l in (script.caption_lines or []) if l.strip()] or [script.chosen_hook]
        weights = [max(1, len(l)) for l in lines]
        wsum = sum(weights)
        acc = 0.0
        ev = []
        for i, (line, w) in enumerate(zip(lines, weights)):
            start = total * (acc / wsum)
            acc += w
            end = total * (acc / wsum)
            style = "Hook" if i == 0 else "Body"
            pop = "\\fscx84\\fscy84\\t(0,160,\\fscx100\\fscy100)"
            ev.append(
                f"Dialogue: 0,{_ts(start)},{_ts(end)},{style},,0,0,0,,"
                f"{{\\an5\\pos({_CX},{_Y_MAIN})\\fad(70,40){pop}\\blur1}}{_esc(line)}"
            )
        return ev

    def stylize(self, job: VideoJob, workdir) -> str:
        workdir = Path(workdir)
        ass = self._build_ass(job, workdir / "captions.ass")
        out = Path(self.s.output_dir) / f"{job.job_id}.mp4"
        vf = (f"ass={_ass_filter_path(ass)}:"
              f"fontsdir={_ass_filter_path(self.s.font_path.parent)}")
        run_ffmpeg(
            ["-i", job.raw_video_path, "-vf", vf,
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
             "-c:a", "copy", str(out)],
            desc="burn_captions",
        )
        job.note(f"동적 자막+표시문구 합성: {out.name}")
        return str(out)
