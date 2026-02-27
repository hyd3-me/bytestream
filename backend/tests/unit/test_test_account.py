import pytest
from web3 import Web3
from dotenv import dotenv_values
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
ENV_PATH = PROJECT_ROOT / ".env"


def test_test_account_private_key_exists():
    """Test that .env file exists and contains TEST_ACCOUNT_PRIVATE_KEY with valid format."""
    assert ENV_PATH.exists(), f".env file not found at {ENV_PATH}"
    env_vars = dotenv_values(ENV_PATH)
    assert (
        "TEST_ACCOUNT_PRIVATE_KEY" in env_vars
    ), "TEST_ACCOUNT_PRIVATE_KEY not found in .env"
    key = env_vars["TEST_ACCOUNT_PRIVATE_KEY"]
    if key.startswith("0x"):
        assert len(key) == 66, f"Private key with 0x must be 66 chars, got {len(key)}"
    else:
        assert (
            len(key) == 64
        ), f"Private key without 0x must be 64 chars, got {len(key)}"


def test_can_recover_account_from_private_key(test_account):
    """Test that we can recover an Ethereum account from the private key in .env."""
    assert test_account.address is not None
    assert isinstance(test_account.address, str)
    assert test_account.address.startswith("0x")
