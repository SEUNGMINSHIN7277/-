"""에셋 수집 (모듈 C). 보조 컷은 Pexels(무료 스톡), 제품 컷은 상품 이미지.

주의(명세 2-3): 제품 클로즈업/상표 노출 컷은 스톡 의존 금지.
여기서는 b-roll(분위기/배경)만 스톡으로 받고, 제품 컷은 상품 이미지로 구성한다.
"""
from __future__ import annotations

import json
import logging
import urllib.parse
import urllib.request
from pathlib import Path

from ..errors import StageError
from ..models import AssetBundle, ProductCandidate, Script, Stage
from .base import AssetProvider

logger = logging.getLogger("shorts_agent")


def _download(url: str, dest: Path) -> Path | None:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "shorts-agent/0.1"})
        with urllib.request.urlopen(req, timeout=30) as r:
            dest.write_bytes(r.read())
        return dest
    except Exception as e:
        logger.warning("다운로드 실패 %s: %s", url, e)
        return None


class PexelsAssetProvider(AssetProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key

    def _search_videos(self, query: str, per_page: int = 5) -> list[dict]:
        q = urllib.parse.urlencode(
            {"query": query, "per_page": per_page, "orientation": "portrait"}
        )
        url = f"https://api.pexels.com/videos/search?{q}"
        req = urllib.request.Request(url, headers={"Authorization": self.api_key})
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                return json.loads(r.read().decode("utf-8")).get("videos", [])
        except Exception as e:
            raise StageError(Stage.ASSETS, f"Pexels 검색 실패: {e}", retryable=True) from e

    def gather(self, script: Script, product: ProductCandidate, workdir) -> AssetBundle:
        workdir = Path(workdir)
        workdir.mkdir(parents=True, exist_ok=True)

        # 제품 컷: 상품 이미지(고유). 없으면 빈 리스트(렌더러가 플레이스홀더 처리)
        product_clips: list[str] = []
        if product.image_url:
            img = _download(product.image_url, workdir / "product.jpg")
            if img:
                product_clips.append(str(img))

        # 보조 컷: 카테고리/분위기 키워드로 portrait 영상
        b_roll: list[str] = []
        query = product.category or "lifestyle"
        try:
            vids = self._search_videos(query, per_page=max(4, len(script.shot_directions)))
        except StageError as e:
            logger.warning("%s", e)
            vids = []
        for i, v in enumerate(vids):
            files = sorted(
                v.get("video_files", []),
                key=lambda f: (f.get("height") or 0),
                reverse=True,
            )
            if not files:
                continue
            dest = workdir / f"broll_{i}.mp4"
            got = _download(files[0]["link"], dest)
            if got:
                b_roll.append(str(got))

        if not product_clips and not b_roll:
            raise StageError(Stage.ASSETS, "에셋을 하나도 확보하지 못함", retryable=True)
        return AssetBundle(product_clips=product_clips, b_roll_clips=b_roll, music_path=None)
