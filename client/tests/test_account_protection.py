"""Tests for client/keystore/account_protection."""

# path: client/tests/test_account_protection.py

# --- Imports ---

from client.keystore import account_protection


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
    import time as _time

    account_protection.set_pin("0xabc", "1234")
    for _ in range(account_protection.MAX_ATTEMPTS):
        account_protection.verify_pin("0xabc", "0000")
    assert account_protection.is_locked("0xabc") is True

    now = _time.time()
    mock_time = mocker.patch("client.keystore.account_protection.time.time")
    mock_time.return_value = now + account_protection.LOCKOUT_SECONDS + 1

    assert account_protection.is_locked("0xabc") is False


def test_clear_protection_exists():
    assert hasattr(account_protection, "clear_protection")
    assert callable(account_protection.clear_protection)


def test_clear_protection_removes_pin_record():
    account_protection.set_pin("0xabc", "1234")
    assert account_protection.get_protection_type("0xabc")["type"] == "pin"

    account_protection.clear_protection("0xabc")

    assert account_protection.get_protection_type("0xabc") == {"type": "none"}


def test_set_device_key_protection_exists():
    assert hasattr(account_protection, "set_device_key_protection")
    assert callable(account_protection.set_device_key_protection)
