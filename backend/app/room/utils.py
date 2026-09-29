"""Room ID generation and address validation."""

# path: backend/app/room/utils.py

# --- Imports ---

from app.core.web3 import get_web3

# --- Public API ---


def sort_addresses(addr1: str, addr2: str):
    """Return tuple of addresses sorted lexicographically."""
    return tuple(sorted([addr1, addr2]))


def get_dm_room_id(addr1: str, addr2: str) -> str:
    """Generate deterministic room ID for a DM between two addresses."""
    sorted_addrs = sort_addresses(addr1, addr2)
    return f"dm:{sorted_addrs[0]}:{sorted_addrs[1]}"


def is_valid_eth_address(address: str) -> bool:
    return get_web3().is_address(address)
