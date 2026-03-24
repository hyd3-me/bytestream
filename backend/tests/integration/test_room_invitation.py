import pytest
from app.ws import manager


@pytest.mark.asyncio
async def test_handle_create_room_request_exists():
    sid = "test_sid"
    data = {"target_address": "0x123"}

    await manager.ws_manager.handle_create_room_request(sid, data)
