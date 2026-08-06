"""Cheap lexical quality signal for asynchronous false-hit review."""

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class QualityCheckResult:
    overlap: float
    false_hit: bool


class QualityChecker:
    def __init__(self, min_overlap: float = 0.35):
        self.min_overlap = min_overlap

    def compare(self, cached_response: str, live_response: str) -> QualityCheckResult:
        cached = set(re.findall(r"\w+", cached_response.lower()))
        live = set(re.findall(r"\w+", live_response.lower()))
        overlap = len(cached & live) / max(len(live), 1)
        return QualityCheckResult(overlap=overlap, false_hit=overlap < self.min_overlap)
