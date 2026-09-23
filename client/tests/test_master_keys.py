from client.keystore import master_keys


def test_store_master_key_exists():
    assert hasattr(master_keys, "store_master_key")
    assert callable(master_keys.store_master_key)


def test_load_master_key_exists():
    assert hasattr(master_keys, "load_master_key")
    assert callable(master_keys.load_master_key)


def test_store_and_load_master_key_roundtrip():
    eth_address = "0xabc"
    master_key_id = "test_mkid"
    master_key = b"\x01" * 32

    master_keys.store_master_key(eth_address, master_key_id, master_key)
    loaded = master_keys.load_master_key(eth_address, master_key_id)

    assert loaded == master_key


def test_list_master_key_ids_exists():
    assert hasattr(master_keys, "list_master_key_ids")
    assert callable(master_keys.list_master_key_ids)
