"""Voice mapping: role -> provider-specific voice (+ pitch/rate for cuteness).

The "cute toddler" effect comes from two things working together:
  1. the script spells words phonetically (여보데요, 머거써) so the TTS reads
     them in a babyish way, and
  2. a young/female voice pitched up a little (Azure/Google support pitch).

You can override any voice via env, e.g. VOICE_AZURE_LITTLE_GIRL=ko-KR-...
or VOICE_ELEVEN_DAD=<voiceId>.
"""
from __future__ import annotations

import os

# edge-tts (FREE, no API key) — same Microsoft ko-KR neural voices as Azure.
# (voice, rate%, pitchHz). Pitch shifts are kept MODEST on purpose: large
# shifts make the neural voice sound chipmunky/robotic, which kills the
# natural feel. We lean on voice CHOICE + small adjustments for character.
EDGE = {
    "little_girl": ("ko-KR-SeoHyeonNeural", "-2%",  "+20Hz"),
    "little_boy":  ("ko-KR-SeoHyeonNeural", "+0%",  "+14Hz"),
    "teen_girl":   ("ko-KR-JiMinNeural",    "+2%",  "+8Hz"),
    "teen_boy":    ("ko-KR-HyunsuMultilingualNeural", "+3%", "+10Hz"),
    "young_woman": ("ko-KR-JiMinNeural",    "+0%",  "+0Hz"),
    "young_man":   ("ko-KR-InJoonNeural",   "+0%",  "+0Hz"),
    "mom":         ("ko-KR-SunHiNeural",    "-2%",  "-2Hz"),
    "dad":         ("ko-KR-InJoonNeural",   "-3%",  "-10Hz"),
    "grandma":     ("ko-KR-SunHiNeural",    "-8%",  "-6Hz"),
    "grandpa":     ("ko-KR-BongJinNeural",  "-8%",  "-14Hz"),
}

# Azure ko-KR neural voices + per-role prosody (pitch, rate) for character.
AZURE = {
    "little_girl": ("ko-KR-SeoHyeonNeural", "+28%", "-4%"),
    "little_boy":  ("ko-KR-SeoHyeonNeural", "+22%", "+0%"),
    "teen_girl":   ("ko-KR-JiMinNeural",    "+8%",  "+2%"),
    "teen_boy":    ("ko-KR-InJoonNeural",   "+12%", "+4%"),
    "young_woman": ("ko-KR-JiMinNeural",    "+2%",  "+0%"),
    "young_man":   ("ko-KR-InJoonNeural",   "+0%",  "+0%"),
    "mom":         ("ko-KR-SunHiNeural",    "-2%",  "-2%"),
    "dad":         ("ko-KR-InJoonNeural",   "-12%", "-4%"),
    "grandma":     ("ko-KR-SunHiNeural",    "-10%", "-10%"),
    "grandpa":     ("ko-KR-BongJinNeural",  "-14%", "-10%"),
}

# Google Cloud TTS ko-KR voices + pitch (semitone-ish, -20..20) + speakingRate.
GOOGLE = {
    "little_girl": ("ko-KR-Wavenet-A", 7.0, 0.96),
    "little_boy":  ("ko-KR-Wavenet-A", 5.0, 1.0),
    "teen_girl":   ("ko-KR-Wavenet-B", 3.0, 1.02),
    "teen_boy":    ("ko-KR-Wavenet-C", 2.0, 1.04),
    "young_woman": ("ko-KR-Neural2-A", 0.0, 1.0),
    "young_man":   ("ko-KR-Neural2-C", 0.0, 1.0),
    "mom":         ("ko-KR-Wavenet-B", -1.0, 0.98),
    "dad":         ("ko-KR-Neural2-C", -4.0, 0.96),
    "grandma":     ("ko-KR-Wavenet-B", -3.0, 0.9),
    "grandpa":     ("ko-KR-Wavenet-D", -5.0, 0.9),
}

# ElevenLabs: pick Korean-capable voices in your account and map IDs via env.
# These name hints are placeholders; real IDs should come from env/config.
ELEVEN = {
    "little_girl": "REPLACE_eleven_child_girl",
    "little_boy":  "REPLACE_eleven_child_boy",
    "teen_girl":   "REPLACE_eleven_teen_girl",
    "teen_boy":    "REPLACE_eleven_teen_boy",
    "young_woman": "REPLACE_eleven_young_woman",
    "young_man":   "REPLACE_eleven_young_man",
    "mom":         "REPLACE_eleven_mom",
    "dad":         "REPLACE_eleven_dad",
    "grandma":     "REPLACE_eleven_grandma",
    "grandpa":     "REPLACE_eleven_grandpa",
}


def _env_override(provider: str, role: str) -> str | None:
    return os.environ.get(f"VOICE_{provider.upper()}_{role.upper()}")


def edge(role: str, explicit: str = "") -> tuple[str, str, str]:
    ov = _env_override("edge", role)
    if ov:
        return (ov, "+0%", "+0Hz")
    if explicit:
        return (explicit, "+0%", "+0Hz")
    return EDGE.get(role, EDGE["young_man"])


def azure(role: str, explicit: str = "") -> tuple[str, str, str]:
    ov = _env_override("azure", role)
    if ov:
        return (ov, "+0%", "+0%")
    if explicit:
        return (explicit, "+0%", "+0%")
    return AZURE.get(role, AZURE["young_man"])


def google(role: str, explicit: str = "") -> tuple[str, float, float]:
    ov = _env_override("google", role)
    if ov:
        return (ov, 0.0, 1.0)
    if explicit:
        return (explicit, 0.0, 1.0)
    return GOOGLE.get(role, GOOGLE["young_man"])


def elevenlabs(role: str, explicit: str = "") -> str:
    return _env_override("eleven", role) or explicit or ELEVEN.get(role, "")
