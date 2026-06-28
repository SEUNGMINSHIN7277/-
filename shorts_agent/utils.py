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


# ======================================================================
#  동적 비주얼 엔진 (모션 배경 + 켄번스 + 제품 카드 + 트랜지션)
#  ※ 이 FFmpeg 정적 빌드는 drawtext 미지원 → 텍스트는 전부 libass.
# ======================================================================

# 모던한 그라데이션 컬러쌍 풀 (cut 별 로테이션)
GRADIENT_PAIRS = [
    ("0x141E30", "0x3A1C71"),  # 네이비→퍼플
    ("0x0F2027", "0x2C5364"),  # 딥틸
    ("0x42275a", "0x734b6d"),  # 플럼
    ("0x1a2a6c", "0xb21f1f"),  # 블루→레드
    ("0x000428", "0x004e92"),  # 미드나잇 블루
    ("0x3E1E68", "0xD76D77"),  # 바이올렛→로즈
    ("0x16222A", "0x3A6073"),  # 그래파이트
]
_TRANSITIONS = ["fade", "slideleft", "slideright", "smoothup", "wipeleft",
                "circleopen", "fadeblack", "slideup"]


def gradient_image(out: Path, c0: str, c1: str, label: str, font: Path,
                   *, sub: str = "", size: tuple[int, int] = (1080, 1350),
                   gtype: str = "radial") -> Path:
    """그라데이션 배경 + 라벨을 한 장의 이미지로 (mock 제품/소스 컷 대용)."""
    w, h = size
    # 라벨이 없으면 깨끗한 그라데이션만 생성(실 b-roll 처럼)
    if not label and not sub:
        run_ffmpeg(["-f", "lavfi", "-i", f"gradients=s={w}x{h}:c0={c0}:c1={c1}:type={gtype}:rate=1",
                    "-frames:v", "1", str(out)], desc="gradient_image")
        return out
    events = [f"Dialogue: 0,0:00:00.00,9:59:59.99,Lbl,,0,0,0,,"
              f"{{\\an5\\pos({w // 2},{int(h * 0.46)})}}{_ass_escape(label)}"]
    if sub:
        events.append(f"Dialogue: 0,0:00:00.00,9:59:59.99,Sub,,0,0,0,,"
                      f"{{\\an5\\pos({w // 2},{int(h * 0.56)})}}{_ass_escape(sub)}")
    ass = out.with_suffix(".lbl.ass")
    ass.write_text(_LABEL_ASS.format(w=w, h=h, font=_FONT_NAME, events="\n".join(events)),
                   encoding="utf-8")
    vf = (f"gradients=s={w}x{h}:c0={c0}:c1={c1}:type={gtype}:rate=1,"
          f"ass={_ass_filter_path(ass)}:fontsdir={_ass_filter_path(font.parent)}")
    run_ffmpeg(["-f", "lavfi", "-i", f"gradients=s={w}x{h}:c0={c0}:c1={c1}:type={gtype}:rate=1",
                "-vf", f"ass={_ass_filter_path(ass)}:fontsdir={_ass_filter_path(font.parent)}",
                "-frames:v", "1", str(out)], desc="gradient_image")
    ass.unlink(missing_ok=True)
    return out


def gradient_motion_clip(out: Path, c0: str, c1: str, duration: float,
                         *, gtype: str = "radial", speed: float = 0.012) -> Path:
    """움직이는 그라데이션 배경 클립 (소스 없을 때의 고급 플레이스홀더)."""
    run_ffmpeg(
        ["-f", "lavfi",
         "-i", (f"gradients=s={WIDTH}x{HEIGHT}:c0={c0}:c1={c1}:type={gtype}:"
                f"speed={speed}:duration={duration:.3f}:rate={FPS}"),
         "-t", f"{duration:.3f}", "-vf", "vignette,format=yuv420p", str(out)],
        desc="gradient_motion_clip",
    )
    return out


def ken_burns_clip(src_img: str, out: Path, duration: float, *, idx: int = 0) -> Path:
    """이미지에 켄번스(서서히 줌인) + 비네팅 + 채도 보정."""
    frames = max(2, int(duration * FPS))
    sw, sh = int(WIDTH * 1.5), int(HEIGHT * 1.5)
    zmax = 1.18 + (idx % 3) * 0.05
    spd = 0.0012 + (idx % 2) * 0.0004
    vf = (
        f"scale={sw}:{sh}:force_original_aspect_ratio=increase,crop={sw}:{sh},"
        f"zoompan=z='min(zoom+{spd},{zmax})':d={frames}:"
        f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={WIDTH}x{HEIGHT}:fps={FPS},"
        f"vignette,eq=saturation=1.12,format=yuv420p"
    )
    run_ffmpeg(["-loop", "1", "-i", src_img, "-t", f"{duration:.3f}", "-vf", vf, str(out)],
               desc="ken_burns_clip")
    return out


def product_card_clip(src_img: str, out: Path, duration: float) -> Path:
    """제품 쇼케이스: 블러 배경 + 선명한 제품 + 느린 줌(전환 강조)."""
    frames = max(2, int(duration * FPS))
    fc = (
        f"[0]scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase,crop={WIDTH}:{HEIGHT},"
        f"gblur=sigma=42,eq=brightness=-0.12:saturation=1.1[bg];"
        f"[0]scale={int(WIDTH * 0.74)}:-1[fg];"
        f"[bg][fg]overlay=(W-w)/2:(H-h)/2,"
        f"zoompan=z='min(zoom+0.0008,1.10)':d={frames}:"
        f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={WIDTH}x{HEIGHT}:fps={FPS},"
        f"vignette,format=yuv420p"
    )
    run_ffmpeg(["-loop", "1", "-i", src_img, "-t", f"{duration:.3f}",
                "-filter_complex", fc, str(out)], desc="product_card_clip")
    return out


def video_motion_clip(src: str, out: Path, duration: float) -> Path:
    """실 영상 소스: 9:16 커버 크롭 + 비네팅/채도(무음)."""
    vf = (f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase,crop={WIDTH}:{HEIGHT},"
          f"setsar=1,fps={FPS},vignette,eq=saturation=1.1,format=yuv420p")
    run_ffmpeg(["-stream_loop", "-1", "-i", src, "-t", f"{duration:.3f}",
                "-an", "-vf", vf, str(out)], desc="video_motion_clip")
    return out


_THUMB_ASS = """[Script Info]
ScriptType: v4.00+
PlayResX: {w}
PlayResY: {h}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Tt,{font},108,&H0000F0FF,&H00101010,&HC0000000,1,1,9,5,8,70,70,150,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,9:59:59.99,Tt,,70,70,150,,{text}
"""


def make_thumbnail(out_jpg: Path, bg_image: str | None, hook: str, font: Path,
                   *, c0: str = "0x141E30", c1: str = "0x3A1C71") -> Path:
    """후킹 문구가 박힌 세로 썸네일(1080x1920) 1장 생성."""
    ass = out_jpg.with_suffix(".thumb.ass")
    ass.write_text(_THUMB_ASS.format(w=WIDTH, h=HEIGHT, font=_FONT_NAME,
                                     text=_ass_escape(hook)), encoding="utf-8")
    ass_vf = f"ass={_ass_filter_path(ass)}:fontsdir={_ass_filter_path(font.parent)}"
    if bg_image and not is_video(bg_image):
        fc = (f"[0]scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase,"
              f"crop={WIDTH}:{HEIGHT},gblur=sigma=30,eq=brightness=-0.08[bg];"
              f"[0]scale={int(WIDTH*0.72)}:-1[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2+120,"
              f"vignette,{ass_vf}")
        run_ffmpeg(["-loop", "1", "-i", bg_image, "-frames:v", "1",
                    "-filter_complex", fc, "-q:v", "3", str(out_jpg)], desc="thumbnail")
    else:
        run_ffmpeg(["-f", "lavfi", "-i", f"gradients=s={WIDTH}x{HEIGHT}:c0={c0}:c1={c1}:type=radial:rate=1",
                    "-frames:v", "1", "-vf", f"vignette,{ass_vf}", "-q:v", "3", str(out_jpg)],
                   desc="thumbnail")
    ass.unlink(missing_ok=True)
    return out_jpg


def xfade_concat(clips: list[Path], durations: list[float], out: Path,
                 *, td: float = 0.35) -> Path:
    """클립들을 xfade 트랜지션으로 연결(영상 전용). 길이=Σd - td*(n-1)."""
    if len(clips) == 1:
        run_ffmpeg(["-i", str(clips[0]), "-c", "copy", str(out)], desc="xfade_single")
        return out
    inputs: list[str] = []
    for c in clips:
        inputs += ["-i", str(c)]
    steps: list[str] = []
    prev = "0:v"
    running = durations[0]
    for i in range(1, len(clips)):
        trans = _TRANSITIONS[(i - 1) % len(_TRANSITIONS)]
        offset = max(0.0, running - td)
        label = f"v{i}" if i < len(clips) - 1 else "vout"
        steps.append(
            f"[{prev}][{i}:v]xfade=transition={trans}:duration={td:.3f}:"
            f"offset={offset:.3f}[{label}]"
        )
        prev = label
        running = running + durations[i] - td
    fc = ";".join(steps)
    run_ffmpeg([*inputs, "-filter_complex", fc, "-map", "[vout]",
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                "-pix_fmt", "yuv420p", str(out)], desc="xfade_concat")
    return out
