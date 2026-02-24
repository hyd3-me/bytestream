import os
import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

TEST_REDIS_URL = os.getenv("TEST_REDIS_URL", "redis://localhost:6379/1")
os.environ["REDIS_URL"] = TEST_REDIS_URL

import pytest, pytest_asyncio
from httpx import AsyncClient, ASGITransport
from main import app
import redis.asyncio as redis
from app.core.redis import get_redis


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


@pytest_asyncio.fixture
async def redis_client():
    client = redis.from_url(TEST_REDIS_URL, decode_responses=True)
    yield client
    await client.flushdb()
    await client.aclose()


@pytest_asyncio.fixture(autouse=True)
async def override_redis_dependency(redis_client):
    app.dependency_overrides[get_redis] = lambda: redis_client
    yield
    app.dependency_overrides.clear()
