"""Tests for client/keystore/at_rest."""

# path: client/tests/test_at_rest.py

# --- Imports ---

from client.keystore import at_rest


# --- Tests ---

def test_encrypt_master_key_exists():
    assert hasattr(at_rest, "encrypt_master_key")
    assert callable(at_rest.encrypt_master_key)


def test_encrypt_master_key_returns_ciphertext_and_nonce():
    master_key = b"\x01" * 32
    key = b"\x02" * 32

    ciphertext, nonce = at_rest.encrypt_master_key(master_key, key)

    assert isinstance(ciphertext, bytes)
    assert isinstance(nonce, bytes)
    assert len(nonce) == 12
    assert ciphertext != master_key


def test_decrypt_master_key_exists():
    assert hasattr(at_rest, "decrypt_master_key")
    assert callable(at_rest.decrypt_master_key)


def test_encrypt_decrypt_master_key_roundtrip():
    master_key = b"\x01" * 32
    key = b"\x02" * 32

    ciphertext, nonce = at_rest.encrypt_master_key(master_key, key)
    decrypted = at_rest.decrypt_master_key(ciphertext, nonce, key)

    assert decrypted == master_key
