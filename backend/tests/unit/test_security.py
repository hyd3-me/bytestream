"""Unit tests for signature verification."""

# path: backend/tests/unit/test_security.py

# --- Imports ---

import base64
import pytest
from cryptography.hazmat.primitives.asymmetric import ed25519
from eth_account.messages import encode_defunct

from app.auth import security

# --- Tests ---


def test_verify_ed25519_signature_exists():
    assert hasattr(security, "verify_ed25519_signature")
    assert callable(security.verify_ed25519_signature)



def test_verify_ed25519_signature_accepts_valid_signature():
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    message = b"challenge_bytes"
    signature = private_key.sign(message)

    public_key_b64 = base64.b64encode(public_key.public_bytes_raw()).decode("ascii")
    signature_b64 = base64.b64encode(signature).decode("ascii")

    assert (
        security.verify_ed25519_signature(public_key_b64, message, signature_b64)
        is True
    )


def test_verify_key_package_exists():
    assert hasattr(security, "verify_key_package")
    assert callable(security.verify_key_package)


def test_verify_key_package_accepts_valid_package(test_account):
    import json

    base_package = {
        "eth_address": test_account.address,
        "x25519_public_key": "dGVzdF94MjU1MTk=",
        "ed25519_public_key": "dGVzdF9lZDI1NTE5",
        "master_key_id": "dGVzdF9ta2lk",
    }
    canonical = json.dumps(base_package, sort_keys=True, separators=(",", ":"))
    message = encode_defunct(text=canonical)
    signature = test_account.sign_message(message).signature
    signed_package = {
        **base_package,
        "eth_signature": base64.b64encode(signature).decode("ascii"),
    }

    assert security.verify_key_package(signed_package) is True
