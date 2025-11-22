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
