from unittest.mock import AsyncMock

import pytest

from app.services.invalidation_service import InvalidationService


@pytest.mark.asyncio
async def test_invalidation_stays_within_tenant_namespace():
    cache = AsyncMock()
    cache.get_cached_queries.return_value = ["cache:acme:query:one"]
    cache._repository.delete.return_value = True

    result = await InvalidationService(cache).invalidate_tenant("acme")

    assert result == 1
    cache.get_cached_queries.assert_awaited_once_with("cache:acme:*")
    cache._repository.delete.assert_awaited_once_with("cache:acme:query:one")
