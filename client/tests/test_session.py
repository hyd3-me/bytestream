"""Tests for client/keystore/session."""

# path: client/tests/test_session.py

# --- Imports ---

from client.keystore import session


# --- Tests ---

def test_unlock_session_exists():
    assert hasattr(session, "unlock_session")
    assert callable(session.unlock_session)
