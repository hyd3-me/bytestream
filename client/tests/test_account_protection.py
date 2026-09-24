from client.keystore import account_protection


def test_get_protection_type_exists():
    assert hasattr(account_protection, "get_protection_type")
    assert callable(account_protection.get_protection_type)


def test_get_protection_type_returns_none_for_unknown_address():
    result = account_protection.get_protection_type("0xunknown")

    assert result == {"type": "none"}


def test_set_pin_exists():
    assert hasattr(account_protection, "set_pin")
    assert callable(account_protection.set_pin)
