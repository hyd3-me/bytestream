from client.keystore import session_store


def test_get_or_create_device_key_exists():
    assert hasattr(session_store, "get_or_create_device_key")
    assert callable(session_store.get_or_create_device_key)


def test_get_or_create_device_key_returns_stable_32_bytes():
    key1 = session_store.get_or_create_device_key()
    key2 = session_store.get_or_create_device_key()

    assert isinstance(key1, bytes)
    assert len(key1) == 32
    assert key1 == key2


def test_encrypt_master_key_exists():
    assert hasattr(session_store, "encrypt_master_key")
    assert callable(session_store.encrypt_master_key)
