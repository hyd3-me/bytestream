import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_get_nonce_returns_200_and_nonce():
    address = "0x1234567890123456789012345678901234567890"
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"/auth/nonce/{address}")

    assert response.status_code == 200
    data = response.json()
    assert "nonce" in data
    assert isinstance(data["nonce"], str)
    assert len(data["nonce"]) > 0
