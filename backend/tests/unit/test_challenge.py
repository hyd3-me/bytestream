"""Unit tests for auth challenge handling."""

# path: backend/tests/unit/test_challenge.py

# --- Imports ---

import pytest

from app.auth import challenge
from app.core.config import get_settings

# --- Setup ---

settings = get_settings()


# --- Tests ---

def test_generate_challenge_exists():
    assert hasattr(challenge, "generate_challenge")
    assert callable(challenge.generate_challenge)


def test_generate_challenge_returns_unique_string():
    c1 = challenge.generate_challenge()
    c2 = challenge.generate_challenge()

    assert isinstance(c1, str)
    assert len(c1) > 0
    assert c1 != c2


def test_store_challenge_exists():
    assert hasattr(challenge, "store_challenge")
    assert callable(challenge.store_challenge)


def test_get_challenge_exists():
    assert hasattr(challenge, "get_challenge")
    assert callable(challenge.get_challenge)


def test_delete_challenge_exists():
    assert hasattr(challenge, "delete_challenge")
    assert callable(challenge.delete_challenge)


def test_get_challenge_key_exists():
    assert hasattr(challenge, "get_challenge_key")
    assert callable(challenge.get_challenge_key)


def test_get_challenge_key_returns_prefixed_key():
    sid = "abc123"
    key = challenge.get_challenge_key(sid)

    assert key == f"{settings.redis_key_prefix}challenge:{sid}"



@pytest.mark.asyncio
async def test_store_and_get_challenge_roundtrip(redis_client):
    sid = "test_sid"
    value = "challenge_value"

    await challenge.store_challenge(redis_client, sid, value)
    loaded = await challenge.get_challenge(redis_client, sid)

    assert loaded == value
