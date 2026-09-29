"""Session store: device key, tab state, and encrypted master keys at rest."""

# path: client/keystore/session_store.py

# --- Imports ---

import secrets

# --- Storage ---

_device_key = None

# --- Public API ---

def get_or_create_device_key() -> bytes:
    global _device_key
    if _device_key is None:
        _device_key = secrets.token_bytes(32)
    return _device_key
