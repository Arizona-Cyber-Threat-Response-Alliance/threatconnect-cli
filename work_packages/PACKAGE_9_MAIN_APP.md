# Work Package 9: Main Application

**Module**: `tc_tui/app.py` and `tc_tui/__main__.py`
**Priority**: High (Application Entry Point)
**Estimated Time**: 4-5 hours
**Dependencies**: Package 3 (Configuration), Package 5 (Search Engine), Package 6 (State), Package 8 (Screens)
**Can Start**: After Package 8 complete
**Assignable To**: Any agent with Python/Textual experience

## Objective

Create the main application entry point that initializes the TUI, loads configuration, sets up the API client and search engine, manages the application lifecycle, and provides CLI argument parsing. This is the final integration package that brings all components together.

## Deliverables

### Files to Create/Update

```
tc_tui/
├── app.py               # Main Textual application class
├── __main__.py          # Entry point for python -m tc_tui
└── cli.py               # CLI argument parsing
```

### 1. `tc_tui/app.py`

```python
"""Main ThreatConnect CLI TUI application."""

import sys
import logging
from typing import Optional

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.driver import Driver

from tc_tui.config import ConfigManager, AppConfig
from tc_tui.api import ThreatConnectClient
from tc_tui.search import SearchEngine
from tc_tui.state import AppState
from tc_tui.screens import MainScreen, HelpScreen


logger = logging.getLogger(__name__)


class ThreatConnectApp(App):
    """ThreatConnect CLI TUI Application.

    Main application class that manages the TUI, coordinates between
    all components, and handles application lifecycle.
    """

    TITLE = "ThreatConnect CLI"
    CSS_PATH = "app.css"  # Optional custom CSS file

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit", show=False),
    ]

    def __init__(
        self,
        config: AppConfig,
        driver_class: Optional[type[Driver]] = None,
        **kwargs
    ):
        """Initialize application.

        Args:
            config: Application configuration
            driver_class: Optional Textual driver class
            **kwargs: Additional arguments for App
        """
        super().__init__(driver_class=driver_class, **kwargs)

        self.config = config

        # Initialize components
        self.app_state = AppState()
        self.client: Optional[ThreatConnectClient] = None
        self.search_engine: Optional[SearchEngine] = None

    def on_mount(self) -> None:
        """Handle application mount."""
        try:
            # Initialize API client
            self.client = ThreatConnectClient(
                access_id=self.config.api.access_id,
                secret_key=self.config.api.secret_key,
                instance=self.config.api.instance,
                verify_ssl=self.config.api.verify_ssl
            )

            # Initialize search engine
            self.search_engine = SearchEngine(self.client)

            # Push main screen
            self.push_screen(
                MainScreen(
                    app_state=self.app_state,
                    search_engine=self.search_engine,
                    instance_name=self.config.api.instance
                )
            )

            logger.info("Application started successfully")

        except Exception as e:
            logger.error(f"Failed to initialize application: {e}")
            self.exit(message=f"Initialization error: {e}", return_code=1)

    def action_quit(self) -> None:
        """Quit the application."""
        logger.info("Application shutting down")
        self.exit()


def run_app(config: Optional[AppConfig] = None) -> int:
    """Run the ThreatConnect TUI application.

    Args:
        config: Optional application configuration. If None, loads from default location.

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    # Load configuration if not provided
    if config is None:
        try:
            config_manager = ConfigManager()
            config = config_manager.load_config()
        except Exception as e:
            print(f"Error loading configuration: {e}", file=sys.stderr)
            print("\nPlease run 'tc-tui config init' to set up your configuration.", file=sys.stderr)
            return 1

    # Validate required configuration
    if not config.api.access_id or not config.api.secret_key:
        print("Error: API credentials not configured", file=sys.stderr)
        print("\nPlease set TC_ACCESS_ID and TC_SECRET_KEY environment variables,", file=sys.stderr)
        print("or run 'tc-tui config init' to configure.", file=sys.stderr)
        return 1

    if not config.api.instance:
        print("Error: ThreatConnect instance not configured", file=sys.stderr)
        print("\nPlease set TC_INSTANCE environment variable,", file=sys.stderr)
        print("or run 'tc-tui config init' to configure.", file=sys.stderr)
        return 1

    # Set up logging
    logging.basicConfig(
        level=logging.DEBUG if config.app.debug else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        filename=config.app.log_file if config.app.log_file else None
    )

    try:
        # Create and run the app
        app = ThreatConnectApp(config=config)
        app.run()
        return 0

    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        return 0

    except Exception as e:
        logger.exception("Unexpected error in application")
        print(f"\nError: {e}", file=sys.stderr)
        return 1
```

### 2. `tc_tui/cli.py`

```python
"""Command-line interface for ThreatConnect TUI."""

import argparse
import sys
from pathlib import Path

from tc_tui.config import ConfigManager
from tc_tui.app import run_app
from tc_tui import __version__


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser.

    Returns:
        Configured argument parser
    """
    parser = argparse.ArgumentParser(
        prog="tc-tui",
        description="ThreatConnect CLI - Terminal User Interface",
        epilog="For more information, visit: https://github.com/your-org/threatconnect-cli"
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )

    parser.add_argument(
        "--config",
        type=Path,
        help="Path to configuration file"
    )

    parser.add_argument(
        "--instance",
        type=str,
        help="ThreatConnect instance name (overrides config)"
    )

    parser.add_argument(
        "--access-id",
        type=str,
        help="API Access ID (overrides config)"
    )

    parser.add_argument(
        "--secret-key",
        type=str,
        help="API Secret Key (overrides config)"
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Config command
    config_parser = subparsers.add_parser(
        "config",
        help="Manage configuration"
    )
    config_parser.add_argument(
        "config_action",
        choices=["init", "show", "edit"],
        help="Configuration action"
    )

    return parser


def handle_config_command(action: str) -> int:
    """Handle config subcommand.

    Args:
        action: Config action (init, show, edit)

    Returns:
        Exit code
    """
    config_manager = ConfigManager()

    if action == "init":
        try:
            # Interactive configuration setup
            print("ThreatConnect CLI Configuration Setup")
            print("=" * 40)

            instance = input("ThreatConnect Instance Name: ").strip()
            access_id = input("API Access ID: ").strip()
            secret_key = input("API Secret Key: ").strip()

            # Verify SSL (optional)
            verify_ssl_input = input("Verify SSL certificates? [Y/n]: ").strip().lower()
            verify_ssl = verify_ssl_input != 'n'

            # Create config
            from tc_tui.config import AppConfig, APIConfig
            config = AppConfig(
                api=APIConfig(
                    instance=instance,
                    access_id=access_id,
                    secret_key=secret_key,
                    verify_ssl=verify_ssl
                )
            )

            # Save config
            config_manager.save_config(config)
            print(f"\n✓ Configuration saved to {config_manager.config_path}")
            return 0

        except Exception as e:
            print(f"Error: Failed to initialize configuration: {e}", file=sys.stderr)
            return 1

    elif action == "show":
        try:
            config = config_manager.load_config()
            print("\nCurrent Configuration:")
            print("=" * 40)
            print(f"Instance: {config.api.instance}")
            print(f"Access ID: {config.api.access_id}")
            print(f"Secret Key: {'*' * 10}")
            print(f"Verify SSL: {config.api.verify_ssl}")
            print(f"Results per page: {config.ui.results_per_page}")
            print(f"Theme: {config.ui.theme}")
            return 0

        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

    elif action == "edit":
        try:
            print(f"Configuration file: {config_manager.config_path}")
            print("\nEdit this file manually with your preferred text editor.")
            return 0

        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

    return 1


def main() -> int:
    """Main entry point.

    Returns:
        Exit code
    """
    parser = create_parser()
    args = parser.parse_args()

    # Handle config subcommand
    if args.command == "config":
        return handle_config_command(args.config_action)

    # Load or create configuration
    try:
        config_manager = ConfigManager(config_path=args.config)
        config = config_manager.load_config()

        # Override with CLI arguments if provided
        if args.instance:
            config.api.instance = args.instance
        if args.access_id:
            config.api.access_id = args.access_id
        if args.secret_key:
            config.api.secret_key = args.secret_key
        if args.debug:
            config.app.debug = True

    except Exception as e:
        print(f"Error loading configuration: {e}", file=sys.stderr)
        print("\nRun 'tc-tui config init' to set up configuration.", file=sys.stderr)
        return 1

    # Run the application
    return run_app(config)


if __name__ == "__main__":
    sys.exit(main())
```

### 3. `tc_tui/__main__.py`

```python
"""Entry point for python -m tc_tui."""

from tc_tui.cli import main

if __name__ == "__main__":
    import sys
    sys.exit(main())
```

### 4. `tc_tui/__init__.py`

Update to include version:

```python
"""ThreatConnect CLI TUI package."""

__version__ = "0.1.0"

from .app import ThreatConnectApp, run_app

__all__ = [
    "ThreatConnectApp",
    "run_app",
    "__version__",
]
```

### 5. `tc_tui/app.css` (Optional)

Optional custom CSS for the application:

```css
/* Global styles */
Screen {
    background: $background;
}

/* Make sure all containers fill space properly */
Container {
    width: 100%;
}

/* Header styling */
Header {
    background: $primary;
    color: $text;
}

/* Custom theme colors (can be overridden) */
:root {
    --primary: #0066cc;
    --accent: #00ccff;
    --warning: #ffcc00;
    --error: #ff3333;
    --success: #00cc66;
}
```

## Testing Requirements

### Test File: `tests/test_app.py`

```python
"""Tests for main application."""

import pytest
from unittest.mock import Mock, patch
from textual.pilot import Pilot

from tc_tui.app import ThreatConnectApp, run_app
from tc_tui.config import AppConfig, APIConfig


@pytest.fixture
def mock_config():
    """Create mock configuration."""
    return AppConfig(
        api=APIConfig(
            instance="test-instance",
            access_id="test-access-id",
            secret_key="test-secret-key"
        )
    )


@pytest.mark.asyncio
async def test_app_initialization(mock_config):
    """Test app initializes correctly."""
    app = ThreatConnectApp(config=mock_config)

    assert app.config == mock_config
    assert app.app_state is not None


@pytest.mark.asyncio
async def test_app_mounts_main_screen(mock_config):
    """Test app mounts main screen on startup."""
    app = ThreatConnectApp(config=mock_config)

    async with app.run_test() as pilot:
        await pilot.pause()

        # Verify main screen is present
        assert len(app.screen_stack) > 0


def test_run_app_with_valid_config(mock_config):
    """Test running app with valid configuration."""
    with patch('tc_tui.app.ThreatConnectApp') as mock_app:
        mock_instance = Mock()
        mock_app.return_value = mock_instance

        # This would normally run the app
        # For testing, we just verify it can be called
        # result = run_app(mock_config)


def test_run_app_without_config():
    """Test running app without configuration."""
    with patch('tc_tui.app.ConfigManager') as mock_config_manager:
        # Mock config loading failure
        mock_config_manager.return_value.load_config.side_effect = Exception("Config not found")

        result = run_app()
        assert result == 1  # Should return error code
```

### Test File: `tests/test_cli.py`

```python
"""Tests for CLI interface."""

import pytest
from unittest.mock import Mock, patch
from io import StringIO

from tc_tui.cli import create_parser, handle_config_command, main


def test_create_parser():
    """Test argument parser creation."""
    parser = create_parser()

    assert parser is not None
    assert parser.prog == "tc-tui"


def test_parser_with_instance_arg():
    """Test parser with instance argument."""
    parser = create_parser()
    args = parser.parse_args(["--instance", "test-instance"])

    assert args.instance == "test-instance"


def test_parser_with_config_arg():
    """Test parser with config argument."""
    parser = create_parser()
    args = parser.parse_args(["--config", "/path/to/config.toml"])

    assert str(args.config) == "/path/to/config.toml"


def test_parser_with_debug_flag():
    """Test parser with debug flag."""
    parser = create_parser()
    args = parser.parse_args(["--debug"])

    assert args.debug is True


def test_parser_config_subcommand():
    """Test config subcommand parsing."""
    parser = create_parser()
    args = parser.parse_args(["config", "init"])

    assert args.command == "config"
    assert args.config_action == "init"


@patch('builtins.input')
@patch('tc_tui.cli.ConfigManager')
def test_handle_config_init(mock_config_manager, mock_input):
    """Test config init command."""
    mock_input.side_effect = [
        "test-instance",  # instance
        "test-access-id",  # access_id
        "test-secret-key",  # secret_key
        "y"  # verify_ssl
    ]

    mock_manager = Mock()
    mock_config_manager.return_value = mock_manager
    mock_manager.config_path = "/path/to/config.toml"

    result = handle_config_command("init")

    assert result == 0
    mock_manager.save_config.assert_called_once()


def test_main_without_args():
    """Test main function without arguments."""
    with patch('sys.argv', ['tc-tui']):
        with patch('tc_tui.cli.ConfigManager') as mock_config_manager:
            # Mock config loading failure
            mock_config_manager.return_value.load_config.side_effect = Exception("Config not found")

            result = main()
            assert result == 1
```

## Acceptance Criteria

- [ ] ThreatConnectApp class created in `tc_tui/app.py`
- [ ] CLI argument parsing in `tc_tui/cli.py`
- [ ] Entry point in `tc_tui/__main__.py`
- [ ] Configuration initialization (config init)
- [ ] Configuration display (config show)
- [ ] CLI arguments override config values
- [ ] API client initialized with config
- [ ] Search engine initialized
- [ ] Main screen pushed on startup
- [ ] Error handling for missing/invalid config
- [ ] Logging set up based on config
- [ ] Version command (--version)
- [ ] Debug flag (--debug)
- [ ] All tests passing with >80% coverage
- [ ] Type hints on all public methods
- [ ] Docstrings complete

## Integration Notes

### Dependencies
- **Package 3 (Configuration)**: Uses ConfigManager, AppConfig
- **Package 5 (Search Engine)**: Initializes SearchEngine
- **Package 6 (State)**: Initializes AppState
- **Package 8 (Screens)**: Pushes MainScreen

### Installation

After this package is complete, the application can be installed with:

```bash
pip install -e .
```

And run with:

```bash
tc-tui
# or
python -m tc_tui
```

### Usage Examples

```bash
# Run with default configuration
tc-tui

# Initialize configuration
tc-tui config init

# Show current configuration
tc-tui config show

# Run with specific instance (override config)
tc-tui --instance my-instance

# Run with debug logging
tc-tui --debug

# Use custom config file
tc-tui --config /path/to/config.toml
```

## Notes

- Entry point can be installed as console script in setup.py
- Configuration loaded from ~/.config/threatconnect-cli/config.toml by default
- Environment variables take precedence over config file
- CLI arguments take precedence over environment variables
- Logging configured based on config.app.debug setting
- Graceful error handling for missing configuration
- Interactive config init for first-time setup
- Custom CSS file optional (falls back to Textual defaults)
- Ctrl+C handled gracefully for clean shutdown
- Exit codes: 0 = success, 1 = error

## Setup.py Integration

Add to `setup.py` or `pyproject.toml`:

```python
# setup.py
entry_points={
    'console_scripts': [
        'tc-tui=tc_tui.cli:main',
    ],
}

# pyproject.toml
[project.scripts]
tc-tui = "tc_tui.cli:main"
```

## Time Estimate

- Application class: 1.5 hours
- CLI argument parsing: 1 hour
- Config subcommands: 1 hour
- Entry points and packaging: 0.5 hours
- Error handling and validation: 0.5 hours
- Tests: 1.5 hours
- Documentation: 0.5 hours

**Total: 4-5 hours**
