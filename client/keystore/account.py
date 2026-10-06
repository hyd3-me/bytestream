"""Account orchestration: setup, unlock, and tab restore."""

# path: client/keystore/account.py

# --- Imports ---

from client.keystore import at_rest
from client.keystore.browser import recovery
from client.keystore.memory import session
from client.keystore.tab import tab_keys, tab_state


# --- Public API ---

def restore_tab_session() -> dict:
    address = tab_state.get_active_address()
    if address is None:
        return {"status": "no_active_session"}
    tab_secret = tab_keys.get_tab_secret()
    if tab_secret is None:
        return {"status": "no_tab_secret"}
