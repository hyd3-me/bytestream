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
