"""Web3 client and message encoding helpers."""

# path: backend/app/core/web3.py

# --- Imports ---

from functools import lru_cache
from web3 import Web3
from eth_account.messages import encode_defunct as _encode_defunct

# --- Public API ---


@lru_cache
def get_web3() -> Web3:
    return Web3()


def encode_defunct(text: str):
    return _encode_defunct(text=text)
