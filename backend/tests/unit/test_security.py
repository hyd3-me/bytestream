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
    # Create token with a different secret
    wrong_secret = "different_secret_for_testing"
    token = jwt.encode(
        {"sub": "test_user"}, wrong_secret, algorithm=settings.jwt_algorithm
    )
    with pytest.raises(JWTError):
        decode_token(token)
