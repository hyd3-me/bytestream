"""Signature verification for packages and auth challenges."""

# path: backend/app/auth/security.py

# --- Imports ---

import base64
import json

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric import ed25519

import app.core.web3 as web3

# --- Public API ---


def verify_signature(address: str, message: str, signature: str) -> bool:
    w3 = web3.get_web3()
    message_encoded = web3.encode_defunct(text=message)
    recovered_address = w3.eth.account.recover_message(
        message_encoded, signature=signature
    )
    return recovered_address.lower() == address.lower()


def verify_ed25519_signature(
    public_key_b64: str, message: bytes, signature_b64: str
) -> bool:
    public_key_bytes = base64.b64decode(public_key_b64)
    signature_bytes = base64.b64decode(signature_b64)
    public_key = ed25519.Ed25519PublicKey.from_public_bytes(public_key_bytes)
    try:
        public_key.verify(signature_bytes, message)
        return True
    except InvalidSignature:
        return False


def verify_key_package(package: dict) -> bool:
    base_package = {
        "eth_address": package["eth_address"],
        "x25519_public_key": package["x25519_public_key"],
        "ed25519_public_key": package["ed25519_public_key"],
        "master_key_id": package["master_key_id"],
    }
    canonical = json.dumps(base_package, sort_keys=True, separators=(",", ":"))
    signature_bytes = base64.b64decode(package["eth_signature"])
    return verify_signature(
        package["eth_address"],
        canonical,
        signature_bytes.hex(),
    )
