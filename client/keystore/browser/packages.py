"""Public key package storage: own and peer packages."""

# path: client/keystore/browser/packages.py

# --- Imports ---

# --- Storage ---

_packages = {}
_latest_peer_ids = {}

# --- Public API ---

def store_key_package(package: dict) -> None:
    eth_address = package["eth_address"]
    master_key_id = package["master_key_id"]
    if eth_address not in _packages:
        _packages[eth_address] = {}
    _packages[eth_address][master_key_id] = package
    _latest_peer_ids[eth_address] = master_key_id


def get_key_package_by_id(eth_address: str, master_key_id: str):
    return _packages.get(eth_address, {}).get(master_key_id)


def clear_packages(eth_address: str) -> None:
    _packages.pop(eth_address, None)
    _latest_peer_ids.pop(eth_address, None)


def get_peer_key_package(peer_address: str) -> dict | None:
    master_key_id = _latest_peer_ids.get(peer_address)
    if master_key_id is None:
        return None
    return _packages.get(peer_address, {}).get(master_key_id)
