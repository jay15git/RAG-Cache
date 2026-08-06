"""Tenant-scoped cache invalidation."""

from typing import Optional

from app.cache.redis_cache import RedisCache


class InvalidationService:
    def __init__(self, cache: RedisCache):
        self.cache = cache

    async def invalidate_tenant(
        self,
        tenant_id: str,
        tags: Optional[list[str]] = None,
        query_prefix: Optional[str] = None,
    ) -> int:
        pattern = f"cache:{tenant_id}:*"
        keys = await self.cache.get_cached_queries(pattern)
        if query_prefix:
            keys = [key for key in keys if query_prefix.lower() in key.lower()]
        if tags:
            matched = []
            for key in keys:
                entry = await self.cache._repository.fetch(key)
                if entry and set(tags).intersection(entry.tags):
                    matched.append(key)
            keys = matched
        deleted = 0
        for key in keys:
            if await self.cache._repository.delete(key):
                deleted += 1
        return deleted

    async def invalidate_all(self, tenant_id: str) -> int:
        return await self.invalidate_tenant(tenant_id)
