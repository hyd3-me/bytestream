"""Integration test for JWT_SECRET_KEY in .env."""

# path: backend/tests/integration/test_env_jwt_key.py

# --- Imports ---

import pytest
from pathlib import Path
from dotenv import dotenv_values

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
ENV_PATH = PROJECT_ROOT / ".env"


# --- Tests ---

def test_jwt_secret_key_exists_and_non_empty():
    """Test that JWT_SECRET_KEY is present in .env and not empty."""
    env_vars = dotenv_values(ENV_PATH)
    assert "JWT_SECRET_KEY" in env_vars, "JWT_SECRET_KEY not found in .env"
    assert env_vars["JWT_SECRET_KEY"], "JWT_SECRET_KEY is empty"
