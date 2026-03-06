from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.auth.router import router as auth_router
from app.core.redis import get_redis_pool
from app.core.config import get_settings
from app.core.logging import setup_logging, get_logger

settings = get_settings()
setup_logging(settings)

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up...")
    redis = get_redis_pool()
    try:
        await redis.ping()
        logger.info("Redis connection successful")
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
        raise RuntimeError("Cannot connect to Redis") from e
    yield
    logger.info("Shutting down...")
    await redis.close()


app = FastAPI(title="Bytestream Messenger API", lifespan=lifespan)

app.include_router(auth_router)


@app.get("/health")
async def health_check():
    logger.debug("Health check called")
    return {"status": "ok"}
