"""업로드 & 메타데이터 (모듈 G). YouTube Data API v3 videos.insert.

자동 삽입(명세 2): 제목 앞/설명 첫 줄 공정위 표시문구, 합성콘텐츠 공개 플래그.
주의: videos.insert 할당량은 2025.12.4 이후 ≈100유닛(하루 ~100개 가능). '5개'는 전략 캡.
"""
from __future__ import annotations

import logging

from ..config import Settings
from ..errors import StageError
from ..models import Stage, VideoJob
from .base import UploadProvider

logger = logging.getLogger("shorts_agent")

_SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


class YouTubeUploadProvider(UploadProvider):
    def __init__(self, settings: Settings):
        self.s = settings

    def _service(self):
        try:
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build
        except ImportError as e:
            raise StageError(
                Stage.UPLOADED, "google-api-python-client 미설치", retryable=False
            ) from e
        if not self.s.youtube_token_file:
            raise StageError(Stage.UPLOADED, "YOUTUBE_TOKEN_FILE 미설정", retryable=False)
        creds = Credentials.from_authorized_user_file(self.s.youtube_token_file, _SCOPES)
        return build("youtube", "v3", credentials=creds, cache_discovery=False)

    def _metadata(self, job: VideoJob) -> dict:
        sc = job.script
        assert sc
        disc = sc.disclosure_text
        # 제목 첫 부분에 표시문구(공정위 위치 강제), 길이 보호
        title = f"[광고] {sc.title or job.product.name}"[:100]
        desc_lines = [
            disc,                              # 설명 '첫 줄'에 표시문구
            "",
            sc.body[:300],
            "",
            f"▶ 구매/정보: {job.product.coupang_deeplink}",
            "",
            " ".join(f"#{h}" for h in (sc.hashtags or [])) + " #쇼츠 #쇼핑",
        ]
        return {
            "snippet": {
                "title": title,
                "description": "\n".join(desc_lines),
                "tags": (sc.hashtags or [])[:15],
                "categoryId": "26",  # Howto & Style
            },
            "status": {
                "privacyStatus": self.s.youtube_privacy,
                "selfDeclaredMadeForKids": False,
                # 합성/변경 콘텐츠 공개(명세 2-2)
                "containsSyntheticMedia": True,
            },
        }

    def upload(self, job: VideoJob) -> str:
        try:
            from googleapiclient.http import MediaFileUpload
        except ImportError as e:
            raise StageError(Stage.UPLOADED, "googleapiclient 미설치", retryable=False) from e
        service = self._service()
        media = MediaFileUpload(job.final_video_path, chunksize=-1, resumable=True)
        try:
            req = service.videos().insert(
                part="snippet,status", body=self._metadata(job), media_body=media
            )
            resp = None
            while resp is None:
                _, resp = req.next_chunk()
        except Exception as e:
            msg = str(e)
            retryable = "quotaExceeded" not in msg and "forbidden" not in msg.lower()
            raise StageError(Stage.UPLOADED, f"업로드 실패: {e}", retryable) from e
        vid = resp["id"]
        # 커스텀 썸네일 설정(best-effort; 권한/할당량 문제 시 무시)
        if job.thumbnail_path:
            try:
                from googleapiclient.http import MediaFileUpload as _MFU
                service.thumbnails().set(
                    videoId=vid, media_body=_MFU(job.thumbnail_path)).execute()
            except Exception as e:
                logger.warning("썸네일 설정 실패(무시): %s", e)
        job.note(f"YouTube 업로드: https://youtu.be/{vid}")
        return vid
