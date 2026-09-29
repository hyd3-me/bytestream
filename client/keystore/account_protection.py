"""Account protection: PIN storage and verification."""

# path: client/keystore/account_protection.py

# --- Imports ---

import hashlib
import hmac
import secrets
import time

PBKDF2_ITERATIONS = 600_000
MAX_ATTEMPTS = 3
LOCKOUT_SECONDS = 900

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
    if is_locked(eth_address):
        return False
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
    if hmac.compare_digest(pin_hash, record["hash"]):
        _attempts.pop(eth_address, None)
        return True
    entry = _attempts.get(eth_address, {"count": 0, "last_attempt": 0.0})
    entry["count"] += 1
    entry["last_attempt"] = time.time()
    if entry["count"] >= MAX_ATTEMPTS:
        entry["count"] = 0
        entry["locked_until"] = time.time() + LOCKOUT_SECONDS
    _attempts[eth_address] = entry
    return False


def is_locked(eth_address: str) -> bool:
    entry = _attempts.get(eth_address)
    if entry is None:
        return False
    locked_until = entry.get("locked_until")
    if locked_until is None:
        return False
    return time.time() < locked_until


def clear_protection(eth_address: str) -> None:
    _account_protection.pop(eth_address, None)
    _attempts.pop(eth_address, None)


def set_device_key_protection(eth_address: str) -> None:
    pass
