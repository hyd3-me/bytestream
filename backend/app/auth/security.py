"""JWT creation, decoding, and Ethereum signature verification."""

# path: backend/app/auth/security.py

# --- Imports ---

import base64
from datetime import datetime, timedelta, timezone

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric import ed25519
from jose import jwt

import app.core.web3 as web3
from ..core.config import get_settings

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
