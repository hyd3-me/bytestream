from redis.asyncio import Redis
from functools import lru_cache
from .config import get_settings


@lru_cache
def get_redis_pool() -> Redis:
    settings = get_settings()
    return Redis.from_url(settings.redis_url, decode_responses=True)


async def get_redis() -> Redis:
    """FastAPI dependency that returns a Redis client."""
    return get_redis_pool()
