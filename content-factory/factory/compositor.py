"""Composite the final vertical short with ffmpeg.

base frame PNG  +  live waveform (showwaves from the real audio)
              +  active-speaker highlight (the non-speaker is dimmed)
              +  timed English subtitles (ASS)
              +  the conversation audio (+ optional background music)
"""
from __future__ import annotations

import os

from . import layout as L
from .config import Settings
from .ffmpeg_util import ffmpeg_exe, run


def _enable_expr(segments, speaker: str) -> str:
    spans = [f"between(t,{s.start},{s.end})" for s in segments if s.speaker == speaker]
    return "+".join(spans) if spans else "0"


def _escape_ass(path: str) -> str:
    return path.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")


def render(base_png: str, voice_track: str, segments, ass_path: str,
           out_path: str, settings: Settings, total: float,
           music_path: str | None = None) -> str:
    ax, ay, aw, ah = L.avatar_box("A")
    bx, by, bw, bh = L.avatar_box("B")
    dim = round(1.0 - settings.dim_inactive, 2)          # overlay alpha
    enA = _enable_expr(segments, "B")  # dim A while B speaks
    enB = _enable_expr(segments, "A")  # dim B while A speaks

    ww, wh = L.WAVEFORM["w"], L.WAVEFORM["h"]
    wx, wy = L.WAVEFORM["cx"] - ww // 2, L.WAVEFORM["cy"] - wh // 2
    wcolor = f"0x{settings.waveform_color}"
    ass = _escape_ass(os.path.abspath(ass_path))

    inputs = ["-loop", "1", "-i", base_png, "-i", voice_track]
    has_music = bool(music_path and os.path.exists(music_path))
    if has_music:
        inputs += ["-stream_loop", "-1", "-i", music_path]

    fc = (
        f"[0:v]scale={L.W}:{L.H},setsar=1,format=rgba[bg];"
        f"[bg]drawbox=x={ax}:y={ay}:w={aw}:h={ah}:color=black@{dim}:t=fill:enable='{enA}',"
        f"drawbox=x={bx}:y={by}:w={bw}:h={bh}:color=black@{dim}:t=fill:enable='{enB}'[bgd];"
        f"[1:a]asplit=2[awav][aout];"
        # render the waveform at half-res then upscale -> a bolder, smoother line.
        f"[awav]volume=2.6,showwaves=s={ww // 2}x{wh // 2}:mode=cline:colors={wcolor}:"
        f"rate={settings.fps}:scale=sqrt,scale={ww}:{wh}:flags=bicubic,"
        f"format=rgba,colorkey=0x000000:0.32:0.08[wave];"
        f"[bgd][wave]overlay={wx}:{wy}[bgw];"
        f"[bgw]ass='{ass}',format=yuv420p[v]"
    )
    if has_music:
        fc += (";[2:a]volume=0.10,aformat=sample_rates=44100:channel_layouts=stereo[mus];"
               "[aout][mus]amix=inputs=2:duration=first:dropout_transition=0[a]")
        amap = "[a]"
    else:
        amap = "[aout]"

    cmd = [
        ffmpeg_exe(), "-y", *inputs,
        "-filter_complex", fc,
        "-map", "[v]", "-map", amap,
        "-t", f"{total:.2f}",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-pix_fmt", "yuv420p", "-r", str(settings.fps),
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart", out_path,
    ]
    run(cmd)
    return out_path
