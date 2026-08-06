"""Deterministic cache policy decisions used by every cache tier."""

from dataclasses import dataclass
from typing import Literal

from app.config import config
from app.models.query import QueryRequest

QueryType = Literal["stable", "time_sensitive", "classification", "creative"]


@dataclass(frozen=True)
class CachePolicyDecision:
    namespace: str
    query_type: QueryType
    threshold: float
    ttl_seconds: int
    stale_while_revalidate: int


class CachePolicy:
    """Classifies requests into conservative, explainable cache policies."""

    _TIME_WORDS = ("latest", "today", "current", "now", "price", "weather", "news")
    _CLASSIFICATION_WORDS = (
        "classify",
        "categorize",
        "is this",
        "yes or no",
        "true or false",
    )
    _CREATIVE_WORDS = ("write", "story", "poem", "brainstorm", "creative", "imagine")

    @classmethod
    def for_request(cls, request: QueryRequest) -> CachePolicyDecision:
        query = request.query.lower()
        if any(word in query for word in cls._TIME_WORDS):
            query_type: QueryType = "time_sensitive"
            threshold, ttl, stale = 0.94, min(config.cache_ttl_seconds, 300), 0
        elif any(word in query for word in cls._CLASSIFICATION_WORDS):
            query_type = "classification"
            threshold, ttl, stale = 0.80, config.cache_ttl_seconds, 300
        elif any(word in query for word in cls._CREATIVE_WORDS) or (
            request.temperature or 0
        ) >= 1.0:
            query_type = "creative"
            threshold, ttl, stale = 0.97, min(config.cache_ttl_seconds, 900), 0
        else:
            query_type = "stable"
            threshold, ttl, stale = (
                config.semantic_similarity_threshold,
                config.cache_ttl_seconds,
                900,
            )
        return CachePolicyDecision(request.tenant_id, query_type, threshold, ttl, stale)
