import pytest
from datetime import timedelta
from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTError
from app.core.config import get_settings

from app.auth.security import create_access_token, decode_token

settings = get_settings()


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
    # Create a token with a different secret (simulate tampering)
    valid_token = create_access_token({"sub": "test_user"})
    # Tamper with the token (change last character)
    invalid_token = valid_token[:-1] + ("a" if valid_token[-1] != "a" else "b")
    with pytest.raises(JWTError):  # JWTError is base for signature errors
        decode_token(invalid_token)
