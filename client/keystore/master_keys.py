"""Master key storage: per-address master keys, encrypted at rest (future)."""

# path: client/keystore/master_keys.py

# --- Storage ---

_master_keys = {}

# --- Public API ---

def store_master_key(
    eth_address: str, master_key_id: str, master_key: bytes
) -> None:
    key = f"{eth_address}:{master_key_id}"
    _master_keys[key] = master_key
def load_master_key(eth_address: str, master_key_id: str) -> bytes | None:
    key = f"{eth_address}:{master_key_id}"
    return _master_keys.get(key)


def list_master_key_ids(eth_address: str) -> list[str]:
    prefix = f"{eth_address}:"
    return [
        key[len(prefix):]
        for key in _master_keys
        if key.startswith(prefix)
    ]
