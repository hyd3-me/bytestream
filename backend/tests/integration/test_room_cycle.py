"""Integration tests for auth and room lifecycle over Socket.IO."""

# path: backend/tests/integration/test_room_cycle.py

# --- Imports ---

import asyncio

import pytest

from app.room import crud, redis_utils, utils


# --- Tests ---


@pytest.mark.asyncio
async def test_auth_client_factory_connects(auth_client_factory, test_account):
    sio = await auth_client_factory(test_account)

    assert sio.connected is True

    await sio.disconnect()
