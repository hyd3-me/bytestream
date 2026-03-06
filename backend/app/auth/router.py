from fastapi import APIRouter, Depends, HTTPException, status
from redis.asyncio import Redis
from app.auth import utils, security, schemas
from ..core.redis import get_redis
from ..core.config import get_settings
from ..core.logging import get_logger

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()
logger = get_logger(__name__)


@router.get("/nonce/{address}")
async def get_nonce(address: str, redis: Redis = Depends(get_redis)):
    logger.info(f"Generating nonce for address {address}")
    nonce = utils.generate_nonce()
    await utils.store_nonce(redis, address, nonce)
    logger.debug(f"Nonce {nonce} stored for {address}")
    return {"nonce": nonce}


@router.post("/verify", response_model=schemas.TokenResponse)
async def verify(request: schemas.VerifyRequest, redis: Redis = Depends(get_redis)):
    logger.info(f"Verifying signature for address {request.address}")
    nonce = await utils.get_nonce(redis, request.address)
    if nonce is None:
        logger.warning(f"Nonce not found or expired for {request.address}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nonce not found or expired",
        )

    if not security.verify_signature(request.address, nonce, request.signature):
        logger.warning(f"Invalid signature for address {request.address}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid signature"
        )

    await utils.delete_nonce(redis, request.address)
    access_token = security.create_access_token(data={"sub": request.address})
    logger.info(f"Successfully verified and created token for {request.address}")
    return schemas.TokenResponse(access_token=access_token)
