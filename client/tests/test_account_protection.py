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
