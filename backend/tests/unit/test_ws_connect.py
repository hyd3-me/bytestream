"""Unit tests for Socket.IO connect handler."""

# path: backend/tests/unit/test_ws_connect.py

# --- Imports ---

import pytest

from app.auth import challenge
from app.ws import manager


# --- Tests ---


@pytest.mark.asyncio
async def test_handle_connect_exists():
    assert hasattr(manager.ws_manager, "handle_connect")
    assert callable(manager.ws_manager.handle_connect)


@pytest.mark.asyncio
async def test_handle_connect_stores_challenge_and_returns_true(
    mocker, redis_client
):
    sid = "test_sid_123"

    mock_emit = mocker.patch.object(manager.ws_manager.sio, "emit")

    result = await manager.ws_manager.handle_connect(sid, {})

    assert result is True
    stored = await challenge.get_challenge(redis_client, sid)
    assert stored is not None
    assert isinstance(stored, str)
    assert len(stored) > 0


def test_disconnect_if_not_authenticated_exists():
    assert hasattr(manager.ws_manager, "_disconnect_if_not_authenticated")
    assert callable(manager.ws_manager._disconnect_if_not_authenticated)
