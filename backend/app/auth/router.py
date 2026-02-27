from fastapi import APIRouter, Depends, HTTPException, status
from redis.asyncio import Redis
from app.auth import utils
from ..core.redis import get_redis
from ..core.config import get_settings
from . import utils, security, schemas

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


@router.get("/nonce/{address}")
async def get_nonce(address: str, redis: Redis = Depends(get_redis)):
    nonce = utils.generate_nonce()
    await utils.store_nonce(redis, address, nonce)
    return {"nonce": nonce}


@router.post("/verify", response_model=schemas.TokenResponse)
async def verify(request: schemas.VerifyRequest, redis: Redis = Depends(get_redis)):
    nonce = await utils.get_nonce(redis, request.address)
    if nonce is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nonce not found or expired",
        )

    # Verify signature first (don't delete yet)
    if not security.verify_signature(request.address, nonce, request.signature):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid signature"
        )

    # If successful, delete nonce and create token
    await utils.delete_nonce(redis, request.address)
    access_token = security.create_access_token(data={"sub": request.address})
    return schemas.TokenResponse(access_token=access_token)
