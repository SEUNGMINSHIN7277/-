"""Shared layout geometry (in final 1080x1920 pixel space).

frame.py renders the static chrome at these coordinates; compositor.py and
subtitles.py place the live waveform / per-line caption / speaker highlight at
the same coordinates so everything lines up.
"""
from __future__ import annotations

W, H = 1080, 1920

AVATAR_W = 344
AVATAR_H = int(AVATAR_W * 1.2)  # avatars are authored at 400x480 (ratio 1.2)

# Centers of the two diagonal avatars (pushed toward opposite corners so the
# animated waveform owns the middle of the frame).
A_CENTER = (278, 520)    # top-left speaker
B_CENTER = (802, 1230)   # bottom-right speaker

LABEL_DY = AVATAR_H // 2 + 34   # label sits below the avatar

TITLE = {"cx": 540, "top": 150, "max_w": 980, "size": 78, "line_gap": 92}

WAVEFORM = {"cx": 540, "cy": 900, "w": 840, "h": 200}

CAPTION = {"cx": 540, "cy": 1610, "max_w": 980, "size": 74}

REC = {"cx": 540, "cy": 1800}


def avatar_box(which: str) -> tuple[int, int, int, int]:
    """Return (x, y, w, h) of the avatar image box for 'A' or 'B'."""
    cx, cy = A_CENTER if which == "A" else B_CENTER
    return (cx - AVATAR_W // 2, cy - AVATAR_H // 2, AVATAR_W, AVATAR_H)


def label_pos(which: str) -> tuple[int, int]:
    cx, cy = A_CENTER if which == "A" else B_CENTER
    return (cx, cy + LABEL_DY)
