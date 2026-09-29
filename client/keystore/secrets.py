"""Derived shared secrets keyed by canonical package_id_pair."""

# path: client/keystore/secrets.py

# --- Storage ---

_secrets = {}


# --- Public API ---


def store_secret(package_id_pair: str, shared_secret: bytes, aes_key: bytes) -> None:
    _secrets[package_id_pair] = {
        "shared_secret": shared_secret,
        "aes_key": aes_key,
    }


def get_secret(package_id_pair: str) -> dict | None:
    return _secrets.get(package_id_pair)


def clear_secrets() -> None:
    _secrets.clear()


def derive_and_store_secret(own_address: str, peer_address: str) -> dict:
    pass
