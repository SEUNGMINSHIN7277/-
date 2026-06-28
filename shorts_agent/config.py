"""환경설정 로더. .env 파일(있으면)과 환경변수에서 설정을 읽는다.

python-dotenv 가 없어도 동작하도록 자체 파서를 둔다.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_FONT = ROOT / "assets" / "fonts" / "NanumGothic.ttf"
DEFAULT_OUTPUT = ROOT / "output"


def _load_dotenv(path: Path) -> None:
    """간단한 .env 파서 (KEY=VALUE, # 주석, 따옴표 제거)."""
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        # 이미 실제 환경변수로 설정된 값은 덮어쓰지 않는다.
        os.environ.setdefault(key, val)


@dataclass
class Settings:
    # --- 운영 ---
    dry_run: bool = True               # 키 없이 mock 프로바이더로 전 과정 시연
    auto: bool = False                 # True면 게이트 자동 통과(무인 운영)
    daily_cap: int = 5                 # 전략적 발행 캡(API 한계 아님; 명세 0-2)
    target_audience: str = "20-30대 여성"
    channel_name: str = "오늘의픽"

    # --- 경로/리소스 ---
    output_dir: Path = field(default_factory=lambda: DEFAULT_OUTPUT)
    font_path: Path = field(default_factory=lambda: DEFAULT_FONT)
    music_dir: Path = field(default_factory=lambda: ROOT / "assets" / "music")

    # --- 컴플라이언스(명세 2-1) ---
    disclosure_text: str = "쿠팡파트너스 활동으로 일정액의 수수료를 제공받습니다"

    # --- API 키 ---
    coupang_access_key: str = ""
    coupang_secret_key: str = ""
    coupang_sub_id: str = ""           # 채널 식별 subId(선택)

    anthropic_api_key: str = ""
    llm_model: str = "claude-sonnet-4-6"   # 대본 생성(비용/품질 균형). 필요시 opus로.

    elevenlabs_api_key: str = ""
    elevenlabs_voice_id: str = ""      # 채널 페르소나 고정용
    elevenlabs_model: str = "eleven_multilingual_v2"

    pexels_api_key: str = ""

    youtube_client_secret_file: str = ""   # OAuth client secret json
    youtube_token_file: str = ""           # 저장된 토큰(refresh) json
    youtube_privacy: str = "private"       # private|unlisted|public (초기엔 private 권장)

    @classmethod
    def load(cls, *, dry_run: bool | None = None, auto: bool | None = None) -> "Settings":
        _load_dotenv(ROOT / ".env")

        def b(name: str, default: bool) -> bool:
            v = os.environ.get(name)
            if v is None:
                return default
            return v.strip().lower() in ("1", "true", "yes", "y", "on")

        s = cls(
            daily_cap=int(os.environ.get("DAILY_CAP", "5")),
            target_audience=os.environ.get("TARGET_AUDIENCE", "20-30대 여성"),
            channel_name=os.environ.get("CHANNEL_NAME", "오늘의픽"),
            output_dir=Path(os.environ.get("OUTPUT_DIR", str(DEFAULT_OUTPUT))),
            font_path=Path(os.environ.get("FONT_PATH", str(DEFAULT_FONT))),
            music_dir=Path(os.environ.get("MUSIC_DIR", str(ROOT / "assets" / "music"))),
            disclosure_text=os.environ.get(
                "DISCLOSURE_TEXT", "쿠팡파트너스 활동으로 일정액의 수수료를 제공받습니다"
            ),
            coupang_access_key=os.environ.get("COUPANG_ACCESS_KEY", ""),
            coupang_secret_key=os.environ.get("COUPANG_SECRET_KEY", ""),
            coupang_sub_id=os.environ.get("COUPANG_SUB_ID", ""),
            anthropic_api_key=os.environ.get("ANTHROPIC_API_KEY", ""),
            llm_model=os.environ.get("LLM_MODEL", "claude-sonnet-4-6"),
            elevenlabs_api_key=os.environ.get("ELEVENLABS_API_KEY", ""),
            elevenlabs_voice_id=os.environ.get("ELEVENLABS_VOICE_ID", ""),
            elevenlabs_model=os.environ.get("ELEVENLABS_MODEL", "eleven_multilingual_v2"),
            pexels_api_key=os.environ.get("PEXELS_API_KEY", ""),
            youtube_client_secret_file=os.environ.get("YOUTUBE_CLIENT_SECRET_FILE", ""),
            youtube_token_file=os.environ.get("YOUTUBE_TOKEN_FILE", ""),
            youtube_privacy=os.environ.get("YOUTUBE_PRIVACY", "private"),
        )

        # dry_run 자동 판정: 명시값 우선, 없으면 핵심 키 유무로 결정
        if dry_run is None:
            dry_run = b("DRY_RUN", not (s.anthropic_api_key and s.coupang_access_key))
        s.dry_run = dry_run
        s.auto = auto if auto is not None else b("AUTO", False)

        s.output_dir.mkdir(parents=True, exist_ok=True)
        return s
