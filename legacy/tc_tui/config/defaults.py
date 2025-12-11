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
