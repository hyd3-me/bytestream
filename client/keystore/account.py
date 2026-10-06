"""Account orchestration: setup, unlock, and tab restore."""

# path: client/keystore/account.py

# --- Imports ---

from client.keystore import at_rest
from client.keystore.browser import recovery
from client.keystore.memory import session
from client.keystore.tab import tab_keys, tab_state


# --- Public API ---

def restore_tab_session() -> dict:
    pass
