"""Master key storage: encrypted blobs for recovery and per-tab restore."""

# path: client/keystore/master_keys.py

# --- Storage ---

_master_keys = {}
_master_keys_for_recovery = {}
_master_keys_for_tab = {}
_current_master_key_ids = {}

# --- Public API ---

def list_master_key_ids(eth_address: str) -> list[str]:
    prefix = f"{eth_address}:"
    return [
        key[len(prefix):]
        for key in _master_keys
        if key.startswith(prefix)
    ]


def list_known_addresses() -> list[str]:
    return list(_current_master_key_ids.keys())


def set_current_master_key_id(eth_address: str, master_key_id: str) -> None:
    _current_master_key_ids[eth_address] = master_key_id


def get_current_master_key_id(eth_address: str) -> str | None:
    return _current_master_key_ids.get(eth_address)


def store_master_key_for_recovery(
    master_key_id: str, ciphertext: bytes, nonce: bytes
) -> None:
    _master_keys_for_recovery[master_key_id] = (ciphertext, nonce)


def load_master_key_for_recovery(
    master_key_id: str,
) -> tuple[bytes, bytes] | None:
    return _master_keys_for_recovery.get(master_key_id)


def store_master_key_for_tab(
    master_key_id: str, ciphertext: bytes, nonce: bytes
) -> None:
    _master_keys_for_tab[master_key_id] = (ciphertext, nonce)


def load_master_key_for_tab(
    master_key_id: str,
) -> tuple[bytes, bytes] | None:
    return _master_keys_for_tab.get(master_key_id)


def delete_master_key(master_key_id: str) -> None:
    _master_keys_for_recovery.pop(master_key_id, None)
    _master_keys_for_tab.pop(master_key_id, None)
