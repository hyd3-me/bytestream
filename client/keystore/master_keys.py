"""Master key storage: encrypted blobs for recovery and per-tab restore."""

# path: client/keystore/master_keys.py

# --- Storage ---

_master_keys = {}
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
