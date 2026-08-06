# CachePilot API reference

Base URL for local Docker: `http://localhost:8000`.

Interactive documentation is available at [http://localhost:8000/docs](http://localhost:8000/docs).

## Health endpoints

| Method | Path | Meaning |
|---|---|---|
| `GET` | `/health` | Liveness response. It does not probe dependencies. |
| `GET` | `/healthz` | Alias for `/health`. |
| `GET` | `/live` | Alias for `/health`. |
| `GET` | `/ready` | Probes Redis and Qdrant and reports whether the configured provider key exists. |

```bash
curl http://localhost:8000/ready
```

Example response:

```json
{
  "status": "healthy",
  "environment": "development",
  "version": "0.1.0",
  "components": {
    "llm_provider": {"status": "healthy", "latency_ms": null, "message": null},
    "redis": {"status": "healthy", "latency_ms": 2.67, "message": null},
    "qdrant": {"status": "healthy", "latency_ms": 5.67, "message": null}
  },
  "uptime_seconds": null
}
```

## Query endpoint

`POST /api/v1/query` processes one request with exact and semantic caching.

```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "What is semantic caching?",
    "tenant_id": "acme",
    "system_prompt_hash": "assistant-v1",
    "temperature": 0.2,
    "tags": ["faq"],
    "use_cache": true,
    "use_semantic_cache": true,
    "allow_stale": false
  }'
```

### Request fields

| Field | Type | Default | Notes |
|---|---|---|---|
| `query` | string | required | 1 to 10,000 characters. |
| `provider` | `openai`, `anthropic`, or `gemini` | null | Accepted by the schema. Per-request routing is not implemented; use `DEFAULT_LLM_PROVIDER`. |
| `model` | string | null | Overrides the default model and participates in exact-cache identity. |
| `max_tokens` | integer | null | `1` to `4000`. |
| `temperature` | number | null | `0.0` to `2.0`; participates in exact-cache identity. |
| `use_cache` | boolean | `true` | Disables both cache reads and writes when false. |
| `use_semantic_cache` | boolean | `true` | Present in the API model. Current service behavior is controlled by `ENABLE_SEMANTIC_CACHE`. |
| `tenant_id` | string | `default` | Required for isolation. Whitespace, `:`, `{`, and `}` are rejected. |
| `system_prompt_hash` | string | `""` | Caller-provided prompt version identifier; participates in exact-cache identity. |
| `tags` | string array | `[]` | Up to 20 tags, used by invalidation. |
| `allow_stale` | boolean | `false` | Allows an exact cache entry in its policy-controlled stale window. |

### Response fields

```json
{
  "response": "Semantic caching reuses a prior response when a new prompt is sufficiently similar.",
  "provider": "gemini",
  "model": "gemini-2.0-flash",
  "usage": {
    "prompt_tokens": 12,
    "completion_tokens": 20,
    "total_tokens": 32
  },
  "cache_info": {
    "cache_hit": true,
    "cache_type": "semantic",
    "similarity_score": 0.91,
    "stale": false
  },
  "latency_ms": 8.42
}
```

`cache_type` is `exact`, `semantic`, or `null` on a miss. `similarity_score` is set only for semantic hits.

Errors from the LLM provider return HTTP `502`. Input validation errors return HTTP `422`.

## Metrics

```bash
curl http://localhost:8000/api/v1/metrics
curl http://localhost:8000/api/v1/metrics/prometheus
```

The Prometheus endpoint includes request, cache hit, cache miss, near-miss, stale-hit, false-hit, latency, LLM token, and estimated-saving metrics. Metric names use the `ragcache_` prefix for backwards compatibility.

## Tenant invalidation

```bash
curl -X DELETE 'http://localhost:8000/api/v1/admin/cache/acme?tag=faq&prefix=semantic'
```

The endpoint deletes only keys in the target tenant namespace. `tag` and `prefix` are optional filters. No authentication middleware is enabled by default. Do not expose this endpoint publicly without adding authentication and authorization.
