# CachePilot configuration

Configuration is loaded by `app.config.AppConfig` from `.env`, then overridden by environment variables. Use `.env.example` for local Docker and `.env.production.example` as the production template.

## Application and API

| Variable | Default | Notes |
|---|---|---|
| `APP_NAME` | `CachePilot` | Display name in JSON metrics. |
| `APP_ENV` | `development` | `development`, `staging`, or `production`. |
| `LOG_LEVEL` | `INFO` | Application log level. |
| `DEBUG` | `false` | FastAPI debug setting. |
| `API_HOST` | `0.0.0.0` | Uvicorn bind host. |
| `API_PORT` | `8000` | Uvicorn bind port. |
| `API_WORKERS` | `4` | Production Uvicorn worker setting. |
| `ALLOWED_ORIGINS` | local hosts | Comma-separated CORS origins. |

## Redis and Qdrant

| Variable | Default | Notes |
|---|---|---|
| `REDIS_HOST` | `localhost` | Use `redis` in Docker. |
| `REDIS_PORT` | `6379` | Redis port. |
| `REDIS_DB` | `0` | Redis database number. |
| `REDIS_PASSWORD` | empty | Set this in production. |
| `REDIS_MAX_CONNECTIONS` | `10` | Redis connection pool size. |
| `QDRANT_HOST` | `localhost` | Use `qdrant` in Docker. |
| `QDRANT_PORT` | `6333` | Qdrant HTTP port. |
| `QDRANT_GRPC_PORT` | `6334` | Qdrant gRPC port. |
| `QDRANT_COLLECTION_NAME` | `query_embeddings` | Semantic cache collection. |
| `QDRANT_VECTOR_SIZE` | `384` | Must match the embedding model. |

## LLM provider

| Variable | Default | Notes |
|---|---|---|
| `GEMINI_API_KEY` | empty | Required for the default Gemini provider. |
| `OPENAI_API_KEY` | empty | Required only when OpenAI is the configured default provider. |
| `ANTHROPIC_API_KEY` | empty | Required only when Anthropic is the configured default provider. |
| `DEFAULT_LLM_PROVIDER` | `gemini` | `gemini`, `openai`, or `anthropic`. |
| `DEFAULT_MODEL` | `gemini-2.0-flash` | Used unless a request supplies `model`. |
| `DEFAULT_MAX_TOKENS` | `1000` | Default generation token cap. |
| `DEFAULT_TEMPERATURE` | `0.7` | Default generation temperature. |

## Embeddings

| Variable | Default | Notes |
|---|---|---|
| `EMBEDDING_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | Local SentenceTransformers model. |
| `EMBEDDING_DEVICE` | `cpu` | Valid values: `cpu`, `cuda`. Docker uses CPU-only PyTorch. |
| `EMBEDDING_BATCH_SIZE` | `32` | Batch size for batch embedding calls. |
| `HF_HOME` | unset outside Compose | Set to `/tmp/huggingface` in Compose to persist downloaded model files. |

The default model produces 384-dimension vectors. If the model changes, update `QDRANT_VECTOR_SIZE` and recreate the Qdrant collection.

## Cache and monitoring

| Variable | Default | Notes |
|---|---|---|
| `CACHE_TTL_SECONDS` | `3600` | Base TTL. Policy can lower it. |
| `SEMANTIC_SIMILARITY_THRESHOLD` | `0.85` | Default stable-request threshold. |
| `ENABLE_SEMANTIC_CACHE` | `true` | Disables Qdrant lookup and writes when false. |
| `ENABLE_EXACT_CACHE` | `true` | Configuration value is exposed in metrics. Exact request behavior currently follows `use_cache`. |
| `ENABLE_METRICS` | `true` | Configuration value is exposed in metrics. |
| `METRICS_PORT` | `9090` | Reserved setting; metrics are served by the API at `/api/v1/metrics/prometheus`. |

## Production configuration

```bash
cp .env.production.example .env.production
```

Set a real `GEMINI_API_KEY`, a strong `REDIS_PASSWORD`, and your public `ALLOWED_ORIGINS`. Keep `.env` and `.env.production` out of version control.
