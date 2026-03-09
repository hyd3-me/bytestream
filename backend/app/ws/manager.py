import urllib.parse
from app.auth import security
from app.core.logging import get_logger

logger = get_logger(__name__)


async def connect(sid, environ):
    auth_header = environ.get("HTTP_AUTHORIZATION")
    if not auth_header:
        logger.warning(
            f"Connection attempt without Authorization header from sid {sid}"
        )
        return False

    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        logger.warning(f"Invalid Authorization header format from sid {sid}")
        return False

    token = parts[1]
    try:
        payload = security.decode_token(token)
        address = payload.get("sub")
        if not address:
            return False
        await sio.save_session(sid, {"address": address})
        logger.info(f"Client {address} connected with sid {sid}")
        return True
    except Exception as e:
        logger.warning(f"Invalid token from sid {sid}: {e}")
        return False
