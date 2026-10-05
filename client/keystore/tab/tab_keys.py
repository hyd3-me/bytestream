"""Tab-scoped keys: tab secret for F5 recovery."""

# path: client/keystore/tab/tab_keys.py

# --- Storage ---

_tab_secret = None

# --- Public API ---

def set_tab_secret(secret: bytes) -> None:
    global _tab_secret
    _tab_secret = secret


def get_tab_secret() -> bytes | None:
    return _tab_secret
