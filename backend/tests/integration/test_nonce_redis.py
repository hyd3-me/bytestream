import pytest
from app.auth.utils import get_nonce_key


@pytest.mark.asyncio
async def test_nonce_stored_in_redis(client, redis_client):
    address = "0x1234567890123456789012345678901234567890"

    response = await client.get(f"/auth/nonce/{address}")
    assert response.status_code == 200
    nonce = response.json()["nonce"]

    key = get_nonce_key(address)
    stored_nonce = await redis_client.get(key)
    assert stored_nonce == nonce
