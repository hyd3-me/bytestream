"""Tests for client/keystore/account."""

# path: client/tests/test_account.py

# --- Imports ---

import secrets

from client.keystore import account, at_rest
from client.keystore.browser import device, protection, recovery
from client.keystore.memory import session
from client.keystore.tab import tab_keys, tab_state


# --- Tests ---

def test_restore_tab_session_exists():
    assert hasattr(account, "restore_tab_session")
    assert callable(account.restore_tab_session)


def test_restore_tab_session_returns_no_active_session_when_empty():
    result = account.restore_tab_session()

    assert result == {"status": "no_active_session"}


def test_restore_tab_session_returns_no_tab_secret_when_secret_missing():
    tab_state.set_active_address("0xabc")

    result = account.restore_tab_session()

    assert result == {"status": "no_tab_secret"}


def test_restore_tab_session_unlocks_and_returns_ok(master_key):
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


def test_unlock_account_with_device_key_unlocks_and_returns_ok(master_key):
    address = "0xabc"
    mkid = "mkid_1"

    device_key = device.get_or_create_device_key()
    ciphertext, nonce = at_rest.encrypt_master_key(master_key, device_key)
    recovery.store_master_key_for_recovery(mkid, ciphertext, nonce)
    protection.set_device_key_protection(address)
    tab_state.set_current_master_key_id(address, mkid)

    result = account.unlock_account(address)

    assert result == {"status": "ok", "master_key_id": mkid}
    assert session.is_session_active(address) is True


def test_unlock_account_returns_pin_required_when_pin_missing():
    address = "0xabc"
    protection.set_pin(address, "1234")

    result = account.unlock_account(address)

    assert result == {"status": "pin_required"}


def test_unlock_account_returns_wrong_pin_for_incorrect_pin():
    address = "0xabc"
    protection.set_pin(address, "1234")

    result = account.unlock_account(address, "9999")

    assert result == {"status": "wrong_pin"}


def test_unlock_account_returns_locked_when_locked():
    address = "0xabc"
    protection.set_pin(address, "1234")
    for _ in range(protection.MAX_ATTEMPTS):
        protection.verify_pin(address, "0000")

    result = account.unlock_account(address, "1234")

    assert result == {"status": "locked"}


def test_unlock_account_sets_active_address(master_key):
    address = "0xabc"
    mkid = "mkid_1"

    device_key = device.get_or_create_device_key()
    ciphertext, nonce = at_rest.encrypt_master_key(master_key, device_key)
    recovery.store_master_key_for_recovery(mkid, ciphertext, nonce)
    protection.set_device_key_protection(address)
    tab_state.set_current_master_key_id(address, mkid)

    account.unlock_account(address)

    assert tab_state.get_active_address() == address
