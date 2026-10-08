"""Unit tests for auth challenge handling."""

# path: backend/tests/unit/test_challenge.py

# --- Imports ---

from app.auth import challenge


# --- Tests ---

def test_generate_challenge_exists():
    assert hasattr(challenge, "generate_challenge")
    assert callable(challenge.generate_challenge)
