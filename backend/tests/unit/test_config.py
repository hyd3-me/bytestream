import pytest
from app.core.config import Settings


def test_logging_settings_have_defaults():
    settings = Settings()
    assert hasattr(settings, "environment")
    assert hasattr(settings, "log_level")
    assert hasattr(settings, "log_file")
    assert hasattr(settings, "log_max_bytes")
    assert hasattr(settings, "log_backup_count")
    assert settings.environment == "development"
    assert settings.log_level == "INFO"
    assert settings.log_file is None
    assert settings.log_max_bytes == 2_097_152
    assert settings.log_backup_count == 3
