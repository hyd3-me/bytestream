import pytest
import asyncpg
from app.core.config import get_settings

settings = get_settings()


@pytest.mark.asyncio
async def test_database_connection():
    dsn = settings.database_url
    if not dsn:
        pytest.fail("TEST_DATABASE_URL not set in environment or .env")

    try:
        conn = await asyncpg.connect(dsn)
    except Exception as e:
        pytest.fail(f"Cannot connect to test database: {e}")

    result = await conn.fetchval("SELECT 1")
    await conn.close()

    assert result == 1
