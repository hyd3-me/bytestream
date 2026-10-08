"""Auth challenge generation and Redis-backed storage."""

# path: backend/app/auth/challenge.py

# --- Imports ---

import secrets

# --- Public API ---


def generate_challenge() -> str:
    return secrets.token_urlsafe(32)
