# Contributing to CachePilot

## Local setup

```bash
git clone https://github.com/jay15git/RAG-Cache.git
cd RAG-Cache
cp .env.example .env
# Add GEMINI_API_KEY to .env
docker compose up --build -d
```

Do not commit `.env`, `.env.production`, provider keys, or downloaded model files.

## Before opening a pull request

```bash
docker compose exec -T api pytest -q tests/unit tests/load --disable-warnings --no-cov
python3 -m compileall -q app scripts tests
git diff --check
```

Run integration and benchmark tests when changing Redis, Qdrant, cache policy, or embedding behavior:

```bash
docker compose exec -T api pytest -q \
  tests/integration/test_redis_performance.py \
  tests/benchmarks/test_qdrant_performance.py \
  --disable-warnings --no-cov
```

## Change guidelines

- Preserve cache isolation across tenant, system-prompt hash, model, and temperature.
- Add or update tests for behavioral changes.
- Keep README and the focused document in `docs/` aligned with public API or configuration changes.
- Keep benchmark claims labeled as simulated unless they come from an end-to-end measured workload.
- Use conventional commit messages, for example `fix(cache): scope semantic entries by tenant`.

## Security

The admin invalidation endpoint has no built-in authentication. Treat it as a local or internally protected endpoint until an authentication layer is implemented.
