"""LLM 대본 생성 (모듈 B). Anthropic Claude 사용.

전환 최적화(후킹·실증·CTA·번들) + 양산 방지(포맷 로테이션 + 고유 통찰) 강제.
출력은 엄격한 JSON 스키마로 받아 Script 로 변환.
"""
from __future__ import annotations

import json
import logging

from ..errors import StageError
from ..models import ProductCandidate, Script, Stage
from .base import ScriptProvider

logger = logging.getLogger("shorts_agent")

_FORMAT_GUIDE = {
    "question": "질문형 — 시청자의 불편을 콕 집는 도발적 질문으로 시작.",
    "measure": "실측형 — 구체적 수치/비교 데이터로 효과를 증명.",
    "compare": "비교형 — 흔한 대안 대비 이 제품의 차이를 대조.",
    "fail_story": "실패담형 — '이거 모르고 샀다가 후회했다'식 1인칭 경험담.",
    "secret": "정보형 — '아는 사람만 쓰는' 꿀팁/노하우로 정보격차 자극.",
    "reaction": "리액션형 — 사용 순간의 즉각적 감탄/반전 리액션 중심.",
}

_SCHEMA_HINT = """반드시 아래 JSON 형식 '하나만' 출력해라. 설명/코드펜스 금지.
{
  "title": "유튜브 제목(28자 이내, 클릭 유도, 과장광고/허위 금지)",
  "hook_variants": ["3초 후킹 후보 5개 (각 18자 이내)"],
  "chosen_hook": "가장 강한 후킹 1개",
  "body": "구어체 나레이션 전문(기-승-전-결, 35~55초 분량, 자연스러운 말투)",
  "caption_lines": ["화면 자막용 짧은 청크 8~12개 (각 16자 이내, 키워드 위주)"],
  "shot_directions": ["컷별 비주얼 지시 6개 이상 (무엇을 보여줄지)"],
  "cta": "행동유도 문구(댓글 링크/제품 태그 클릭 유도)",
  "hashtags": ["관련 해시태그 5개 (# 제외)"]
}"""


def _fmt_trends(trend_hints: dict | None) -> str:
    if not trend_hints:
        return ""
    hooks = trend_hints.get("winning_hooks") or []
    angles = trend_hints.get("angles") or []
    if not hooks and not angles:
        return ""
    return (
        "\n[바이럴 학습 — 최근 잘 터진 패턴(참고만, 복붙 금지)]\n"
        + ("- 먹힌 후킹: " + " / ".join(hooks[:6]) + "\n" if hooks else "")
        + ("- 먹힌 앵글: " + " / ".join(angles[:6]) + "\n" if angles else "")
        + "→ 이 '구조/심리'만 흡수하고 표현은 이 제품에 맞게 완전히 새로 써라.\n"
    )


def _fmt_style(style_profile: dict | None) -> str:
    if not style_profile:
        return ""
    tone = style_profile.get("tone", "")
    do = style_profile.get("do", [])
    dont = style_profile.get("dont", [])
    ex = style_profile.get("example_hooks", [])
    parts = ["\n[채널 스타일 가이드(사람 말투 — 반드시 준수)]"]
    if tone:
        parts.append(f"- 톤: {tone}")
    if do:
        parts.append("- 권장: " + " / ".join(do[:6]))
    if dont:
        parts.append("- 금지: " + " / ".join(dont[:6]))
    if ex:
        parts.append("- 예시 후킹 느낌: " + " / ".join(ex[:4]))
    return "\n".join(parts) + "\n"


def _build_prompt(p: ProductCandidate, fmt: str, audience: str, recent_hooks: list[str],
                  trend_hints: dict | None, style_profile: dict | None) -> str:
    avoid = "\n".join(f"- {h}" for h in recent_hooks[-10:]) or "- (없음)"
    return f"""너는 한국 쇼핑 쇼츠 전문 카피라이터다. 아래 제품으로 9:16 세로 쇼츠 대본을 쓴다.

[제품]
- 이름: {p.name}
- 카테고리: {p.category}
- 가격: {p.price:,}원
- 선정 근거: {p.rationale}

[타깃 시청자] {audience}
[이번 영상 포맷] {fmt}: {_FORMAT_GUIDE.get(fmt, fmt)}
{_fmt_trends(trend_hints)}{_fmt_style(style_profile)}
[필수 원칙]
1. 초반 3초 후킹으로 스와이프 이탈을 막아라(정보격차/패턴인터럽트/두괄식).
2. 타깃의 '마음을 훔치는' 감정 포인트를 정확히 건드려라(공감→욕구→해결).
3. 제품 '실증'을 묘사하라(사용 장면/전후 비교/구체적 수치). 허위·과장·의학적 효능 단정 금지.
4. 마지막에 명확한 CTA. 함께 쓰면 좋은 보조 상품 1개를 자연스럽게 곁들여 객단가를 높여라.
5. 고유 통찰을 넣어라(이 제품의 구체적 단점/사용 맥락/대안 비교) — 템플릿 양산 금지.
6. 아래 '최근 사용한 후킹'과 표현·구조가 겹치지 않게 완전히 새로 써라:
{avoid}

[사람이 쓴 것처럼(중요)] 너무 매끈한 광고체 금지. 실제 사람처럼 구어체·짧은 문장·자연스러운
추임새("솔직히", "근데", "진짜")·미세한 비격식. AI 특유의 균일한 만연체·과한 형용사 금지.

{_SCHEMA_HINT}
"""


class LLMScriptProvider(ScriptProvider):
    def __init__(self, api_key: str, model: str, naturalness_pass: bool = True):
        self.api_key = api_key
        self.model = model
        self.naturalness_pass = naturalness_pass

    def _client(self):
        try:
            import anthropic
        except ImportError as e:
            raise StageError(Stage.SCRIPTED, "anthropic 패키지 미설치", retryable=False) from e
        return anthropic.Anthropic(api_key=self.api_key)

    def _ask(self, prompt: str, max_tokens: int = 2000) -> str:
        try:
            resp = self._client().messages.create(
                model=self.model, max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}])
        except Exception as e:
            raise StageError(Stage.SCRIPTED, f"LLM 호출 실패: {e}", retryable=True) from e
        return "".join(getattr(b, "text", "") for b in resp.content).strip()

    def write(self, product, recent_hooks, format_type, target_audience, disclosure_text,
              trend_hints=None, style_profile=None) -> Script:
        prompt = _build_prompt(product, format_type, target_audience, recent_hooks,
                               trend_hints, style_profile)
        text = self._ask(prompt)
        data = _extract_json(text)
        if not data:
            raise StageError(Stage.SCRIPTED, "LLM JSON 파싱 실패", retryable=True)

        # 자연스러움 자기검열 패스: AI티 제거 후 본문/자막 재작성
        if self.naturalness_pass and data.get("body"):
            data = self._naturalize(data, target_audience, style_profile)

        hooks = data.get("hook_variants") or [data.get("chosen_hook", "")]
        return Script(
            hook_variants=hooks[:5],
            chosen_hook=data.get("chosen_hook") or (hooks[0] if hooks else ""),
            body=data.get("body", ""),
            caption_lines=data.get("caption_lines") or _auto_chunks(data.get("body", "")),
            shot_directions=data.get("shot_directions") or ["제품 클로즈업", "사용 장면", "전후 비교"],
            cta=data.get("cta", "자세한 정보는 댓글 링크 확인!"),
            disclosure_text=disclosure_text,
            format_type=format_type,
            title=data.get("title", product.name),
            hashtags=data.get("hashtags", []),
            target_audience=target_audience,
        )


    def _naturalize(self, data: dict, audience: str, style_profile: dict | None) -> dict:
        """AI 티 자기검열 → 사람 말투로 재작성(본문/후킹/자막)."""
        style = _fmt_style(style_profile)
        prompt = (
            "아래 쇼츠 대본을 '사람이 직접 말한 것처럼' 다듬어라. "
            "AI 티(균일한 만연체, 과한 형용사, 광고체, 어색한 번역투)를 제거하고 "
            f"실제 한국 {audience} 크리에이터의 구어체로 바꿔라. 의미·길이는 유지.\n"
            f"{style}\n"
            "다음 JSON 의 body / chosen_hook / hook_variants / caption_lines / cta 만 자연스럽게 "
            "고쳐서 '같은 스키마의 JSON' 으로만 출력해라:\n"
            + json.dumps({k: data.get(k) for k in
                          ["chosen_hook", "hook_variants", "body", "caption_lines", "cta"]},
                         ensure_ascii=False)
        )
        try:
            fixed = _extract_json(self._ask(prompt, max_tokens=1800))
        except StageError:
            return data
        if fixed:
            data.update({k: v for k, v in fixed.items() if v})
        return data


def _extract_json(text: str) -> dict | None:
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        text = text[text.find("{"):]
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        return None
    try:
        return json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return None


def _auto_chunks(body: str, max_len: int = 16) -> list[str]:
    """본문을 자막용 짧은 청크로 분할(폴백)."""
    import re

    out: list[str] = []
    for sent in re.split(r"(?<=[.!?。…])\s+|\n+", body):
        sent = sent.strip()
        while len(sent) > max_len:
            cut = sent.rfind(" ", 0, max_len)
            cut = cut if cut > 0 else max_len
            out.append(sent[:cut].strip())
            sent = sent[cut:].strip()
        if sent:
            out.append(sent)
    return [c for c in out if c]
