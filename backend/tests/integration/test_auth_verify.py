import pytest
from web3 import Web3
from eth_account.messages import encode_defunct
from app.auth import utils as auth_utils


@pytest.mark.asyncio
async def test_verify_endpoint_success(client, redis_client, test_account):
    address = test_account.address

    # Step 1: get nonce
    response = await client.get(f"/auth/nonce/{address}")
    assert response.status_code == 200
    nonce = response.json()["nonce"]

    # Step 2: sign the nonce using proper Ethereum message format
    message = encode_defunct(text=nonce)
    signature = test_account.sign_message(message).signature.hex()

    # Step 3: send verify request
    payload = {"address": address, "signature": signature}
    response = await client.post("/auth/verify", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

    # Step 4: check that nonce was deleted
    key = auth_utils.get_nonce_key(address)
    stored = await redis_client.get(key)
    assert stored is None


@pytest.mark.asyncio
async def test_verify_endpoint_invalid_signature(client, redis_client, test_account):
    address = test_account.address

    # get nonce
    response = await client.get(f"/auth/nonce/{address}")
    nonce = response.json()["nonce"]

    # sign with wrong message
    wrong_nonce = "some other string"
    message = encode_defunct(text=wrong_nonce)
    signature = test_account.sign_message(message).signature.hex()

    payload = {"address": address, "signature": signature}
    response = await client.post("/auth/verify", json=payload)
    assert response.status_code == 401

    # nonce should still exist
    key = auth_utils.get_nonce_key(address)
    stored = await redis_client.get(key)
    assert stored == nonce
