# CachePilot case study

CachePilot is a multi-tenant semantic cache for LLM requests. It extends the upstream RAG-Cache foundation with cache identity, policy, isolation, invalidation, quality, and measurement controls.

## Engineering signals

- Tenant namespaces and model/system-prompt-aware cache identity prevent cross-context leakage.
- Query-type policies adapt semantic thresholds, TTL, and stale serving.
- Tenant-scoped invalidation supports tags and prefixes.
- Privacy-safe audit events redact emails, phone numbers, and API-key-like secrets.
- Prometheus-compatible metrics expose hit rate, latency, near misses, false hits, stale hits, and estimated cost savings.

## Reproduce benchmark

```bash
docker compose exec -T api python scripts/load_test.py \
  --requests 2000 \
  --repeat-ratio 0.6 \
  --tenants 3 \
  --miss-latency-ms 25 \
  --seed 42 \
  --output benchmark.json
```

Reference local run: 2,000 requests, 3 tenants, 61.45% hit rate, P50 0.024 ms, P75 26.071 ms, P95 29.618 ms, P99 30.348 ms, and 614,500 estimated tokens avoided.

The benchmark is deterministic cache simulation. It models a 25 ms miss path and does not call Gemini, Redis, Qdrant, or a live HTTP endpoint. Do not present its estimates as production provider latency or billing data.
