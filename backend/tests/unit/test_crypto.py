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


def test_derive_ed25519_keypair_exists():
    assert hasattr(crypto, "derive_ed25519_keypair")
    assert callable(crypto.derive_ed25519_keypair)


def test_derive_ed25519_keypair_deterministic():
    master_key = b"\x02" * 32

    priv1, pub1 = crypto.derive_ed25519_keypair(master_key)
    priv2, pub2 = crypto.derive_ed25519_keypair(master_key)

    assert priv1.private_bytes_raw() == priv2.private_bytes_raw()
    assert pub1.public_bytes_raw() == pub2.public_bytes_raw()


def test_compute_shared_secret_exists():
    assert hasattr(crypto, "compute_shared_secret")
    assert callable(crypto.compute_shared_secret)


def test_compute_shared_secret_symmetric():
    master_key_a = b"\x03" * 32
    master_key_b = b"\x04" * 32

    alice_priv, alice_pub = crypto.derive_x25519_keypair(master_key_a)
    bob_priv, bob_pub = crypto.derive_x25519_keypair(master_key_b)

    secret_alice = crypto.compute_shared_secret(alice_priv, bob_pub)
    secret_bob = crypto.compute_shared_secret(bob_priv, alice_pub)

    assert isinstance(secret_alice, bytes)
    assert len(secret_alice) == 32
    assert secret_alice == secret_bob


def test_encrypt_message_exists():
    assert hasattr(crypto, "encrypt_message")
    assert callable(crypto.encrypt_message)


def test_decrypt_message_exists():
    assert hasattr(crypto, "decrypt_message")
    assert callable(crypto.decrypt_message)


def test_encrypt_message_returns_ciphertext():
    key = b"\x11" * 32
    plaintext = b"Hello, Bob!"
    nonce = b"\x22" * 12

    ciphertext = crypto.encrypt_message(key, plaintext, nonce)

    assert isinstance(ciphertext, bytes)
    assert ciphertext != plaintext


def test_decrypt_message_returns_plaintext():
    key = b"\x11" * 32
    plaintext = b"Hello, Bob!"
    nonce = b"\x22" * 12

    ciphertext = crypto.encrypt_message(key, plaintext, nonce)
    decrypted = crypto.decrypt_message(key, ciphertext, nonce)

    assert decrypted == plaintext


def test_generate_timestamp_exists():
    assert hasattr(crypto, "generate_timestamp")
    assert callable(crypto.generate_timestamp)


def test_generate_timestamp_returns_positive_int():
    ts = crypto.generate_timestamp()

    assert isinstance(ts, int)
    assert ts > 0


def test_generate_nonce_exists():
    assert hasattr(crypto, "generate_nonce")
    assert callable(crypto.generate_nonce)
