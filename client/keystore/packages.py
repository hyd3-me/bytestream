"""Package facade: current pointers and routers over browser/packages."""

# path: client/keystore/packages.py

# --- Imports ---

from client.keystore.browser import packages as browser_packages

# --- Storage ---

_current_package_ids = {}

# --- Public API ---

def store_key_package(package: dict) -> None:
    browser_packages.store_key_package(package)


def get_key_package_by_id(eth_address: str, package_id: str):
    return browser_packages.get_key_package_by_id(eth_address, package_id)


def get_peer_key_package(peer_address: str) -> dict | None:
    return browser_packages.get_peer_key_package(peer_address)


def set_current_key_package(eth_address: str, package_id: str) -> None:
    _current_package_ids[eth_address] = package_id


def get_current_key_package(eth_address: str) -> dict:
    package_id = _current_package_ids.get(eth_address)
    if package_id is None:
        raise ValueError("No current key package")
    package = browser_packages.get_key_package_by_id(eth_address, package_id)
    if package is None:
        raise ValueError("Current package not found")
    return package


def get_key_package(eth_address: str, package_id: str = "current"):
    if package_id == "current":
        try:
            return get_current_key_package(eth_address)
        except ValueError:
            return None
    return browser_packages.get_key_package_by_id(eth_address, package_id)


def clear_key_package(eth_address: str) -> None:
    browser_packages.clear_packages(eth_address)
    _current_package_ids.pop(eth_address, None)
