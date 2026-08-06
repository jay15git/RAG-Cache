"""Bounded, privacy-aware audit trail."""

import re
from collections import deque


class AuditService:
    def __init__(self, max_entries: int = 1000):
        self._events = deque(maxlen=max_entries)

    @staticmethod
    def redact_query(query: str) -> str:
        value = re.sub(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", "[EMAIL]", query)
        value = re.sub(r"\b(?:\+?\d[\d ()-]{7,}\d)\b", "[PHONE]", value)
        value = re.sub(
            r"\b(?:sk|api|key)[_-][A-Za-z0-9_-]{8,}",
            "[SECRET]",
            value,
            flags=re.I,
        )
        return value[:256]

    def record(self, event: dict) -> dict:
        safe = dict(event)
        if "query" in safe:
            safe["query"] = self.redact_query(str(safe["query"]))
        self._events.append(safe)
        return safe

    def recent(self, limit: int = 100) -> list[dict]:
        return list(self._events)[-limit:]
