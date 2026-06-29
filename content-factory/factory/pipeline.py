"""Render one dialogue short end-to-end.

  script -> audio (multi-voice TTS) -> base frame -> subtitles -> composite
         -> metadata + thumbnail
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from . import audio, compositor, frame, frame_scene, metadata, subtitles
from . import layout as L
from .config import ROOT, Settings
from .script_model import Script


@dataclass
class RenderResult:
    video: str
    thumbnail: str
    metadata_path: str
    duration: float
    out_dir: str


def render_video(script: Script, settings: Settings,
                 out_dir: str | None = None, keep_intermediate: bool = False) -> RenderResult:
    errs = script.validate()
    if errs:
        raise ValueError(f"invalid script {script.id}: {errs}")

    out_dir = out_dir or str(ROOT / "output" / script.id)
    Path(out_dir).mkdir(parents=True, exist_ok=True)

    audio_res = audio.build(script, settings, out_dir)
    video = str(Path(out_dir) / f"{script.id}.mp4")
    music = os.environ.get("MUSIC_PATH")

    if settings.video_format == "scene":
        base_png = frame_scene.render_base(script, settings, out_dir)
        ass_path = subtitles.build_ass(audio_res.segments, settings,
                                       str(Path(out_dir) / "subs.ass"),
                                       positions=L.scene_caption_pos())
        compositor.render_scene(base_png, audio_res.path, audio_res.segments, ass_path,
                                video, settings, audio_res.total, music_path=music)
    else:
        base_png = frame.render_base(script, settings, out_dir)
        ass_path = subtitles.build_ass(audio_res.segments, settings,
                                       str(Path(out_dir) / "subs.ass"))
        compositor.render(base_png, audio_res.path, audio_res.segments, ass_path,
                          video, settings, audio_res.total, music_path=music)

    meta = metadata.build_metadata(script)
    meta["duration"] = audio_res.total
    meta_path = metadata.write_sidecar(meta, out_dir)
    thumb = metadata.grab_thumbnail(video, audio_res.segments,
                                    str(Path(out_dir) / "thumbnail.png"))

    if not keep_intermediate:
        _cleanup(out_dir)

    return RenderResult(video=video, thumbnail=thumb, metadata_path=meta_path,
                        duration=audio_res.total, out_dir=out_dir)


def _cleanup(out_dir: str) -> None:
    p = Path(out_dir)
    for pat in ("line_*.wav", "sil_*.wav", "concat.txt", "frame.html", "frame_scene.html"):
        for f in p.glob(pat):
            f.unlink(missing_ok=True)
