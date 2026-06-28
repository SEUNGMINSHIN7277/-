"""Generate an original dialogue script.

Provider ``anthropic`` writes a fresh skit with Claude using a prompt distilled
from what makes this genre work (recurring characters, a curiosity gap that
pulls viewers to the end, cute phonetic Korean for the kid, witty but faithful
English subtitles). Provider ``seed`` rotates the hand-written library so the
pipeline always has content offline.
"""
from __future__ import annotations

import json
import os
import random
import re

from .config import ROOT, Settings
from .script_model import VALID_ROLES, Script, load_scripts

SEED_PATH = ROOT / "scripts" / "seed_scripts.json"

PAIRS = {
    "dad_daughter":       ("dad", "little_girl", "Dad", "Daughter"),
    "mom_son":            ("mom", "little_boy", "Mom", "Son"),
    "couple":             ("young_man", "young_woman", "Him", "Her"),
    "grandma_grandchild": ("grandma", "teen_boy", "Grandma", "Grandson"),
    "grandpa_grandchild": ("grandpa", "teen_girl", "Grandpa", "Granddaughter"),
    "siblings":           ("teen_girl", "little_boy", "Big Sis", "Lil Bro"),
}

SYSTEM = """You write ORIGINAL short-form skits for a faceless channel of cute/funny
KOREAN phone-call conversations with ENGLISH subtitles, for an overseas audience.

What makes these work (follow all):
- Two recurring character types talking on the phone; warm, real, funny.
- A curiosity gap: the first 2 lines set up a question that's only resolved at
  the end, so viewers stay to find out.
- Natural rhythm: short back-and-forth lines, interruptions, a misunderstanding
  or an adorable twist. NOT a list of jokes. NOT cringe or generic.
- Wholesome and universally relatable (family love, money, food, tech, school).
- 12-18 lines total, ~45 seconds when spoken.

Two text fields per line:
- "tts": the Korean a TTS voice will SPEAK. For a small child, spell words
  PHONETICALLY so it sounds babyish/cute (e.g. 여보세요->여보데요, 먹었어->머거써,
  쌀이->쌀이, stretch vowels with ~). For adults, write clean natural Korean.
- "en": a witty, faithful English subtitle (keep the cuteness; a toddler can
  use baby-English like "Hewwo", "wice", "pwease"). Never a literal stiff gloss.

Return STRICT JSON only, matching exactly:
{
 "id": "slug_unique",
 "pair": "<one of: %PAIRS%>",
 "title_en": "Hooky title\\nsecond line",
 "characters": {
   "A": {"id":"A","role":"<role>","label":"<short EN>","corner":"top_left"},
   "B": {"id":"B","role":"<role>","label":"<short EN>","corner":"bottom_right"}
 },
 "lines": [ {"speaker":"A","tts":"...","en":"...","emote":"neutral|laugh|shy|surprised|pout"}, ... ],
 "hashtags": ["...","...","...","...","..."],
 "description_en": "one-line description"
}
Roles must be from: %ROLES%. Output JSON only, no prose, no code fences."""


def _anthropic(settings: Settings, pair: str | None, topic: str | None) -> Script:
    import anthropic

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    sys = (SYSTEM.replace("%PAIRS%", ", ".join(PAIRS))
                 .replace("%ROLES%", ", ".join(sorted(VALID_ROLES))))
    want_pair = pair or random.choice(list(PAIRS))
    ask = (f"Write a NEW skit. Pair: {want_pair}. "
           f"Topic seed: {topic or 'your choice — make it fresh and funny'}. "
           f"Use distinct characters and a strong curiosity-gap opening.")
    msg = client.messages.create(
        model=os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-8"),
        max_tokens=3000, system=sys,
        messages=[{"role": "user", "content": ask}],
    )
    text = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
    data = _extract_json(text)
    script = Script.from_dict(data)
    errs = script.validate()
    if errs:
        raise ValueError(f"model returned invalid script: {errs}")
    return script


def _extract_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    start, end = text.find("{"), text.rfind("}")
    return json.loads(text[start:end + 1])


_seed_order: list[int] = []


def _seed(settings: Settings, pair: str | None) -> Script:
    scripts = load_scripts(SEED_PATH)
    if pair:
        matching = [s for s in scripts if s.pair == pair]
        scripts = matching or scripts
    global _seed_order
    if not _seed_order:
        _seed_order = list(range(len(scripts)))
        random.shuffle(_seed_order)
    idx = _seed_order.pop()
    return scripts[idx % len(scripts)]


def generate(settings: Settings, pair: str | None = None,
             topic: str | None = None) -> Script:
    if settings.llm_provider == "anthropic" and os.environ.get("ANTHROPIC_API_KEY"):
        try:
            return _anthropic(settings, pair, topic)
        except Exception as exc:
            print(f"[script] anthropic failed ({exc}); falling back to seed library")
    return _seed(settings, pair)
