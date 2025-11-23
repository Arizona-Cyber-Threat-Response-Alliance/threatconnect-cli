"""Status bar widget for displaying application status and hints."""

from typing import Optional
from textual.app import ComposeResult
from textual.widgets import Static
from textual.containers import Horizontal
from textual.reactive import Reactive

from tc_tui.state import ViewMode


class StatusBar(Horizontal):
    """Status bar widget displaying pagination, hints, and status.

    Shows:
    - Left: Pagination info (Page X/Y | Results: N)
    - Center: Status/error messages
    - Right: Keyboard hints based on current view
    """

    DEFAULT_CSS = """
    StatusBar {
        height: 1;
        background: $surface;
        color: $text;
        dock: bottom;
    }

    StatusBar > .status-left {
        width: 30;
        padding: 0 2;
        color: $text;
    }

    StatusBar > .status-center {
        width: 1fr;
        text-align: center;
        padding: 0 2;
    }

    StatusBar > .status-center.loading {
        color: $warning;
        text-style: bold;
    }

    StatusBar > .status-center.error {
        color: $error;
        text-style: bold;
    }

    StatusBar > .status-center.success {
        color: $success;
    }

    StatusBar > .status-right {
        width: 60;
        text-align: right;
        padding: 0 2;
        color: $text-muted;
    }

    StatusBar > .keybinding-hint {
        color: $accent;
        text-style: bold;
    }
    """

    # Reactive properties
    current_page: Reactive[int] = Reactive(0)
    total_pages: Reactive[int] = Reactive(0)
    total_results: Reactive[int] = Reactive(0)
    view_mode: Reactive[ViewMode] = Reactive(ViewMode.SEARCH)
    is_loading: Reactive[bool] = Reactive(False)
    status_message: Reactive[Optional[str]] = Reactive(None)
    error_message: Reactive[Optional[str]] = Reactive(None)

    def __init__(self, id: str = "status-bar") -> None:
        """Initialize status bar widget.

        Args:
            id: Widget ID
        """
        super().__init__(id=id)

    def compose(self) -> ComposeResult:
        """Compose the status bar widget."""
        yield Static("", classes="status-left", id="status-left")
        yield Static("", classes="status-center", id="status-center")
        yield Static("", classes="status-right", id="status-right")

    def on_mount(self) -> None:
        """Handle widget mount."""
        self._update_display()

    def watch_current_page(self, value: int) -> None:
        """Watch current_page changes.

        Args:
            value: New current page value
        """
        self._update_left()

    def watch_total_pages(self, value: int) -> None:
        """Watch total_pages changes.

        Args:
            value: New total pages value
        """
        self._update_left()

    def watch_total_results(self, value: int) -> None:
        """Watch total_results changes.

        Args:
            value: New total results value
        """
        self._update_left()

    def watch_view_mode(self, value: ViewMode) -> None:
        """Watch view_mode changes.

        Args:
            value: New view mode
        """
        self._update_right()

    def watch_is_loading(self, value: bool) -> None:
        """Watch is_loading changes.

        Args:
            value: New loading state
        """
        self._update_center()

    def watch_status_message(self, value: Optional[str]) -> None:
        """Watch status_message changes.

        Args:
            value: New status message
        """
        self._update_center()

    def watch_error_message(self, value: Optional[str]) -> None:
        """Watch error_message changes.

        Args:
            value: New error message
        """
        self._update_center()

    def _update_display(self) -> None:
        """Update all sections of the status bar."""
        self._update_left()
        self._update_center()
        self._update_right()

    def _update_left(self) -> None:
        """Update left section with pagination info."""
        left = self.query_one("#status-left", Static)

        if self.total_results > 0:
            page_info = f"Page {self.current_page + 1}/{self.total_pages}"
            results_info = f"Results: {self.total_results}"
            left.update(f"{page_info} | {results_info}")
        else:
            left.update("")

    def _update_center(self) -> None:
        """Update center section with status/error messages."""
        center = self.query_one("#status-center", Static)

        # Priority: error > loading > status > empty
        if self.error_message:
            center.update(f"❌ {self.error_message}")
            center.remove_class("loading", "success")
            center.add_class("error")

        elif self.is_loading:
            loading_msg = self.status_message or "Loading..."
            center.update(f"⏳ {loading_msg}")
            center.remove_class("error", "success")
            center.add_class("loading")

        elif self.status_message:
            center.update(f"✓ {self.status_message}")
            center.remove_class("error", "loading")
            center.add_class("success")

        else:
            center.update("")
            center.remove_class("error", "loading", "success")

    def _update_right(self) -> None:
        """Update right section with keyboard hints based on view mode."""
        right = self.query_one("#status-right", Static)

        hints = self._get_keyboard_hints()
        right.update(hints)

    def _get_keyboard_hints(self) -> str:
        """Get keyboard hints for current view mode.

        Returns:
            Formatted keyboard hints string
        """
        if self.view_mode == ViewMode.SEARCH:
            return "Enter: Search | ?: Help | q: Quit"

        elif self.view_mode == ViewMode.RESULTS:
            return "↑/↓: Navigate | Enter: Details | /: Search | ?: Help"

        elif self.view_mode == ViewMode.DETAIL:
            return "Esc: Back | ?: Help | q: Quit"

        elif self.view_mode == ViewMode.HELP:
            return "Esc: Close | q: Quit"

        elif self.view_mode == ViewMode.SETTINGS:
            return "Esc: Cancel | Enter: Save | q: Quit"

        else:
            return "?: Help | q: Quit"

    def set_pagination(
        self,
        current_page: int,
        total_pages: int,
        total_results: int
    ) -> None:
        """Set pagination information.

        Args:
            current_page: Current page number (0-indexed)
            total_pages: Total number of pages
            total_results: Total number of results
        """
        self.current_page = current_page
        self.total_pages = total_pages
        self.total_results = total_results

    def set_view_mode(self, mode: ViewMode) -> None:
        """Set current view mode.

        Args:
            mode: New view mode
        """
        self.view_mode = mode

    def set_loading(self, loading: bool, message: Optional[str] = None) -> None:
        """Set loading state.

        Args:
            loading: Whether app is loading
            message: Optional loading message
        """
        self.is_loading = loading
        if message:
            self.status_message = message
        elif not loading:
            self.status_message = None

    def set_error(self, error: Optional[str]) -> None:
        """Set error message.

        Args:
            error: Error message or None to clear
        """
        self.error_message = error

    def set_status(self, message: Optional[str]) -> None:
        """Set status message.

        Args:
            message: Status message or None to clear
        """
        self.status_message = message

    def clear_messages(self) -> None:
        """Clear all status and error messages."""
        self.status_message = None
        self.error_message = None
        self.is_loading = False

    def show_connection_status(self, connected: bool, instance: str = "") -> None:
        """Show connection status message.

        Args:
            connected: Whether connected to API
            instance: Instance name if connected
        """
        if connected:
            msg = f"Connected to {instance}" if instance else "Connected"
            self.set_status(msg)
        else:
            self.set_error("Not connected")
