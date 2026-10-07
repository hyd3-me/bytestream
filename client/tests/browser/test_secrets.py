"""Tests for client/keystore/browser/secrets."""

# path: client/tests/browser/test_secrets.py

# --- Imports ---

from client.keystore.browser import secrets

# --- Tests ---


def test_build_master_key_id_pair_exists():
    assert hasattr(secrets, "build_master_key_id_pair")
    assert callable(secrets.build_master_key_id_pair)


def test_build_master_key_id_pair_is_symmetric():
    mkid_a = "AAAB"
    mkid_b = "AAAC"

    pair_ab = secrets.build_master_key_id_pair(mkid_a, mkid_b)
    pair_ba = secrets.build_master_key_id_pair(mkid_b, mkid_a)

    assert pair_ab == pair_ba


def test_build_master_key_id_pair_returns_sorted_pair_with_colon():
    mkid_a = "ZZZZ"
    mkid_b = "AAAA"

    pair = secrets.build_master_key_id_pair(mkid_a, mkid_b)

    assert pair == "AAAA:ZZZZ"
