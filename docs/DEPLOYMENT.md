# CachePilot deployment

## Local Docker deployment

```bash
cp .env.example .env
# Set GEMINI_API_KEY in .env
docker compose up --build -d
docker compose ps
curl http://localhost:8000/ready
```

Open [http://localhost:8000/docs](http://localhost:8000/docs) to use the API interactively.

The local Compose stack exposes:

| Service | Host port | Purpose |
|---|---:|---|
| API | 8000 | CachePilot API and metrics |
| Redis | 6379 | Exact cache |
| Qdrant | 6333 and 6334 | Semantic cache |

The API has a named Hugging Face cache volume. The first semantic request downloads the local embedding model. Later container restarts reuse it.

## Production Compose template

Build the production image, then create the production environment file:

```bash
docker build --target production -t ragcache:latest .
cp .env.production.example .env.production
# Set GEMINI_API_KEY, REDIS_PASSWORD, and ALLOWED_ORIGINS.
docker compose -f docker-compose.prod.yml up -d
```

Check the deployed service:

```bash
docker compose -f docker-compose.prod.yml ps
curl http://localhost:8000/ready
```

The production Compose template includes an API service, Redis, Qdrant, and Nginx. Its `deploy.replicas` and resource fields are useful with Docker Swarm; standard `docker compose up` starts one API container unless you scale it explicitly. The template assumes you provide a valid `nginx/nginx.conf` and TLS files under `nginx/ssl`. It does not set up a managed database, automated backups, secret manager, or certificate issuance.

## Required production controls

Before public exposure:

- Set non-empty `REDIS_PASSWORD`.
- Restrict `ALLOWED_ORIGINS` to trusted domains.
- Place the API and admin invalidation route behind authentication and authorization.
- Store provider credentials in a secret manager instead of committed files or shell history.
- Terminate TLS at a managed load balancer or correctly configured Nginx.
- Back up Redis and Qdrant storage according to your retention requirements.
- Monitor `/ready` and scrape `/api/v1/metrics/prometheus`.

## Common operations

```bash
# Follow local logs
docker compose logs -f api

# Restart only the API after changing .env
docker compose up -d --force-recreate api

# Stop the stack while retaining local data
docker compose down

# Remove local containers and all cache/model data
docker compose down -v
```

`docker compose down -v` is destructive for local cache and embedding-model volumes.
