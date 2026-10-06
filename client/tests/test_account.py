"""Tests for client/keystore/account."""

# path: client/tests/test_account.py

# --- Imports ---

from client.keystore import account


# --- Tests ---

def test_restore_tab_session_exists():
    assert hasattr(account, "restore_tab_session")
    assert callable(account.restore_tab_session)


def test_restore_tab_session_returns_no_active_session_when_empty():
    result = account.restore_tab_session()

    assert result == {"status": "no_active_session"}
