import socket
import threading
import time

import pytest
import pytest_asyncio
import asyncio
import socketio
import uvicorn

from main import app
from app.core.redis import get_redis_pool
from app.core.database import db_manager


def reset_redis_pool():
    get_redis_pool.cache_clear()


async def reset_db_pool():
    if db_manager._pool is not None:
        await db_manager.close()


async def reset_infrastructure():
    reset_redis_pool()
    await reset_db_pool()


@pytest_asyncio.fixture
async def live_server():
    await reset_infrastructure()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()

    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning")
    server = uvicorn.Server(config)
    task = asyncio.create_task(server.serve())
    await asyncio.sleep(0.1)

    yield f"http://127.0.0.1:{port}"

    server.should_exit = True
    await task


@pytest_asyncio.fixture
async def socketio_client_factory(live_server):
    async def _create(token):
        sio = socketio.AsyncClient()
        await asyncio.wait_for(
            sio.connect(
                live_server,
                transports=["websocket"],
                headers={"Authorization": f"Bearer {token}"},
            ),
            timeout=5,
        )
        return sio

    yield _create


@pytest.mark.asyncio
async def test_socketio_connect_with_jwt(room_users, socketio_client_factory):
    user_a = room_users["a"]

    sio = await socketio_client_factory(user_a["token"])

    assert sio.connected is True

    await sio.disconnect()
