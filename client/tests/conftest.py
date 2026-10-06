"""Shared pytest fixtures for client tests."""

# path: client/tests/conftest.py

# --- Imports ---

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent  # source directory
backend_dir = project_root / "backend"

sys.path.insert(0, str(project_root))
sys.path.insert(0, str(backend_dir))

from dotenv import dotenv_values
from web3 import Web3
from eth_account.messages import encode_defunct
import pytest

from client import crypto, crypto_constants
from client.keystore import package_ops
from client.keystore.browser import packages as keystore_browser_packages
from client.keystore.browser import packages as keystore_browser_packages
from client.keystore.tab import tab_state as keystore_tab_state
from client.keystore.browser import secrets as keystore_secrets
from client.keystore.browser import protection as keystore_account_protection
from client.keystore.memory import session as keystore_session
from client.keystore.tab import tab_keys as keystore_tab_keys
from client.keystore.browser import device as keystore_device
from client.keystore.browser import recovery as keystore_recovery
from client.keystore.tab import tab_state as keystore_tab_state

env_path = project_root / ".env"


# --- Fixtures ---


@pytest.fixture(scope="session")
def test_account():
    env_vars = dotenv_values(env_path)
    private_key = env_vars.get("TEST_ACCOUNT_PRIVATE_KEY")
    if not private_key:
        pytest.fail("TEST_ACCOUNT_PRIVATE_KEY not set in .env")
    w3 = Web3()
    return w3.eth.account.from_key(private_key)


@pytest.fixture(scope="session")
def test_account_b():
    env_vars = dotenv_values(env_path)
    private_key = env_vars.get("TEST_ACCOUNT_PRIVATE_KEY_2")
    if not private_key:
        pytest.fail("TEST_ACCOUNT_PRIVATE_KEY_2 not set in .env")
    w3 = Web3()
    return w3.eth.account.from_key(private_key)


@pytest.fixture(scope="session")
def master_key_a(test_account):
    message = encode_defunct(text=crypto_constants.FIXED_MESSAGE)
    signature = test_account.sign_message(message).signature
    return crypto.derive_master_key(signature)


@pytest.fixture(scope="session")
def master_key_b(test_account_b):
    message = encode_defunct(text=crypto_constants.FIXED_MESSAGE)
    signature = test_account_b.sign_message(message).signature
    return crypto.derive_master_key(signature)


@pytest.fixture(scope="session")
def x25519_keypair_a(master_key_a):
    return crypto.derive_x25519_keypair(master_key_a)


@pytest.fixture(scope="session")
def x25519_keypair_b(master_key_b):
    return crypto.derive_x25519_keypair(master_key_b)


@pytest.fixture(scope="session")
def ed25519_keypair_a(master_key_a):
    return crypto.derive_ed25519_keypair(master_key_a)


@pytest.fixture(scope="session")
def ed25519_keypair_b(master_key_b):
    return crypto.derive_ed25519_keypair(master_key_b)


@pytest.fixture
def master_key():
    return b"\x01" * 32


@pytest.fixture
def x25519_keypair(master_key):
    return crypto.derive_x25519_keypair(master_key)


@pytest.fixture
def ed25519_keypair(master_key):
    return crypto.derive_ed25519_keypair(master_key)


@pytest.fixture
def signed_package(test_account, x25519_keypair_a, ed25519_keypair_a):
    _, x_pub = x25519_keypair_a
    _, e_pub = ed25519_keypair_a
    base = package_ops.build_key_package(test_account.address, x_pub, e_pub)
    return package_ops.sign_key_package(test_account, base)


@pytest.fixture(autouse=True)
def _clear_crypto_state():
    keystore_browser_packages._packages.clear()
    keystore_secrets._secrets.clear()
    keystore_recovery._master_keys_for_recovery.clear()
    keystore_tab_state._current_master_key_ids.clear()
    keystore_account_protection._account_protection.clear()
    keystore_account_protection._attempts.clear()
    keystore_device._device_key = None
    keystore_tab_keys._tab_secret = None
    keystore_tab_keys._master_keys_for_tab.clear()
    keystore_tab_state._active_address = None
    keystore_session._sessions.clear()
    keystore_session._sessions.clear()
    yield
    keystore_browser_packages._packages.clear()
    keystore_secrets._secrets.clear()
    keystore_recovery._master_keys_for_recovery.clear()
    keystore_tab_state._current_master_key_ids.clear()
    keystore_account_protection._account_protection.clear()
    keystore_account_protection._attempts.clear()
    keystore_device._device_key = None
    keystore_tab_keys._tab_secret = None
    keystore_tab_keys._master_keys_for_tab.clear()
    keystore_tab_state._active_address = None


@pytest.fixture
def signed_package_b(test_account_b, x25519_keypair_b, ed25519_keypair_b):
    _, x_pub = x25519_keypair_b
    _, e_pub = ed25519_keypair_b
    base = package_ops.build_key_package(test_account_b.address, x_pub, e_pub)
    return package_ops.sign_key_package(test_account_b, base)
