"""Timed English subtitles (ASS), colored per speaker, big and kinetic.

The subtitle is the retention driver (most viewers watch on mute), so it is
large, high-contrast, centered, and pops in on each line.
"""
from __future__ import annotations

from pathlib import Path

from . import layout as L
from .config import Settings


def _ass_color(hex_rgb: str) -> str:
    h = hex_rgb.lstrip("#")
    r, g, b = h[0:2], h[2:4], h[4:6]
    return f"&H00{b}{g}{r}".upper()


def _ts(seconds: float) -> str:
    seconds = max(0.0, seconds)
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def _wrap(text: str, max_chars: int = 19, max_lines: int = 3) -> str:
    words, lines, cur = text.split(), [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > max_chars:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        lines.append(cur)
    if len(lines) > max_lines:  # re-balance: allow slightly longer lines
        return _wrap(text, max_chars + 4, max_lines + 1) if max_chars < 32 else "\\N".join(lines)
    return "\\N".join(lines)


def build_ass(segments, settings: Settings, out_path: str,
              positions: dict | None = None) -> str:
    """positions: optional {"A": (cx,cy), "B": (cx,cy)} to place each speaker's
    caption (used by the scene format). Defaults to the single CAPTION spot."""
    size = L.CAPTION["size"]
    margin = (L.W - L.CAPTION["max_w"]) // 2
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {L.W}
PlayResY: {L.H}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, Italic, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,{settings.caption_font},{size},&H00FFFFFF,&H00000000,&H80000000,-1,0,1,6,3,5,{margin},{margin},0,1

[Events]
Format: Layer, Start, End, Style, MarginL, MarginR, MarginV, Effect, Text
"""
    default = (L.CAPTION["cx"], L.CAPTION["cy"])
    rows = []
    for seg in segments:
        cx, cy = (positions or {}).get(seg.speaker, default)
        color = _ass_color(settings.speaker_color(seg.speaker))
        text = _wrap(seg.en)
        over = f"\\an5\\pos({cx},{cy})\\c{color}\\fad(90,50)"
        rows.append(f"Dialogue: 0,{_ts(seg.start)},{_ts(seg.end)},Cap,0,0,0,,{{{over}}}{text}")
    Path(out_path).write_text(header + "\n".join(rows) + "\n", encoding="utf-8")
    return out_path
