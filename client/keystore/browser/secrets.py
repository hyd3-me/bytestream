"""Derived shared secrets keyed by canonical master_key_id_pair."""

# path: client/keystore/browser/secrets.py

# --- Storage ---

_secrets = {}


# --- Public API ---


def build_master_key_id_pair(mkid_1: str, mkid_2: str) -> str:
    return ":".join(sorted([mkid_1, mkid_2]))


def store_secret(master_key_id_pair: str, shared_secret: bytes, aes_key: bytes) -> None:
    _secrets[master_key_id_pair] = {
        "shared_secret": shared_secret,
        "aes_key": aes_key,
    }


def get_secret(master_key_id_pair: str) -> dict | None:
    return _secrets.get(master_key_id_pair)


def clear_secrets() -> None:
    _secrets.clear()


def derive_and_store_secret(own_address: str, peer_address: str) -> dict:
    pass
