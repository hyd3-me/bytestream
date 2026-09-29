"""Integration test for /db-health."""

# path: backend/tests/integration/test_db_health.py

# --- Imports ---

import pytest

# --- Tests ---


@pytest.mark.asyncio
async def test_db_health(client):
    response = await client.get("/db-health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
