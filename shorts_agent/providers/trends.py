"""바이럴 학습 루프 (모듈 A+ 고도화).

같은 니치의 '잘 터진' 경쟁 쇼츠를 수집·분석해 '승자 패턴'을 추출한다.
- 데이터 소스: YouTube Data API search.list + videos.list(statistics) — API 키만 필요(OAuth X).
- 추정 지표: 조회수, 조회속도(views/age), 참여율((likes+comments)/views).
  ※ 남의 영상의 '실제 수익/시청지속률'은 비공개라 추정만 가능.
- 분석: 상위 영상의 제목/태그/제품을 LLM 이 요약 → winning_hooks/hot_products/angles/...
  LLM 미설정 시 휴리스틱(제목 토큰 빈도)로 폴백.
결과는 output/trends.json 에 저장하고, 다음 배치의 대본/상품선정에 주입된다.
"""
from __future__ import annotations

import json
import logging
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

from ..config import Settings
from .base import TrendMiner

logger = logging.getLogger("shorts_agent")

_EMPTY_TRENDS = {
    "winning_hooks": [], "title_patterns": [], "hot_products": [],
    "hot_categories": [], "angles": [], "hashtags": [], "notes": "",
}


def load_trends(settings: Settings) -> dict:
    f = Path(settings.output_dir) / "trends.json"
    if not f.exists():
        return dict(_EMPTY_TRENDS)
    try:
        return {**_EMPTY_TRENDS, **json.loads(f.read_text(encoding="utf-8"))}
    except Exception:
        return dict(_EMPTY_TRENDS)


def _save_trends(settings: Settings, data: dict) -> None:
    Path(settings.output_dir, "trends.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


class YouTubeTrendMiner(TrendMiner):
    def __init__(self, settings: Settings, api_key: str):
        self.s = settings
        self.api_key = api_key

    def _get(self, path: str, params: dict) -> dict:
        params = {**params, "key": self.api_key}
        url = f"https://www.googleapis.com/youtube/v3/{path}?{urllib.parse.urlencode(params)}"
        with urllib.request.urlopen(url, timeout=20) as r:
            return json.loads(r.read().decode("utf-8"))

    def _search_ids(self, seed: str, n: int) -> list[str]:
        after = (datetime.now(timezone.utc)
                 - timedelta(days=self.s.trend_lookback_days)).strftime("%Y-%m-%dT%H:%M:%SZ")
        data = self._get("search", {
            "part": "id", "q": seed, "type": "video", "videoDuration": "short",
            "order": "viewCount", "maxResults": n, "publishedAfter": after,
            "regionCode": "KR", "relevanceLanguage": "ko",
        })
        return [it["id"]["videoId"] for it in data.get("items", []) if it.get("id", {}).get("videoId")]

    def _stats(self, ids: list[str]) -> list[dict]:
        if not ids:
            return []
        data = self._get("videos", {"part": "snippet,statistics", "id": ",".join(ids[:50])})
        out = []
        now = datetime.now(timezone.utc)
        for it in data.get("items", []):
            sn, st = it.get("snippet", {}), it.get("statistics", {})
            views = int(st.get("viewCount", 0) or 0)
            try:
                pub = datetime.fromisoformat(sn.get("publishedAt", "").replace("Z", "+00:00"))
                age = max(1.0, (now - pub).total_seconds() / 86400)
            except Exception:
                age = 30.0
            likes = int(st.get("likeCount", 0) or 0)
            comments = int(st.get("commentCount", 0) or 0)
            out.append({
                "title": sn.get("title", ""), "tags": sn.get("tags", []),
                "channel": sn.get("channelTitle", ""), "views": views,
                "velocity": round(views / age, 1),
                "engagement": round((likes + comments) / max(1, views), 4),
            })
        return out

    def mine(self, seeds: list[str]) -> dict:
        rows: list[dict] = []
        for seed in seeds:
            try:
                rows += self._stats(self._search_ids(seed, 12))
            except Exception as e:
                logger.warning("트렌드 수집 실패(%s): %s", seed, e)
        if not rows:
            return load_trends(self.s)
        rows.sort(key=lambda r: r["velocity"], reverse=True)
        top = rows[:20]
        insights = _analyze(top, seeds, self.s)
        insights["notes"] = (f"{len(rows)}개 분석, 상위 조회속도 "
                             f"{top[0]['velocity']:,.0f}/일 ({top[0]['channel']})")
        _save_trends(self.s, insights)
        return insights


def _analyze(top: list[dict], seeds: list[str], s: Settings) -> dict:
    """상위 영상 → 승자 패턴. Anthropic 있으면 LLM, 없으면 휴리스틱."""
    if s.anthropic_api_key:
        try:
            return _llm_analyze(top, seeds, s)
        except Exception as e:
            logger.warning("LLM 트렌드 분석 실패 → 휴리스틱: %s", e)
    # 휴리스틱: 제목 토큰/태그 빈도
    tokens = Counter()
    tags = Counter()
    for r in top:
        for t in r["title"].replace("#", " ").split():
            if len(t) >= 2:
                tokens[t] += 1
        for tg in r["tags"]:
            tags[tg] += 1
    return {
        "winning_hooks": [r["title"] for r in top[:8]],
        "title_patterns": [w for w, _ in tokens.most_common(12)],
        "hot_products": [], "hot_categories": list(dict.fromkeys(seeds)),
        "angles": [], "hashtags": [w for w, _ in tags.most_common(10)],
        "notes": "",
    }


def _llm_analyze(top: list[dict], seeds: list[str], s: Settings) -> dict:
    import anthropic

    listing = "\n".join(
        f"- {r['title']} | 조회 {r['views']:,} | 속도 {r['velocity']:,.0f}/일 | 참여 {r['engagement']}"
        for r in top
    )
    prompt = (
        f"너는 쇼핑 쇼츠 트렌드 분석가다. 아래는 '{', '.join(seeds)}' 니치에서 "
        f"최근 잘 터진 쇼츠 상위 목록(제목/지표)이다.\n{listing}\n\n"
        "이걸 분석해 '다음 영상에 반영할 승자 패턴'을 뽑아라. 반드시 이 JSON 만 출력:\n"
        '{"winning_hooks":["효과적 후킹 문구 8개"],'
        '"title_patterns":["반복되는 제목 공식 6개"],'
        '"hot_products":[{"name":"자주 등장한 제품/품목","why":"왜 잘 되는지"}],'
        '"hot_categories":["유망 카테고리 5개"],'
        '"angles":["먹히는 콘텐츠 앵글 6개"],'
        '"hashtags":["해시태그 10개"]}'
    )
    client = anthropic.Anthropic(api_key=s.anthropic_api_key)
    resp = client.messages.create(model=s.llm_model, max_tokens=1500,
                                  messages=[{"role": "user", "content": prompt}])
    text = "".join(getattr(b, "text", "") for b in resp.content)
    a, b2 = text.find("{"), text.rfind("}")
    data = json.loads(text[a : b2 + 1])
    return {**_EMPTY_TRENDS, **data}


class MockTrendMiner(TrendMiner):
    """네트워크 없이 그럴듯한 승자 패턴 생성(dry-run 시연)."""

    def __init__(self, settings: Settings):
        self.s = settings

    def mine(self, seeds: list[str]) -> dict:
        data = {
            "winning_hooks": [
                "이거 모르고 산 사람 손?", "3초 만에 끝나는 OO 꿀팁",
                "왜 이제 알았지 진짜…", "샀다가 인생템 된 거", "이 가격 실화냐",
            ],
            "title_patterns": ["[숫자]+초/원", "이거모르면+손해", "OO하는법", "내돈내산", "현실후기"],
            "hot_products": [
                {"name": "휴대용 미니 가전", "why": "들고다니며 보여주기 좋고 즉시구매 전환↑"},
                {"name": "뷰티 디바이스", "why": "전후 비교가 강력한 후킹"},
            ],
            "hot_categories": list(dict.fromkeys((seeds or []) + ["뷰티", "생활가전", "주방용품"])),
            "angles": ["실패담→해결", "전후 비교 실측", "남들 모르는 꿀팁", "가격 충격", "리얼 리액션"],
            "hashtags": ["쇼핑꿀템", "내돈내산", "꿀템추천", "자취필수템", "갓성비"],
            "notes": "[MOCK] 예시 승자 패턴(실모드에선 YouTube API 분석값으로 대체)",
        }
        _save_trends(self.s, data)
        return data
