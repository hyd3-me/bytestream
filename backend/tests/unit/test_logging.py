import pytest
import logging
import tempfile
import os
from pathlib import Path
from app.core.config import Settings
from app.core.logging import setup_logging, get_logger


def test_get_logger_returns_logger():
    logger = get_logger(__name__)
    assert isinstance(logger, logging.Logger)
    logger.debug("debug")
    logger.info("info")
    logger.warning("warning")
    logger.error("error")


def test_setup_logging_development():
    settings = Settings(environment="development", log_level="DEBUG")
    setup_logging(settings)
    root_logger = logging.getLogger()
    handlers = root_logger.handlers
    assert len(handlers) >= 1
    assert any(isinstance(h, logging.StreamHandler) for h in handlers)
    assert root_logger.level == logging.DEBUG


def test_setup_logging_production_without_file_raises():
    settings = Settings(environment="production", log_file=None)
    with pytest.raises(ValueError, match="LOG_FILE must be set"):
        setup_logging(settings)


def test_setup_logging_production_with_writable_file(tmp_path):
    log_file = tmp_path / "app.log"
    settings = Settings(
        environment="production", log_file=str(log_file), log_level="INFO"
    )
    setup_logging(settings)
    root_logger = logging.getLogger()
    handlers = root_logger.handlers
    assert len(handlers) >= 1
    file_handlers = [
        h for h in handlers if isinstance(h, logging.handlers.RotatingFileHandler)
    ]
    assert len(file_handlers) == 1
    test_logger = logging.getLogger("test")
    test_logger.info("Test message")
    assert log_file.exists()
    content = log_file.read_text()
    assert "Test message" in content


def test_setup_logging_production_with_unwritable_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = Path(tmpdir) / "subdir" / "app.log"
        log_path.parent.mkdir()
        os.chmod(log_path.parent, 0o555)  # r-xr-xr-x
        settings = Settings(
            environment="production", log_file=str(log_path), log_level="INFO"
        )
        with pytest.raises(RuntimeError, match="Cannot write to log file"):
            setup_logging(settings)
