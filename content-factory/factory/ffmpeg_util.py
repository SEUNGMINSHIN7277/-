"""Locate the ffmpeg / ffprobe binaries.

We prefer a system ffmpeg if present, otherwise fall back to the static
binary bundled by the ``imageio-ffmpeg`` pip package (no apt / root needed).
"""
from __future__ import annotations

import os
import shutil
import subprocess


def ffmpeg_exe() -> str:
    env = os.environ.get("FFMPEG_BINARY")
    if env and os.path.exists(env):
        return env
    sys_ff = shutil.which("ffmpeg")
    if sys_ff:
        return sys_ff
    try:
        import imageio_ffmpeg  # type: ignore

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(
            "ffmpeg not found. Install system ffmpeg or `pip install imageio-ffmpeg`."
        ) from exc


def ffprobe_exe() -> str | None:
    """ffprobe is optional; the bundled imageio build ships ffmpeg only."""
    env = os.environ.get("FFPROBE_BINARY")
    if env and os.path.exists(env):
        return env
    return shutil.which("ffprobe")


def run(args: list[str], **kw) -> subprocess.CompletedProcess:
    """Run an ffmpeg command, raising with stderr on failure."""
    proc = subprocess.run(args, capture_output=True, text=True, **kw)
    if proc.returncode != 0:
        tail = "\n".join(proc.stderr.strip().splitlines()[-15:])
        raise RuntimeError(f"ffmpeg failed ({proc.returncode}):\n{tail}")
    return proc
