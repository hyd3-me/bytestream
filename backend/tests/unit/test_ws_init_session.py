import pytest
from app.ws import manager


@pytest.mark.asyncio
async def test_init_session_with_address_joins_personal_room_and_confirms(mocker):
    sid = "test_sid_123"
    address = "0x1234567890123456789012345678901234567890"
    mock_get_session = mocker.patch.object(
        manager.ws_manager.sio, "get_session", return_value={"address": address}
    )
    mock_enter_room = mocker.patch.object(manager.ws_manager.sio, "enter_room")
    mock_emit = mocker.patch.object(manager.ws_manager.sio, "emit")

    await manager.ws_manager.handle_init_session(sid)

    mock_get_session.assert_awaited_once_with(sid)
    mock_enter_room.assert_awaited_once_with(sid, f"user:{address}")
    mock_emit.assert_awaited_once_with("session_initialized", room=sid)


@pytest.mark.asyncio
async def test_init_session_missing_address_logs_error_and_does_nothing(mocker):
    sid = "test_sid_123"
    mock_get_session = mocker.patch.object(
        manager.ws_manager.sio, "get_session", return_value={}
    )
    mock_enter_room = mocker.patch.object(manager.ws_manager.sio, "enter_room")
    mock_emit = mocker.patch.object(manager.ws_manager.sio, "emit")
    mock_logger = mocker.patch("app.ws.manager.logger")

    await manager.ws_manager.handle_init_session(sid)

    mock_get_session.assert_awaited_once_with(sid)
    mock_enter_room.assert_not_called()
    mock_emit.assert_not_called()
    mock_logger.error.assert_called_once_with(
        f"No address in session for sid {sid}, cannot init session"
    )
