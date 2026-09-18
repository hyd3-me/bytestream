import base64

_packages = {}
_current_package_ids = {}


def store_key_package(package: dict) -> None:
    eth_address = package["eth_address"]
    package_id = package["package_id"]
    if eth_address not in _packages:
        _packages[eth_address] = {}
    _packages[eth_address][package_id] = package


def set_current_key_package(eth_address: str, package_id: str) -> None:
    _current_package_ids[eth_address] = package_id


def get_current_key_package(eth_address: str) -> dict:
    package_id = _current_package_ids.get(eth_address)
    if package_id is None:
        raise ValueError("No current key package")
    package = _packages.get(eth_address, {}).get(package_id)
    if package is None:
        raise ValueError("Current package not found")
    return package


def get_key_package_by_id(eth_address: str, package_id: str):
    return _packages.get(eth_address, {}).get(package_id)


def get_key_package(eth_address: str, package_id: str = "current"):
    if package_id == "current":
        try:
            return get_current_key_package(eth_address)
        except ValueError:
            return None
    return get_key_package_by_id(eth_address, package_id)


def clear_key_package(eth_address: str) -> None:
    _packages.pop(eth_address, None)
    _current_package_ids.pop(eth_address, None)


def get_peer_key_package(peer_address: str) -> dict | None:
    packages = _packages.get(peer_address)
    if not packages:
        return None
    latest_id = max(
        packages.keys(),
        key=lambda pid: base64.b64decode(pid)[:8],
    )
    return packages[latest_id]
