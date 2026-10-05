"""Tab-scoped storage: tab secret and per-tab encrypted master keys."""

# path: client/keystore/session_store.py

# --- Imports ---

import secrets
import client.crypto as crypto

# --- Storage ---

_tab_secret = None

# --- Public API ---


def encrypt_master_key(master_key: bytes, key: bytes) -> tuple[bytes, bytes]:
    nonce = crypto.generate_nonce()
    ciphertext = crypto.encrypt_message(key, master_key, nonce)
    return ciphertext, nonce


def decrypt_master_key(ciphertext: bytes, nonce: bytes, key: bytes) -> bytes:
    return crypto.decrypt_message(key, ciphertext, nonce)


def set_tab_secret(secret: bytes) -> None:
    global _tab_secret
    _tab_secret = secret


def get_tab_secret() -> bytes | None:
    return _tab_secret
