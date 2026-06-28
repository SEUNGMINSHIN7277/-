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


def build_trend_miner(s: Settings):
    """바이럴 학습용 트렌드 마이너. 실모드+API키면 YouTube, 아니면 Mock."""
    from .providers import trends
    if not s.dry_run and s.youtube_api_key:
        logger.info("트렌드: YouTube Data API 실연동")
        return trends.YouTubeTrendMiner(s, s.youtube_api_key)
    if not s.dry_run:
        logger.warning("YOUTUBE_API_KEY 없음 → MockTrendMiner")
    return trends.MockTrendMiner(s)


def _build_voice(s: Settings):
    """TTS_PROVIDER 우선, 없으면 사용 가능한 키로 자동 선택. 최종 폴백=무료 edge-tts."""
    p = (s.tts_provider or "").lower()

    def edge():
        from .providers.tts_free import EdgeTTSVoiceProvider
        logger.info("TTS: edge-tts 무료(%s)", s.edge_voice)
        return EdgeTTSVoiceProvider(s.edge_voice)

    if p == "edge":
        return edge()
    if p == "clova" and s.clova_client_id and s.clova_client_secret:
        from .providers.tts_kr import CLOVAVoiceProvider
        logger.info("TTS: Naver CLOVA Voice")
        return CLOVAVoiceProvider(s.clova_client_id, s.clova_client_secret, s.clova_speaker)
    if p == "typecast" and s.typecast_api_key and s.typecast_actor_id:
        from .providers.tts_kr import TypecastVoiceProvider
        logger.info("TTS: Typecast")
        return TypecastVoiceProvider(s.typecast_api_key, s.typecast_actor_id)
    if p == "elevenlabs" and s.elevenlabs_api_key and s.elevenlabs_voice_id:
        from .providers.tts import ElevenLabsVoiceProvider
        logger.info("TTS: ElevenLabs")
        return ElevenLabsVoiceProvider(s.elevenlabs_api_key, s.elevenlabs_voice_id, s.elevenlabs_model)
    # 키 기반 자동 + 무료 폴백
    if s.elevenlabs_api_key and s.elevenlabs_voice_id:
        from .providers.tts import ElevenLabsVoiceProvider
        return ElevenLabsVoiceProvider(s.elevenlabs_api_key, s.elevenlabs_voice_id, s.elevenlabs_model)
    return edge()   # 무료·키 불필요


def build_providers(s: Settings) -> Providers:
    from .providers import mock

    render = FFmpegRenderProvider(s)       # 렌더/자막은 항상 실제 FFmpeg
    caption = ASSCaptionProvider(s)

    # 피드백: Analytics 토큰 있으면 실연동, 없으면 로컬 performance.json
    if not s.dry_run and s.youtube_analytics_token_file:
        from .providers.feedback import YouTubeAnalyticsFeedback
        feedback = YouTubeAnalyticsFeedback(s, s.youtube_analytics_token_file)
        logger.info("피드백: YouTube Analytics 실연동")
    else:
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

    # 특색 상품 LLM 큐레이션(Anthropic 키 있으면 래핑)
    if s.anthropic_api_key:
        from .providers.curation import LLMCuratedResearch
        research = LLMCuratedResearch(research, s.anthropic_api_key, s.llm_model, s.target_audience)
        logger.info("연구: LLM 특색 큐레이션 활성화")

    if s.anthropic_api_key:
        from .providers.llm import LLMScriptProvider
        script = LLMScriptProvider(s.anthropic_api_key, s.llm_model, s.naturalness_pass)
        logger.info("대본 LLM: Claude(%s)", s.llm_model)
    elif s.gemini_api_key:
        from .providers.llm import GeminiScriptProvider
        script = GeminiScriptProvider(s.gemini_api_key, s.gemini_model, s.naturalness_pass)
        logger.info("대본 LLM: Gemini 무료(%s)", s.gemini_model)
    else:
        logger.warning("LLM 키 없음 → MockScript 폴백")
        script = mock.MockScript()

    # 에셋: 로컬 실소재(직접촬영/제조사) 우선 + Pexels 보조. 둘 다 없으면 mock.
    from .providers.local_assets import LocalAssetProvider, _MEDIA
    pexels = None
    if s.pexels_api_key:
        from .providers.pexels import PexelsAssetProvider
        pexels = PexelsAssetProvider(s.pexels_api_key)

    def _has_media(d) -> bool:
        return d.exists() and any(p.suffix.lower() in _MEDIA for p in d.rglob("*"))

    has_local = _has_media(s.products_dir) or _has_media(s.broll_dir)
    if has_local or pexels:
        asset = LocalAssetProvider(s, fallback=pexels)
        logger.info("에셋: LocalAssetProvider (로컬 실소재 우선%s)",
                    " + Pexels 보조" if pexels else "")
    else:
        logger.warning("로컬 소재/Pexels 키 없음 → MockAsset(그라데이션) 폴백")
        asset = mock.MockAsset(s)

    voice = _build_voice(s) or mock.MockVoice()
    if isinstance(voice, mock.MockVoice):
        logger.warning("TTS 키 없음 → MockVoice(무음+타이밍) 폴백")

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
