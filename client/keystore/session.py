"""Unlocked session keys in memory (per browser tab)."""

# path: client/keystore/session.py

# --- Storage ---

_sessions = {}

# --- Public API ---


def unlock_session(eth_address: str, master_key_id: str, master_key: bytes) -> None:
    pass


def get_session_keys(eth_address: str, master_key_id: str | None = None) -> dict:
    pass
