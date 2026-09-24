from client.keystore import account_protection


def test_get_protection_type_exists():
    assert hasattr(account_protection, "get_protection_type")
    assert callable(account_protection.get_protection_type)
