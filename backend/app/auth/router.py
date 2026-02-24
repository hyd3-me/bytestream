from fastapi import APIRouter
from .utils import generate_nonce

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/nonce/{address}")
async def get_nonce(address: str):
    """
    Get a nonce for the given Ethereum address.
    The nonce should be signed by the user to authenticate.
    """
    nonce = generate_nonce()
    # TODO: store nonce in cache (Redis) with address as key for later verification
    return {"nonce": nonce}
