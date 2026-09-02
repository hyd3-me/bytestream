from app import crypto
from web3 import Web3
from eth_account.messages import encode_defunct


def test_derive_master_key_exists():
    assert hasattr(crypto, "derive_master_key")
    assert callable(crypto.derive_master_key)


def test_derive_master_key_returns_32_bytes(test_account):
    w3 = Web3()
    message = encode_defunct(
        text="Bytestream v1: Generate messaging keys for this device."
    )
    signature = test_account.sign_message(message).signature

    key = crypto.derive_master_key(signature)

    assert isinstance(key, bytes)
    assert len(key) == 32
