"""Operational cache controls."""

from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_redis_cache
from app.cache.redis_cache import RedisCache
from app.services.invalidation_service import InvalidationService

router = APIRouter()


@router.delete("/admin/cache/{tenant_id}")
async def invalidate_cache(
    tenant_id: str,
    tag: Optional[str] = Query(default=None),
    prefix: Optional[str] = Query(default=None),
    cache: RedisCache = Depends(get_redis_cache),
) -> dict:
    """Invalidate one tenant's cache, optionally filtered by tag or prefix."""
    count = await InvalidationService(cache).invalidate_tenant(
        tenant_id, tags=[tag] if tag else None, query_prefix=prefix
    )
    return {"tenant_id": tenant_id, "invalidated": count}
