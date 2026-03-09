import socketio
from app.core.logging import get_logger
from app.auth import security

logger = get_logger(__name__)


class SocketIOManager:
    def __init__(self):
        self.sio = socketio.AsyncServer(
            async_mode="asgi",
            cors_allowed_origins="*",
            logger=logger,
            engineio_logger=False,
        )
        self._register_handlers()

    def _register_handlers(self):
        @self.sio.event
        async def connect(sid, environ):
            return await self._handle_connect(sid, environ)

        @self.sio.event
        async def disconnect(sid):
            await self._handle_disconnect(sid)

    async def _handle_connect(self, sid, environ):
        auth_header = environ.get("HTTP_AUTHORIZATION")
        if not auth_header:
            logger.warning(f"Connection attempt without auth header from sid {sid}")
            return False

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            logger.warning(f"Invalid auth header format from sid {sid}")
            return False

        token = parts[1]
        try:
            payload = security.decode_token(token)
            address = payload.get("sub")
            if not address:
                return False
            await self.sio.save_session(sid, {"address": address})
            logger.info(f"Client {address} connected with sid {sid}")
            return True
        except Exception as e:
            logger.warning(f"Invalid token from sid {sid}: {e}")
            return False

    async def _handle_disconnect(self, sid):
        session = await self.sio.get_session(sid)
        address = session.get("address") if session else None
        logger.info(f"Client {address} disconnected (sid {sid})")

    def get_asgi_app(self, fastapi_app):
        return socketio.ASGIApp(self.sio, other_asgi_app=fastapi_app)


ws_manager = SocketIOManager()


async def connect(sid, environ):
    return await ws_manager._handle_connect(sid, environ)
