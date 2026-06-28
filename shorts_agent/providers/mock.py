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
from ..utils import make_solid_clip, silent_audio
from .base import AssetProvider, ResearchProvider, ScriptProvider, UploadProvider, VoiceProvider

logger = logging.getLogger("shorts_agent")

_SAMPLE = [
    ("실리콘 주방 멀티 집게", "주방용품", 8900),
    ("욕실 물때 제거 스프레이", "청소용품", 11900),
    ("무선 미니 핸디 선풍기", "생활가전", 15900),
    ("폼클렌징 모공 클렌저", "뷰티", 13500),
    ("접이식 다용도 수납 정리함", "수납정리", 9900),
    ("저소음 미니 가습기", "생활가전", 19900),
    ("발 각질 제거 풋파일", "뷰티", 6900),
    ("논슬립 옷걸이 50개입", "수납정리", 12900),
    ("향기 오래가는 섬유향수", "생활용품", 10900),
    ("LED 메이크업 거울", "뷰티", 22900),
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
    """플레이스홀더 컬러 클립으로 에셋 번들 구성(실 FFmpeg 렌더로 실제 영상 생성)."""

    def __init__(self, settings: Settings):
        self.s = settings

    def gather(self, script: Script, product: ProductCandidate, workdir) -> AssetBundle:
        workdir = Path(workdir)
        workdir.mkdir(parents=True, exist_ok=True)
        font = self.s.font_path
        palette = ["0x1e293b", "0x7c2d12", "0x4c1d95", "0x0f766e", "0x9d174d", "0x334155"]
        product_clip = make_solid_clip(
            workdir / "prod.mp4", text=product.name[:18], color="0x111827",
            duration=2.5, font=font, sub="[제품 컷 자리]",
        )
        b_roll = []
        for i, shot in enumerate(script.shot_directions[:6]):
            c = make_solid_clip(
                workdir / f"broll_{i}.mp4", text=shot[:20],
                color=palette[i % len(palette)], duration=2.5, font=font,
            )
            b_roll.append(str(c))
        return AssetBundle(product_clips=[str(product_clip)], b_roll_clips=b_roll, music_path=None)


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
