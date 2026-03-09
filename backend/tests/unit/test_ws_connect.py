import pytest
from app.ws import manager


@pytest.mark.asyncio
async def test_connect_without_auth_header_rejected():
    environ = {}
    result = await manager.connect("dummy_sid", environ)
    assert result is False


@pytest.mark.asyncio
async def test_connect_with_invalid_token_rejected():
    environ = {"HTTP_AUTHORIZATION": "Bearer invalidtoken"}
    result = await manager.connect("dummy_sid", environ)
    assert result is False


@pytest.mark.asyncio
async def test_connect_with_wrong_auth_format_rejected():
    environ = {"HTTP_AUTHORIZATION": "Basic xyz"}
    result = await manager.connect("dummy_sid", environ)
    assert result is False
