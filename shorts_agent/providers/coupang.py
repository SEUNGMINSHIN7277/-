"""쿠팡 파트너스 API 클라이언트 + 시장조사/상품선정 (모듈 A).

인증: HMAC-SHA256 (CEA 알고리즘). signed-date 는 GMT 의 yyMMdd'T'HHmmss'Z'.
message = signed-date + method + path(+query)  → hex(hmac_sha256(secret, message)).
"""
from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone

from ..errors import StageError
from ..models import FORMAT_TYPES, ProductCandidate, Stage
from .base import ResearchProvider

logger = logging.getLogger("shorts_agent")

_DOMAIN = "https://api-gateway.coupang.com"
_BASE = "/v2/providers/affiliate_open_api/apis/openapi/v1"

# 전환이 잘 되는(저관여·소액·반복구매) 카테고리 시드 → 후킹 점수 가중에 사용
_HIGH_CONV_HINTS = [
    "청소", "주방", "수납", "정리", "욕실", "세제", "다이어트", "뷰티", "화장",
    "헤어", "마사지", "꿀템", "생활", "간식", "원룸", "자취", "반려", "디퓨저",
]
_HOOK_WORDS = ["꿀템", "신상", "역대", "대박", "필수", "마성", "갓성비", "리얼", "가성비"]


class CoupangClient:
    def __init__(self, access_key: str, secret_key: str, sub_id: str = ""):
        self.access_key = access_key
        self.secret_key = secret_key
        self.sub_id = sub_id

    def _auth_header(self, method: str, path_with_query: str) -> str:
        signed_date = datetime.now(timezone.utc).strftime("%y%m%dT%H%M%SZ")
        # path 와 query 를 분리해 message 구성 (쿠팡 규격)
        path, _, query = path_with_query.partition("?")
        message = signed_date + method + path + query
        signature = hmac.new(
            self.secret_key.encode("utf-8"), message.encode("utf-8"), hashlib.sha256
        ).hexdigest()
        return (
            "CEA algorithm=HmacSHA256, "
            f"access-key={self.access_key}, signed-date={signed_date}, signature={signature}"
        )

    def _request(self, method: str, path_with_query: str, body: dict | None = None) -> dict:
        url = _DOMAIN + path_with_query
        data = json.dumps(body).encode("utf-8") if body is not None else None
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("Authorization", self._auth_header(method, path_with_query))
        req.add_header("Content-Type", "application/json;charset=UTF-8")
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            retryable = e.code in (429, 500, 502, 503, 504)
            raise StageError(Stage.SELECTED, f"쿠팡 API {e.code}: {e.read()[:200]!r}", retryable)
        except urllib.error.URLError as e:
            raise StageError(Stage.SELECTED, f"쿠팡 API 네트워크 오류: {e}", retryable=True)
        if payload.get("rCode") not in (None, "0", 0):
            raise StageError(Stage.SELECTED, f"쿠팡 API 오류: {payload.get('rMessage')}", False)
        return payload

    def search(self, keyword: str, limit: int = 10) -> list[dict]:
        q = urllib.parse.urlencode({"keyword": keyword, "limit": limit})
        path = f"{_BASE}/products/search?{q}"
        data = self._request("GET", path)
        return (data.get("data") or {}).get("productData", []) or []

    def best_categories(self, category_id: int, limit: int = 10) -> list[dict]:
        q = urllib.parse.urlencode({"limit": limit})
        path = f"{_BASE}/products/bestcategories/{category_id}?{q}"
        data = self._request("GET", path)
        return data.get("data", []) or []

    def deeplink(self, urls: list[str]) -> list[dict]:
        path = f"{_BASE}/deeplink"
        body: dict = {"coupangUrls": urls}
        if self.sub_id:
            body["subId"] = self.sub_id
        data = self._request("POST", path, body)
        return data.get("data", []) or []


def _hook_score(name: str, category: str) -> float:
    text = f"{name} {category}"
    s = 0.4
    s += 0.1 * sum(w in text for w in _HOOK_WORDS)
    return min(s, 1.0)


def _conversion_score(name: str, category: str, price: int) -> float:
    text = f"{name} {category}"
    s = 0.3
    s += 0.12 * sum(h in text for h in _HIGH_CONV_HINTS)
    if 0 < price <= 30000:      # 소액·저관여일수록 즉시구매 전환↑
        s += 0.25
    elif price <= 60000:
        s += 0.1
    return min(s, 1.0)


class CoupangResearch(ResearchProvider):
    """쿠팡 검색 결과 → 후킹/전환 스코어링 → 딥링크 생성."""

    def __init__(self, client: CoupangClient):
        self.client = client

    def find_products(self, seeds: list[str], n: int) -> list[ProductCandidate]:
        seen: dict[str, ProductCandidate] = {}
        per = max(3, (n * 2) // max(1, len(seeds)))
        for seed in seeds:
            try:
                items = self.client.search(seed, limit=per)
            except StageError as e:
                logger.warning("검색 실패(%s): %s", seed, e)
                continue
            for it in items:
                pid = str(it.get("productId", ""))
                if not pid or pid in seen:
                    continue
                name = it.get("productName", "")
                price = int(it.get("productPrice", 0) or 0)
                cand = ProductCandidate(
                    name=name,
                    category=it.get("categoryName", seed),
                    coupang_url=it.get("productUrl", ""),
                    coupang_deeplink=it.get("productUrl", ""),  # 아래서 딥링크로 교체
                    product_id=pid,
                    image_url=it.get("productImage", ""),
                    price=price,
                    est_commission_rate=0.03,
                    hook_score=_hook_score(name, seed),
                    conversion_score=_conversion_score(name, seed, price),
                    source_availability="stock_only",
                    rationale=f"'{seed}' 키워드 상위 노출 · 가격 {price:,}원",
                )
                seen[pid] = cand

        ranked = sorted(seen.values(), key=lambda c: c.total_score, reverse=True)[:n]
        # 딥링크 일괄 변환(추적용)
        urls = [c.coupang_url for c in ranked if c.coupang_url]
        if urls:
            try:
                links = self.client.deeplink(urls)
                byu = {l.get("originalUrl"): l.get("shortenUrl") or l.get("landingUrl")
                       for l in links}
                for c in ranked:
                    c.coupang_deeplink = byu.get(c.coupang_url, c.coupang_url)
            except StageError as e:
                logger.warning("딥링크 생성 실패: %s", e)
        return ranked
