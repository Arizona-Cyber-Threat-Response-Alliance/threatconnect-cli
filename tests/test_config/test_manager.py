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
    orig_access = os.environ.get("TC_ACCESS_ID")
    orig_secret = os.environ.get("TC_SECRET_KEY")
    orig_instance = os.environ.get("TC_INSTANCE")

    try:
        os.environ["TC_ACCESS_ID"] = "env_id"
        os.environ["TC_SECRET_KEY"] = "env_secret"
        os.environ["TC_INSTANCE"] = "envcompany"

        config = ConfigManager.load()

        assert config.api.access_id == "env_id"
        assert config.api.secret_key == "env_secret"
        assert config.api.instance == "envcompany"
    finally:
        # Cleanup
        if orig_access is not None:
            os.environ["TC_ACCESS_ID"] = orig_access
        else:
            os.environ.pop("TC_ACCESS_ID", None)

        if orig_secret is not None:
            os.environ["TC_SECRET_KEY"] = orig_secret
        else:
            os.environ.pop("TC_SECRET_KEY", None)

        if orig_instance is not None:
            os.environ["TC_INSTANCE"] = orig_instance
        else:
            os.environ.pop("TC_INSTANCE", None)


def test_legacy_env_vars():
    """Test legacy environment variable names."""
    # Save original env vars
    orig_access = os.environ.get("tc_accessid")
    orig_secret = os.environ.get("tc_secretkey")
    orig_company = os.environ.get("tc_company")

    try:
        os.environ["tc_accessid"] = "legacy_id"
        os.environ["tc_secretkey"] = "legacy_secret"
        os.environ["tc_company"] = "legacycompany"

        config = ConfigManager.load()

        assert config.api.access_id == "legacy_id"
        assert config.api.secret_key == "legacy_secret"
        assert config.api.instance == "legacycompany"
    finally:
        # Cleanup
        if orig_access is not None:
            os.environ["tc_accessid"] = orig_access
        else:
            os.environ.pop("tc_accessid", None)

        if orig_secret is not None:
            os.environ["tc_secretkey"] = orig_secret
        else:
            os.environ.pop("tc_secretkey", None)

        if orig_company is not None:
            os.environ["tc_company"] = orig_company
        else:
            os.environ.pop("tc_company", None)


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


def test_init_config_already_exists(tmp_path):
    """Test initializing config when it already exists."""
    config_path = tmp_path / "config.toml"

    # Create initial config
    ConfigManager.init_config(config_path)

    # Modify config
    config = ConfigManager.load(config_path)
    config.ui.theme = "light"
    ConfigManager.save(config, config_path)

    # Initialize again (should not overwrite)
    ConfigManager.init_config(config_path)

    # Verify it wasn't overwritten
    loaded_config = ConfigManager.load(config_path)
    assert loaded_config.ui.theme == "light"


def test_get_config_path():
    """Test getting default config path."""
    path = ConfigManager.get_config_path()
    assert isinstance(path, Path)
    assert path.name == "config.toml"


def test_config_to_dict():
    """Test converting config to dictionary."""
    config = AppConfig()
    config.api.access_id = "test_id"

    config_dict = config.to_dict()

    assert isinstance(config_dict, dict)
    assert "api" in config_dict
    assert config_dict["api"]["access_id"] == "test_id"


def test_config_from_dict():
    """Test creating config from dictionary."""
    data = {
        "api": {
            "access_id": "test_id",
            "secret_key": "test_secret",
            "instance": "testcompany"
        },
        "ui": {
            "theme": "light"
        }
    }

    config = AppConfig.from_dict(data)

    assert config.api.access_id == "test_id"
    assert config.api.secret_key == "test_secret"
    assert config.api.instance == "testcompany"
    assert config.ui.theme == "light"


def test_partial_config_from_dict():
    """Test creating config from partial dictionary."""
    data = {
        "api": {
            "access_id": "test_id"
        }
    }

    config = AppConfig.from_dict(data)

    # Should have the provided value
    assert config.api.access_id == "test_id"
    # Should have defaults for missing values
    assert config.api.api_version == "v3"
    assert config.ui.theme == "dark"
