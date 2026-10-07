"""Derived shared secrets keyed by canonical master_key_id_pair."""

# path: client/keystore/browser/secrets.py

# --- Imports ---

import client.crypto as crypto
from client.keystore.browser import packages as browser_packages
from client.keystore.memory import session
from client.keystore.tab import tab_state

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


def derive_and_store_secret(
    own_address: str,
    peer_address: str,
    own_mkid: str | None = None,
    peer_mkid: str | None = None,
) -> dict | None:
    if own_mkid is None:
        own_mkid = tab_state.get_current_master_key_id(own_address)
    if own_mkid is None:
        return None
    own_package = browser_packages.get_key_package_by_id(own_address, own_mkid)
    if own_package is None:
        return None

    if peer_mkid is None:
        peer_package = browser_packages.get_peer_key_package(peer_address)
    else:
        peer_package = browser_packages.get_key_package_by_id(peer_address, peer_mkid)
    if peer_package is None:
        return None
    peer_mkid = peer_package["master_key_id"]

    try:
        own_keys = session.get_session_keys(own_address, own_mkid)
    except ValueError:
        return None

    peer_x25519 = crypto.load_x25519_public_key(peer_package["x25519_public_key"])
    shared_secret = crypto.compute_shared_secret(
        own_keys["x25519_private"], peer_x25519
    )
    aes_key = crypto.derive_aes_key(shared_secret)

    pair = build_master_key_id_pair(own_mkid, peer_mkid)
    store_secret(pair, shared_secret, aes_key)
    return {"shared_secret": shared_secret, "aes_key": aes_key}
