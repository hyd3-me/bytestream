import socketio
import secrets
from app.core.database import db_manager
from app.core.redis import get_redis_pool
from app.core.logging import get_logger
from app.auth import security
from app.room import crud, utils, redis_utils

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
            return await self.handle_connect(sid, environ)

        @self.sio.event
        async def disconnect(sid):
            await self._handle_disconnect(sid)

        @self.sio.event
        async def init_session(sid):
            await self.handle_init_session(sid)

        @self.sio.event
        async def create_room_request(sid, data):
            await self.handle_create_room_request(sid, data)

        @self.sio.event
        async def respond_to_room_request(sid, data):
            await self.handle_respond_to_room_request(sid, data)

    async def handle_connect(self, sid, environ):
        """Public method for testing and internal use."""
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

    async def handle_init_session(self, sid: str):
        """Handle client initialization: join personal room and send confirmation."""
        session = await self.sio.get_session(sid)
        address = session.get("address")
        if not address:
            logger.error(f"No address in session for sid {sid}, cannot init session")
            return

        personal_room = f"user:{address}"
        await self.sio.enter_room(sid, personal_room)
        logger.info(f"Client {address} joined personal room {personal_room}")
        await self.sio.emit("session_initialized", room=sid)

    def get_asgi_app(self, fastapi_app):
        return socketio.ASGIApp(self.sio, other_asgi_app=fastapi_app)

    async def handle_create_room_request(self, sid, data):
        session = await self.sio.get_session(sid)
        address = session.get("address")
        if not address:
            return
        target = data.get("target_address")
        if not target or not utils.is_valid_eth_address(target):
            return

        async with db_manager.get_conn() as conn:
            if await crud.room_exists(conn, address, target):
                room_id = utils.get_dm_room_id(address, target)
                await self.sio.enter_room(sid, room_id)
                await self.sio.emit("room_ready", {"room_id": room_id}, room=sid)
                return

        request_id = secrets.token_urlsafe(16)
        redis = get_redis_pool()
        await redis_utils.save_room_request(redis, request_id, address, target)

        personal_room = f"user:{target}"
        await self.sio.emit(
            "room_invitation",
            {"from": address, "request_id": request_id},
            room=personal_room,
        )

    async def handle_respond_to_room_request(self, sid, data):
        session = await self.sio.get_session(sid)
        address = session.get("address")
        if not address:
            return

        request_id = data.get("request_id")
        action = data.get("action")
        if not request_id or not action:
            return

        redis = get_redis_pool()
        request_info = await redis_utils.get_room_request(redis, request_id)
        if not request_info:
            return

        from_address = request_info["from"]

        if action == "decline":
            await redis_utils.delete_room_request(redis, request_id)
            personal_room = f"user:{from_address}"
            await self.sio.emit("room_declined", room=personal_room)
            return


ws_manager = SocketIOManager()
