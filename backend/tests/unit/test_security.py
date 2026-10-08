"""Unit tests for JWT creation and decoding."""

# path: backend/tests/unit/test_security.py

# --- Imports ---

import base64
from datetime import timedelta

import pytest
from cryptography.hazmat.primitives.asymmetric import ed25519
from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTError

from app.auth import security
from app.auth.security import create_access_token, decode_token
from app.core.config import get_settings

# --- Setup ---

settings = get_settings()


# --- Tests ---


def test_create_access_token_returns_string():
    token = create_access_token({"sub": "test_user"})
    assert isinstance(token, str)
    assert len(token) > 0


def test_decode_valid_token():
    data = {"sub": "test_user", "role": "user"}
    token = create_access_token(data)
    payload = decode_token(token)
    assert payload["sub"] == "test_user"
    assert payload["role"] == "user"
    assert "exp" in payload


def test_decode_expired_token():
    # Create token with negative expiry (already expired)
    expired_delta = timedelta(seconds=-1)
    token = create_access_token({"sub": "test_user"}, expires_delta=expired_delta)
    with pytest.raises(ExpiredSignatureError):
        decode_token(token)


def test_decode_token_with_invalid_signature():
    # Create token with a different secret
    wrong_secret = "different_secret_for_testing"
    token = jwt.encode(
        {"sub": "test_user"}, wrong_secret, algorithm=settings.jwt_algorithm
    )
    with pytest.raises(JWTError):
        decode_token(token)


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
