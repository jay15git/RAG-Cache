"""Asynchronous quality-review queue for sampled semantic cache hits."""

import asyncio
from dataclasses import dataclass
from typing import Optional

from app.monitoring.prometheus import get_metrics
from app.quality.quality_checker import QualityCheckResult, QualityChecker


@dataclass(frozen=True)
class QualityReview:
    cached_response: str
    live_response: str
    tenant_id: str


class BackgroundQualityChecker:
    """Compares sampled cache hits outside the request path."""

    def __init__(self, checker: Optional[QualityChecker] = None):
        self._checker = checker or QualityChecker()
        self._queue: asyncio.Queue[QualityReview] = asyncio.Queue()
        self._results: list[QualityCheckResult] = []

    async def submit(self, review: QualityReview) -> None:
        await self._queue.put(review)

    async def process_one(self) -> Optional[QualityCheckResult]:
        if self._queue.empty():
            return None
        review = await self._queue.get()
        result = self._checker.compare(review.cached_response, review.live_response)
        self._results.append(result)
        get_metrics().track_quality_check(result.false_hit)
        self._queue.task_done()
        return result

    @property
    def pending(self) -> int:
        return self._queue.qsize()
