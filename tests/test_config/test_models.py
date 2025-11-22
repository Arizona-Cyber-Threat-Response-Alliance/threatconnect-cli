"""Tests for configuration models."""

from tc_tui.config import (
    APIConfig,
    UIConfig,
    KeyBindings,
    CacheConfig,
    DefaultsConfig,
    AppConfig
)


def test_api_config_defaults():
    """Test APIConfig default values."""
    config = APIConfig()

    assert config.access_id == ""
    assert config.secret_key == ""
    assert config.instance == ""
    assert config.api_version == "v3"
    assert config.timeout == 30


def test_ui_config_defaults():
    """Test UIConfig default values."""
    config = UIConfig()

    assert config.theme == "dark"
    assert config.results_per_page == 100
    assert config.show_confidence is True
    assert config.show_rating is True
    assert config.show_icons is True
    assert config.color_by_rating is True
    assert config.date_format == "%B %d, %Y %H:%M:%S"


def test_keybindings_defaults():
    """Test KeyBindings default values."""
    config = KeyBindings()

    assert config.quit == "q"
    assert config.search == "/"
    assert config.help == "?"
    assert config.navigate_up == "k,up"
    assert config.navigate_down == "j,down"
    assert config.select == "enter"
    assert config.back == "escape"


def test_cache_config_defaults():
    """Test CacheConfig default values."""
    config = CacheConfig()

    assert config.enabled is True
    assert config.ttl_seconds == 300
    assert config.max_size_mb == 100


def test_defaults_config_defaults():
    """Test DefaultsConfig default values."""
    config = DefaultsConfig()

    assert config.owner == ""
    assert config.search_type == "indicators"
    assert config.include_tags is True
    assert config.include_attributes is True
    assert config.result_limit == 100


def test_app_config_composition():
    """Test AppConfig composition of all configs."""
    config = AppConfig()

    assert isinstance(config.api, APIConfig)
    assert isinstance(config.ui, UIConfig)
    assert isinstance(config.keybindings, KeyBindings)
    assert isinstance(config.cache, CacheConfig)
    assert isinstance(config.defaults, DefaultsConfig)


def test_app_config_custom_values():
    """Test AppConfig with custom values."""
    api_config = APIConfig(
        access_id="test_id",
        secret_key="test_secret",
        instance="testcompany"
    )
    ui_config = UIConfig(theme="light", results_per_page=50)

    config = AppConfig(api=api_config, ui=ui_config)

    assert config.api.access_id == "test_id"
    assert config.ui.theme == "light"
    assert config.ui.results_per_page == 50


def test_app_config_to_dict():
    """Test converting AppConfig to dictionary."""
    config = AppConfig()
    config.api.access_id = "test_id"
    config.ui.theme = "light"

    result = config.to_dict()

    assert isinstance(result, dict)
    assert "api" in result
    assert "ui" in result
    assert result["api"]["access_id"] == "test_id"
    assert result["ui"]["theme"] == "light"


def test_app_config_from_dict():
    """Test creating AppConfig from dictionary."""
    data = {
        "api": {
            "access_id": "test_id",
            "secret_key": "test_secret"
        },
        "ui": {
            "theme": "monokai"
        },
        "cache": {
            "enabled": False
        }
    }

    config = AppConfig.from_dict(data)

    assert config.api.access_id == "test_id"
    assert config.api.secret_key == "test_secret"
    assert config.ui.theme == "monokai"
    assert config.cache.enabled is False


def test_app_config_from_empty_dict():
    """Test creating AppConfig from empty dictionary."""
    config = AppConfig.from_dict({})

    # Should have all default values
    assert config.api.api_version == "v3"
    assert config.ui.theme == "dark"
    assert config.cache.enabled is True


def test_app_config_roundtrip():
    """Test roundtrip conversion to/from dict."""
    original = AppConfig()
    original.api.access_id = "test_id"
    original.ui.theme = "light"
    original.cache.ttl_seconds = 600

    # Convert to dict and back
    data = original.to_dict()
    restored = AppConfig.from_dict(data)

    assert restored.api.access_id == original.api.access_id
    assert restored.ui.theme == original.ui.theme
    assert restored.cache.ttl_seconds == original.cache.ttl_seconds
