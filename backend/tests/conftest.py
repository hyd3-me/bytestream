"""Shared pytest fixtures for backend tests."""

# path: backend/tests/conftest.py

# --- Imports ---

import asyncio
import base64
import os
import socket
import sys
from pathlib import Path

import asyncpg
import pytest
import pytest_asyncio
import redis.asyncio as redis
import socketio
import uvicorn
from asgi_lifespan import LifespanManager
from dotenv import load_dotenv, dotenv_values
from eth_account.messages import encode_defunct
from httpx import ASGITransport, AsyncClient
from web3 import Web3

# Load environment variables from .env file located in the project root
project_root = Path(__file__).parent.parent.parent  # source directory
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

# Add source and backend to Python path
backend_dir = project_root / "backend"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(backend_dir))

TEST_REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/1")
os.environ["REDIS_URL"] = TEST_REDIS_URL

from client import crypto, wallet
from client.keystore import package_ops
from main import app, fastapi_app
from app.core.config import get_settings
from app.core.redis import get_redis

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


# --- Fixtures ---


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
async def auth_client_factory(live_server):
    async def _create(signer):
        signature = wallet.sign_fixed_message(signer)
        master_key = crypto.derive_master_key(signature)
        _, x_pub = crypto.derive_x25519_keypair(master_key)
        ed_priv, ed_pub = crypto.derive_ed25519_keypair(master_key)

        base_package = package_ops.build_key_package(signer.address, x_pub, ed_pub)
        signed_package = package_ops.sign_key_package(signer, base_package)

        sio = socketio.AsyncClient()

        challenge_event = asyncio.Event()
        challenge_holder = {}

        @sio.on("auth_challenge")
        async def _on_challenge(data):
            challenge_holder["challenge"] = data["challenge"]
            challenge_event.set()

        auth_ok_event = asyncio.Event()

        @sio.on("auth_ok")
        async def _on_auth_ok():
            auth_ok_event.set()

        await asyncio.wait_for(
            sio.connect(live_server, transports=["websocket"]),
            timeout=5,
        )
        await asyncio.wait_for(challenge_event.wait(), timeout=5)

        challenge_value = challenge_holder["challenge"]
        ed_sig = ed_priv.sign(challenge_value.encode())
        ed_sig_b64 = base64.b64encode(ed_sig).decode("ascii")

        await sio.emit(
            "auth_response",
            {
                "address": signer.address,
                "signature": ed_sig_b64,
                "package": signed_package,
            },
        )
        await asyncio.wait_for(auth_ok_event.wait(), timeout=5)
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
async def redis_client():
    """Direct Redis client for test assertions. Cleans up after each test."""
    client = redis.from_url(TEST_REDIS_URL, decode_responses=True)
    yield client
    await client.flushdb()
    await client.aclose()


@pytest.fixture(autouse=True)
def reset_redis_pool_cache():
    reset_redis_pool()
    yield


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


@pytest.fixture(scope="session")
def test_account_b():
    env_vars = dotenv_values(env_path)
    private_key = env_vars.get("TEST_ACCOUNT_PRIVATE_KEY_2")
    if not private_key:
        pytest.fail("TEST_ACCOUNT_PRIVATE_KEY_2 not set in .env")
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
    await conn.execute("TRUNCATE TABLE rooms;")
    await conn.execute("BEGIN")
    yield conn
    await conn.execute("ROLLBACK")
    await conn.close()
