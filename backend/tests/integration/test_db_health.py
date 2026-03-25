import pytest


@pytest.mark.asyncio
async def test_db_health(client):
    response = await client.get("/db-health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
