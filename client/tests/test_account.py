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


def test_restore_tab_session_returns_no_tab_secret_when_secret_missing():
    from client.keystore.tab import tab_state

    tab_state.set_active_address("0xabc")

    result = account.restore_tab_session()

    assert result == {"status": "no_tab_secret"}


def test_restore_tab_session_unlocks_and_returns_ok(master_key):
    import secrets
    from client.keystore import at_rest
    from client.keystore.tab import tab_keys, tab_state
    from client.keystore.memory import session

    address = "0xabc"
    mkid = "mkid_1"
    tab_secret = secrets.token_bytes(32)
    ciphertext, nonce = at_rest.encrypt_master_key(master_key, tab_secret)

    tab_state.set_active_address(address)
    tab_state.set_current_master_key_id(address, mkid)
    tab_keys.set_tab_secret(tab_secret)
    tab_keys.store_master_key_for_tab(mkid, ciphertext, nonce)

    result = account.restore_tab_session()

    assert result == {"status": "ok", "master_key_id": mkid}
    assert session.is_session_active(address) is True


def test_unlock_account_exists():
    assert hasattr(account, "unlock_account")
    assert callable(account.unlock_account)


def test_unlock_account_returns_no_master_key_for_unknown_address():
    result = account.unlock_account("0xunknown")

    assert result == {"status": "no_master_key"}
