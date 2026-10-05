"""Recovery blobs: encrypted master keys retrievable after closing the tab."""

# path: client/keystore/browser/recovery.py

# --- Storage ---

_master_keys_for_recovery = {}
_master_keys = {}

# --- Public API ---

def list_master_key_ids(eth_address: str) -> list[str]:
    # TODO: implement with address -> [mkids] index
    return []


def store_master_key_for_recovery(
    master_key_id: str, ciphertext: bytes, nonce: bytes
) -> None:
    _master_keys_for_recovery[master_key_id] = (ciphertext, nonce)


def load_master_key_for_recovery(
    master_key_id: str,
) -> tuple[bytes, bytes] | None:
    return _master_keys_for_recovery.get(master_key_id)


def delete_master_key(master_key_id: str) -> None:
    _master_keys_for_recovery.pop(master_key_id, None)
