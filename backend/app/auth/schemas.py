"""Pydantic schemas for authentication endpoints."""

# path: backend/app/auth/schemas.py

# --- Imports ---

from pydantic import BaseModel

# --- Public API ---

class VerifyRequest(BaseModel):
    address: str
    signature: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
