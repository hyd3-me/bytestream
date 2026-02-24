from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.auth.router import router as auth_router
from app.core.redis import get_redis_pool


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = get_redis_pool()
    try:
        await redis.ping()
        print("✅ Redis connection successful")
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        raise RuntimeError("Cannot connect to Redis") from e
    yield
    await redis.close()


app = FastAPI(title="Bytestream Messenger API", lifespan=lifespan)

app.include_router(auth_router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
