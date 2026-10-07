"""Wallet interface: sign fixed message and adapt signers."""

# path: client/wallet.py

# --- Imports ---

from app.core.web3 import encode_defunct

from client import crypto_constants

# --- Public API ---


def sign_fixed_message(signer) -> bytes:
    message = encode_defunct(text=crypto_constants.FIXED_MESSAGE)
    return signer.sign_message(message).signature
