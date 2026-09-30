"""Tests for client/keystore/session."""

# path: client/tests/test_session.py

# --- Imports ---

from client.keystore import session

# --- Tests ---


def test_unlock_session_exists():
    assert hasattr(session, "unlock_session")
    assert callable(session.unlock_session)


def test_unlock_session_stores_derived_keys(master_key_a, x25519_keypair_a, ed25519_keypair_a):
    from client import crypto

    eth_address = "0xabc"
    master_key_id = "mkid_1"

    session.unlock_session(eth_address, master_key_id, master_key_a)

    stored = session.get_session_keys(eth_address, master_key_id)

    _, expected_x_pub = x25519_keypair_a
    _, expected_e_pub = ed25519_keypair_a
    assert stored["x25519_public"].public_bytes_raw() == expected_x_pub.public_bytes_raw()
    assert stored["ed25519_public"].public_bytes_raw() == expected_e_pub.public_bytes_raw()


def test_is_session_active_exists():
    assert hasattr(session, "is_session_active")
    assert callable(session.is_session_active)


def test_is_session_active_returns_false_when_not_unlocked():
    assert session.is_session_active("0xabc") is False
