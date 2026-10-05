"""Unlocked session keys in memory (per browser tab)."""

# path: client/keystore/session.py

# --- Imports ---

import client.crypto as crypto
from client.keystore.tab import tab_state as keystore_tab_state

# --- Storage ---

_sessions = {}

# --- Public API ---


def unlock_session(eth_address: str, master_key_id: str, master_key: bytes) -> None:
    x25519_private, x25519_public = crypto.derive_x25519_keypair(master_key)
    ed25519_private, ed25519_public = crypto.derive_ed25519_keypair(master_key)
    _sessions.setdefault(eth_address, {})[master_key_id] = {
        "x25519_private": x25519_private,
        "x25519_public": x25519_public,
        "ed25519_private": ed25519_private,
        "ed25519_public": ed25519_public,
    }


def get_session_keys(eth_address: str, master_key_id: str | None = None) -> dict:
    if master_key_id is None:
        master_key_id = keystore_tab_state.get_current_master_key_id(eth_address)
    keys = _sessions.get(eth_address, {}).get(master_key_id)
    if keys is None:
        raise ValueError("Session keys not found")
    return keys


def is_session_active(eth_address: str) -> bool:
    return eth_address in _sessions and bool(_sessions[eth_address])
