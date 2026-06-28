"""FFmpeg 래퍼 및 공용 유틸."""
from __future__ import annotations

import logging
import re
import subprocess
from functools import lru_cache
from pathlib import Path

logger = logging.getLogger("shorts_agent")

WIDTH, HEIGHT = 1080, 1920   # 쇼츠 9:16
FPS = 30


@lru_cache(maxsize=1)
def ffmpeg_bin() -> str:
    """imageio-ffmpeg 의 정적 바이너리를 우선 사용, 없으면 PATH의 ffmpeg."""
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"


def run_ffmpeg(args: list[str], *, desc: str = "ffmpeg") -> None:
    """ffmpeg 실행. 실패 시 stderr 일부를 담아 예외."""
    cmd = [ffmpeg_bin(), "-hide_banner", "-loglevel", "error", "-y", *args]
    logger.debug("%s: %s", desc, " ".join(cmd))
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        tail = (proc.stderr or "").strip().splitlines()[-8:]
        raise RuntimeError(f"{desc} 실패(rc={proc.returncode}):\n" + "\n".join(tail))


def media_duration(path: str | Path) -> float:
    """ffmpeg 로 미디어 길이(초) 추출 (ffprobe 없이 stderr 파싱)."""
    cmd = [ffmpeg_bin(), "-hide_banner", "-i", str(path)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", proc.stderr or "")
    if not m:
        return 0.0
    h, mnt, sec = int(m.group(1)), int(m.group(2)), float(m.group(3))
    return h * 3600 + mnt * 60 + sec


def is_video(path: str) -> bool:
    return Path(path).suffix.lower() in {".mp4", ".mov", ".webm", ".mkv", ".m4v"}


# 라벨용 ASS 헤더 (libass — 이 정적 빌드는 drawtext 미지원, ass 만 가능)
_LABEL_ASS = """[Script Info]
ScriptType: v4.00+
PlayResX: {w}
PlayResY: {h}
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, BorderStyle, Outline, Shadow, Alignment, Encoding
Style: Lbl,{font},62,&H00FFFFFF,&H00101010,&H64000000,1,1,4,2,5,1
Style: Sub,{font},36,&H00D6C8C8,&H00101010,&H64000000,0,1,3,1,5,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
{events}
"""

_FONT_NAME = "NanumGothic"


def _ass_escape(text: str) -> str:
    return text.replace("\n", " ").replace("{", "(").replace("}", ")").strip()


def _ass_filter_path(p: str | Path) -> str:
    """ass/subtitles 필터 인자용 경로 이스케이프."""
    return str(p).replace("\\", "/").replace(":", r"\:")


def burn_ass(base_args: list[str], ass_path: Path, fontsdir: Path, out: Path,
             *, reencode_audio: str = "copy") -> Path:
    """주어진 입력(base_args)에 ASS 자막을 굽는다."""
    vf = f"ass={_ass_filter_path(ass_path)}:fontsdir={_ass_filter_path(fontsdir)}"
    run_ffmpeg(
        [*base_args, "-vf", vf, "-c:v", "libx264", "-preset", "veryfast",
         "-crf", "20", "-c:a", reencode_audio, str(out)],
        desc="burn_ass",
    )
    return out


def make_solid_clip(
    out: Path, text: str, color: str, duration: float, font: Path,
    *, sub: str = "", size: tuple[int, int] = (WIDTH, HEIGHT),
) -> Path:
    """단색 배경 + 라벨 텍스트 클립 생성 (mock 에셋/플레이스홀더용, libass 사용)."""
    w, h = size
    events = [
        f"Dialogue: 0,0:00:00.00,9:59:59.99,Lbl,,0,0,0,,"
        f"{{\\an5\\pos({w // 2},{int(h * 0.46)})}}{_ass_escape(text)}"
    ]
    if sub:
        events.append(
            f"Dialogue: 0,0:00:00.00,9:59:59.99,Sub,,0,0,0,,"
            f"{{\\an5\\pos({w // 2},{int(h * 0.54)})}}{_ass_escape(sub)}"
        )
    ass = out.with_suffix(".lbl.ass")
    ass.write_text(
        _LABEL_ASS.format(w=w, h=h, font=_FONT_NAME, events="\n".join(events)),
        encoding="utf-8",
    )
    vf = f"ass={_ass_filter_path(ass)}:fontsdir={_ass_filter_path(font.parent)}"
    run_ffmpeg(
        [
            "-f", "lavfi", "-i", f"color=c={color}:s={w}x{h}:r={FPS}",
            "-t", f"{duration:.3f}", "-vf", vf,
            "-pix_fmt", "yuv420p", str(out),
        ],
        desc="make_solid_clip",
    )
    ass.unlink(missing_ok=True)
    return out


def normalize_clip(
    src: str, out: Path, duration: float, font: Path,
    *, size: tuple[int, int] = (WIDTH, HEIGHT),
) -> Path:
    """임의 이미지/영상 소스를 9:16 규격, 지정 길이의 무음 클립으로 정규화."""
    w, h = size
    scale_crop = (
        f"scale={w}:{h}:force_original_aspect_ratio=increase,"
        f"crop={w}:{h},setsar=1,fps={FPS}"
    )
    if is_video(src):
        args = [
            "-stream_loop", "-1", "-i", src, "-t", f"{duration:.3f}",
            "-vf", scale_crop, "-an", "-pix_fmt", "yuv420p", str(out),
        ]
    else:  # 이미지 → 정지 클립
        args = [
            "-loop", "1", "-i", src, "-t", f"{duration:.3f}",
            "-vf", scale_crop, "-pix_fmt", "yuv420p", str(out),
        ]
    run_ffmpeg(args, desc="normalize_clip")
    return out


def concat_clips(clips: list[Path], out: Path) -> Path:
    """동일 규격 클립들을 concat demuxer 로 이어붙임."""
    listfile = out.with_suffix(".txt")
    listfile.write_text("".join(f"file '{c.resolve()}'\n" for c in clips), encoding="utf-8")
    run_ffmpeg(
        ["-f", "concat", "-safe", "0", "-i", str(listfile),
         "-c", "copy", str(out)],
        desc="concat_clips",
    )
    listfile.unlink(missing_ok=True)
    return out


def mux_audio(video: Path, audio: str, out: Path, *, music: str | None = None) -> Path:
    """무음 영상에 나레이션(+선택 배경음악 덕킹) 결합. 영상 길이에 맞춰 종료."""
    if music:
        args = [
            "-i", str(video), "-i", audio, "-i", music,
            "-filter_complex",
            "[2:a]volume=0.12[bg];[1:a][bg]amix=inputs=2:duration=first:dropout_transition=2[a]",
            "-map", "0:v", "-map", "[a]",
            "-c:v", "copy", "-c:a", "aac", "-shortest", str(out),
        ]
    else:
        args = [
            "-i", str(video), "-i", audio,
            "-map", "0:v", "-map", "1:a",
            "-c:v", "copy", "-c:a", "aac", "-shortest", str(out),
        ]
    run_ffmpeg(args, desc="mux_audio")
    return out


def silent_audio(out: Path, duration: float) -> Path:
    """무음 트랙 생성 (mock TTS / 폴백용)."""
    run_ffmpeg(
        ["-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
         "-t", f"{duration:.3f}", "-c:a", "aac", str(out)],
        desc="silent_audio",
    )
    return out
