import pytest
import redis.asyncio as redis


TEST_REDIS_URL = "redis://localhost:6379/1"


@pytest.fixture
async def redis_client():
    client = redis.from_url(TEST_REDIS_URL, decode_responses=True)
    yield client
    await client.flushdb()
    await client.close()


@pytest.mark.asyncio
async def test_nonce_stored_in_redis(client, redis_client):
    address = "0x1234567890123456789012345678901234567890"

    response = await client.get(f"/auth/nonce/{address}")
    assert response.status_code == 200
    nonce = response.json()["nonce"]

    key = f"nonce:{address}"
    stored_nonce = await redis_client.get(key)
    assert stored_nonce == nonce
