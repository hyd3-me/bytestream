"""Tests for client/keystore/browser/protection."""

# path: client/tests/browser/test_protection.py

# --- Imports ---

from client.keystore.browser import protection as account_protection

# --- Tests ---


def test_get_protection_type_exists():
    assert hasattr(account_protection, "get_protection_type")
    assert callable(account_protection.get_protection_type)


def test_get_protection_type_returns_none_for_unknown_address():
    result = account_protection.get_protection_type("0xunknown")

    assert result == {"type": "none"}


def test_set_pin_exists():
    assert hasattr(account_protection, "set_pin")
    assert callable(account_protection.set_pin)


def test_set_pin_stores_salt_and_hash():
    account_protection.set_pin("0xabc", "1234")

    result = account_protection.get_protection_type("0xabc")

    assert result["type"] == "pin"
    assert "salt" in result
    assert "hash" in result
    assert isinstance(result["salt"], bytes)
    assert isinstance(result["hash"], bytes)
    assert len(result["salt"]) > 0
    assert len(result["hash"]) > 0


def test_verify_pin_exists():
    assert hasattr(account_protection, "verify_pin")
    assert callable(account_protection.verify_pin)


def test_verify_pin_returns_true_for_correct_pin():
    account_protection.set_pin("0xabc", "1234")

    assert account_protection.verify_pin("0xabc", "1234") is True


def test_verify_pin_returns_false_for_wrong_pin():
    account_protection.set_pin("0xabc", "1234")

    assert account_protection.verify_pin("0xabc", "9999") is False


def test_is_locked_exists():
    assert hasattr(account_protection, "is_locked")
    assert callable(account_protection.is_locked)


def test_is_locked_returns_false_for_unknown_address():
    assert account_protection.is_locked("0xunknown") is False


def test_is_locked_returns_true_after_max_attempts():
    account_protection.set_pin("0xabc", "1234")
    for _ in range(account_protection.MAX_ATTEMPTS):
        account_protection.verify_pin("0xabc", "0000")

    assert account_protection.is_locked("0xabc") is True


def test_verify_pin_resets_counter_on_success():
    account_protection.set_pin("0xabc", "1234")
    account_protection.verify_pin("0xabc", "0000")
    account_protection.verify_pin("0xabc", "0000")

    account_protection.verify_pin("0xabc", "1234")

    assert account_protection._attempts.get("0xabc") is None


def test_is_locked_expires_after_lockout_period(mocker):
    mock_time = mocker.patch("client.keystore.browser.protection.time.time")
    mock_time.return_value = 1000.0

    account_protection.set_pin("0xabc", "1234")
    for _ in range(account_protection.MAX_ATTEMPTS):
        account_protection.verify_pin("0xabc", "0000")
    assert account_protection.is_locked("0xabc") is True

    mock_time.return_value = 1000.0 + account_protection.LOCKOUT_SECONDS + 1
    assert account_protection.is_locked("0xabc") is False


def test_clear_protection_exists():
    assert hasattr(account_protection, "clear_protection")
    assert callable(account_protection.clear_protection)


def test_clear_protection_resets_to_device_key():
    account_protection.set_pin("0xabc", "1234")
    assert account_protection.get_protection_type("0xabc")["type"] == "pin"

    account_protection.clear_protection("0xabc")

    assert account_protection.get_protection_type("0xabc") == {"type": "device_key"}


def test_set_device_key_protection_exists():
    assert hasattr(account_protection, "set_device_key_protection")
    assert callable(account_protection.set_device_key_protection)


def test_set_device_key_protection_sets_type():
    account_protection.set_device_key_protection("0xabc")

    result = account_protection.get_protection_type("0xabc")

    assert result == {"type": "device_key"}


def test_set_pin_overrides_device_key_protection():
    account_protection.set_device_key_protection("0xabc")

    account_protection.set_pin("0xabc", "1234")

    result = account_protection.get_protection_type("0xabc")
    assert result["type"] == "pin"


def test_derive_pin_key_exists():
    assert hasattr(account_protection, "derive_pin_key")
    assert callable(account_protection.derive_pin_key)


def test_derive_pin_key_returns_32_bytes_deterministic():
    account_protection.set_pin("0xabc", "1234")

    key1 = account_protection.derive_pin_key("0xabc", "1234")
    key2 = account_protection.derive_pin_key("0xabc", "1234")

    assert isinstance(key1, bytes)
    assert len(key1) == 32
    assert key1 == key2
