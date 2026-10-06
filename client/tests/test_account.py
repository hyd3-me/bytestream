"""Tests for client/keystore/account."""

# path: client/tests/test_account.py

# --- Imports ---

from client.keystore import account


# --- Tests ---

def test_restore_tab_session_exists():
    assert hasattr(account, "restore_tab_session")
    assert callable(account.restore_tab_session)
