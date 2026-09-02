from app import crypto, crypto_constants
import app.core.web3 as web3


def test_derive_master_key_exists():
    assert hasattr(crypto, "derive_master_key")
    assert callable(crypto.derive_master_key)


def test_derive_master_key_returns_32_bytes(test_account):
    message = web3.encode_defunct(text=crypto_constants.FIXED_MESSAGE)
    signature = test_account.sign_message(message).signature

    key = crypto.derive_master_key(signature)

    assert isinstance(key, bytes)
    assert len(key) == 32


def test_derive_master_key_deterministic(test_account):
    message = web3.encode_defunct(text=crypto_constants.FIXED_MESSAGE)
    signature = test_account.sign_message(message).signature

    key1 = crypto.derive_master_key(signature)
    key2 = crypto.derive_master_key(signature)

    assert key1 == key2


def test_derive_x25519_keypair_exists():
    assert hasattr(crypto, "derive_x25519_keypair")
    assert callable(crypto.derive_x25519_keypair)


def test_derive_x25519_keypair_deterministic():
    master_key = b"\x01" * 32

    priv1, pub1 = crypto.derive_x25519_keypair(master_key)
    priv2, pub2 = crypto.derive_x25519_keypair(master_key)

    assert priv1.private_bytes_raw() == priv2.private_bytes_raw()
    assert pub1.public_bytes_raw() == pub2.public_bytes_raw()
