import os
import sys
from pathlib import Path
from dotenv import load_dotenv, dotenv_values
from web3 import Web3
import asyncpg
from eth_account.messages import encode_defunct
import socket
import uvicorn
import socketio
import asyncio

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
from app.auth import security

settings = get_settings()


def reset_redis_pool():
    from app.core.redis import get_redis_pool

    get_redis_pool.cache_clear()


async def reset_db_pool():
    from app.core.database import db_manager

    if db_manager._pool is not None:
        await db_manager.close()


async def reset_infrastructure():
    reset_redis_pool()
    await reset_db_pool()


@pytest_asyncio.fixture
async def live_server():
    await reset_infrastructure()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()

    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning")
    server = uvicorn.Server(config)
    task = asyncio.create_task(server.serve())
    while not server.started:
        await asyncio.sleep(0.01)

    yield f"http://127.0.0.1:{port}"

    server.should_exit = True
    await task


@pytest_asyncio.fixture
async def socketio_client_factory(live_server):
    async def _create(token):
        sio = socketio.AsyncClient()
        await asyncio.wait_for(
            sio.connect(
                live_server,
                transports=["websocket"],
                headers={"Authorization": f"Bearer {token}"},
            ),
            timeout=5,
        )
        return sio

    yield _create


@pytest_asyncio.fixture
async def client():
    async with LifespanManager(app) as manager:
        async with AsyncClient(
            transport=ASGITransport(app=manager.app), base_url="http://test"
        ) as client:
            yield client


@pytest_asyncio.fixture
async def auth_token(client, test_account):
    address = test_account.address

    response = await client.get(f"/auth/nonce/{address}")
    assert response.status_code == 200
    nonce = response.json()["nonce"]

    message = encode_defunct(text=nonce)
    signature = test_account.sign_message(message).signature.hex()

    payload = {"address": address, "signature": signature}
    response = await client.post("/auth/verify", json=payload)
    assert response.status_code == 200

    return response.json()["access_token"]


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


@pytest.fixture
def room_users(test_account):
    w3 = Web3()
    account_b = w3.eth.account.create()

    address_a = test_account.address
    address_b = account_b.address

    token_a = security.create_access_token({"sub": address_a})
    token_b = security.create_access_token({"sub": address_b})

    return {
        "a": {"address": address_a, "token": token_a},
        "b": {"address": address_b, "token": token_b},
    }


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
