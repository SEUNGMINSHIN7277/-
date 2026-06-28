"""설정에 따라 프로바이더 세트를 조립(dry-run=mock, 실모드=실 API).

부분 키만 있는 경우에도 가능한 만큼 실제 프로바이더를 쓰고 나머지는 mock 으로 대체.
"""
from __future__ import annotations

import logging

from .config import Settings
from .pipeline import Providers
from .providers.caption import ASSCaptionProvider
from .providers.feedback import LocalFeedbackProvider
from .providers.render import FFmpegRenderProvider

logger = logging.getLogger("shorts_agent")


def build_providers(s: Settings) -> Providers:
    from .providers import mock

    render = FFmpegRenderProvider(s)       # 렌더/자막은 항상 실제 FFmpeg
    caption = ASSCaptionProvider(s)
    feedback = LocalFeedbackProvider(s)

    if s.dry_run:
        logger.info("DRY-RUN 모드: mock 프로바이더 사용(외부 API 호출 없음)")
        return Providers(
            research=mock.MockResearch(),
            script=mock.MockScript(),
            asset=mock.MockAsset(s),
            voice=mock.MockVoice(),
            render=render,
            caption=caption,
            upload=mock.MockUpload(s),
            feedback=feedback,
        )

    # ---- 실모드: 키 있는 모듈만 실제, 없으면 mock 폴백 ----
    if s.coupang_access_key and s.coupang_secret_key:
        from .providers.coupang import CoupangClient, CoupangResearch
        research = CoupangResearch(
            CoupangClient(s.coupang_access_key, s.coupang_secret_key, s.coupang_sub_id))
    else:
        logger.warning("쿠팡 키 없음 → MockResearch 폴백")
        research = mock.MockResearch()

    if s.anthropic_api_key:
        from .providers.llm import LLMScriptProvider
        script = LLMScriptProvider(s.anthropic_api_key, s.llm_model)
    else:
        logger.warning("Anthropic 키 없음 → MockScript 폴백")
        script = mock.MockScript()

    # 에셋: 로컬 실소재(직접촬영/제조사) 우선 + Pexels 보조. 둘 다 없으면 mock.
    from .providers.local_assets import LocalAssetProvider
    pexels = None
    if s.pexels_api_key:
        from .providers.pexels import PexelsAssetProvider
        pexels = PexelsAssetProvider(s.pexels_api_key)
    has_local = (s.products_dir.exists() and any(s.products_dir.iterdir())) or \
                (s.broll_dir.exists() and any(s.broll_dir.iterdir()))
    if has_local or pexels:
        asset = LocalAssetProvider(s, fallback=pexels)
        logger.info("에셋: LocalAssetProvider (로컬 실소재 우선%s)",
                    " + Pexels 보조" if pexels else "")
    else:
        logger.warning("로컬 소재/Pexels 키 없음 → MockAsset(그라데이션) 폴백")
        asset = mock.MockAsset(s)

    if s.elevenlabs_api_key and s.elevenlabs_voice_id:
        from .providers.tts import ElevenLabsVoiceProvider
        voice = ElevenLabsVoiceProvider(
            s.elevenlabs_api_key, s.elevenlabs_voice_id, s.elevenlabs_model)
    else:
        logger.warning("ElevenLabs 키 없음 → MockVoice(무음+타이밍) 폴백")
        voice = mock.MockVoice()

    if s.youtube_token_file:
        from .providers.youtube import YouTubeUploadProvider
        upload = YouTubeUploadProvider(s)
    else:
        logger.warning("YouTube 토큰 없음 → MockUpload 폴백")
        upload = mock.MockUpload(s)

    return Providers(
        research=research, script=script, asset=asset, voice=voice,
        render=render, caption=caption, upload=upload, feedback=feedback,
    )
