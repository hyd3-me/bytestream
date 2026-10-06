"""Account orchestration: setup, unlock, and tab restore."""

# path: client/keystore/account.py

# --- Imports ---

from client.keystore import at_rest
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
    return {"status": "ok", "master_key_id": master_key_id}
