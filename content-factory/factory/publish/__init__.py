"""Publish dispatcher. Currently supports YouTube; extend for TikTok/Reels."""
from __future__ import annotations

from ..config import Settings


def publish(video: str, thumbnail: str, meta: dict, settings: Settings) -> dict | None:
    if settings.publish_provider == "youtube":
        from . import youtube
        return youtube.upload(video, thumbnail, meta)
    return None
