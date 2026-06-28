"""Configuration: creative/style settings (config.yaml) + secrets (.env).

The on-screen language is ENGLISH (title, speaker labels, subtitles) so the
videos export overseas cleanly and we avoid a CJK-font dependency in the
renderer. Only the TTS *audio* is Korean.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _load_dotenv() -> None:
    env_path = ROOT / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))


def _load_yaml(path: Path) -> dict:
    try:
        import yaml  # type: ignore
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except ModuleNotFoundError:
        data: dict = {}
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.split("#", 1)[0].rstrip()
            if not line or ":" not in line or line[0] in " -":
                continue
            k, _, v = line.partition(":")
            v = v.strip().strip('"').strip("'")
            if v:
                data[k.strip()] = v
        return data


@dataclass
class Settings:
    # ---- canvas ----
    width: int = 1080
    height: int = 1920
    fps: int = 30
    supersample: int = 2          # render HTML at 2x then downscale = crisp

    # ---- pacing (seconds) ----
    lead_in: float = 0.45         # silence before first line
    gap: float = 0.22             # natural gap between lines
    lead_out: float = 0.7         # tail after last line
    syllables_per_sec: float = 4.2  # used only for offline duration estimate

    # ---- look ----
    title_color: str = "FFE53B"           # yellow title (matches reference)
    color_a: str = "FFFFFF"               # speaker A subtitle (white)
    color_b: str = "FF8FC7"               # speaker B subtitle (pink)
    waveform_color: str = "FFFFFF"
    caption_font: str = "DejaVu Sans"
    dim_inactive: float = 0.45            # opacity of the non-speaking avatar

    # ---- providers (env can override) ----
    llm_provider: str = "anthropic"       # anthropic | seed
    tts_provider: str = "demo"            # elevenlabs | azure | google | demo
    avatar_provider: str = "svg"          # svg | files | openai
    publish_provider: str = "none"        # youtube | none

    # ---- creative direction for the script writer ----
    channel_name: str = "Korean Call Diaries"
    niche: str = "cute & funny Korean family/couple phone-call skits"

    raw: dict = field(default_factory=dict)

    def speaker_color(self, char_id: str) -> str:
        return self.color_a if char_id == "A" else self.color_b


def load_settings() -> Settings:
    _load_dotenv()
    s = Settings()
    cfg = ROOT / "config.yaml"
    if cfg.exists():
        data = _load_yaml(cfg)
        s.raw = data
        for key in (
            "title_color", "color_a", "color_b", "waveform_color", "caption_font",
            "llm_provider", "tts_provider", "avatar_provider", "publish_provider",
            "channel_name", "niche",
        ):
            if data.get(key):
                setattr(s, key, str(data[key]))
        for key in ("width", "height", "fps", "supersample"):
            if data.get(key):
                setattr(s, key, int(data[key]))
        for key in ("lead_in", "gap", "lead_out", "syllables_per_sec", "dim_inactive"):
            if data.get(key):
                setattr(s, key, float(data[key]))
    for env_key, attr in (
        ("LLM_PROVIDER", "llm_provider"), ("TTS_PROVIDER", "tts_provider"),
        ("AVATAR_PROVIDER", "avatar_provider"), ("PUBLISH_PROVIDER", "publish_provider"),
    ):
        if os.environ.get(env_key):
            setattr(s, attr, os.environ[env_key])
    return s
