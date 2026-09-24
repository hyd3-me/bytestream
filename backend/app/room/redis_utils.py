"""Redis helpers for room keys and invitations."""

# path: backend/app/room/redis_utils.py

# --- Imports ---

import json
from redis.asyncio import Redis
from app.core.config import get_settings

# --- Setup ---

settings = get_settings()


# --- Public API ---

def get_personal_room_key(address: str) -> str:
    return f"{settings.redis_key_prefix}user:{address}"


def get_room_request_key(request_id: str) -> str:
    return f"{settings.redis_key_prefix}room_request:{request_id}"


async def save_room_request(
    redis: Redis, request_id: str, from_addr: str, to_addr: str, ttl: int = 1800
):
    """Save room invitation request in Redis with TTL."""
    key = get_room_request_key(request_id)
    value = json.dumps({"from": from_addr, "to": to_addr})
    await redis.setex(key, ttl, value)


async def get_room_request(redis: Redis, request_id: str):
    """Retrieve room invitation request from Redis."""
    key = get_room_request_key(request_id)
    value = await redis.get(key)
    if value:
        return json.loads(value)
    return None


async def delete_room_request(redis: Redis, request_id: str):
    """Delete room invitation request from Redis."""
    key = get_room_request_key(request_id)
    await redis.delete(key)
