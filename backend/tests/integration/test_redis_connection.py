import pytest
from app.core.redis import get_redis_pool


@pytest.mark.asyncio
async def test_redis_ping():
    redis = get_redis_pool()
    assert await redis.ping() is True
