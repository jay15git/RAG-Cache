# CachePilot module map

| Path | Main responsibility |
|---|---|
| `app/config.py` | Pydantic settings loaded from environment and `.env`. |
| `app/main.py` | FastAPI app setup, lifecycle, middleware, and routers. |
| `app/api/deps.py` | Dependency creation for Redis, providers, embeddings, and semantic matching. |
| `app/api/routes/query.py` | `POST /api/v1/query`. |
| `app/api/routes/health.py` | Liveness and readiness endpoints. |
| `app/api/routes/metrics.py` | JSON and Prometheus metrics endpoints. |
| `app/api/routes/admin.py` | Tenant cache invalidation endpoint. |
| `app/services/query_service.py` | Cache lookup order, LLM miss path, writes, metrics, audit events. |
| `app/services/invalidation_service.py` | Tenant, tag, and prefix invalidation logic. |
| `app/cache/policy.py` | Request classification and threshold, TTL, stale-window decisions. |
| `app/cache/redis_cache.py` | High-level exact cache operations. |
| `app/repositories/redis_repository.py` | Redis I/O. |
| `app/repositories/qdrant_repository.py` | Qdrant collection, vector write, similarity search, and filters. |
| `app/embeddings/embedding_generator.py` | Local SentenceTransformers download and CPU embedding generation. |
| `app/pipeline/semantic_matcher.py` | Converts queries to vectors and vector results to semantic cache entries. |
| `app/llm/gemini_provider.py` | Gemini REST provider. |
| `app/llm/openai_provider.py` | OpenAI provider. |
| `app/llm/anthropic_provider.py` | Anthropic provider. |
| `app/llm/factory.py` | Provider selection from configuration. |
| `app/monitoring/prometheus.py` | In-process Prometheus-compatible metric registry. |
| `app/services/audit_service.py` | Bounded, redacted cache audit history. |
| `scripts/load_test.py` | Deterministic cache workload benchmark. |

For behavior and commands, use the focused documents in this directory rather than treating this file as an API reference.
