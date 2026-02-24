import pytest


@pytest.mark.asyncio
async def test_get_nonce_returns_200_and_nonce(client):
    address = "0x1234567890123456789012345678901234567890"
    response = await client.get(f"/auth/nonce/{address}")
    assert response.status_code == 200
    data = response.json()
    assert "nonce" in data
    assert isinstance(data["nonce"], str)
    assert len(data["nonce"]) > 0
