# CachePilot performance and benchmark methodology

## What the benchmark measures

`scripts/load_test.py` is a deterministic simulation of cache behavior. It creates a mixed workload across tenant namespaces, repeats a configurable share of previously cached keys, and applies a configurable delay only to cache misses.

It reports hit rate, P50, P75, P95, P99, estimated tokens avoided, and estimated cost savings.

It does not call Gemini, Redis, Qdrant, or the HTTP API. It must not be described as production end-to-end latency or real provider cost savings.

## Reproduce the reference run

```bash
docker compose exec -T api python scripts/load_test.py \
  --requests 2000 \
  --repeat-ratio 0.6 \
  --tenants 3 \
  --miss-latency-ms 25 \
  --seed 42
```

Reference output from the local Docker environment:

| Metric | Result |
|---|---:|
| Requests | 2,000 |
| Tenants | 3 |
| Repeated-request ratio | 0.60 |
| Hits | 1,229 |
| Misses | 771 |
| Hit rate | 61.45% |
| P50 latency | 0.024 ms |
| P75 latency | 26.071 ms |
| P95 latency | 29.618 ms |
| P99 latency | 30.348 ms |
| Estimated tokens avoided | 614,500 |
| Estimated cost avoided | $0.092175 |

The small differences in percentile values between runs are normal scheduler variation around the configured 25 ms simulated miss. Hit count and hit rate are reproducible with the same seed.

## Real component checks

The test suite separately exercises Redis and Qdrant performance behavior with the Docker services:

```bash
docker compose exec -T api pytest -q \
  tests/integration/test_redis_performance.py \
  tests/benchmarks/test_qdrant_performance.py \
  --disable-warnings --no-cov
```

Run a full correctness check before presenting the project:

```bash
docker compose exec -T api pytest -q tests/unit tests/load --disable-warnings --no-cov
```

The latest local unit and load validation completed with `1187 passed, 2 skipped`.

## Interpreting results

Use a result sentence such as:

> On a deterministic 2,000-request local workload with a 60% repeated-request ratio and a modeled 25 ms miss path, CachePilot achieved a 61.45% cache hit rate and 29.6 ms P95 simulated latency.

Do not convert the simulated estimate into a claim about real Gemini costs or latency without an end-to-end experiment using measured provider responses and an explicit workload dataset.
