"""
API Routes module.

Contains all API endpoint routers.
"""

from app.api.routes import admin, docs, health, metrics, query

__all__ = ["admin", "health", "query", "metrics", "docs"]
