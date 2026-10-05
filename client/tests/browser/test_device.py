"""Tests for client/keystore/browser/device."""

# path: client/tests/browser/test_device.py

# --- Imports ---

from client.keystore.browser import device


# --- Tests ---

def test_get_or_create_device_key_exists():
    assert hasattr(device, "get_or_create_device_key")
    assert callable(device.get_or_create_device_key)


def test_get_or_create_device_key_returns_stable_32_bytes():
    key1 = device.get_or_create_device_key()
    key2 = device.get_or_create_device_key()

    assert isinstance(key1, bytes)
    assert len(key1) == 32
    assert key1 == key2
