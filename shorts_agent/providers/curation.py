"""특색 상품 LLM 큐레이션 (모듈 A 고도화).

기본 ResearchProvider 가 뽑은 후보를 LLM 이 '스크롤을 멈추게 할 특색/후킹/전환'
관점에서 재선별·순위화한다. LLM 실패/미설정 시 기본 순위를 그대로 사용(폴백).
"""
from __future__ import annotations

import json
import logging

from ..models import ProductCandidate
from .base import ResearchProvider

logger = logging.getLogger("shorts_agent")


class LLMCuratedResearch(ResearchProvider):
    def __init__(self, base: ResearchProvider, api_key: str, model: str, audience: str):
        self.base = base
        self.api_key = api_key
        self.model = model
        self.audience = audience

    def find_products(self, seeds: list[str], n: int) -> list[ProductCandidate]:
        pool = self.base.find_products(seeds, n=max(n * 3, n + 5))
        if len(pool) <= n:
            return pool
        try:
            picks = self._curate(pool, n)
        except Exception as e:
            logger.warning("LLM 큐레이션 실패 → 기본 순위 사용: %s", e)
            return pool[:n]
        if not picks:
            return pool[:n]
        by_id = {p.product_id: p for p in pool}
        out: list[ProductCandidate] = []
        for pick in picks:
            p = by_id.get(str(pick.get("id")))
            if p and p not in out:
                reason = pick.get("reason", "")
                if reason:
                    p.rationale = reason
                p.hook_score = min(1.0, p.hook_score + 0.1)  # 큐레이션 선택 가산
                out.append(p)
        for p in pool:  # 부족분 채움
            if len(out) >= n:
                break
            if p not in out:
                out.append(p)
        return out[:n]

    def _curate(self, pool: list[ProductCandidate], n: int) -> list[dict]:
        import anthropic

        listing = "\n".join(
            f"- id={p.product_id} | {p.name} | {p.category} | {p.price:,}원" for p in pool
        )
        prompt = (
            f"너는 쇼핑 쇼츠 기획자다. 타깃 시청자는 '{self.audience}'.\n"
            f"아래 상품들 중 **스크롤을 멈추게 할 만큼 특색 있고(신박/화제성), "
            f"후킹과 구매 전환이 잘 될** 상위 {n}개를 골라라.\n"
            f"흔하고 밋밋한 제품은 제외. 저관여·즉시구매형을 선호.\n\n{listing}\n\n"
            f'반드시 이 JSON 만 출력: {{"picks":[{{"id":"...","reason":"한 줄 선정 이유"}}]}}'
        )
        client = anthropic.Anthropic(api_key=self.api_key)
        resp = client.messages.create(
            model=self.model, max_tokens=1000,
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(getattr(b, "text", "") for b in resp.content)
        s, e = text.find("{"), text.rfind("}")
        if s == -1:
            return []
        return json.loads(text[s : e + 1]).get("picks", [])
