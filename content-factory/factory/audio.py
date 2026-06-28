"""Assemble per-line TTS clips into one conversation track + a sync timeline.

Layout on the timeline:
  [lead_in silence] line0 [gap] line1 [gap] ... lineN [lead_out silence]

Returns the combined WAV path, the total duration, and a list of segments
(one per line) with absolute start/end times used to drive captions and the
active-speaker highlight.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from . import tts
from .config import Settings
from .ffmpeg_util import ffmpeg_exe, run
from .script_model import Script

AR = "44100"


@dataclass
class Segment:
    index: int
    speaker: str       # "A" | "B"
    start: float
    end: float
    en: str
    emote: str


@dataclass
class AudioResult:
    path: str
    total: float
    segments: list


def _silence(dur: float, out: str) -> str:
    run([ffmpeg_exe(), "-y", "-f", "lavfi",
         "-i", f"anullsrc=r={AR}:cl=stereo", "-t", f"{dur:.3f}", out])
    return out


def build(script: Script, settings: Settings, out_dir: str) -> AudioResult:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    parts: list[str] = []
    segments: list[Segment] = []
    t = 0.0

    if settings.lead_in > 0:
        parts.append(_silence(settings.lead_in, str(out / "sil_in.wav")))
        t += settings.lead_in

    sil_gap = _silence(settings.gap, str(out / "sil_gap.wav")) if settings.gap > 0 else None

    for i, line in enumerate(script.lines):
        char = script.char(line.speaker)
        clip, dur = tts.synthesize_line(line, char, i, str(out), settings)
        segments.append(Segment(i, line.speaker, round(t, 3), round(t + dur, 3),
                                line.en, line.emote))
        parts.append(clip)
        t += dur
        if sil_gap and i < len(script.lines) - 1:
            parts.append(sil_gap)
            t += settings.gap

    if settings.lead_out > 0:
        parts.append(_silence(settings.lead_out, str(out / "sil_out.wav")))
        t += settings.lead_out

    # concat (all parts share 44.1kHz/stereo)
    listfile = out / "concat.txt"
    listfile.write_text("".join(f"file '{Path(p).resolve()}'\n" for p in parts),
                        encoding="utf-8")
    full = str(out / "voice_track.wav")
    run([ffmpeg_exe(), "-y", "-f", "concat", "-safe", "0", "-i", str(listfile),
         "-c", "copy", full])

    return AudioResult(path=full, total=round(t, 3), segments=segments)
