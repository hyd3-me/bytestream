"""Account orchestration: setup, unlock, and tab restore."""

# path: client/keystore/account.py

# --- Imports ---

import secrets

import client.crypto as crypto
import client.wallet as wallet
from client.keystore import at_rest, package_ops
from client.keystore.browser import packages as browser_packages
from client.keystore.browser import device, protection, recovery
from client.keystore.memory import session
from client.keystore.tab import tab_keys, tab_state


# --- Public API ---

def restore_tab_session() -> dict:
    address = tab_state.get_active_address()
    if address is None:
        return {"status": "no_active_session"}
    tab_secret = tab_keys.get_tab_secret()
    if tab_secret is None:
        return {"status": "no_tab_secret"}
    master_key_id = tab_state.get_current_master_key_id(address)
    if master_key_id is None:
        return {"status": "no_current_key"}
    blob = tab_keys.load_master_key_for_tab(master_key_id)
    if blob is None:
        return {"status": "no_master_key"}
    ciphertext, nonce = blob
    master_key = at_rest.decrypt_master_key(ciphertext, nonce, tab_secret)
    session.unlock_session(address, master_key_id, master_key)
    return {"status": "ok", "master_key_id": master_key_id}


def unlock_account(eth_address: str, pin: str | None = None) -> dict:
    protection_record = protection.get_protection_type(eth_address)
    if protection_record["type"] == "none":
        return {"status": "no_master_key"}
    if protection_record["type"] == "device_key":
        recovery_key = device.get_or_create_device_key()
    elif protection_record["type"] == "pin":
        if protection.is_locked(eth_address):
            return {"status": "locked"}
        if pin is None:
            return {"status": "pin_required"}
        if not protection.verify_pin(eth_address, pin):
            return {"status": "wrong_pin"}
        recovery_key = protection.derive_pin_key(eth_address, pin)
    else:
        return {"status": "unknown_protection_type"}
    master_key_id = tab_state.get_current_master_key_id(eth_address)
    if master_key_id is None:
        return {"status": "no_current_key"}
    blob = recovery.load_master_key_for_recovery(master_key_id)
    if blob is None:
        return {"status": "no_master_key"}
    ciphertext, nonce = blob
    master_key = at_rest.decrypt_master_key(ciphertext, nonce, recovery_key)
    session.unlock_session(eth_address, master_key_id, master_key)
    tab_state.set_active_address(eth_address)
    return {"status": "ok", "master_key_id": master_key_id}


def setup_new_account(eth_address: str, signer) -> dict:
    signature = wallet.sign_fixed_message(signer)
    master_key = crypto.derive_master_key(signature)
    _, x25519_public = crypto.derive_x25519_keypair(master_key)
    _, ed25519_public = crypto.derive_ed25519_keypair(master_key)

    base_package = package_ops.build_key_package(
        eth_address, x25519_public, ed25519_public
    )
    signed_package = package_ops.sign_key_package(signer, base_package)
    master_key_id = signed_package["master_key_id"]

    device_key = device.get_or_create_device_key()
    tab_secret = secrets.token_bytes(32)
    recovery_ciphertext, recovery_nonce = at_rest.encrypt_master_key(
        master_key, device_key
    )
    tab_ciphertext, tab_nonce = at_rest.encrypt_master_key(master_key, tab_secret)

    browser_packages.store_key_package(signed_package)
    tab_state.set_current_master_key_id(eth_address, master_key_id)
    protection.set_device_key_protection(eth_address)
    recovery.store_master_key_for_recovery(
        master_key_id, recovery_ciphertext, recovery_nonce
    )
    tab_keys.set_tab_secret(tab_secret)
    tab_keys.store_master_key_for_tab(master_key_id, tab_ciphertext, tab_nonce)

    session.unlock_session(eth_address, master_key_id, master_key)
    tab_state.set_active_address(eth_address)

    return {"status": "ok", "master_key_id": master_key_id}
