import secrets
from ..core.config import get_settings

settings = get_settings()


def generate_nonce() -> str:
    """Generate a cryptographically secure random nonce."""
    return secrets.token_urlsafe(32)


def get_nonce_key(address: str) -> str:
    """
    Return Redis key for storing nonce associated with the given Ethereum address.
    Key format: {prefix}nonce:{address}
    """
    return f"{settings.redis_key_prefix}nonce:{address}"
