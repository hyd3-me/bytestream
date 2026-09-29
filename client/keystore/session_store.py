"""Session store: device key, tab state, and encrypted master keys at rest."""

# path: client/keystore/session_store.py

# --- Imports ---

import secrets
import client.crypto as crypto

# --- Storage ---

_device_key = None

# --- Public API ---


def get_or_create_device_key() -> bytes:
    global _device_key
    if _device_key is None:
        _device_key = secrets.token_bytes(32)
    return _device_key


def encrypt_master_key(master_key: bytes, key: bytes) -> tuple[bytes, bytes]:
    nonce = crypto.generate_nonce()
    ciphertext = crypto.encrypt_message(key, master_key, nonce)
    return ciphertext, nonce


def decrypt_master_key(ciphertext: bytes, nonce: bytes, key: bytes) -> bytes:
    pass
