"""Tests for configuration management."""

from pathlib import Path

import pytest

from cakemail_mcp.config import Config, get_config


def test_config_default_values(monkeypatch):
    """Test configuration with default values."""
    # Clear environment variables
    monkeypatch.delenv("OPENAPI_SPEC_PATH", raising=False)
    monkeypatch.delenv("LOG_LEVEL", raising=False)

    config = get_config()

    assert config.log_level == "INFO"
    assert "openapi.json" in config.openapi_spec_path


def test_config_custom_values(monkeypatch):
    """Test configuration with custom environment variables."""
    monkeypatch.setenv("OPENAPI_SPEC_PATH", "/custom/path/spec.json")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")

    config = get_config()

    assert config.openapi_spec_path == "/custom/path/spec.json"
    assert config.log_level == "DEBUG"


def test_config_url_spec_path(monkeypatch):
    """Test configuration with URL spec path."""
    monkeypatch.setenv("OPENAPI_SPEC_PATH", "https://example.com/openapi.json")

    config = get_config()

    assert config.openapi_spec_path == "https://example.com/openapi.json"


def test_config_relative_path_conversion(monkeypatch, tmp_path):
    """Test that relative paths are converted to absolute."""
    monkeypatch.setenv("OPENAPI_SPEC_PATH", "relative/path.json")
    monkeypatch.chdir(tmp_path)

    config = get_config()

    assert Path(config.openapi_spec_path).is_absolute()
    assert config.openapi_spec_path == str(tmp_path / "relative" / "path.json")


def test_config_invalid_log_level():
    """Test that invalid log level raises ValueError."""
    with pytest.raises(ValueError, match="Invalid LOG_LEVEL"):
        Config(openapi_spec_path="./spec.json", log_level="INVALID")


def test_config_valid_log_levels():
    """Test all valid log levels."""
    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

    for level in valid_levels:
        config = Config(openapi_spec_path="./spec.json", log_level=level)
        assert config.log_level == level


def test_config_case_insensitive_log_level():
    """Test that log level validation is case-insensitive."""
    config = Config(openapi_spec_path="./spec.json", log_level="debug")
    assert config.log_level == "debug"  # Value is preserved
