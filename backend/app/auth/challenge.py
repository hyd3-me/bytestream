"""Auth challenge generation and Redis-backed storage."""

# path: backend/app/auth/challenge.py

# --- Imports ---

import secrets

from ..core.config import get_settings

# --- Setup ---

settings = get_settings()

# --- Public API ---


def generate_challenge() -> str:
    return secrets.token_urlsafe(32)


async def store_challenge(redis, sid: str, challenge_value: str) -> None:
    key = get_challenge_key(sid)
    await redis.setex(key, settings.challenge_ttl_seconds, challenge_value)


async def get_challenge(redis, sid: str) -> str | None:
    key = get_challenge_key(sid)
    return await redis.get(key)


async def delete_challenge(redis, sid: str) -> None:
    key = get_challenge_key(sid)
    await redis.delete(key)



def get_challenge_key(sid: str) -> str:
    return f"{settings.redis_key_prefix}challenge:{sid}"
