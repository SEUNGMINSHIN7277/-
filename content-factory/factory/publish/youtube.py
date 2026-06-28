"""Upload a finished short to YouTube via the Data API v3.

One-time setup (see README): create OAuth client creds, run the helper once to
mint a refresh token, then set env:
  YOUTUBE_CLIENT_SECRETS=/path/client_secret.json
  YOUTUBE_TOKEN=/path/token.json   (created on first auth)
Uploads are PRIVATE by default; flip YOUTUBE_PRIVACY=public when you trust it.
"""
from __future__ import annotations

import os


def _service():
    from google.oauth2.credentials import Credentials  # type: ignore
    from googleapiclient.discovery import build  # type: ignore

    token = os.environ["YOUTUBE_TOKEN"]
    creds = Credentials.from_authorized_user_file(
        token, ["https://www.googleapis.com/auth/youtube.upload"])
    return build("youtube", "v3", credentials=creds)


def upload(video: str, thumbnail: str, meta: dict) -> dict:
    from googleapiclient.http import MediaFileUpload  # type: ignore

    yt = _service()
    body = {
        "snippet": {
            "title": meta["title"],
            "description": meta["description"],
            "tags": meta.get("tags", []),
            "categoryId": "23",  # Comedy
        },
        "status": {
            "privacyStatus": os.environ.get("YOUTUBE_PRIVACY", "private"),
            "selfDeclaredMadeForKids": False,
        },
    }
    req = yt.videos().insert(
        part="snippet,status", body=body,
        media_body=MediaFileUpload(video, chunksize=-1, resumable=True))
    resp = req.execute()
    vid = resp["id"]
    if thumbnail and os.path.exists(thumbnail):
        try:
            from googleapiclient.http import MediaFileUpload as MFU
            yt.thumbnails().set(videoId=vid, media_body=MFU(thumbnail)).execute()
        except Exception as exc:  # non-fatal (thumbnails need verified channel)
            print(f"[youtube] thumbnail skipped: {exc}")
    url = f"https://youtube.com/shorts/{vid}"
    print(f"[youtube] uploaded {url}")
    return {"id": vid, "url": url}
