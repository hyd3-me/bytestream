import pytest
import pytest_asyncio

from app.ws import manager
from app.room import utils, redis_utils


@pytest_asyncio.fixture
async def decline_setup(mocker):
    sid = "test_sid"
    data = {"request_id": "req123", "action": "decline"}
    address = "0xbbb"
    request_info = {"from": "0xaaa", "to": address}

    mocker.patch.object(
        manager.ws_manager.sio, "get_session", return_value={"address": address}
    )
    mock_get_room_request = mocker.patch(
        "app.room.redis_utils.get_room_request", return_value=request_info
    )
    mock_delete_room_request = mocker.patch("app.room.redis_utils.delete_room_request")
    mock_emit = mocker.patch.object(manager.ws_manager.sio, "emit")
    mock_create_room = mocker.patch("app.room.crud.create_room")

    await manager.ws_manager.handle_respond_to_room_request(sid, data)

    return {
        "mock_get_room_request": mock_get_room_request,
        "mock_delete_room_request": mock_delete_room_request,
        "mock_emit": mock_emit,
        "mock_create_room": mock_create_room,
    }


def test_create_room_request_handler_is_registered():
    handlers = manager.ws_manager.sio.handlers["/"]
    assert "create_room_request" in handlers
    assert callable(handlers["create_room_request"])


@pytest.mark.asyncio
async def test_create_room_request_handler_calls_handle(mocker):
    handler = manager.ws_manager.sio.handlers["/"]["create_room_request"]
    mock_handle = mocker.patch.object(manager.ws_manager, "handle_create_room_request")

    sid = "test_sid"
    data = {"target_address": "0x123"}
    await handler(sid, data)

    mock_handle.assert_awaited_once_with(sid, data)


def test_handle_respond_to_room_request_exists():
    assert hasattr(manager.ws_manager, "handle_respond_to_room_request")
    assert callable(manager.ws_manager.handle_respond_to_room_request)


def test_respond_to_room_request_handler_is_registered():
    handlers = manager.ws_manager.sio.handlers["/"]
    assert "respond_to_room_request" in handlers
    assert callable(handlers["respond_to_room_request"])


@pytest.mark.asyncio
async def test_respond_to_room_request_handler_calls_handle(mocker):
    handler = manager.ws_manager.sio.handlers["/"]["respond_to_room_request"]
    mock_handle = mocker.patch.object(
        manager.ws_manager, "handle_respond_to_room_request"
    )

    sid = "test_sid"
    data = {"request_id": "abc", "action": "accept"}
    await handler(sid, data)

    mock_handle.assert_awaited_once_with(sid, data)


@pytest.mark.asyncio
async def test_decline_gets_room_request_from_redis(decline_setup):
    mock_get = decline_setup["mock_get_room_request"]
    mock_get.assert_awaited_once()
    call_args = mock_get.call_args
    assert call_args.args[1] == "req123"


@pytest.mark.asyncio
async def test_decline_does_not_create_room(decline_setup):
    decline_setup["mock_create_room"].assert_not_called()


@pytest.mark.asyncio
async def test_decline_deletes_room_request(decline_setup):
    mock_delete = decline_setup["mock_delete_room_request"]
    mock_delete.assert_awaited_once()
    call_args = mock_delete.call_args
    assert call_args.args[1] == "req123"


@pytest.mark.asyncio
async def test_decline_emits_room_declined_to_requester(decline_setup):
    mock_emit = decline_setup["mock_emit"]
    mock_emit.assert_awaited_once()
    call_args = mock_emit.call_args
    assert call_args.args[0] == "room_declined"
    assert call_args.kwargs["room"] == redis_utils.get_personal_room_key("0xaaa")


@pytest_asyncio.fixture
async def accept_setup(mocker):
    sid = "test_sid"
    data = {"request_id": "req123", "action": "accept"}
    address_a = "0xaaa"
    address_b = "0xbbb"
    request_info = {"from": address_a, "to": address_b}

    mocker.patch.object(
        manager.ws_manager.sio, "get_session", return_value={"address": address_b}
    )
    mock_get_room_request = mocker.patch(
        "app.room.redis_utils.get_room_request", return_value=request_info
    )
    mock_delete_room_request = mocker.patch("app.room.redis_utils.delete_room_request")
    mock_emit = mocker.patch.object(manager.ws_manager.sio, "emit")
    mock_enter_room = mocker.patch.object(manager.ws_manager.sio, "enter_room")
    mock_create_room = mocker.patch("app.room.crud.create_room")

    await manager.ws_manager.handle_respond_to_room_request(sid, data)

    return {
        "mock_get_room_request": mock_get_room_request,
        "mock_delete_room_request": mock_delete_room_request,
        "mock_emit": mock_emit,
        "mock_enter_room": mock_enter_room,
        "mock_create_room": mock_create_room,
        "address_a": address_a,
        "address_b": address_b,
        "sid": sid,
    }


@pytest.mark.asyncio
async def test_accept_creates_room_with_correct_id_and_addresses(accept_setup, mocker):
    mock_create = accept_setup["mock_create_room"]
    address_a = accept_setup["address_a"]
    address_b = accept_setup["address_b"]
    room_id = utils.get_dm_room_id(address_a, address_b)

    mock_create.assert_awaited_once_with(mocker.ANY, room_id, address_a, address_b)


@pytest.mark.asyncio
async def test_accept_emits_room_ready_to_both_users(accept_setup):
    mock_emit = accept_setup["mock_emit"]
    room_id = utils.get_dm_room_id(accept_setup["address_a"], accept_setup["address_b"])
    personal_room_a = redis_utils.get_personal_room_key(accept_setup["address_a"])

    mock_emit.assert_any_await("room_ready", {"room_id": room_id}, room=personal_room_a)
    mock_emit.assert_any_await(
        "room_ready", {"room_id": room_id}, room=accept_setup["sid"]
    )


@pytest.mark.asyncio
async def test_accept_deletes_room_request(accept_setup, mocker):
    mock_delete = accept_setup["mock_delete_room_request"]
    mock_delete.assert_awaited_once_with(mocker.ANY, "req123")
