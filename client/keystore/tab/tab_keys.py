"""Tab-scoped keys: tab secret for F5 recovery."""

# path: client/keystore/tab/tab_keys.py

# --- Storage ---

_tab_secret = None
_master_keys_for_tab = {}

# --- Public API ---


def set_tab_secret(secret: bytes) -> None:
    global _tab_secret
    _tab_secret = secret


def get_tab_secret() -> bytes | None:
    return _tab_secret


def store_master_key_for_tab(
    master_key_id: str, ciphertext: bytes, nonce: bytes
) -> None:
    _master_keys_for_tab[master_key_id] = (ciphertext, nonce)


def load_master_key_for_tab(
    master_key_id: str,
) -> tuple[bytes, bytes] | None:
    return _master_keys_for_tab.get(master_key_id)
