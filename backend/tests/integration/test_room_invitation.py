import pytest
from app.ws import manager


@pytest.mark.asyncio
async def test_handle_create_room_request_exists():
    sid = "test_sid"
    data = {"target_address": "0x123"}

    await manager.ws_manager.handle_create_room_request(sid, data)


@pytest.mark.asyncio
async def test_handle_create_room_request_gets_address_from_session(mocker):
    sid = "test_sid"
    data = {"target_address": "0x123"}
    mock_get_session = mocker.patch.object(
        manager.ws_manager.sio, "get_session", return_value={"address": "0xaaa"}
    )
    mock_emit = mocker.patch.object(manager.ws_manager.sio, "emit")

    await manager.ws_manager.handle_create_room_request(sid, data)

    mock_get_session.assert_awaited_once_with(sid)
    mock_emit.assert_not_called()
