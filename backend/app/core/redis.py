from redis.asyncio import Redis
from functools import lru_cache
from .config import get_settings
from .logging import get_logger

logger = get_logger(__name__)


@lru_cache
def get_redis_pool() -> Redis:
    settings = get_settings()
    logger.debug(f"Creating Redis pool with URL: {settings.redis_url}")
    return Redis.from_url(settings.redis_url, decode_responses=True)


async def get_redis() -> Redis:
    logger.debug("Getting Redis client from pool")
    return get_redis_pool()
