import pytest
from app.ws import manager


@pytest.mark.asyncio
async def test_handle_create_room_request_exists(mocker):
    sid = "test_sid"
    data = {"target_address": "0x123"}

    mocker.patch.object(
        manager.ws_manager.sio, "get_session", return_value={"address": "0xaaa"}
    )
    mocker.patch("app.room.utils.is_valid_eth_address", return_value=True)
    mocker.patch.object(manager.ws_manager.sio, "emit")

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
