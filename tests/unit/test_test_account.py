import os
import pytest
from web3 import Web3
from dotenv import dotenv_values
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
ENV_PATH = PROJECT_ROOT / ".env"

def test_test_account_private_key_exists():
    env_vars = dotenv_values(ENV_PATH)
    assert "TEST_ACCOUNT_PRIVATE_KEY" in env_vars, "TEST_ACCOUNT_PRIVATE_KEY not found in .env"
    key = env_vars["TEST_ACCOUNT_PRIVATE_KEY"]
    assert key.startswith("0x"), "Private key must start with 0x"
    assert len(key) == 66, "Private key length should be 66 characters (including 0x)"

def test_can_recover_account_from_private_key():
    env_vars = dotenv_values(ENV_PATH)
    key = env_vars.get("TEST_ACCOUNT_PRIVATE_KEY")
    if not key:
        pytest.skip("No TEST_ACCOUNT_PRIVATE_KEY in .env")
    w3 = Web3()
    account = w3.eth.account.from_key(key)
    assert account.address is not None
    assert isinstance(account.address, str)
    assert account.address.startswith("0x")