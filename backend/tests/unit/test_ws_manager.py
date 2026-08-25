from app.ws import manager


def test_create_room_request_handler_is_registered():
    handlers = manager.ws_manager.sio.handlers["/"]
    assert "create_room_request" in handlers
    assert callable(handlers["create_room_request"])
