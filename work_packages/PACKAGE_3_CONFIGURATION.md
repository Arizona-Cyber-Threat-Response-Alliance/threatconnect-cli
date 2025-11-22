# Work Package 3: Configuration Management

**Module**: `tc_tui/config/`
**Priority**: High (Foundation)
**Estimated Time**: 3-4 hours
**Dependencies**: None
**Can Start**: Immediately
**Assignable To**: Any agent with Python/config file experience

## Objective

Create configuration management system that handles loading/saving settings from TOML files, environment variables, and provides sensible defaults.

## Deliverables

### Files to Create

```
tc_tui/config/
├── __init__.py          # Public exports
├── manager.py           # Config loading/saving
├── models.py            # Config data classes
└── defaults.py          # Default values
```

### 1. `tc_tui/config/models.py`

Define configuration data structures:

```python
"""Configuration data models."""

from dataclasses import dataclass, field, asdict
from typing import Dict, Optional


@dataclass
class APIConfig:
    """API configuration."""

    access_id: str = ""
    secret_key: str = ""
    instance: str = ""
    api_version: str = "v3"
    timeout: int = 30


@dataclass
class UIConfig:
    """UI configuration."""

    theme: str = "dark"  # dark, light, monokai
    results_per_page: int = 100
    show_confidence: bool = True
    show_rating: bool = True
    show_icons: bool = True
    color_by_rating: bool = True
    date_format: str = "%B %d, %Y %H:%M:%S"


@dataclass
class KeyBindings:
    """Keyboard shortcuts configuration."""

    quit: str = "q"
    search: str = "/"
    help: str = "?"
    navigate_up: str = "k,up"
    navigate_down: str = "j,down"
    navigate_left: str = "h,left"
    navigate_right: str = "l,right"
    page_up: str = "ctrl+u"
    page_down: str = "ctrl+d"
    jump_to_top: str = "g"
    jump_to_bottom: str = "G"
    select: str = "enter"
    back: str = "escape"
    tab: str = "tab"


@dataclass
class CacheConfig:
    """Cache configuration."""

    enabled: bool = True
    ttl_seconds: int = 300  # 5 minutes
    max_size_mb: int = 100


@dataclass
class DefaultsConfig:
    """Default search/filter settings."""

    owner: str = ""
    search_type: str = "indicators"  # indicators, groups, both
    include_tags: bool = True
    include_attributes: bool = True
    result_limit: int = 100


@dataclass
class AppConfig:
    """Complete application configuration."""

    api: APIConfig = field(default_factory=APIConfig)
    ui: UIConfig = field(default_factory=UIConfig)
    keybindings: KeyBindings = field(default_factory=KeyBindings)
    cache: CacheConfig = field(default_factory=CacheConfig)
    defaults: DefaultsConfig = field(default_factory=DefaultsConfig)

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "api": asdict(self.api),
            "ui": asdict(self.ui),
            "keybindings": asdict(self.keybindings),
            "cache": asdict(self.cache),
            "defaults": asdict(self.defaults)
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "AppConfig":
        """Create from dictionary."""
        return cls(
            api=APIConfig(**data.get("api", {})),
            ui=UIConfig(**data.get("ui", {})),
            keybindings=KeyBindings(**data.get("keybindings", {})),
            cache=CacheConfig(**data.get("cache", {})),
            defaults=DefaultsConfig(**data.get("defaults", {}))
        )
```

### 2. `tc_tui/config/defaults.py`

Define default configuration:

```python
"""Default configuration values."""

import tomli_w
from pathlib import Path
from .models import AppConfig


DEFAULT_CONFIG = AppConfig()


DEFAULT_CONFIG_TOML = """# ThreatConnect CLI Configuration

[api]
# API credentials (can also be set via environment variables)
access_id = ""
secret_key = ""
instance = ""
api_version = "v3"
timeout = 30

[ui]
# UI preferences
theme = "dark"
results_per_page = 100
show_confidence = true
show_rating = true
show_icons = true
color_by_rating = true
date_format = "%B %d, %Y %H:%M:%S"

[keybindings]
# Keyboard shortcuts (comma-separated for multiple bindings)
quit = "q"
search = "/"
help = "?"
navigate_up = "k,up"
navigate_down = "j,down"
navigate_left = "h,left"
navigate_right = "l,right"
page_up = "ctrl+u"
page_down = "ctrl+d"
jump_to_top = "g"
jump_to_bottom = "G"
select = "enter"
back = "escape"
tab = "tab"

[cache]
# Caching settings
enabled = true
ttl_seconds = 300
max_size_mb = 100

[defaults]
# Default search settings
owner = ""
search_type = "indicators"
include_tags = true
include_attributes = true
result_limit = 100
"""


def create_default_config_file(config_path: Path) -> None:
    """
    Create default config file.

    Args:
        config_path: Path to create config file
    """
    config_path.parent.mkdir(parents=True, exist_ok=True)

    with open(config_path, 'w') as f:
        f.write(DEFAULT_CONFIG_TOML)
```

### 3. `tc_tui/config/manager.py`

Configuration manager:

```python
"""Configuration management."""

import os
import tomli
import tomli_w
from pathlib import Path
from platformdirs import user_config_dir
from typing import Optional, Tuple
import logging

from .models import AppConfig, APIConfig
from .defaults import DEFAULT_CONFIG, create_default_config_file

logger = logging.getLogger(__name__)


class ConfigManager:
    """Manage application configuration."""

    CONFIG_DIR = Path(user_config_dir("threatconnect-cli", "tc"))
    CONFIG_FILE = CONFIG_DIR / "config.toml"

    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> AppConfig:
        """
        Load configuration from file and environment variables.

        Priority (highest to lowest):
        1. Environment variables
        2. Config file
        3. Defaults

        Args:
            config_path: Optional custom config file path

        Returns:
            AppConfig object
        """
        # Use default path if not specified
        if config_path is None:
            config_path = cls.CONFIG_FILE

        # Load from file if exists, otherwise use defaults
        if config_path.exists():
            logger.info(f"Loading config from {config_path}")
            config = cls._load_from_file(config_path)
        else:
            logger.info(f"Config file not found at {config_path}, using defaults")
            config = AppConfig()

        # Override with environment variables
        config = cls._override_with_env(config)

        return config

    @classmethod
    def save(cls, config: AppConfig, config_path: Optional[Path] = None) -> None:
        """
        Save configuration to file.

        Args:
            config: AppConfig to save
            config_path: Optional custom config file path
        """
        if config_path is None:
            config_path = cls.CONFIG_FILE

        # Create directory if needed
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Write to file
        logger.info(f"Saving config to {config_path}")
        with open(config_path, 'wb') as f:
            tomli_w.dump(config.to_dict(), f)

    @classmethod
    def _load_from_file(cls, config_path: Path) -> AppConfig:
        """Load config from TOML file."""
        try:
            with open(config_path, 'rb') as f:
                data = tomli.load(f)
            return AppConfig.from_dict(data)
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            logger.warning("Using default configuration")
            return AppConfig()

    @classmethod
    def _override_with_env(cls, config: AppConfig) -> AppConfig:
        """Override config with environment variables."""
        # API credentials from environment
        if os.getenv("TC_ACCESS_ID") or os.getenv("tc_accessid"):
            config.api.access_id = (
                os.getenv("TC_ACCESS_ID") or
                os.getenv("tc_accessid") or
                config.api.access_id
            )

        if os.getenv("TC_SECRET_KEY") or os.getenv("tc_secretkey"):
            config.api.secret_key = (
                os.getenv("TC_SECRET_KEY") or
                os.getenv("tc_secretkey") or
                config.api.secret_key
            )

        if os.getenv("TC_INSTANCE") or os.getenv("tc_company"):
            config.api.instance = (
                os.getenv("TC_INSTANCE") or
                os.getenv("tc_company") or
                config.api.instance
            )

        return config

    @classmethod
    def get_api_credentials(cls, config: Optional[AppConfig] = None) -> Tuple[str, str, str]:
        """
        Get API credentials from config or environment.

        Args:
            config: Optional AppConfig (loads from file if not provided)

        Returns:
            Tuple of (access_id, secret_key, instance)

        Raises:
            ValueError: If credentials are missing
        """
        if config is None:
            config = cls.load()

        access_id = config.api.access_id
        secret_key = config.api.secret_key
        instance = config.api.instance

        if not access_id or not secret_key or not instance:
            raise ValueError(
                "Missing API credentials. Set them in config file or environment variables:\n"
                "  TC_ACCESS_ID or tc_accessid\n"
                "  TC_SECRET_KEY or tc_secretkey\n"
                "  TC_INSTANCE or tc_company"
            )

        return access_id, secret_key, instance

    @classmethod
    def init_config(cls, config_path: Optional[Path] = None) -> Path:
        """
        Initialize config file with defaults if it doesn't exist.

        Args:
            config_path: Optional custom config file path

        Returns:
            Path to config file
        """
        if config_path is None:
            config_path = cls.CONFIG_FILE

        if not config_path.exists():
            logger.info(f"Creating default config at {config_path}")
            create_default_config_file(config_path)
        else:
            logger.info(f"Config already exists at {config_path}")

        return config_path

    @classmethod
    def get_config_path(cls) -> Path:
        """Get default config file path."""
        return cls.CONFIG_FILE
```

### 4. `tc_tui/config/__init__.py`

Public exports:

```python
"""Configuration management."""

from .manager import ConfigManager
from .models import (
    AppConfig,
    APIConfig,
    UIConfig,
    KeyBindings,
    CacheConfig,
    DefaultsConfig
)
from .defaults import DEFAULT_CONFIG

__all__ = [
    "ConfigManager",
    "AppConfig",
    "APIConfig",
    "UIConfig",
    "KeyBindings",
    "CacheConfig",
    "DefaultsConfig",
    "DEFAULT_CONFIG",
]
```

### 5. Create `.env.example` in project root

```bash
# ThreatConnect API Credentials
TC_ACCESS_ID=your_access_id_here
TC_SECRET_KEY=your_secret_key_here
TC_INSTANCE=yourcompany

# Alternative environment variable names (legacy)
# tc_accessid=your_access_id_here
# tc_secretkey=your_secret_key_here
# tc_company=yourcompany
```

## Testing Requirements

### Test File: `tests/test_config/test_manager.py`

```python
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
    os.environ["TC_ACCESS_ID"] = "env_id"
    os.environ["TC_SECRET_KEY"] = "env_secret"
    os.environ["TC_INSTANCE"] = "envcompany"

    config = ConfigManager.load()

    assert config.api.access_id == "env_id"
    assert config.api.secret_key == "env_secret"
    assert config.api.instance == "envcompany"

    # Cleanup
    del os.environ["TC_ACCESS_ID"]
    del os.environ["TC_SECRET_KEY"]
    del os.environ["TC_INSTANCE"]


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
```

## Acceptance Criteria

- [ ] Config loads from TOML file correctly
- [ ] Config can be saved to TOML file
- [ ] Environment variables override file config
- [ ] Default config is used when no file exists
- [ ] Config validation works (raises errors for invalid values)
- [ ] All tests pass with >90% coverage
- [ ] Config file is created in platform-appropriate directory
- [ ] Proper file permissions (600) on created config files
- [ ] Documentation for all configuration options
- [ ] `.env.example` file created

## Dependencies

```python
# Add to requirements.txt
platformdirs>=4.0.0
tomli>=2.0.0
tomli-w>=1.0.0
```

## Integration Points

- **Used By**: Module 2 (API Client) for credentials
- **Used By**: Module 9 (Main App) for all settings
- **Used By**: Module 7 (Widgets) for UI preferences

## Notes

- Use `platformdirs` for cross-platform config directory
- Support both new (`TC_*`) and legacy (`tc_*`) environment variables
- TOML chosen over YAML for simplicity and Python 3.11+ stdlib support (tomllib)
- Config file should have comments explaining each option
- Sensitive data (API keys) should not be logged
- Consider keyring integration in future for secure credential storage

## References

- [platformdirs Documentation](https://platformdirs.readthedocs.io/)
- [TOML Specification](https://toml.io/)
- [tomli/tomli-w Documentation](https://github.com/hukkin/tomli)

---

**Status**: Ready to Start
**Branch**: `module/3-config`
**Estimated Completion**: 3-4 hours
