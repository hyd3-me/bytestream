import pytest
import asyncio

from app.room import crud, utils, redis_utils


@pytest.mark.asyncio
async def test_socketio_connect_with_jwt(room_users, socketio_client_factory):
    user_a = room_users["a"]

    sio = await socketio_client_factory(user_a["token"])

    assert sio.connected is True

    await sio.disconnect()


@pytest.mark.asyncio
async def test_full_room_cycle(
    room_users, socketio_client_factory, async_db, redis_client
):
    user_a = room_users["a"]
    user_b = room_users["b"]

    sio_a = await socketio_client_factory(user_a["token"])
    sio_b = await socketio_client_factory(user_b["token"])

    try:
        init_a = asyncio.Event()
        init_b = asyncio.Event()

        @sio_a.on("session_initialized")
        async def _init_a():
            init_a.set()

        @sio_b.on("session_initialized")
        async def _init_b():
            init_b.set()

        await sio_a.emit("init_session")
        await sio_b.emit("init_session")
        await asyncio.wait_for(init_a.wait(), timeout=5)
        await asyncio.wait_for(init_b.wait(), timeout=5)

        invitation_event = asyncio.Event()
        invitation_data = {}

        @sio_b.on("room_invitation")
        async def _invitation(data):
            invitation_data.update(data)
            invitation_event.set()

        await sio_a.emit("create_room_request", {"target_address": user_b["address"]})
        await asyncio.wait_for(invitation_event.wait(), timeout=5)

        assert invitation_data["from"] == user_a["address"]
        request_id = invitation_data["request_id"]

        room_ready_a = asyncio.Event()
        room_ready_b = asyncio.Event()
        room_id_holder = {}

        @sio_a.on("room_ready")
        async def _ready_a(data):
            room_id_holder["room_id"] = data["room_id"]
            room_ready_a.set()

        @sio_b.on("room_ready")
        async def _ready_b(data):
            room_id_holder["room_id"] = data["room_id"]
            room_ready_b.set()

        await sio_b.emit(
            "respond_to_room_request",
            {"request_id": request_id, "action": "accept"},
        )
        await asyncio.wait_for(room_ready_a.wait(), timeout=5)
        await asyncio.wait_for(room_ready_b.wait(), timeout=5)

        room_id = room_id_holder["room_id"]
        assert room_id == utils.get_dm_room_id(user_a["address"], user_b["address"])

        joined_a = asyncio.Event()
        joined_b = asyncio.Event()

        @sio_a.on("joined_room")
        async def _joined_a(data):
            joined_a.set()

        @sio_b.on("joined_room")
        async def _joined_b(data):
            joined_b.set()

        await sio_a.emit("join_room", {"room_id": room_id})
        await sio_b.emit("join_room", {"room_id": room_id})
        await asyncio.wait_for(joined_a.wait(), timeout=5)
        await asyncio.wait_for(joined_b.wait(), timeout=5)

        room = await crud.get_room(async_db, room_id)
        assert room is not None
        assert room["user1"] == user_a["address"]
        assert room["user2"] == user_b["address"]

        request_key = redis_utils.get_room_request_key(request_id)
        assert await redis_client.exists(request_key) == 0

    finally:
        await sio_a.disconnect()
        await sio_b.disconnect()
