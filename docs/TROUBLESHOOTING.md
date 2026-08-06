# CachePilot troubleshooting

## Start with readiness

```bash
docker compose ps
curl http://localhost:8000/ready
docker compose logs --tail=100 api
```

`/health` checks only that FastAPI is running. Use `/ready` to check Redis, Qdrant, and whether the configured LLM provider key is present.

## API is not reachable

```bash
docker compose up --build -d
docker compose logs --tail=100 api
```

If port 8000 is busy, stop the other local process or change the host-port mapping in `docker-compose.yml`.

## Gemini returns HTTP 429 or 403

The local stack can be healthy while Gemini rejects requests because of quota, rate limits, invalid credentials, or model access.

```bash
docker compose logs --tail=100 api
```

Confirm `GEMINI_API_KEY` is set in `.env` and check the key's quota and model access in Google AI Studio. Do not paste API keys into issues, logs, or commits.

## First semantic request takes a long time

The first semantic request downloads the SentenceTransformers model. Later requests reuse the `hf-cache` Docker volume.

```bash
docker compose logs -f api
```

Do not remove Docker volumes unless you are willing to download the model again:

```bash
docker compose down -v
```

## Redis or Qdrant is unhealthy

```bash
docker compose logs --tail=100 redis
docker compose logs --tail=100 qdrant
docker compose restart redis qdrant
curl http://localhost:8000/ready
```

The Docker API container must use `REDIS_HOST=redis` and `QDRANT_HOST=qdrant`. Those values are set by Compose. A locally run API needs `localhost` instead.

## Semantic cache is not hitting

Check that semantic caching is enabled and that the requests use the same tenant:

```bash
docker compose exec -T api sh -lc 'echo "$ENABLE_SEMANTIC_CACHE"'
```

Semantic hits require the same tenant namespace and a score above the request policy threshold. Time-sensitive and creative requests use stricter thresholds by design. Use `/api/v1/metrics/prometheus` to inspect near-miss counters.

## Tests fail because services are unavailable

Start the stack before integration and benchmark tests:

```bash
docker compose up --build -d
docker compose exec -T api pytest -q tests/unit tests/load --disable-warnings --no-cov
```

Use `tests/unit` and `tests/load` for the standard fast verification command. Run integration and benchmark groups separately when validating Redis and Qdrant behavior.
