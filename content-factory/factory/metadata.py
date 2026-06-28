"""Publishing metadata + a thumbnail grab for each video."""
from __future__ import annotations

import json
from pathlib import Path

from .ffmpeg_util import ffmpeg_exe, run
from .script_model import Script


def build_metadata(script: Script) -> dict:
    title = script.title_en.replace("\n", " ").strip()
    tags = script.hashtags
    hashtag_str = " ".join(f"#{t}" for t in (tags + ["shorts", "korean", "funny"]))
    description = (
        f"{script.description_en}\n\n"
        f"😂 Cute & funny Korean call skit — English subtitles.\n"
        f"🔔 Follow for a new one every day!\n\n{hashtag_str}"
    )
    return {
        "title": (title + " 😂 #shorts")[:100],
        "description": description,
        "tags": tags,
        "category": "Comedy",
        "language_audio": "ko",
        "language_subtitles": "en",
    }


def grab_thumbnail(video: str, segments, out_png: str) -> str:
    """Grab a frame from a punchy moment (prefer a laugh/pout line)."""
    pick = None
    for s in segments:
        if s.emote in ("pout", "laugh", "surprised"):
            pick = s
            break
    pick = pick or (segments[len(segments) // 2] if segments else None)
    t = (pick.start + pick.end) / 2 if pick else 1.0
    run([ffmpeg_exe(), "-y", "-ss", f"{t:.2f}", "-i", video,
         "-frames:v", "1", out_png])
    return out_png


def write_sidecar(meta: dict, out_dir: str) -> str:
    path = Path(out_dir) / "metadata.json"
    path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(path)
