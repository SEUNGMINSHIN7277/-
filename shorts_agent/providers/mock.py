"""Dry-run 용 mock 프로바이더 — API 키 없이 전 과정을 실제로 굴려 .mp4 까지 산출.

렌더/자막은 실제 FFmpeg 구현을 그대로 쓰고, 외부 API 부분만 mock 으로 대체한다.
(보이스는 무음 + 타이밍만 생성 — 영상 길이/자막 싱크는 실제와 동일하게 동작)
"""
from __future__ import annotations

import json
import logging
import shutil
from pathlib import Path

from ..config import Settings
from ..models import FORMAT_TYPES, AssetBundle, ProductCandidate, Script, VideoJob
from ..utils import GRADIENT_PAIRS, gradient_image, silent_audio
from .base import AssetProvider, ResearchProvider, ScriptProvider, UploadProvider, VoiceProvider

logger = logging.getLogger("shorts_agent")

# 특색(신박·휴대·전동 등) 있고 여성 타깃 친화적인 샘플 상품 풀
_SAMPLE = [
    ("LED 터치 무드등 미니 가습기", "생활가전", 23900),
    ("냉온 진동 아이마사지기", "뷰티", 29900),
    ("무선 미니 휴대용 고데기", "뷰티", 21900),
    ("진동 실리콘 클렌징 브러시", "뷰티", 14900),
    ("목걸이형 핸즈프리 선풍기", "생활가전", 16900),
    ("자동 거품 디스펜서", "주방용품", 19900),
    ("전동 발뒤꿈치 풋케어", "뷰티", 18900),
    ("접이식 실리콘 트래블 물병", "여행용품", 12900),
    ("무드 캔들 워머 조명", "인테리어", 25900),
    ("초미니 휴대용 의류 보풀제거기", "생활용품", 9900),
]

_HOOK_TMPL = {
    "question": "아직도 {n} 이렇게 쓰세요?",
    "measure": "{n} 써보니 시간 절반으로 줄었어요",
    "compare": "비싼 거 말고 {n} 이거면 끝",
    "fail_story": "{n} 모르고 살 뻔했잖아",
    "secret": "아는 사람만 쓴다는 {n}",
    "reaction": "{n} 처음 써본 솔직 반응",
}


class MockResearch(ResearchProvider):
    def find_products(self, seeds: list[str], n: int) -> list[ProductCandidate]:
        out: list[ProductCandidate] = []
        for i, (name, cat, price) in enumerate(_SAMPLE):
            out.append(
                ProductCandidate(
                    name=name, category=cat, product_id=f"mock-{i}",
                    coupang_url=f"https://www.coupang.com/vp/products/mock{i}",
                    coupang_deeplink=f"https://link.coupang.com/a/mock{i}",
                    price=price,
                    hook_score=round(0.6 + (i % 4) * 0.1, 2),
                    conversion_score=round(0.55 + (i % 3) * 0.12, 2),
                    source_availability="stock_only",
                    rationale=f"'{(seeds or ['생활'])[i % max(1,len(seeds))]}' 연관 · {price:,}원 저관여 즉시구매형",
                )
            )
        out.sort(key=lambda c: c.total_score, reverse=True)
        return out[:n]


class MockScript(ScriptProvider):
    def write(self, product, recent_hooks, format_type, target_audience, disclosure_text) -> Script:
        n = product.name
        hook = _HOOK_TMPL.get(format_type, "{n} 솔직 후기").format(n=n)
        variants = [tmpl.format(n=n) for tmpl in _HOOK_TMPL.values()]
        body = (
            f"{hook} "
            f"사실 {product.category} 고르는 게 제일 어렵잖아요. "
            f"제가 직접 써봤는데, {n}는 가격은 {product.price:,}원인데 활용도가 진짜 높아요. "
            f"특히 {target_audience}이라면 이거 하나로 번거로움이 확 줄어요. "
            f"다만 단점도 있어요 — 처음엔 적응이 좀 필요해요. 그래도 이 가격이면 충분히 만족. "
            f"함께 쓰면 좋은 보조템도 댓글에 정리해뒀어요. "
            f"{product.rationale}"
        )
        captions = [
            hook, f"{product.category} 고민 끝", f"{n}", f"가격 {product.price:,}원",
            "활용도 최고", f"{target_audience} 강추", "단점도 솔직하게", "이 가격이면 만족",
            "보조템은 댓글에", "지금 확인하세요",
        ]
        shots = [
            f"{n} 패키지 오프닝(후킹)", "사용 전 불편한 상황", f"{n} 클로즈업",
            "실제 사용 장면", "전/후 비교", "디테일 강조샷", "CTA 화면",
        ]
        return Script(
            hook_variants=variants[:5],
            chosen_hook=hook,
            body=body,
            caption_lines=captions,
            shot_directions=shots,
            cta="지금 댓글 링크 확인 👇",
            disclosure_text=disclosure_text,
            format_type=format_type,
            title=hook[:28],
            hashtags=["쇼핑꿀템", product.category, "가성비", "추천템", "리뷰"],
            target_audience=target_audience,
        )


class MockAsset(AssetProvider):
    """그라데이션 이미지로 에셋 번들 구성 → 렌더러의 켄번스/제품카드/트랜지션을 실제로 시연.

    실모드에서는 PexelsAssetProvider(영상) + 상품 이미지로 대체됨.
    """

    def __init__(self, settings: Settings):
        self.s = settings

    def gather(self, script: Script, product: ProductCandidate, workdir) -> AssetBundle:
        workdir = Path(workdir)
        workdir.mkdir(parents=True, exist_ok=True)
        font = self.s.font_path
        # 제품 이미지(고유 컷 대용) — 따뜻한 톤 카드
        product_img = gradient_image(
            workdir / "prod.png", "0xFF9966", "0xFF5E62",
            label=product.name[:16], font=font, sub=f"{product.price:,}원",
            size=(1080, 1350), gtype="radial",
        )
        # 보조 컷 — 컷별 비주얼 지시 라벨이 박힌 그라데이션 이미지
        b_roll = []
        for i, shot in enumerate(script.shot_directions[:6]):
            c0, c1 = GRADIENT_PAIRS[i % len(GRADIENT_PAIRS)]
            # 라벨 없이 깨끗한 그라데이션(실모드의 b-roll 영상 자리)
            img = gradient_image(
                workdir / f"broll_{i}.png", c0, c1, label="", font=font,
                size=(1080, 1920), gtype="linear" if i % 2 else "radial",
            )
            b_roll.append(str(img))
        return AssetBundle(product_clips=[str(product_img)], b_roll_clips=b_roll, music_path=None)


class MockVoice(VoiceProvider):
    """무음 + 단어 타임스탬프만 생성(한국어 발화속도 ≈ 5.5자/초 가정)."""

    def synthesize(self, text: str, out_path) -> tuple[str, list[dict], float]:
        out_path = Path(out_path)
        chars = max(1, len(text.replace(" ", "")))
        duration = round(min(58.0, max(18.0, chars / 5.5)), 2)
        silent_audio(out_path, duration)
        words = text.split()
        per = duration / max(1, len(words))
        ts = [
            {"word": w, "start": round(i * per, 2), "end": round((i + 1) * per, 2)}
            for i, w in enumerate(words)
        ]
        return str(out_path), ts, duration


class MockUpload(UploadProvider):
    """업로드하지 않고 최종 영상 + 메타데이터(json)를 output 에 보관."""

    def __init__(self, settings: Settings):
        self.s = settings

    def upload(self, job: VideoJob) -> str:
        vid = f"DRYRUN-{job.job_id}"
        meta = {
            "would_upload": job.final_video_path,
            "thumbnail": job.thumbnail_path,
            "title": f"[광고] {job.script.title}",
            "disclosure_first_line": job.script.disclosure_text,
            "deeplink": job.product.coupang_deeplink,
            "hashtags": job.script.hashtags,
            "privacy": self.s.youtube_privacy,
            "containsSyntheticMedia": True,
        }
        Path(self.s.output_dir, f"{job.job_id}.meta.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        job.note(f"[DRY-RUN] 업로드 생략 — 메타 저장: {job.job_id}.meta.json")
        return vid
