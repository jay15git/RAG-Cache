# CachePilot case study

CachePilot is the production layer around RAG-Cache: a multi-tenant semantic cache that prevents redundant LLM calls while preserving isolation and response freshness controls.

## Engineering signals

- Tenant namespaces and model/system-prompt-aware cache identity prevent cross-context leakage.
- Query-type policies adapt semantic thresholds, TTL, and stale serving.
- Tenant-scoped invalidation supports tags and prefixes.
- Privacy-safe audit events redact emails, phone numbers, and API-key-like secrets.
- Prometheus-compatible metrics expose hit rate, latency, near misses, false hits, stale hits, and estimated cost savings.

## Reproduce benchmark

```bash
python scripts/load_test.py --requests 2000 --repeat-ratio 0.6 --tenants 3 --output benchmark.json
```

Benchmark output is measured locally. Do not claim savings beyond the generated report.
