import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent  # source directory

# Add backend directory to Python path
backend_dir = project_root / "backend"
sys.path.insert(0, str(backend_dir))

import pytest
from asgi_lifespan import LifespanManager
from httpx import AsyncClient
from main import app


@pytest.mark.asyncio
async def test_db_health():
    async with LifespanManager(app) as manager:
        async with AsyncClient(app=manager.app, base_url="http://test") as client:
            response = await client.get("/db-health")
            assert response.status_code == 200
            assert response.json() == {"status": "ok"}
