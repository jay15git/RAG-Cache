# CachePilot security notes

CachePilot processes prompts and LLM responses. Redis and Qdrant can therefore contain sensitive application data.

## Current protections

- Exact cache identity includes tenant namespace, system-prompt hash, model, and temperature.
- Semantic Qdrant lookup is scoped by tenant namespace.
- Cache TTL limits retention.
- The audit service has bounded storage and redacts common emails, phone numbers, and API-key-like values.
- Gemini requests send the API key in the `x-goog-api-key` header rather than in the URL.
- Docker images use a non-root application user.

## Important current limitations

- HTTP authentication and authorization are not enabled by default.
- The tenant identifier is supplied by the request body. It is not derived from an authenticated identity.
- Redis and Qdrant are exposed on local host ports by development Compose.
- The production Compose file is a template and does not provision secret management, backups, or certificate issuance.

## Production checklist

- Keep `.env` and `.env.production` out of source control.
- Put the API behind TLS.
- Add authentication before exposing query or admin routes.
- Derive tenant identity from authenticated claims rather than an untrusted request field.
- Set a strong `REDIS_PASSWORD` and avoid exposing Redis and Qdrant publicly.
- Use a secret manager for provider keys.
- Encrypt persistent volumes where required by your data policy.
- Establish backup, retention, deletion, and incident-response procedures.
- Review audit retention and avoid logging raw prompt content outside the bounded redacted audit trail.

## Reporting a security issue

Do not publish secrets or exploit details in a public issue. Contact the repository owner privately with reproduction steps and the affected version.
