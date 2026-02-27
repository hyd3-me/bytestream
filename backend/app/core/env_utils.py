from pathlib import Path
import secrets
from dotenv import dotenv_values, set_key


def ensure_jwt_secret_in_env(env_path: Path) -> None:
    """
    Ensure that the .env file contains a non-empty JWT_SECRET_KEY.
    If the key is missing or empty, generate a secure random key and add it.
    """
    # Load current variables
    env_vars = dotenv_values(env_path)
    current = env_vars.get("JWT_SECRET_KEY", "")
    if not current:
        # Generate a new key
        new_key = secrets.token_urlsafe(32)
        # Write it to the .env file (preserving existing content)
        set_key(str(env_path), "JWT_SECRET_KEY", new_key)
        print(f"JWT_SECRET_KEY added to {env_path}")
    else:
        print("JWT_SECRET_KEY already exists and is non-empty.")
