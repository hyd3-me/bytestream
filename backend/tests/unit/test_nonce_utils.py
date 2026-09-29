"""Unit tests for nonce deletion."""

# path: backend/tests/unit/test_nonce_utils.py

# --- Imports ---

import pytest
from app.auth import utils as auth_utils
from app.core.config import get_settings

# --- Setup ---

settings = get_settings()


# --- Tests ---


@pytest.mark.asyncio
async def test_delete_nonce_removes_key(redis_client):
    address = "0x1234567890123456789012345678901234567890"
    nonce = "test_nonce_value"
    key = auth_utils.get_nonce_key(address)

    # Arrange: store a nonce manually
    await redis_client.setex(key, 300, nonce)

    # Act
    await auth_utils.delete_nonce(redis_client, address)

    # Assert
    stored = await redis_client.get(key)
    assert stored is None
