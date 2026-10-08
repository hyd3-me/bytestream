"""Unit tests for auth challenge handling."""

# path: backend/tests/unit/test_challenge.py

# --- Imports ---

from app.auth import challenge


# --- Tests ---

def test_generate_challenge_exists():
    assert hasattr(challenge, "generate_challenge")
    assert callable(challenge.generate_challenge)


def test_generate_challenge_returns_unique_string():
    c1 = challenge.generate_challenge()
    c2 = challenge.generate_challenge()

    assert isinstance(c1, str)
    assert len(c1) > 0
    assert c1 != c2


def test_store_challenge_exists():
    assert hasattr(challenge, "store_challenge")
    assert callable(challenge.store_challenge)
