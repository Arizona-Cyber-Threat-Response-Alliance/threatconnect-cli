"""Tests for configuration manager."""

import pytest
import os
from pathlib import Path
from tc_tui.config import ConfigManager, AppConfig


def test_load_default_config(tmp_path):
    """Test loading default config when file doesn't exist."""
    config_path = tmp_path / "config.toml"

    config = ConfigManager.load(config_path)

    assert isinstance(config, AppConfig)
    assert config.ui.theme == "dark"
    assert config.ui.results_per_page == 100


def test_save_and_load_config(tmp_path):
    """Test saving and loading config."""
    config_path = tmp_path / "config.toml"

    # Create config
    config = AppConfig()
    config.api.access_id = "test_id"
    config.api.instance = "testcompany"
    config.ui.theme = "light"

    # Save
    ConfigManager.save(config, config_path)

    # Load
    loaded_config = ConfigManager.load(config_path)

    assert loaded_config.api.access_id == "test_id"
    assert loaded_config.api.instance == "testcompany"
    assert loaded_config.ui.theme == "light"


def test_env_override():
    """Test environment variable override."""
    # Save original env vars
    original_env = {}
    env_vars = ["TC_ACCESS_ID", "TC_SECRET_KEY", "TC_INSTANCE"]
    for var in env_vars:
        original_env[var] = os.environ.get(var)

    try:
        os.environ["TC_ACCESS_ID"] = "env_id"
        os.environ["TC_SECRET_KEY"] = "env_secret"
        os.environ["TC_INSTANCE"] = "envcompany"

        config = ConfigManager.load()

        assert config.api.access_id == "env_id"
        assert config.api.secret_key == "env_secret"
        assert config.api.instance == "envcompany"
    finally:
        # Cleanup - restore original env vars
        for var in env_vars:
            if original_env[var] is None:
                os.environ.pop(var, None)
            else:
                os.environ[var] = original_env[var]


def test_get_api_credentials():
    """Test getting API credentials."""
    config = AppConfig()
    config.api.access_id = "test_id"
    config.api.secret_key = "test_secret"
    config.api.instance = "testcompany"

    access_id, secret_key, instance = ConfigManager.get_api_credentials(config)

    assert access_id == "test_id"
    assert secret_key == "test_secret"
    assert instance == "testcompany"


def test_get_api_credentials_raises_on_missing():
    """Test that missing credentials raise an error."""
    config = AppConfig()  # Empty config

    with pytest.raises(ValueError, match="Missing API credentials"):
        ConfigManager.get_api_credentials(config)


def test_init_config(tmp_path):
    """Test initializing config file."""
    config_path = tmp_path / "config.toml"

    # Should create file
    result_path = ConfigManager.init_config(config_path)

    assert result_path == config_path
    assert config_path.exists()

    # Should load valid config
    config = ConfigManager.load(config_path)
    assert isinstance(config, AppConfig)
