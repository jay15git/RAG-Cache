"""
API Documentation configuration.

OpenAPI documentation for the CachePilot API.

Sandi Metz Principles:
- Single Responsibility: API documentation
- Clear naming: Descriptive tags and descriptions
"""

from typing import Any, Dict

# API Tags metadata for OpenAPI documentation
TAGS_METADATA = [
    {
        "name": "health",
        "description": "Health check endpoints for monitoring service status.",
    },
    {
        "name": "query",
        "description": "Query processing endpoints. Submit queries to get cached or fresh LLM responses.",
    },
    {
        "name": "metrics",
        "description": "Metrics and monitoring endpoints for observability.",
    },
    {
        "name": "admin",
        "description": "Tenant-scoped cache invalidation controls.",
    },
]


# API Description
API_DESCRIPTION = """
# CachePilot API

CachePilot checks an exact Redis cache, then a tenant-scoped semantic Qdrant cache, before calling the configured LLM provider.

## Features

- Exact Redis cache with tenant, system-prompt, model, and temperature-aware keys
- Semantic Qdrant cache backed by local CPU embeddings
- Query-aware similarity, TTL, and stale-response policies
- Prometheus-compatible metrics and a bounded, PII-redacted audit trail

## Authentication

No HTTP authentication middleware is enabled by default. Do not expose the query or admin endpoints publicly without adding authentication and authorization.

## Response Formats

All responses are JSON. Successful responses include:
- `response`: The LLM-generated or cached response
- `cache_info`: Information about cache hit/miss
- `usage`: Token usage metrics
- `latency_ms`: Request processing time

## Error Handling

Errors return appropriate HTTP status codes with details:
- `422`: Invalid request body
- `500`: Internal server error
- `502`: LLM provider error
"""


# Contact information
API_CONTACT = {
    "name": "CachePilot",
    "url": "https://github.com/jay15git/RAG-Cache",
}


# License information
API_LICENSE = {
    "name": "MIT",
    "url": "https://opensource.org/licenses/MIT",
}


def get_openapi_config() -> Dict[str, Any]:
    """
    Get OpenAPI configuration.

    Returns:
        OpenAPI configuration dictionary
    """
    return {
        "title": "CachePilot API",
        "description": API_DESCRIPTION,
        "version": "0.1.0",
        "contact": API_CONTACT,
        "license_info": API_LICENSE,
        "openapi_tags": TAGS_METADATA,
        "servers": [
            {"url": "/", "description": "Current server"},
            {"url": "http://localhost:8000", "description": "Local development"},
        ],
    }


# Example request/response for documentation
QUERY_EXAMPLE = {
    "query": "What is semantic caching?",
    "use_cache": True,
    "provider": "gemini",
    "model": "gemini-2.0-flash",
    "max_tokens": 1000,
    "temperature": 0.2,
    "tenant_id": "demo",
    "system_prompt_hash": "assistant-v1",
    "tags": ["documentation"],
}

QUERY_RESPONSE_EXAMPLE = {
    "response": "Semantic caching reuses a response for a sufficiently similar prompt.",
    "provider": "gemini",
    "model": "gemini-2.0-flash",
    "usage": {
        "prompt_tokens": 10,
        "completion_tokens": 20,
        "total_tokens": 30,
    },
    "cache_info": {
        "cache_hit": True,
        "cache_type": "semantic",
        "similarity_score": 0.91,
        "stale": False,
    },
    "latency_ms": 8.42,
}
