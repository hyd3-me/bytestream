"""Unit tests for Socket.IO connect handler."""

# path: backend/tests/unit/test_ws_connect.py

# --- Imports ---

import pytest

from app.auth import challenge
from app.ws import manager


# --- Tests ---


@pytest.mark.asyncio
async def test_handle_connect_exists():
    assert hasattr(manager.ws_manager, "handle_connect")
    assert callable(manager.ws_manager.handle_connect)
