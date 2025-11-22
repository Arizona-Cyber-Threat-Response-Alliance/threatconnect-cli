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
