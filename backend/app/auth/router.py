from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from app.auth import utils
from ..core.redis import get_redis
from ..core.config import get_settings

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


@router.get("/nonce/{address}")
async def get_nonce(address: str, redis: Redis = Depends(get_redis)):
    nonce = utils.generate_nonce()
    await utils.store_nonce(redis, address, nonce)
    return {"nonce": nonce}
