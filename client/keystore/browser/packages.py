"""Public key package storage: own and peer packages."""

# path: client/keystore/browser/packages.py

# --- Imports ---

import base64

# --- Storage ---

_packages = {}

# --- Public API ---

def store_key_package(package: dict) -> None:
    eth_address = package["eth_address"]
    package_id = package["package_id"]
    if eth_address not in _packages:
        _packages[eth_address] = {}
    _packages[eth_address][package_id] = package


def get_key_package_by_id(eth_address: str, package_id: str):
    return _packages.get(eth_address, {}).get(package_id)


def clear_packages(eth_address: str) -> None:
    _packages.pop(eth_address, None)


def get_peer_key_package(peer_address: str) -> dict | None:
    packages = _packages.get(peer_address)
    if not packages:
        return None
    latest_id = max(
        packages.keys(),
        key=lambda pid: base64.b64decode(pid)[:8],
    )
    return packages[latest_id]
