from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, ValidationError
from functools import lru_cache


class Settings(BaseSettings):
    redis_url: str = "redis://localhost:6379/0"
    redis_key_prefix: str = "bytestream:"
    nonce_ttl_seconds: int = 300

    # JWT settings
    jwt_secret_key: str = Field(..., env="JWT_SECRET_KEY")
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings():
    try:
        return Settings()
    except ValidationError as e:
        # Extract names of missing fields
        missing_fields = [
            err["loc"][0] for err in e.errors() if err["type"] == "missing"
        ]
        if missing_fields:
            raise RuntimeError(
                f"Missing required environment variables: {', '.join(missing_fields)}. "
                "Please set them in the .env file or in your environment."
            ) from e
        raise  # re-raise other validation errors
