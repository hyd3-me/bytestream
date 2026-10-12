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

    mocker.patch.object(manager.ws_manager.sio, "emit")

    def consume_coroutine(coro, *args, **kwargs):
        coro.close()
        return mocker.Mock()

    mocker.patch("asyncio.create_task", side_effect=consume_coroutine)

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


@pytest.mark.asyncio
async def test_handle_connect_schedules_timeout_task(mocker):
    sid = "test_sid_123"

    mocker.patch.object(manager.ws_manager.sio, "emit")
    mocker.patch(
        "app.auth.challenge.generate_challenge", return_value="test_challenge"
    )
    mocker.patch(
        "app.auth.challenge.store_challenge", new_callable=mocker.AsyncMock
    )

    def consume_coroutine(coro, *args, **kwargs):
        coro.close()
        return mocker.Mock()

    mock_create_task = mocker.patch(
        "asyncio.create_task", side_effect=consume_coroutine
    )

    await manager.ws_manager.handle_connect(sid, {})

    mock_create_task.assert_called_once()


def test_handle_auth_response_exists():
    assert hasattr(manager.ws_manager, "handle_auth_response")
    assert callable(manager.ws_manager.handle_auth_response)


@pytest.mark.asyncio
async def test_handle_auth_response_success(mocker, redis_client, test_account):
    import base64
    import json

    from cryptography.hazmat.primitives.asymmetric import ed25519
    from eth_account.messages import encode_defunct

    from app.auth import challenge as challenge_module

    sid = "test_sid_123"
    challenge_value = "test_challenge_value"

    ed_priv = ed25519.Ed25519PrivateKey.generate()
    ed_pub = ed_priv.public_key()
    ed_pub_b64 = base64.b64encode(ed_pub.public_bytes_raw()).decode("ascii")

    x_pub_b64 = base64.b64encode(b"\x01" * 32).decode("ascii")
    base_package = {
        "eth_address": test_account.address,
        "x25519_public_key": x_pub_b64,
        "ed25519_public_key": ed_pub_b64,
        "master_key_id": "test_mkid",
    }
    canonical = json.dumps(base_package, sort_keys=True, separators=(",", ":"))
    eth_message = encode_defunct(text=canonical)
    eth_sig = test_account.sign_message(eth_message).signature
    package = {
        **base_package,
        "eth_signature": base64.b64encode(eth_sig).decode("ascii"),
    }

    ed_sig = ed_priv.sign(challenge_value.encode())
    ed_sig_b64 = base64.b64encode(ed_sig).decode("ascii")

    await challenge_module.store_challenge(redis_client, sid, challenge_value)

    mock_emit = mocker.patch.object(manager.ws_manager.sio, "emit")
    mock_save = mocker.patch.object(manager.ws_manager.sio, "save_session")
    mock_disconnect = mocker.patch.object(manager.ws_manager.sio, "disconnect")

    data = {
        "address": test_account.address,
        "signature": ed_sig_b64,
        "package": package,
    }

    await manager.ws_manager.handle_auth_response(sid, data)

    mock_save.assert_awaited_once_with(sid, {"address": test_account.address})
    mock_emit.assert_any_await("auth_ok", room=sid)
    mock_disconnect.assert_not_called()
    assert await challenge_module.get_challenge(redis_client, sid) is None
