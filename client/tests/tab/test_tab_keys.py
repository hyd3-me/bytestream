"""Tests for client/keystore/tab/tab_keys."""

# path: client/tests/tab/test_tab_keys.py

# --- Imports ---

from client.keystore.tab import tab_keys


# --- Tests ---

def test_set_tab_secret_exists():
    assert hasattr(tab_keys, "set_tab_secret")
    assert callable(tab_keys.set_tab_secret)


def test_get_tab_secret_exists():
    assert hasattr(tab_keys, "get_tab_secret")
    assert callable(tab_keys.get_tab_secret)


def test_set_and_get_tab_secret_roundtrip():
    secret = b"\xab" * 32

    tab_keys.set_tab_secret(secret)

    assert tab_keys.get_tab_secret() == secret


def test_store_master_key_for_tab_exists():
    assert hasattr(tab_keys, "store_master_key_for_tab")
    assert callable(tab_keys.store_master_key_for_tab)


def test_load_master_key_for_tab_exists():
    assert hasattr(tab_keys, "load_master_key_for_tab")
    assert callable(tab_keys.load_master_key_for_tab)
