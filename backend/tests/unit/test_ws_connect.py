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


@pytest.mark.asyncio
async def test_disconnect_if_not_authenticated_disconnects_when_no_address(mocker):
    sid = "test_sid"
    timeout = 60

    mocker.patch("asyncio.sleep", new_callable=mocker.AsyncMock)
    mocker.patch.object(manager.ws_manager.sio, "get_session", return_value={})
    mock_disconnect = mocker.patch.object(manager.ws_manager.sio, "disconnect")

    await manager.ws_manager._disconnect_if_not_authenticated(sid, timeout)

    mock_disconnect.assert_awaited_once_with(sid)


@pytest.mark.asyncio
async def test_disconnect_if_not_authenticated_keeps_authenticated(mocker):
    sid = "test_sid"
    timeout = 60

    mocker.patch("asyncio.sleep", new_callable=mocker.AsyncMock)
    mocker.patch.object(
        manager.ws_manager.sio,
        "get_session",
        return_value={"address": "0xabc"},
    )
    mock_disconnect = mocker.patch.object(manager.ws_manager.sio, "disconnect")

    await manager.ws_manager._disconnect_if_not_authenticated(sid, timeout)

    mock_disconnect.assert_not_called()
