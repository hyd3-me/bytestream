import sys
from pathlib import Path
import pytest, pytest_asyncio
from httpx import AsyncClient, ASGITransport

backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from main import app


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client
