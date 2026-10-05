"""Tests for client/keystore/browser/recovery."""

# path: client/tests/browser/test_recovery.py

# --- Imports ---

from client.keystore.browser import recovery as master_keys


# --- Tests ---

def test_list_master_key_ids_exists():
    assert hasattr(master_keys, "list_master_key_ids")
    assert callable(master_keys.list_master_key_ids)


def test_store_master_key_for_recovery_exists():
    assert hasattr(master_keys, "store_master_key_for_recovery")
    assert callable(master_keys.store_master_key_for_recovery)


def test_load_master_key_for_recovery_exists():
    assert hasattr(master_keys, "load_master_key_for_recovery")
    assert callable(master_keys.load_master_key_for_recovery)


def test_store_and_load_master_key_for_recovery_roundtrip():
    master_key_id = "mkid_1"
    ciphertext = b"\xab" * 48
    nonce = b"\xcd" * 12

    master_keys.store_master_key_for_recovery(master_key_id, ciphertext, nonce)
    loaded = master_keys.load_master_key_for_recovery(master_key_id)

    assert loaded == (ciphertext, nonce)


def test_delete_master_key_exists():
    assert hasattr(master_keys, "delete_master_key")
    assert callable(master_keys.delete_master_key)


def test_delete_master_key_removes_recovery_store():
    master_key_id = "mkid_1"
    master_keys.store_master_key_for_recovery(master_key_id, b"\xaa" * 48, b"\x01" * 12)

    master_keys.delete_master_key(master_key_id)

    assert master_keys.load_master_key_for_recovery(master_key_id) is None
