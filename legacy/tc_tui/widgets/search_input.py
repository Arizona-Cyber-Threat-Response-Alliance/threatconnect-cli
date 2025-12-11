"""Search input widget for ThreatConnect CLI."""

from textual.app import ComposeResult
from textual.containers import Horizontal, Container
from textual.widgets import Input, Select, Static
from textual.message import Message
from textual.reactive import Reactive

from tc_tui.state import SearchType
from tc_tui.utils import Validators


class SearchInput(Container):
    """Search input widget with type selector and text input.

    Emits SearchSubmitted message when search is submitted.
    Supports search history navigation with Up/Down arrows.
    """

    DEFAULT_CSS = """
    SearchInput {
        height: 3;
        border: solid $primary;
        padding: 0 1;
    }

    SearchInput > Horizontal {
        height: 1;
        align: left middle;
    }

    SearchInput Select {
        width: 15;
        margin-right: 1;
    }

    SearchInput Input {
        width: 1fr;
    }

    SearchInput .search-hint {
        color: $text-muted;
        margin-left: 1;
    }
    """

    # Reactive properties
    search_type: Reactive[SearchType] = Reactive(SearchType.INDICATORS)
    current_value: Reactive[str] = Reactive("")

    class SearchSubmitted(Message):
        """Message emitted when search is submitted."""

        def __init__(self, query: str, search_type: SearchType) -> None:
            """Initialize message.

            Args:
                query: The search query
                search_type: Type of search (indicators, groups, both)
            """
            super().__init__()
            self.query = query
            self.search_type = search_type

    class SearchTypeChanged(Message):
        """Message emitted when search type changes."""

        def __init__(self, search_type: SearchType) -> None:
            """Initialize message.

            Args:
                search_type: New search type
            """
            super().__init__()
            self.search_type = search_type

    def __init__(self, id: str = "search-input") -> None:
        """Initialize search input widget.

        Args:
            id: Widget ID
        """
        super().__init__(id=id)
        self._history: list[str] = []
        self._history_index: int = -1

    def compose(self) -> ComposeResult:
        """Compose the search input widget."""
        # Type selector dropdown
        type_select = Select(
            [
                ("Indicators", SearchType.INDICATORS.value),
                ("Groups", SearchType.GROUPS.value),
                ("Both", SearchType.BOTH.value),
            ],
            value=SearchType.INDICATORS.value,
            id="search-type-select",
        )

        # Search input field
        search_input = Input(
            placeholder="Enter indicator, group name, or TQL query...",
            id="search-input-field",
        )

        with Horizontal():
            yield type_select
            yield search_input
            yield Static("Press / to focus, Enter to search", classes="search-hint")

    def on_mount(self) -> None:
        """Handle widget mount."""
        # Focus the input field
        self.query_one("#search-input-field", Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission.

        Args:
            event: Input submitted event
        """
        if event.input.id == "search-input-field":
            query = event.value.strip()
            if query:
                self._add_to_history(query)
                self.post_message(self.SearchSubmitted(query, self.search_type))

    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle search type selection change.

        Args:
            event: Select changed event
        """
        if event.select.id == "search-type-select":
            self.search_type = SearchType(event.value)
            self.post_message(self.SearchTypeChanged(self.search_type))

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle input value change.

        Args:
            event: Input changed event
        """
        if event.input.id == "search-input-field":
            self.current_value = event.value

    async def on_key(self, event) -> None:
        """Handle key events for history navigation.

        Args:
            event: Key event
        """
        input_field = self.query_one("#search-input-field", Input)

        # Only handle if input is focused
        if not input_field.has_focus:
            return

        # History navigation with Up/Down arrows
        if event.key == "up":
            self._navigate_history_up()
            event.prevent_default()
        elif event.key == "down":
            self._navigate_history_down()
            event.prevent_default()

    def _add_to_history(self, query: str) -> None:
        """Add query to history.

        Args:
            query: Query to add
        """
        # Don't add duplicates consecutively
        if self._history and self._history[-1] == query:
            return

        self._history.append(query)
        self._history_index = len(self._history)

        # Limit history size
        if len(self._history) > 50:
            self._history.pop(0)
            self._history_index -= 1

    def _navigate_history_up(self) -> None:
        """Navigate to previous search in history."""
        if not self._history or self._history_index <= 0:
            return

        self._history_index -= 1
        self._set_input_value(self._history[self._history_index])

    def _navigate_history_down(self) -> None:
        """Navigate to next search in history."""
        if not self._history:
            return

        if self._history_index >= len(self._history) - 1:
            # At the end, clear input
            self._history_index = len(self._history)
            self._set_input_value("")
        else:
            self._history_index += 1
            self._set_input_value(self._history[self._history_index])

    def _set_input_value(self, value: str) -> None:
        """Set input field value.

        Args:
            value: Value to set
        """
        input_field = self.query_one("#search-input-field", Input)
        input_field.value = value
        # Move cursor to end
        input_field.cursor_position = len(value)

    def set_value(self, value: str) -> None:
        """Set the search input value programmatically.

        Args:
            value: Value to set
        """
        self._set_input_value(value)

    def clear(self) -> None:
        """Clear the search input."""
        self._set_input_value("")

    def get_value(self) -> str:
        """Get current input value.

        Returns:
            Current input value
        """
        input_field = self.query_one("#search-input-field", Input)
        return input_field.value

    def set_search_type(self, search_type: SearchType) -> None:
        """Set the search type.

        Args:
            search_type: Search type to set
        """
        select = self.query_one("#search-type-select", Select)
        select.value = search_type.value
        self.search_type = search_type

    def get_search_type(self) -> SearchType:
        """Get current search type.

        Returns:
            Current search type
        """
        return self.search_type

    def focus_input(self) -> None:
        """Focus the search input field."""
        input_field = self.query_one("#search-input-field", Input)
        input_field.focus()

    def detect_query_type(self, query: str) -> str | None:
        """Detect indicator type from query.

        Args:
            query: Query string

        Returns:
            Detected indicator type or None
        """
        if self.search_type == SearchType.INDICATORS:
            return Validators.detect_indicator_type(query)
        return None

    def is_tql_query(self, query: str) -> bool:
        """Check if query looks like TQL.

        Args:
            query: Query string

        Returns:
            True if query appears to be TQL
        """
        return Validators.is_tql_query(query)
