# CachePilot diagrams

## Deployment view

```mermaid
flowchart TB
    Client --> API[FastAPI API container]
    API --> Redis[(Redis exact cache)]
    API --> Qdrant[(Qdrant semantic cache)]
    API --> Gemini[Gemini API]
    API --> OpenAI[OpenAI API]
    API --> Anthropic[Anthropic API]
    API --> HF[Persisted CPU embedding model]
```

Only one provider is selected at runtime through `DEFAULT_LLM_PROVIDER`. Gemini is the default.

## Cache decision view

```mermaid
flowchart TD
    A[Request] --> B[Derive tenant and policy]
    B --> C[Redis exact key]
    C -->|hit| D[Return exact cache response]
    C -->|miss| E[Generate local CPU embedding]
    E --> F[Qdrant tenant-filtered search]
    F -->|score clears policy threshold| G[Return semantic cache response]
    F -->|no acceptable result| H[Call selected LLM]
    H --> I[Store exact entry in Redis]
    H --> J[Store vector and metadata in Qdrant]
    I --> K[Return generated response]
    J --> K
```

Exact keys include the request tenant, system-prompt hash, model, and temperature. Qdrant semantic queries are scoped by tenant namespace.
