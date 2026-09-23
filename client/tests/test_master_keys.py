from client.keystore import master_keys


def test_store_master_key_exists():
    assert hasattr(master_keys, "store_master_key")
    assert callable(master_keys.store_master_key)
