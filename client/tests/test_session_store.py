from client.keystore import session_store


def test_get_or_create_device_key_exists():
    assert hasattr(session_store, "get_or_create_device_key")
    assert callable(session_store.get_or_create_device_key)
