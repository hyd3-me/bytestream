"""Tests for client/keystore/master_keys."""

# path: client/tests/test_master_keys.py

# --- Imports ---

from client.keystore import master_keys


# --- Tests ---

def test_list_master_key_ids_exists():
    assert hasattr(master_keys, "list_master_key_ids")
    assert callable(master_keys.list_master_key_ids)


def test_list_known_addresses_exists():
    assert hasattr(master_keys, "list_known_addresses")
    assert callable(master_keys.list_known_addresses)


def test_set_current_master_key_id_exists():
    assert hasattr(master_keys, "set_current_master_key_id")
    assert callable(master_keys.set_current_master_key_id)


def test_get_current_master_key_id_exists():
    assert hasattr(master_keys, "get_current_master_key_id")
    assert callable(master_keys.get_current_master_key_id)


def test_set_and_get_current_master_key_id_roundtrip():
    master_keys.set_current_master_key_id("0xabc", "mkid_1")

    assert master_keys.get_current_master_key_id("0xabc") == "mkid_1"


def test_list_known_addresses_returns_addresses_with_current_key():
    master_keys.set_current_master_key_id("0xaaa", "mkid_a1")
    master_keys.set_current_master_key_id("0xbbb", "mkid_b1")

    result = master_keys.list_known_addresses()

    assert sorted(result) == ["0xaaa", "0xbbb"]


def test_list_known_addresses_returns_empty_when_no_current_keys():
    assert master_keys.list_known_addresses() == []


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
    master_keys.store_master_key_for_recovery(
        master_key_id, b"\xaa" * 48, b"\x01" * 12
    )

    master_keys.delete_master_key(master_key_id)

    assert master_keys.load_master_key_for_recovery(master_key_id) is None
