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
    pass


async def get_challenge(redis, sid: str) -> str | None:
    pass


async def delete_challenge(redis, sid: str) -> None:
    pass



def get_challenge_key(sid: str) -> str:
    pass
