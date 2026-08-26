import pytest

from app.ws import manager


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
async def test_handle_respond_to_room_request_decline_notifies_and_deletes(mocker):
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

    mock_get_room_request.assert_awaited_once_with(mocker.ANY, "req123")
    mock_create_room.assert_not_called()
    mock_delete_room_request.assert_awaited_once_with(mocker.ANY, "req123")
    mock_emit.assert_awaited_once()
    call_args = mock_emit.call_args
    assert call_args.args[0] == "room_declined"
    assert call_args.kwargs["room"] == "user:0xaaa"
