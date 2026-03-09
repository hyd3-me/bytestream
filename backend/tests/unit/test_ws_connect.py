import pytest
from app.ws import manager


@pytest.mark.asyncio
async def test_connect_without_auth_header_rejected():
    environ = {}
    result = await manager.connect("dummy_sid", environ)
    assert result is False
