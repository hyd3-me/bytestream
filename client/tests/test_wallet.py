"""Tests for client/wallet."""

# path: client/tests/test_wallet.py

# --- Imports ---

from client import wallet


# --- Tests ---

def test_sign_fixed_message_exists():
    assert hasattr(wallet, "sign_fixed_message")
    assert callable(wallet.sign_fixed_message)


def test_sign_fixed_message_returns_65_bytes(test_account):
    signature = wallet.sign_fixed_message(test_account)

    assert isinstance(signature, bytes)
    assert len(signature) == 65
