"""에러 타입 및 재시도 유틸 (명세 6 — 에러 핸들링 설계)."""
from __future__ import annotations

import logging
import time
from typing import Callable, TypeVar

from .models import Stage

logger = logging.getLogger("shorts_agent")

T = TypeVar("T")


class StageError(Exception):
    """파이프라인 단계 에러.

    retryable=True  : 쿼터초과/rate limit/일시 5xx → 백오프 후 재시도
    retryable=False : 인증/정책/표시문구 누락/금칙어 → 즉시 중단
    """

    def __init__(self, stage: Stage, msg: str, retryable: bool = True):
        self.stage = stage
        self.retryable = retryable
        super().__init__(msg)


def with_retry(
    fn: Callable[[], T],
    *,
    stage: Stage,
    attempts: int = 3,
    base_delay: float = 2.0,
    sleep: Callable[[float], None] = time.sleep,
) -> T:
    """API 연동 공통 에러 핸들링: 지수 백오프(2s,4s,8s), 치명오류 즉시 중단."""
    last: Exception | None = None
    for i in range(1, attempts + 1):
        try:
            return fn()
        except StageError as e:
            last = e
            if not e.retryable or i == attempts:
                raise
            delay = base_delay * (2 ** (i - 1))
            logger.warning("[%s] 재시도 %d/%d (%.1fs): %s", stage.value, i, attempts, delay, e)
            sleep(delay)
    assert last is not None
    raise last
