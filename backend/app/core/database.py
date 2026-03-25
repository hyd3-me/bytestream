import asyncpg
from .config import get_settings
from .logging import get_logger
from contextlib import asynccontextmanager

logger = get_logger(__name__)


class DatabaseManager:
    def __init__(self):
        self._pool = None

    async def initialize(self):
        settings = get_settings()
        self._pool = await asyncpg.create_pool(
            settings.database_url,
            min_size=1,
            max_size=10,
        )
        async with self._pool.acquire() as conn:
            await conn.execute("SELECT 1")
        logger.info("Database pool created and connection verified")

    async def close(self):
        if self._pool:
            await self._pool.close()
            logger.info("Database pool closed")

    @asynccontextmanager
    async def get_conn(self):
        async with self._pool.acquire() as conn:
            yield conn
