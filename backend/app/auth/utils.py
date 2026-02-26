import secrets
from redis.asyncio import Redis
from ..core.config import get_settings

settings = get_settings()


def generate_nonce() -> str:
    """Generate a cryptographically secure random nonce."""
    return secrets.token_urlsafe(32)


async def store_nonce(redis: Redis, address: str, nonce: str) -> None:
    """Store nonce in Redis with TTL."""
    key = get_nonce_key(address)
    await redis.setex(key, settings.nonce_ttl_seconds, nonce)


def get_nonce_key(address: str) -> str:
    """
    Return Redis key for storing nonce associated with the given Ethereum address.
    Key format: {prefix}nonce:{address}
    """
    return f"{settings.redis_key_prefix}nonce:{address}"


async def delete_nonce(redis: Redis, address: str) -> None:
    """Delete the nonce associated with the given address from Redis."""
    key = get_nonce_key(address)
    await redis.delete(key)
