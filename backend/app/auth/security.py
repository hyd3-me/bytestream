"""JWT creation, decoding, and Ethereum signature verification."""

# path: backend/app/auth/security.py

# --- Imports ---

from datetime import datetime, timedelta, timezone
from jose import jwt
from ..core.config import get_settings
import app.core.web3 as web3

# --- Setup ---

settings = get_settings()


# --- Public API ---

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.jwt_expire_minutes
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )
    return encoded_jwt


def decode_token(token: str) -> dict:
    return jwt.decode(
        token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
    )


def verify_signature(address: str, message: str, signature: str) -> bool:
    w3 = web3.get_web3()
    message_encoded = web3.encode_defunct(text=message)
    recovered_address = w3.eth.account.recover_message(
        message_encoded, signature=signature
    )
    return recovered_address.lower() == address.lower()
