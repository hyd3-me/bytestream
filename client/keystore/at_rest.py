"""At-rest encryption helpers: wrap and unwrap secrets with AES-GCM."""

# path: client/keystore/at_rest.py

# --- Imports ---

import client.crypto as crypto

# --- Public API ---


def encrypt_master_key(master_key: bytes, key: bytes) -> tuple[bytes, bytes]:
    nonce = crypto.generate_nonce()
    ciphertext = crypto.encrypt_message(key, master_key, nonce)
    return ciphertext, nonce


def decrypt_master_key(ciphertext: bytes, nonce: bytes, key: bytes) -> bytes:
    return crypto.decrypt_message(key, ciphertext, nonce)
