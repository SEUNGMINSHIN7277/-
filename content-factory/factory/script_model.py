"""Data model for a dialogue-shorts script + JSON (de)serialization.

A script is a back-and-forth between exactly two characters. Each line carries
the Korean text fed to TTS (`tts`, written with cute phonetic spellings so the
voice sounds natural/cute) and the witty English subtitle shown on screen (`en`).
"""
from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path

CORNERS = ("top_left", "bottom_right")
VALID_ROLES = {
    "little_girl", "little_boy", "dad", "mom", "grandma", "grandpa",
    "young_woman", "young_man", "teen_girl", "teen_boy",
}


@dataclass
class Character:
    id: str                     # "A" or "B"
    role: str                   # one of VALID_ROLES -> picks the avatar + default voice
    label: str                  # English on-screen label, e.g. "Dad"
    corner: str                 # "top_left" | "bottom_right"
    voice: str = ""             # optional explicit provider voice id/name


@dataclass
class Line:
    speaker: str                # "A" | "B"
    tts: str                    # Korean text for TTS (cute phonetics allowed)
    en: str                     # English subtitle (witty, sensible translation)
    emote: str = "neutral"      # neutral | laugh | shy | surprised | pout (future use)


@dataclass
class Script:
    id: str
    pair: str                   # e.g. "dad_daughter"
    title_en: str               # 1-2 line hook title shown at top
    characters: dict            # {"A": Character, "B": Character}
    lines: list                 # [Line, ...]
    hashtags: list = field(default_factory=list)
    description_en: str = ""

    # ---------- helpers ----------
    def char(self, cid: str) -> Character:
        return self.characters[cid]

    def korean_syllables(self, text: str) -> int:
        return len(re.findall(r"[가-힣]", text)) or max(1, len(text.split()))

    # ---------- (de)serialization ----------
    @staticmethod
    def from_dict(d: dict) -> "Script":
        chars = {
            k: Character(**v) if not isinstance(v, Character) else v
            for k, v in d["characters"].items()
        }
        lines = [Line(**l) if not isinstance(l, Line) else l for l in d["lines"]]
        return Script(
            id=d["id"], pair=d.get("pair", "custom"), title_en=d["title_en"],
            characters=chars, lines=lines,
            hashtags=d.get("hashtags", []), description_en=d.get("description_en", ""),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id, "pair": self.pair, "title_en": self.title_en,
            "characters": {k: asdict(v) for k, v in self.characters.items()},
            "lines": [asdict(l) for l in self.lines],
            "hashtags": self.hashtags, "description_en": self.description_en,
        }

    def validate(self) -> list[str]:
        errs = []
        if set(self.characters) != {"A", "B"}:
            errs.append("characters must be exactly {A, B}")
        corners = {c.corner for c in self.characters.values()}
        if corners != set(CORNERS):
            errs.append("characters must occupy top_left and bottom_right")
        for i, ln in enumerate(self.lines):
            if ln.speaker not in ("A", "B"):
                errs.append(f"line {i}: bad speaker {ln.speaker!r}")
            if not ln.tts.strip() or not ln.en.strip():
                errs.append(f"line {i}: empty tts/en")
        for c in self.characters.values():
            if c.role not in VALID_ROLES:
                errs.append(f"char {c.id}: unknown role {c.role!r}")
        return errs


def load_scripts(path: str | Path) -> list[Script]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return [Script.from_dict(d) for d in data]


def save_script(script: Script, path: str | Path) -> None:
    Path(path).write_text(json.dumps(script.to_dict(), ensure_ascii=False, indent=2),
                          encoding="utf-8")
