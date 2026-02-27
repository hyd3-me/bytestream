import os
import sys
from pathlib import Path
from dotenv import load_dotenv, dotenv_values
from web3 import Web3


# Load environment variables from .env file located in the project root
project_root = Path(__file__).parent.parent.parent  # source directory
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

# Add backend directory to Python path
backend_dir = project_root / "backend"
sys.path.insert(0, str(backend_dir))

# Use the REDIS_URL from environment (already includes password and DB)
# For tests, we expect the DB to be set appropriately (e.g., /1)
TEST_REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/1")
os.environ["REDIS_URL"] = TEST_REDIS_URL
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-pytest-only")

import pytest, pytest_asyncio
from httpx import AsyncClient, ASGITransport
from main import app
import redis.asyncio as redis
from app.core.redis import get_redis


@pytest_asyncio.fixture
async def client():
    """HTTP client for testing endpoints."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


@pytest_asyncio.fixture
async def redis_client():
    """Direct Redis client for test assertions. Cleans up after each test."""
    client = redis.from_url(TEST_REDIS_URL, decode_responses=True)
    yield client
    await client.flushdb()  # clear test database
    await client.aclose()  # properly close connection


@pytest_asyncio.fixture(autouse=True)
async def override_redis_dependency(redis_client):
    """Override the app's get_redis dependency to use the test client."""
    app.dependency_overrides[get_redis] = lambda: redis_client
    yield
    app.dependency_overrides.clear()


@pytest.fixture(scope="session")
def test_account():
    env_vars = dotenv_values(env_path)
    private_key = env_vars.get("TEST_ACCOUNT_PRIVATE_KEY")
    if not private_key:
        pytest.fail("TEST_ACCOUNT_PRIVATE_KEY not set in .env")
    w3 = Web3()
    account = w3.eth.account.from_key(private_key)
    return account
