import os
import sys
from pathlib import Path
from dotenv import load_dotenv, dotenv_values
from web3 import Web3
import asyncpg
import pytest_asyncio


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
from asgi_lifespan import LifespanManager
from main import fastapi_app, app
import redis.asyncio as redis
from app.core.redis import get_redis
from app.core.config import get_settings

settings = get_settings()


@pytest_asyncio.fixture
async def client():
    async with LifespanManager(app) as manager:
        async with AsyncClient(
            transport=ASGITransport(app=manager.app), base_url="http://test"
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
    fastapi_app.dependency_overrides[get_redis] = lambda: redis_client
    yield
    fastapi_app.dependency_overrides.clear()


@pytest.fixture(scope="session")
def test_account():
    env_vars = dotenv_values(env_path)
    private_key = env_vars.get("TEST_ACCOUNT_PRIVATE_KEY")
    if not private_key:
        pytest.fail("TEST_ACCOUNT_PRIVATE_KEY not set in .env")
    w3 = Web3()
    account = w3.eth.account.from_key(private_key)
    return account


@pytest_asyncio.fixture(scope="session")
async def setup_db():
    conn = await asyncpg.connect(settings.database_url)
    schema_path = Path(__file__).parent / "fixtures" / "schema.sql"
    with open(schema_path) as f:
        schema_sql = f.read()
    await conn.execute(schema_sql)
    await conn.close()


@pytest_asyncio.fixture
async def async_db(setup_db):
    conn = await asyncpg.connect(settings.database_url)
    await conn.execute("BEGIN")
    yield conn
    await conn.execute("ROLLBACK")
    await conn.close()
