# Start here

CachePilot is a FastAPI semantic caching service using Redis, Qdrant, local CPU embeddings, and a configurable LLM provider. The default provider is Gemini.

## Run it

```bash
cp .env.example .env
# Set GEMINI_API_KEY in .env
docker compose up --build -d
curl http://localhost:8000/ready
```

Open [http://localhost:8000/docs](http://localhost:8000/docs) for the interactive API.

## Validate it

```bash
docker compose exec -T api pytest -q tests/unit tests/load --disable-warnings --no-cov
docker compose exec -T api python scripts/load_test.py --requests 2000 --repeat-ratio 0.6 --tenants 3
```

Read [README.md](README.md) for the complete architecture, API, configuration, deployment, and benchmark guide.
