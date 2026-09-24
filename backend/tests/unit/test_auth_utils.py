"""Unit tests for app.auth.utils."""

# path: backend/tests/unit/test_auth_utils.py

# --- Imports ---

import pytest
from app.auth.utils import generate_nonce


# --- Tests ---

def test_generate_nonce_returns_string():
    nonce = generate_nonce()
    assert isinstance(nonce, str)
    assert len(nonce) > 0


def test_generate_nonce_is_unique():
    nonce1 = generate_nonce()
    nonce2 = generate_nonce()
    assert nonce1 != nonce2
