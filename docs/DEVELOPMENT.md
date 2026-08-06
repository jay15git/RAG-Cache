# CachePilot development

## Recommended workflow

Use Docker Compose. It installs the pinned Python dependencies, starts Redis and Qdrant, persists the local embedding model, and runs FastAPI with reload enabled.

```bash
cp .env.example .env
# Add GEMINI_API_KEY to .env
docker compose up --build -d
docker compose logs -f api
```

The API source, tests, and benchmark script are mounted into the development container. Changes to `app/` trigger reload.

## Local Python option

If you prefer not to run the API in Docker, install Python 3.11 dependencies and start Redis and Qdrant with Compose:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install --index-url https://download.pytorch.org/whl/cpu torch==2.13.0
python -m pip install -r requirements-dev.txt
docker compose up -d redis qdrant
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Set `REDIS_HOST=localhost`, `QDRANT_HOST=localhost`, and `HF_HOME` to a writable local directory in your `.env` when using this option.

## Useful commands

```bash
docker compose ps
docker compose logs -f api
docker compose exec -T api pytest -q tests/unit tests/load --disable-warnings --no-cov
docker compose exec -T api python scripts/load_test.py --requests 2000 --repeat-ratio 0.6 --tenants 3
curl http://localhost:8000/ready
```

## Code areas

| Path | Responsibility |
|---|---|
| `app/services/query_service.py` | Exact and semantic cache orchestration. |
| `app/cache/policy.py` | Deterministic cache policy decisions. |
| `app/pipeline/semantic_matcher.py` | Embedding generation and Qdrant similarity lookup. |
| `app/llm/` | Gemini, OpenAI, Anthropic providers, retries, rate limiting. |
| `app/api/routes/` | Query, health, metrics, and admin HTTP routes. |
| `app/monitoring/` | Metrics registry, audit, and Grafana dashboard definitions. |
| `scripts/load_test.py` | Reproducible in-memory benchmark. |

Run `git diff --check` and the verification command before committing.
