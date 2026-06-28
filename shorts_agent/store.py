"""Job/이력 영속화 (JSON). 게이트 승인이 여러 CLI 호출에 걸쳐 동작하도록."""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from .models import VideoJob


class Store:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.data: dict = {
            "jobs": {},          # job_id -> job dict
            "recent_hooks": [],  # 양산 방지 이력
            "format_cursor": 0,  # 포맷 로테이션 커서
            "upload_day": "",    # YYYY-MM-DD (PT 기준 운영 권장)
            "uploaded_today": 0,
        }
        self._load()

    def _load(self) -> None:
        if self.path.exists():
            try:
                self.data.update(json.loads(self.path.read_text(encoding="utf-8")))
            except Exception:
                pass

    def save(self) -> None:
        self.path.write_text(
            json.dumps(self.data, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    # ---- jobs ----
    def put(self, job: VideoJob) -> None:
        self.data["jobs"][job.job_id] = job.to_dict()
        self.save()

    def get(self, job_id: str) -> VideoJob | None:
        d = self.data["jobs"].get(job_id)
        return VideoJob.from_dict(d) if d else None

    def all_jobs(self) -> list[VideoJob]:
        return [VideoJob.from_dict(d) for d in self.data["jobs"].values()]

    # ---- 양산 방지 이력 ----
    @property
    def recent_hooks(self) -> list[str]:
        return self.data.get("recent_hooks", [])

    def add_hook(self, hook: str) -> None:
        hooks = self.data.setdefault("recent_hooks", [])
        hooks.append(hook)
        self.data["recent_hooks"] = hooks[-20:]

    # ---- 포맷 로테이션 ----
    def next_format_index(self) -> int:
        i = self.data.get("format_cursor", 0)
        self.data["format_cursor"] = i + 1
        return i

    # ---- 일일 발행 캡 (전략적, PT 자정 리셋 권장) ----
    def uploaded_today(self, today: str) -> int:
        if self.data.get("upload_day") != today:
            self.data["upload_day"] = today
            self.data["uploaded_today"] = 0
        return self.data["uploaded_today"]

    def inc_uploaded(self, today: str) -> None:
        self.uploaded_today(today)
        self.data["uploaded_today"] += 1
        self.save()
