"""Per-line Korean TTS with a role-appropriate voice.

Each line is synthesized separately so different characters get different
voices and we can measure each clip's exact duration for caption sync.

Providers: elevenlabs | azure | google | demo (offline, speech-like noise).
All clips are normalized to 44.1kHz stereo WAV.
"""
from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

from . import voices
from .config import Settings
from .ffmpeg_util import ffmpeg_exe, ffprobe_exe, run
from .script_model import Character, Line

AR = "44100"


def estimate_duration(text: str, settings: Settings, emote: str = "neutral") -> float:
    syl = len(re.findall(r"[가-힣]", text)) or max(1, len(text.split()))
    base = syl / settings.syllables_per_sec
    # punctuation adds little pauses; long-vowel "~" stretches cuteness
    base += 0.18 * len(re.findall(r"[?!.…]", text)) + 0.06 * text.count("~")
    if emote in ("laugh", "pout", "surprised"):
        base += 0.3
    return round(max(0.7, base + 0.15), 2)


def _normalize(src: str, dst: str) -> None:
    run([ffmpeg_exe(), "-y", "-i", src, "-ar", AR, "-ac", "2", dst])


def probe_duration(path: str) -> float | None:
    fp = ffprobe_exe()
    if fp:
        try:
            out = subprocess.run(
                [fp, "-v", "quiet", "-show_entries", "format=duration",
                 "-of", "default=nw=1:nk=1", path],
                capture_output=True, text=True)
            return float(out.stdout.strip())
        except Exception:
            return None
    return None


# ---------------- providers ----------------

def _edge(text: str, role: str, explicit: str, out: str) -> str:
    """FREE Microsoft Edge neural TTS (no API key). Korean ko-KR voices."""
    import asyncio
    import edge_tts  # pip install edge-tts

    voice, rate, pitch = voices.edge(role, explicit)
    mp3 = out + ".mp3"

    async def _run():
        comm = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
        await comm.save(mp3)

    asyncio.run(_run())
    _normalize(mp3, out)
    return out


def _elevenlabs(text: str, role: str, explicit: str, out: str) -> str:
    import requests
    vid = voices.elevenlabs(role, explicit)
    r = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{vid}",
        headers={"xi-api-key": os.environ["ELEVENLABS_API_KEY"],
                 "Content-Type": "application/json"},
        json={"text": text,
              "model_id": os.environ.get("ELEVENLABS_MODEL", "eleven_multilingual_v2"),
              "voice_settings": {"stability": 0.4, "similarity_boost": 0.85, "style": 0.3}},
        timeout=120)
    r.raise_for_status()
    mp3 = out + ".mp3"
    Path(mp3).write_bytes(r.content)
    _normalize(mp3, out)
    return out


def _azure(text: str, role: str, explicit: str, out: str) -> str:
    import requests
    voice, pitch, rate = voices.azure(role, explicit)
    region = os.environ["AZURE_SPEECH_REGION"]
    ssml = (f"<speak version='1.0' xml:lang='ko-KR'><voice name='{voice}'>"
            f"<prosody pitch='{pitch}' rate='{rate}'>{_xml_escape(text)}</prosody>"
            f"</voice></speak>")
    r = requests.post(
        f"https://{region}.tts.speech.microsoft.com/cognitiveservices/v1",
        headers={"Ocp-Apim-Subscription-Key": os.environ["AZURE_SPEECH_KEY"],
                 "Content-Type": "application/ssml+xml",
                 "X-Microsoft-OutputFormat": "audio-24khz-96kbitrate-mono-mp3"},
        data=ssml.encode("utf-8"), timeout=120)
    r.raise_for_status()
    mp3 = out + ".mp3"
    Path(mp3).write_bytes(r.content)
    _normalize(mp3, out)
    return out


def _google(text: str, role: str, explicit: str, out: str) -> str:
    import base64
    import requests
    voice, pitch, rate = voices.google(role, explicit)
    key = os.environ["GOOGLE_TTS_API_KEY"]
    r = requests.post(
        f"https://texttospeech.googleapis.com/v1/text:synthesize?key={key}",
        json={"input": {"text": text},
              "voice": {"languageCode": "ko-KR", "name": voice},
              "audioConfig": {"audioEncoding": "MP3", "pitch": pitch, "speakingRate": rate}},
        timeout=120)
    r.raise_for_status()
    mp3 = out + ".mp3"
    Path(mp3).write_bytes(base64.b64decode(r.json()["audioContent"]))
    _normalize(mp3, out)
    return out


# role -> rough vocal band for the offline placeholder (Hz). Higher = younger.
_DEMO_BAND = {
    "little_girl": 1700, "little_boy": 1500, "teen_girl": 1300, "teen_boy": 1100,
    "young_woman": 1150, "young_man": 850, "mom": 1050, "dad": 720,
    "grandma": 950, "grandpa": 640,
}


def _demo(text: str, role: str, dur: float, out: str) -> str:
    """Offline placeholder audio: band-limited noise with a syllable-rate
    tremolo envelope so the on-screen waveform looks like real speech."""
    band = _DEMO_BAND.get(role, 1000)
    af = (f"bandpass=f={band}:width_type=h:w={int(band * 1.3)},"
          f"tremolo=f=6.5:d=0.85,volume=0.6,"
          f"afade=t=in:st=0:d=0.04,afade=t=out:st={max(0, dur - 0.07):.2f}:d=0.07")
    run([ffmpeg_exe(), "-y", "-f", "lavfi",
         "-i", f"anoisesrc=d={dur:.2f}:c=pink:a=0.7:r={AR}",
         "-af", af, "-ac", "2", out])
    return out


def _xml_escape(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;"))


def synthesize_line(line: Line, char: Character, idx: int, out_dir: str,
                    settings: Settings) -> tuple[str, float]:
    out = str(Path(out_dir) / f"line_{idx:02d}.wav")
    p = settings.tts_provider
    try:
        if p == "edge":  # free, no key required
            _edge(line.tts, char.role, char.voice, out)
        elif p == "elevenlabs" and os.environ.get("ELEVENLABS_API_KEY"):
            _elevenlabs(line.tts, char.role, char.voice, out)
        elif p == "azure" and os.environ.get("AZURE_SPEECH_KEY"):
            _azure(line.tts, char.role, char.voice, out)
        elif p == "google" and os.environ.get("GOOGLE_TTS_API_KEY"):
            _google(line.tts, char.role, char.voice, out)
        else:
            raise RuntimeError("no-tts-key")
        dur = probe_duration(out) or estimate_duration(line.tts, settings, line.emote)
        return out, dur
    except Exception as exc:
        if p != "demo":
            print(f"[tts] {p} failed on line {idx} ({exc}); using offline placeholder")
        dur = estimate_duration(line.tts, settings, line.emote)
        return _demo(line.tts, char.role, dur, out), dur
