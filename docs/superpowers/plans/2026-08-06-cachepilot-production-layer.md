# CachePilot Production Layer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Turn RAG-Cache into a resume-ready multi-tenant semantic cache with explicit cache policy, safe invalidation, observable quality/cost behavior, and reproducible load-test evidence.

**Architecture:** Keep Redis exact caching, Qdrant semantic search, and `QueryService` orchestration. Add a pure policy module for tenant namespace, query class, threshold, and TTL decisions; thread tenant/policy metadata through cache entries and Qdrant payloads; expose operational endpoints and metrics without replacing existing APIs.

**Tech Stack:** Python 3.11, FastAPI, Pydantic, Redis, Qdrant, pytest, Prometheus text format, GitHub Actions.

## Global Constraints

- Preserve existing `/api/v1/query`, health, metrics, Redis, Qdrant, and provider interfaces.
- Keep policy deterministic and dependency-free so unit tests run without Redis, Qdrant, or an LLM key.
- Never log raw query text; audit records use redacted query metadata.
- Scope invalidation to a tenant unless an explicit admin/all-tenants operation is requested.

### Task 1: Tenant-aware request and cache policy

**Files:**
- Create: `app/cache/policy.py`
- Modify: `app/models/query.py`
- Modify: `app/models/cache_entry.py`
- Modify: `app/utils/hasher.py`
- Test: `tests/unit/cache/test_policy.py`

**Interfaces:**
- `CachePolicy.for_request(request) -> CachePolicyDecision`
- `CachePolicyDecision.namespace`, `threshold`, `ttl_seconds`, `stale_while_revalidate`, `query_type`
- `QueryRequest.tenant_id`, `system_prompt_hash`, `tags`, `allow_stale`
- `generate_cache_key(query, namespace="default", system_prompt_hash="", model="", temperature=None)`

- [ ] Add request fields with safe defaults and validation; default tenant `default`.
- [ ] Implement query classification (`stable`, `time_sensitive`, `classification`, `creative`) using bounded keyword rules and deterministic thresholds/TTLs.
- [ ] Include namespace, system prompt hash, model, and temperature in exact keys.
- [ ] Add cache-entry namespace, tags, expires-at, stale-until metadata.
- [ ] Test tenant key isolation, policy tiers, and model/system-prompt separation.

### Task 2: Thread policy through Redis/Qdrant/query orchestration

**Files:**
- Modify: `app/cache/redis_cache.py`
- Modify: `app/pipeline/semantic_matcher.py`
- Modify: `app/services/query_service.py`
- Modify: `app/models/qdrant_point.py`
- Test: `tests/unit/cache/test_tenant_isolation.py`
- Test: `tests/unit/services/test_query_policy.py`

**Interfaces:**
- `RedisCache.get(query, namespace="default", key_context=None)`
- `RedisCache.set(entry, ttl_seconds=None)`
- `SemanticMatcher.find_match(query, namespace="default", threshold=None)`
- `SemanticMatcher.store_for_matching(..., namespace="default", tags=None, expires_at=None)`

- [ ] Pass policy decision from `QueryService.process` to exact and semantic lookup/store.
- [ ] Add Qdrant payload filtering on namespace and preserve backward compatibility when payload lacks it.
- [ ] Enforce expiry/stale behavior: fresh hits return; stale hits only when `allow_stale`, marked stale; expired entries miss.
- [ ] Keep provider/model/temperature/system hash in cache identity.
- [ ] Test cross-tenant isolation and stale opt-in with fakes.

### Task 3: Invalidation and audit-safe operations

**Files:**
- Create: `app/services/invalidation_service.py`
- Create: `app/services/audit_service.py`
- Modify: `app/models/audit.py`
- Create: `app/api/routes/admin.py`
- Modify: `app/main.py`
- Test: `tests/unit/services/test_invalidation_service.py`
- Test: `tests/unit/services/test_audit_service.py`

**Interfaces:**
- `InvalidationService.invalidate_tenant(tenant_id, tags=None, query_prefix=None) -> int`
- `InvalidationService.invalidate_all(tenant_id) -> int`
- `AuditService.record(event)`, `AuditService.redact_query(query) -> str`
- `DELETE /api/v1/admin/cache/{tenant_id}` with optional `tag` and `prefix` query params

- [ ] Implement tenant-scoped Redis pattern invalidation and return count.
- [ ] Add audit record redaction (emails, phone numbers, API-key-like tokens) and bounded in-memory sink.
- [ ] Add protected operational endpoint using existing API-key middleware conventions.
- [ ] Add invalidation event type and tests proving no raw PII appears.

### Task 4: Quality, cost, and hit-rate telemetry

**Files:**
- Create: `app/quality/quality_checker.py`
- Modify: `app/monitoring/prometheus.py`
- Modify: `app/api/routes/metrics.py`
- Modify: `app/services/query_service.py`
- Test: `tests/unit/quality/test_quality_checker.py`
- Test: `tests/unit/monitoring/test_cachepilot_metrics.py`

**Interfaces:**
- `QualityChecker.compare(cached_response, live_response) -> QualityCheckResult`
- `PrometheusMetrics.track_cache_decision(...)`, `track_quality_check(...)`, `track_cost_saving(...)`
- Metrics fields: hit rate, false-hit count/rate, near-miss count, stale hits, estimated cost saved, latency by hit/miss.

- [ ] Add lightweight lexical quality checker with configurable overlap threshold; no second LLM call in request path.
- [ ] Track exact/semantic hits, misses, near misses, stale hits, false hits, latency, and estimated savings.
- [ ] Expose these in JSON and Prometheus endpoints.
- [ ] Test metric counters and quality decisions.

### Task 5: Reproducible load test, CI, and resume-facing documentation

**Files:**
- Create: `scripts/load_test.py`
- Create: `tests/load/test_cachepilot_load.py`
- Create: `.github/workflows/ci.yml`
- Modify: `README.md`
- Create: `docs/CACHEPILOT_CASE_STUDY.md`

- [ ] Add dependency-free async benchmark against an in-memory fake with configurable request count and repeat ratio.
- [ ] Emit JSON report with hit rate, P50/P95 latency, estimated tokens/cost saved, and false-hit rate.
- [ ] Add CI workflow for lint, unit tests, and load smoke test.
- [ ] Rewrite README positioning around CachePilot outcomes, architecture, safety controls, and exact commands to reproduce evidence.
- [ ] Add case study with clearly labeled benchmark methodology/results placeholders only where locally measured.

## Self-review

Coverage: all requested features map to Tasks 1–5. No core rewrite, provider routing, streaming, Grafana deployment, or OpenAI embedding replacement included because existing architecture already demonstrates those concepts and adding them would expand scope without stronger resume signal.

