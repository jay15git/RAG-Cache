# CachePilot quick reference

## Start and verify

```bash
cp .env.example .env
# Set GEMINI_API_KEY in .env
docker compose up --build -d
curl http://localhost:8000/ready
open http://localhost:8000/docs
```

## Query

```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "Explain cache invalidation.",
    "tenant_id": "demo",
    "system_prompt_hash": "assistant-v1",
    "temperature": 0.2,
    "tags": ["faq"]
  }'
```

## Invalidate one tenant

```bash
curl -X DELETE 'http://localhost:8000/api/v1/admin/cache/demo?tag=faq'
curl -X DELETE 'http://localhost:8000/api/v1/admin/cache/demo?prefix=cache'
```

## Metrics

```bash
curl http://localhost:8000/api/v1/metrics
curl http://localhost:8000/api/v1/metrics/prometheus
```

## Test and benchmark

```bash
docker compose exec -T api pytest -q tests/unit tests/load --disable-warnings --no-cov
docker compose exec -T api python scripts/load_test.py --requests 2000 --repeat-ratio 0.6 --tenants 3
```

## Stop

```bash
docker compose down
```

Use `docker compose down -v` only when you intend to delete all local cache data and the downloaded embedding model.
