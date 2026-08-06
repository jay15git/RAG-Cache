# CachePilot testing

Tests run inside the API container so they use the same Python dependencies as the application.

## Quick verification

```bash
docker compose up --build -d
docker compose exec -T api pytest -q tests/unit tests/load --disable-warnings --no-cov
curl http://localhost:8000/ready
```

Latest local run: `1187 passed, 2 skipped` for unit and load tests.

## Test groups

| Command | Purpose |
|---|---|
| `docker compose exec -T api pytest -q tests/unit --disable-warnings --no-cov` | Fast, isolated unit coverage. |
| `docker compose exec -T api pytest -q tests/load --disable-warnings --no-cov` | Deterministic benchmark smoke test. |
| `docker compose exec -T api pytest -q tests/integration --disable-warnings --no-cov` | Integration coverage. Requires Redis and Qdrant. |
| `docker compose exec -T api pytest -q tests/integration/test_redis_performance.py tests/benchmarks/test_qdrant_performance.py --disable-warnings --no-cov` | Component benchmark checks. |
| `docker compose exec -T api python scripts/load_test.py --requests 2000 --repeat-ratio 0.6 --tenants 3` | Deterministic workload report. |

## Static checks

```bash
python3 -m compileall -q app scripts tests
git diff --check
```

## Notes

- Gemini network calls are not needed for the unit and load suites.
- The API is considered locally ready when `/ready` reports Redis and Qdrant as healthy and the selected provider key is configured.
- A Gemini API key can still be rate-limited or quota-limited by Google. That is an external provider response, not a failed local installation.
