"""Tests for client/keystore/session_store."""

# path: client/tests/test_session_store.py

# --- Imports ---

from client.keystore import session_store

# --- Tests ---


def test_get_or_create_device_key_exists():
    assert hasattr(session_store, "get_or_create_device_key")
    assert callable(session_store.get_or_create_device_key)


def test_get_or_create_device_key_returns_stable_32_bytes():
    key1 = session_store.get_or_create_device_key()
    key2 = session_store.get_or_create_device_key()

    assert isinstance(key1, bytes)
    assert len(key1) == 32
    assert key1 == key2


def test_encrypt_master_key_exists():
    assert hasattr(session_store, "encrypt_master_key")
    assert callable(session_store.encrypt_master_key)


def test_encrypt_master_key_returns_ciphertext_and_nonce():
    master_key = b"\x01" * 32
    key = b"\x02" * 32

    ciphertext, nonce = session_store.encrypt_master_key(master_key, key)

    assert isinstance(ciphertext, bytes)
    assert isinstance(nonce, bytes)
    assert len(nonce) == 12
    assert ciphertext != master_key


def test_decrypt_master_key_exists():
    assert hasattr(session_store, "decrypt_master_key")
    assert callable(session_store.decrypt_master_key)


def test_encrypt_decrypt_master_key_roundtrip():
    master_key = b"\x01" * 32
    key = b"\x02" * 32

    ciphertext, nonce = session_store.encrypt_master_key(master_key, key)
    decrypted = session_store.decrypt_master_key(ciphertext, nonce, key)

    assert decrypted == master_key


def test_set_tab_secret_exists():
    assert hasattr(session_store, "set_tab_secret")
    assert callable(session_store.set_tab_secret)


def test_get_tab_secret_exists():
    assert hasattr(session_store, "get_tab_secret")
    assert callable(session_store.get_tab_secret)


def test_set_and_get_tab_secret_roundtrip():
    secret = b"\xab" * 32

    session_store.set_tab_secret(secret)

    assert session_store.get_tab_secret() == secret
