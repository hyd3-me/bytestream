import pytest


@pytest.mark.asyncio
async def test_socketio_connect_with_jwt(room_users, socketio_client_factory):
    user_a = room_users["a"]

    sio = await socketio_client_factory(user_a["token"])

    assert sio.connected is True

    await sio.disconnect()
