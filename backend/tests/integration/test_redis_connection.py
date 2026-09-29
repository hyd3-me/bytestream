"""Integration test for Redis connectivity."""

# path: backend/tests/integration/test_redis_connection.py

# --- Imports ---

import pytest
from app.core.redis import get_redis_pool

# --- Tests ---


@pytest.mark.asyncio
async def test_redis_ping():
    redis = get_redis_pool()
    assert await redis.ping() is True
