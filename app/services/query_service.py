"""
Query processing service.

Orchestrates cache checking (exact + semantic) and LLM calls.

Sandi Metz Principles:
- Single Responsibility: Query orchestration
- Small methods: Each method < 10 lines
- Dependency Injection: Cache, semantic matcher, and LLM injected
"""

import time
from datetime import datetime, timedelta
from typing import Optional

from app.cache.redis_cache import RedisCache
from app.cache.policy import CachePolicy
from app.config import config
from app.llm.provider import BaseLLMProvider
from app.models.cache_entry import CacheEntry
from app.models.query import QueryRequest
from app.models.response import CacheInfo, QueryResponse, UsageMetrics
from app.pipeline.request_context import RequestContextManager
from app.pipeline.semantic_matcher import SemanticMatch, SemanticMatcher
from app.monitoring.prometheus import get_metrics
from app.services.audit_service import AuditService
from app.utils.hasher import generate_cache_key
from app.utils.logger import get_logger

logger = get_logger(__name__)


class QueryService:
    """
    Main query processing service.

    Coordinates exact cache, semantic cache, and LLM operations.
    """

    def __init__(
        self,
        cache: RedisCache,
        llm_provider: BaseLLMProvider,
        semantic_matcher: Optional[SemanticMatcher] = None,
        audit_service: Optional[AuditService] = None,
    ):
        """
        Initialize service.

        Args:
            cache: Redis cache service for exact matching
            llm_provider: LLM provider
            semantic_matcher: Optional semantic matcher for semantic cache
        """
        self._cache = cache
        self._llm = llm_provider
        self._semantic = semantic_matcher
        self._enable_semantic = config.enable_semantic_cache and semantic_matcher
        self._audit = audit_service or AuditService()

    async def process(self, request: QueryRequest) -> QueryResponse:
        """
        Process query with caching.

        Order: Exact cache -> Semantic cache -> LLM

        Args:
            request: Query request

        Returns:
            Query response
        """
        start_time = time.time()
        policy = CachePolicy.for_request(request)
        model = request.model or config.default_model

        # Start request context
        ctx = RequestContextManager.start(query=request.query)

        try:
            # Try exact cache if enabled
            if request.use_cache:
                cached = await self._check_exact_cache(request, policy, model)
                if cached:
                    if cached.is_stale and not request.allow_stale:
                        cached = None
                    else:
                        ctx.mark_cache_checked(hit=True)
                        get_metrics().track_cache_decision(
                            "stale" if cached.is_stale else "exact",
                            latency_ms=(time.time() - start_time) * 1000,
                            cost_saved_usd=(cached.total_tokens / 1_000_000) * 0.15,
                        )
                        return self._build_cached_response(cached, start_time)
                ctx.mark_cache_checked(hit=False)

            # Try semantic cache if enabled
            if request.use_cache and self._enable_semantic:
                match = await self._check_semantic_cache(request, policy)
                if match and not match.is_expired:
                    ctx.mark_semantic_checked(hit=True)
                    get_metrics().track_cache_decision(
                        "semantic",
                        latency_ms=(time.time() - start_time) * 1000,
                        cost_saved_usd=0.000075,
                    )
                    return self._build_semantic_response(match, start_time)
                ctx.mark_semantic_checked(hit=False)

            # Call LLM
            ctx.mark_llm_called()
            get_metrics().track_cache_decision("miss")
            llm_response = await self._call_llm(request)

            # Store in caches
            if request.use_cache:
                await self._store_in_caches(request, llm_response, policy)

            # Build response
            return self._build_response(llm_response, start_time)

        finally:
            self._audit.record(
                {
                    "request_id": ctx.request_id,
                    "tenant_id": request.tenant_id,
                    "query": request.query,
                    "query_hash": generate_cache_key(request.query, namespace=policy.namespace),
                    "cache_hit": ctx.cache_hit or ctx.semantic_hit,
                    "latency_ms": round((time.time() - start_time) * 1000, 2),
                    "provider": self._llm.get_name(),
                }
            )
            # End request context
            RequestContextManager.end()

    async def _check_exact_cache(
        self, request: QueryRequest, policy, model: str
    ) -> Optional[CacheEntry]:
        """
        Check exact cache for query.

        Args:
            request: Query request

        Returns:
            Cache entry if found
        """
        try:
            return await self._cache.get(
                request.query,
                namespace=policy.namespace,
                key_context={
                    "system_prompt_hash": request.system_prompt_hash,
                    "model": model,
                    "temperature": request.temperature,
                },
            )
        except Exception as e:
            logger.error("Exact cache check failed", error=str(e))
            return None

    async def _check_semantic_cache(
        self, request: QueryRequest, policy
    ) -> Optional[SemanticMatch]:
        """
        Check semantic cache for similar queries.

        Args:
            request: Query request

        Returns:
            Semantic match if found above threshold
        """
        if not self._semantic:
            return None

        try:
            return await self._semantic.find_match(
                request.query,
                namespace=policy.namespace,
                threshold=policy.threshold,
            )
        except Exception as e:
            logger.error("Semantic cache check failed", error=str(e))
            return None

    async def _call_llm(self, request: QueryRequest):
        """
        Call LLM provider.

        Args:
            request: Query request

        Returns:
            LLM response
        """
        return await self._llm.complete(request)

    async def _store_in_caches(self, request: QueryRequest, llm_response, policy):
        """
        Store response in both exact and semantic caches.

        Args:
            request: Query request
            llm_response: LLM response
        """
        query_hash = generate_cache_key(
            request.query,
            namespace=policy.namespace,
            system_prompt_hash=request.system_prompt_hash,
            model=llm_response.model,
            temperature=request.temperature,
        )
        expires_at = datetime.utcnow() + timedelta(seconds=policy.ttl_seconds)
        stale_until = expires_at + timedelta(seconds=policy.stale_while_revalidate)

        # Store in exact cache
        entry = CacheEntry(
            query_hash=query_hash,
            original_query=request.query,
            response=llm_response.content,
            provider=self._llm.get_name(),
            model=llm_response.model,
            prompt_tokens=llm_response.prompt_tokens,
            completion_tokens=llm_response.completion_tokens,
            embedding=None,
            namespace=policy.namespace,
            tags=request.tags,
            expires_at=expires_at,
            stale_until=stale_until,
        )

        try:
            await self._cache.set(entry, ttl_seconds=policy.ttl_seconds + policy.stale_while_revalidate)
        except Exception as e:
            logger.error("Exact cache store failed", error=str(e))

        # Store in semantic cache
        if self._semantic:
            try:
                await self._semantic.store_for_matching(
                    query=request.query,
                    query_hash=query_hash,
                    response=llm_response.content,
                    provider=self._llm.get_name(),
                    model=llm_response.model,
                    namespace=policy.namespace,
                    tags=request.tags,
                    expires_at=expires_at.timestamp(),
                )
            except Exception as e:
                logger.error("Semantic cache store failed", error=str(e))

    def _build_cached_response(
        self, entry: CacheEntry, start_time: float
    ) -> QueryResponse:
        """
        Build response from exact cache entry.

        Args:
            entry: Cache entry
            start_time: Request start time

        Returns:
            Query response
        """
        latency = (time.time() - start_time) * 1000

        return QueryResponse(
            response=entry.response,
            provider=entry.provider,
            model=entry.model,
            usage=UsageMetrics.create(entry.prompt_tokens, entry.completion_tokens),
            cache_info=CacheInfo.exact_hit(stale=entry.is_stale),
            latency_ms=latency,
        )

    def _build_semantic_response(
        self, match: SemanticMatch, start_time: float
    ) -> QueryResponse:
        """
        Build response from semantic cache match.

        Args:
            match: Semantic match
            start_time: Request start time

        Returns:
            Query response
        """
        latency = (time.time() - start_time) * 1000

        return QueryResponse(
            response=match.cached_response,
            provider=match.provider,
            model=match.model,
            usage=UsageMetrics.create(0, 0),  # No new tokens used
            cache_info=CacheInfo.semantic_hit(match.similarity_score),
            latency_ms=latency,
        )

    def _build_response(self, llm_response, start_time: float) -> QueryResponse:
        """
        Build response from LLM.

        Args:
            llm_response: LLM response
            start_time: Request start time

        Returns:
            Query response
        """
        latency = (time.time() - start_time) * 1000

        return QueryResponse(
            response=llm_response.content,
            provider=self._llm.get_name(),
            model=llm_response.model,
            usage=UsageMetrics.create(
                llm_response.prompt_tokens, llm_response.completion_tokens
            ),
            cache_info=CacheInfo.miss(),
            latency_ms=latency,
        )
