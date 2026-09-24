"""Account protection: PIN storage and verification."""

# path: client/keystore/account_protection.py

# --- Imports ---

import hashlib
import hmac
import secrets

PBKDF2_ITERATIONS = 600_000

# --- Storage ---

_account_protection = {}
_attempts = {}


# --- Public API ---

def get_protection_type(eth_address: str) -> dict:
    record = _account_protection.get(eth_address)
    if record is None:
        return {"type": "none"}
    return record


def set_pin(eth_address: str, pin: str) -> None:
    salt = secrets.token_bytes(16)
    pin_hash = hashlib.pbkdf2_hmac(
        "sha256",
        pin.encode("utf-8"),
        salt,
        PBKDF2_ITERATIONS,
        dklen=32,
    )
    _account_protection[eth_address] = {
        "type": "pin",
        "salt": salt,
        "hash": pin_hash,
    }


def verify_pin(eth_address: str, pin: str) -> bool:
    record = _account_protection.get(eth_address)
    if record is None:
        return False
    pin_hash = hashlib.pbkdf2_hmac(
        "sha256",
        pin.encode("utf-8"),
        record["salt"],
        PBKDF2_ITERATIONS,
        dklen=32,
    )
    return hmac.compare_digest(pin_hash, record["hash"])


def is_locked(eth_address: str) -> bool:
    pass
