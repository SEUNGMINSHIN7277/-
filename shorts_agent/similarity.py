"""양산 방지용 텍스트 유사도 (명세 모듈 B — 인트로 유사도 검사).

임베딩 의존성 없이 동작하도록 토큰 Jaccard + 시퀀스 유사도를 결합.
"""
from __future__ import annotations

import re
from difflib import SequenceMatcher


def _tokens(text: str) -> set[str]:
    text = re.sub(r"[^0-9A-Za-z가-힣 ]", " ", text.lower())
    return {t for t in text.split() if len(t) >= 2}


def similarity(a: str, b: str) -> float:
    """0~1. 1에 가까울수록 비슷함."""
    if not a or not b:
        return 0.0
    ta, tb = _tokens(a), _tokens(b)
    jac = len(ta & tb) / len(ta | tb) if (ta | tb) else 0.0
    seq = SequenceMatcher(None, a, b).ratio()
    return round(0.6 * jac + 0.4 * seq, 3)


def max_similarity(candidate: str, history: list[str]) -> float:
    return max((similarity(candidate, h) for h in history), default=0.0)


def too_similar(candidate: str, history: list[str], threshold: float = 0.72) -> bool:
    return max_similarity(candidate, history) >= threshold
