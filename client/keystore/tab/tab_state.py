"""Tab-scoped state: known addresses and current key/package pointers."""

# path: client/keystore/tab/tab_state.py

# --- Imports ---

from client.keystore.browser import packages as browser_packages

# --- Storage ---

_active_address = None
_current_master_key_ids = {}

# --- Public API ---


def list_known_addresses() -> list[str]:
    return list(_current_master_key_ids.keys())


def set_current_master_key_id(eth_address: str, master_key_id: str) -> None:
    _current_master_key_ids[eth_address] = master_key_id


def get_current_master_key_id(eth_address: str) -> str | None:
    return _current_master_key_ids.get(eth_address)


def get_current_key_package(eth_address: str) -> dict:
    master_key_id = _current_master_key_ids.get(eth_address)
    if master_key_id is None:
        raise ValueError("No current key package")
    package = browser_packages.get_key_package_by_id(eth_address, master_key_id)
    if package is None:
        raise ValueError("Current package not found")
    return package


def get_key_package(eth_address: str, master_key_id: str = "current"):
    if master_key_id == "current":
        try:
            return get_current_key_package(eth_address)
        except ValueError:
            return None
    return browser_packages.get_key_package_by_id(eth_address, master_key_id)


def set_active_address(eth_address: str) -> None:
    global _active_address
    _active_address = eth_address


def get_active_address() -> str | None:
    return _active_address
