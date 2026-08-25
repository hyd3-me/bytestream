import pytest
import json
from app.ws import manager
from app.room import utils


@pytest.mark.asyncio
async def test_handle_create_room_request_exists():
    assert hasattr(manager.ws_manager, "handle_create_room_request")
    assert callable(manager.ws_manager.handle_create_room_request)


@pytest.mark.asyncio
async def test_handle_create_room_request_gets_address_from_session(mocker):
    sid = "test_sid"
    data = {"target_address": "0x123"}
    mock_get_session = mocker.patch.object(
        manager.ws_manager.sio, "get_session", return_value={"address": "0xaaa"}
    )
    mocker.patch("app.room.utils.is_valid_eth_address", return_value=True)
    mocker.patch(
        "app.core.database.db_manager.get_conn", return_value=FakeAsyncContextManager()
    )
    mocker.patch("app.room.crud.room_exists", return_value=False)
    mocker.patch("app.core.redis.get_redis_pool", return_value=mocker.AsyncMock())
    mock_emit = mocker.patch.object(manager.ws_manager.sio, "emit")

    await manager.ws_manager.handle_create_room_request(sid, data)

    mock_get_session.assert_awaited_once_with(sid)


@pytest.mark.asyncio
async def test_handle_create_room_request_skips_invalid_target_address(mocker):
    sid = "test_sid"
    data = {"target_address": "invalid"}
    mock_get_session = mocker.patch.object(
        manager.ws_manager.sio, "get_session", return_value={"address": "0xaaa"}
    )
    mock_is_valid = mocker.patch(
        "app.room.utils.is_valid_eth_address", return_value=False
    )
    mock_emit = mocker.patch.object(manager.ws_manager.sio, "emit")

    await manager.ws_manager.handle_create_room_request(sid, data)

    mock_is_valid.assert_called_once_with("invalid")
    mock_emit.assert_not_called()


@pytest.mark.asyncio
async def test_handle_create_room_request_returns_early_if_no_address_in_session(
    mocker,
):
    sid = "test_sid"
    data = {"target_address": "0x123"}
    mock_get_session = mocker.patch.object(
        manager.ws_manager.sio, "get_session", return_value={}
    )
    mock_emit = mocker.patch.object(manager.ws_manager.sio, "emit")
    mock_is_valid = mocker.patch("app.room.utils.is_valid_eth_address")

    await manager.ws_manager.handle_create_room_request(sid, data)

    mock_get_session.assert_awaited_once_with(sid)
    mock_is_valid.assert_not_called()
    mock_emit.assert_not_called()


@pytest.mark.asyncio
async def test_handle_create_room_request_returns_early_if_target_address_missing(
    mocker,
):
    sid = "test_sid"
    data = {}
    mock_get_session = mocker.patch.object(
        manager.ws_manager.sio, "get_session", return_value={"address": "0xaaa"}
    )
    mock_emit = mocker.patch.object(manager.ws_manager.sio, "emit")
    mock_is_valid = mocker.patch("app.room.utils.is_valid_eth_address")

    await manager.ws_manager.handle_create_room_request(sid, data)

    mock_get_session.assert_awaited_once_with(sid)
    mock_is_valid.assert_not_called()
    mock_emit.assert_not_called()


@pytest.mark.asyncio
async def test_handle_create_room_request_joins_existing_room(mocker):
    sid = "test_sid"
    address_a = "0xaaa"
    address_b = "0xbbb"
    data = {"target_address": address_b}
    room_id = utils.get_dm_room_id(address_a, address_b)

    mock_get_session = mocker.patch.object(
        manager.ws_manager.sio, "get_session", return_value={"address": address_a}
    )
    mock_room_exists = mocker.patch("app.room.crud.room_exists", return_value=True)
    mock_get_conn = mocker.patch(
        "app.core.database.db_manager.get_conn", return_value=FakeAsyncContextManager()
    )
    mock_enter_room = mocker.patch.object(manager.ws_manager.sio, "enter_room")
    mock_emit = mocker.patch.object(manager.ws_manager.sio, "emit")
    mock_is_valid = mocker.patch(
        "app.room.utils.is_valid_eth_address", return_value=True
    )

    await manager.ws_manager.handle_create_room_request(sid, data)

    mock_room_exists.assert_awaited_once()
    mock_enter_room.assert_awaited_once_with(sid, room_id)
    mock_emit.assert_awaited_once_with("room_ready", {"room_id": room_id}, room=sid)


class FakeAsyncContextManager:
    async def __aenter__(self):
        return None

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


@pytest.mark.asyncio
async def test_handle_create_room_request_sends_invitation_when_room_does_not_exist(
    mocker,
):
    sid = "test_sid"
    address_a = "0xaaa"
    address_b = "0xbbb"
    data = {"target_address": address_b}

    mock_get_session = mocker.patch.object(
        manager.ws_manager.sio, "get_session", return_value={"address": address_a}
    )
    mock_room_exists = mocker.patch("app.room.crud.room_exists", return_value=False)
    mock_is_valid = mocker.patch(
        "app.room.utils.is_valid_eth_address", return_value=True
    )
    mock_emit = mocker.patch.object(manager.ws_manager.sio, "emit")
    mock_get_conn = mocker.patch(
        "app.core.database.db_manager.get_conn", return_value=FakeAsyncContextManager()
    )
    mock_get_redis_pool = mocker.patch(
        "app.ws.manager.get_redis_pool", return_value=mocker.AsyncMock()
    )

    await manager.ws_manager.handle_create_room_request(sid, data)

    mock_get_redis_pool.assert_called_once()
