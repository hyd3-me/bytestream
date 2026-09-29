"""Integration test for .env file presence."""

# path: backend/tests/integration/test_env_file_exists.py

# --- Imports ---

import pytest
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
ENV_PATH = PROJECT_ROOT / ".env"


# --- Tests ---


def test_env_file_exists():
    """Test that .env file exists in the project root."""
    assert ENV_PATH.exists(), f".env file not found at {ENV_PATH}"
