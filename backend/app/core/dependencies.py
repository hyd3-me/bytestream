"""FastAPI dependency providers."""

# path: backend/app/core/dependencies.py

# --- Imports ---

from fastapi import Request
from app.core.database import db_manager


# --- Public API ---

async def get_db_conn(request: Request):
    async with db_manager.get_conn() as conn:
        yield conn
