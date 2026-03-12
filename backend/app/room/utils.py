def sort_addresses(addr1: str, addr2: str):
    """Return tuple of addresses sorted lexicographically."""
    return tuple(sorted([addr1, addr2]))


def get_dm_room_id(addr1: str, addr2: str) -> str:
    """Generate deterministic room ID for a DM between two addresses."""
    sorted_addrs = sort_addresses(addr1, addr2)
    return f"dm:{sorted_addrs[0]}:{sorted_addrs[1]}"
