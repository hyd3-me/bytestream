"""Tests for client/wallet."""

# path: client/tests/test_wallet.py

# --- Imports ---

from client import wallet


# --- Tests ---

def test_sign_fixed_message_exists():
    assert hasattr(wallet, "sign_fixed_message")
    assert callable(wallet.sign_fixed_message)
