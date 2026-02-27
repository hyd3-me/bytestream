from datetime import datetime, timedelta, timezone
from jose import jwt
from ..core.config import get_settings
from web3 import Web3
from eth_account.messages import encode_defunct

settings = get_settings()


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
    w3 = Web3()
    message_encoded = encode_defunct(text=message)
    recovered_address = w3.eth.account.recover_message(
        message_encoded, signature=signature
    )
    return recovered_address.lower() == address.lower()
