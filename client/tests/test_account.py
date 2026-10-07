"""Tests for client/keystore/account."""

# path: client/tests/test_account.py

# --- Imports ---

import secrets

from client import crypto
from client.keystore import account, at_rest, exchange
from client.keystore.browser import device, packages as browser_packages, protection, recovery
from client.keystore.browser import secrets as browser_secrets
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


def test_setup_new_account_exists():
    assert hasattr(account, "setup_new_account")
    assert callable(account.setup_new_account)


def test_setup_new_account_returns_ok_with_master_key_id(test_account):
    result = account.setup_new_account(test_account.address, test_account)

    assert result["status"] == "ok"
    assert "master_key_id" in result
    assert isinstance(result["master_key_id"], str)
    assert result["master_key_id"]


def test_setup_new_account_persists_all_state(test_account):
    address = test_account.address

    result = account.setup_new_account(address, test_account)
    mkid = result["master_key_id"]

    package = browser_packages.get_key_package_by_id(address, mkid)
    assert package is not None
    assert tab_state.get_current_master_key_id(address) == mkid
    assert protection.get_protection_type(address) == {"type": "device_key"}
    assert recovery.load_master_key_for_recovery(mkid) is not None
    assert tab_keys.get_tab_secret() is not None
    assert tab_keys.load_master_key_for_tab(mkid) is not None
    assert session.is_session_active(address) is True
    assert tab_state.get_active_address() == address



def test_full_cycle_setup_exchange_encrypt_decrypt(test_account, test_account_b):
    alice = test_account.address
    bob = test_account_b.address

    result_a = account.setup_new_account(alice, test_account)
    result_b = account.setup_new_account(bob, test_account_b)
    assert result_a["status"] == "ok"
    assert result_b["status"] == "ok"

    request = exchange.build_key_exchange_request(alice, bob)
    response = exchange.handle_key_exchange_request(request, bob)
    exchange.handle_key_exchange_response(response, alice)

    secret_a = browser_secrets.derive_and_store_secret(alice, bob)
    secret_b = browser_secrets.derive_and_store_secret(bob, alice)
    assert secret_a is not None
    assert secret_b is not None
    assert secret_a["shared_secret"] == secret_b["shared_secret"]

    aes_key = secret_a["aes_key"]
    plaintext = b"Hello, Bob!"
    nonce = crypto.generate_nonce()
    ciphertext = crypto.encrypt_message(aes_key, plaintext, nonce)
    decrypted = crypto.decrypt_message(secret_b["aes_key"], ciphertext, nonce)
    assert decrypted == plaintext
