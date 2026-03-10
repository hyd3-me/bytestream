import pytest
from app.ws import manager
from app.auth import security


@pytest.mark.asyncio
async def test_connect_without_auth_header_rejected():
    result = await manager.ws_manager.handle_connect("dummy_sid", {})
    assert result is False


@pytest.mark.asyncio
async def test_connect_with_invalid_token_rejected():
    environ = {"HTTP_AUTHORIZATION": "Bearer invalidtoken"}
    result = await manager.ws_manager.handle_connect("dummy_sid", environ)
    assert result is False


@pytest.mark.asyncio
async def test_connect_with_wrong_auth_format_rejected():
    environ = {"HTTP_AUTHORIZATION": "Basic xyz"}
    result = await manager.ws_manager.handle_connect("dummy_sid", environ)
    assert result is False


@pytest.mark.asyncio
async def test_connect_with_valid_token_success(mocker):
    address = "0x1234567890123456789012345678901234567890"
    token = security.create_access_token({"sub": address})
    environ = {"HTTP_AUTHORIZATION": f"Bearer {token}"}
    sid = "test_sid_123"

    mock_save_session = mocker.patch.object(
        manager.ws_manager.sio, "save_session", return_value=None
    )

    result = await manager.ws_manager.handle_connect(sid, environ)

    assert result is True
    mock_save_session.assert_awaited_once_with(sid, {"address": address})
