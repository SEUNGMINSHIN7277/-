"""로컬 실소재 에셋 (모듈 C). 직접 촬영/제조사 제공 소재를 우선 사용.

전환의 핵심 병목은 '제품 실증 소재'(명세 1-3). 이 프로바이더는 사용자가
폴더에 넣어둔 실제 제품 영상/이미지를 최우선으로 쓰고, 부족하면 b-roll 폴더,
그래도 없으면 fallback(예: Pexels)로 보조 컷을 채운다. 아무것도 없으면 빈
번들을 반환(렌더러가 움직이는 그라데이션으로 대체).

폴더 규칙:
  assets/products/<상품키>/  ← 해당 상품의 실제 컷(jpg/png/mp4/mov)
      (상품키 = 상품명 일부 또는 product_id. 매칭 안되면 _default 폴더 사용)
  assets/broll/              ← 공용 보조 컷
"""
from __future__ import annotations

import logging
import re
from pathlib import Path

from ..config import Settings
from ..models import AssetBundle, ProductCandidate, Script
from .base import AssetProvider

logger = logging.getLogger("shorts_agent")

_MEDIA = {".jpg", ".jpeg", ".png", ".webp", ".mp4", ".mov", ".m4v", ".webm", ".mkv"}


def _norm(s: str) -> str:
    return re.sub(r"[^0-9a-z가-힣]", "", s.lower())


def _media_in(folder: Path) -> list[str]:
    if not folder.exists():
        return []
    return [str(p) for p in sorted(folder.iterdir()) if p.suffix.lower() in _MEDIA]


class LocalAssetProvider(AssetProvider):
    def __init__(self, settings: Settings, fallback: AssetProvider | None = None):
        self.s = settings
        self.fallback = fallback

    def _match_product_dir(self, product: ProductCandidate) -> Path | None:
        base = self.s.products_dir
        if not base.exists():
            return None
        cands = [d for d in base.iterdir() if d.is_dir()]
        # 1) product_id 정확 매칭
        for d in cands:
            if product.product_id and product.product_id in d.name:
                return d
        # 2) 상품명 토큰 부분매칭
        pname = _norm(product.name)
        for d in cands:
            dn = _norm(d.name)
            if dn and (dn in pname or pname[:6] and pname[:6] in dn):
                return d
        # 3) _default
        dflt = base / "_default"
        return dflt if dflt.exists() else None

    def gather(self, script: Script, product: ProductCandidate, workdir) -> AssetBundle:
        product_clips: list[str] = []
        pdir = self._match_product_dir(product)
        if pdir:
            product_clips = _media_in(pdir)
            logger.info("로컬 제품 소재 %d개 사용: %s", len(product_clips), pdir.name)

        b_roll = _media_in(self.s.broll_dir)

        # 제품 이미지 url(쿠팡 상세 이미지)도 보조로 활용
        if not product_clips and product.image_url:
            img = _download(product.image_url, Path(workdir) / "product.jpg")
            if img:
                product_clips.append(img)

        # 보조 컷이 부족하면 fallback(예: Pexels)로 채움
        if self.fallback and len(b_roll) < 3:
            try:
                fb = self.fallback.gather(script, product, workdir)
                b_roll += fb.b_roll_clips
                if not product_clips:
                    product_clips += fb.product_clips
            except Exception as e:
                logger.warning("fallback 에셋 실패: %s", e)

        return AssetBundle(product_clips=product_clips, b_roll_clips=b_roll, music_path=None)


def _download(url: str, dest: Path) -> str | None:
    import urllib.request
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "shorts-agent/0.1"})
        with urllib.request.urlopen(req, timeout=30) as r:
            dest.write_bytes(r.read())
        return str(dest)
    except Exception as e:
        logger.warning("이미지 다운로드 실패: %s", e)
        return None
