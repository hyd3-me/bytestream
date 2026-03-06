import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional
from .config import Settings


def setup_logging(settings: Settings) -> None:
    """Configure root logger based on environment."""
    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Clear existing handlers
    if root_logger.handlers:
        root_logger.handlers.clear()

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    if settings.environment == "production":
        if not settings.log_file:
            raise ValueError("LOG_FILE must be set in production")

        log_path = Path(settings.log_file)
        # Create parent directory if it doesn't exist
        log_path.parent.mkdir(parents=True, exist_ok=True)

        # Check if we can write to the file
        try:
            with open(log_path, "a") as f:
                pass
        except Exception as e:
            raise RuntimeError(f"Cannot write to log file {log_path}: {e}")

        file_handler = RotatingFileHandler(
            log_path,
            maxBytes=settings.log_max_bytes,
            backupCount=settings.log_backup_count,
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        root_logger.addHandler(file_handler)
    else:
        # Development: console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(level)
        root_logger.addHandler(console_handler)


def get_logger(name: str) -> logging.Logger:
    """Return a logger with the given name."""
    return logging.getLogger(name)
