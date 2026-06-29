"""Offline Korean TTS via the bundled libespeak-ng (no model download, no network).

Quality is robotic, but it's REAL, audible Korean — so a video always has a
voice even with no API keys and no internet (e.g. in a locked-down sandbox).
On a normal machine, prefer TTS_PROVIDER=edge for natural voices.

We call the shared library that ships with the `espeakng-loader` wheel directly
through ctypes (the `espeak-ng` command-line binary is not required).
"""
from __future__ import annotations

import ctypes
import os
import struct
import wave

_AUDIO_RETRIEVAL = 1
_CHARS_UTF8 = 1
_P_RATE, _P_PITCH = 1, 3

# role -> (espeak voice+variant, pitch 0-100, rate wpm)
_ROLE = {
    "little_girl": ("ko+f4", 92, 168),
    "little_boy":  ("ko+m4", 86, 172),
    "teen_girl":   ("ko+f3", 66, 178),
    "teen_boy":    ("ko+m3", 54, 182),
    "young_woman": ("ko+f2", 56, 176),
    "young_man":   ("ko+m1", 40, 176),
    "mom":         ("ko+f2", 50, 170),
    "dad":         ("ko+m3", 32, 166),
    "grandma":     ("ko+f1", 46, 150),
    "grandpa":     ("ko+m5", 30, 146),
}

_lib = None
_rate = 22050
_buf: list[int] = []


def _cb(wav, n, events):
    if wav and n > 0:
        _buf.extend(wav[i] for i in range(n))
    return 0


_CBTYPE = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.POINTER(ctypes.c_short),
                           ctypes.c_int, ctypes.c_void_p)
_cb_ref = _CBTYPE(_cb)


def available() -> bool:
    try:
        _ensure()
        return True
    except Exception:
        return False


def _ensure():
    global _lib, _rate
    if _lib is not None:
        return
    import espeakng_loader  # provided by the espeakng-loader wheel

    libpath = espeakng_loader.get_library_path()
    parent = os.path.dirname(espeakng_loader.get_data_path())
    lib = ctypes.CDLL(libpath)
    lib.espeak_Initialize.restype = ctypes.c_int
    _rate = lib.espeak_Initialize(_AUDIO_RETRIEVAL, 0, parent.encode(), 0)
    if _rate < 0:
        raise RuntimeError("espeak_Initialize failed")
    lib.espeak_SetSynthCallback(_cb_ref)
    _lib = lib


def synth(text: str, role: str, out_wav: str) -> str:
    """Synthesize Korean `text` for `role` to a mono WAV at out_wav."""
    _ensure()
    voice, pitch, rate = _ROLE.get(role, ("ko+m1", 50, 175))
    if _lib.espeak_SetVoiceByName(voice.encode()) != 0:
        _lib.espeak_SetVoiceByName(b"ko")  # variant unsupported -> plain ko
    _lib.espeak_SetParameter(_P_RATE, int(rate), 0)
    _lib.espeak_SetParameter(_P_PITCH, int(pitch), 0)

    _buf.clear()
    raw = text.encode("utf-8")
    _lib.espeak_Synth(raw, len(raw) + 1, 0, 0, 0, _CHARS_UTF8, None, None)
    _lib.espeak_Synchronize()
    if not _buf:
        raise RuntimeError("espeak produced no audio")

    with wave.open(out_wav, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(_rate)
        w.writeframes(struct.pack("<%dh" % len(_buf), *_buf))
    return out_wav
