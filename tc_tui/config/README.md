# Configuration Module

This module handles configuration management for the ThreatConnect CLI application.

## Features

- Load/save configuration from TOML files
- Environment variable override support
- Platform-appropriate config directory using `platformdirs`
- Support for both new (`TC_*`) and legacy (`tc_*`) environment variables
- Type-safe configuration with dataclasses

## Usage

### Loading Configuration

```python
from tc_tui.config import ConfigManager

# Load from default location
config = ConfigManager.load()

# Load from custom path
from pathlib import Path
config = ConfigManager.load(Path("/custom/path/config.toml"))
```

### Saving Configuration

```python
from tc_tui.config import ConfigManager, AppConfig

config = AppConfig()
config.api.access_id = "your_access_id"
config.ui.theme = "light"

ConfigManager.save(config)
```

### Getting API Credentials

```python
from tc_tui.config import ConfigManager

try:
    access_id, secret_key, instance = ConfigManager.get_api_credentials()
except ValueError as e:
    print(f"Missing credentials: {e}")
```

### Initializing Config File

```python
from tc_tui.config import ConfigManager

# Create default config file if it doesn't exist
config_path = ConfigManager.init_config()
print(f"Config created at: {config_path}")
```

## Configuration Structure

The configuration is organized into five main sections:

- **api**: API credentials and settings
- **ui**: UI preferences and display options
- **keybindings**: Keyboard shortcut mappings
- **cache**: Caching configuration
- **defaults**: Default search and filter settings

See `models.py` for the complete structure.

## Environment Variables

The following environment variables are supported:

- `TC_ACCESS_ID` or `tc_accessid`: ThreatConnect Access ID
- `TC_SECRET_KEY` or `tc_secretkey`: ThreatConnect Secret Key
- `TC_INSTANCE` or `tc_company`: ThreatConnect Instance

Environment variables take precedence over config file values.

## Config File Location

The default config file location is platform-specific:

- **Linux**: `~/.config/threatconnect-cli/config.toml`
- **macOS**: `~/Library/Application Support/tc/threatconnect-cli/config.toml`
- **Windows**: `%LOCALAPPDATA%\tc\threatconnect-cli\config.toml`

## Testing

Run tests with:

```bash
pytest tests/test_config/ -v --cov=tc_tui/config
```

Current test coverage: 95%
