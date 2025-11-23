# Work Package 7a: SearchInput Widget

**Module**: `tc_tui/widgets/search_input.py`
**Priority**: Medium (UI Component)
**Estimated Time**: 3-4 hours
**Dependencies**: Package 1 (Data Models), Package 4 (Utilities), Package 6 (State)
**Can Start**: After Packages 1, 4, and 6 complete
**Assignable To**: Any agent with Python/Textual experience

## Objective

Create a search input widget with dropdown selector for search type (Indicators/Groups/Both) and text input for queries. Support both simple indicator searches and TQL queries with search history navigation.

## Deliverables

### Files to Create

```
tc_tui/widgets/
├── __init__.py          # Public exports
└── search_input.py      # Search input widget
```

### 1. `tc_tui/widgets/search_input.py`

```python
"""Search input widget for ThreatConnect CLI."""

from textual.app import ComposeResult
from textual.containers import Horizontal, Container
from textual.widgets import Input, Select, Static
from textual.message import Message
from textual.reactive import Reactive

from tc_tui.state import SearchType
from tc_tui.utils import detect_indicator_type


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
            return detect_indicator_type(query)
        return None

    def is_tql_query(self, query: str) -> bool:
        """Check if query looks like TQL.

        Args:
            query: Query string

        Returns:
            True if query appears to be TQL
        """
        # Simple heuristic: contains TQL keywords
        tql_keywords = [
            "typeName",
            "summary",
            "rating",
            "confidence",
            "dateAdded",
            "lastModified",
            " in ",
            " and ",
            " or ",
            " > ",
            " < ",
            " = ",
        ]
        query_lower = query.lower()
        return any(keyword.lower() in query_lower for keyword in tql_keywords)
```

### 2. `tc_tui/widgets/__init__.py`

```python
"""TUI widgets module."""

from .search_input import SearchInput

__all__ = [
    "SearchInput",
]
```

## Testing Requirements

### Test File: `tests/test_widgets/test_search_input.py`

```python
"""Tests for search input widget."""

import pytest
from textual.widgets import Input, Select

from tc_tui.widgets import SearchInput
from tc_tui.state import SearchType


@pytest.mark.asyncio
async def test_search_input_initialization():
    """Test search input initializes correctly."""
    widget = SearchInput()

    assert widget.search_type == SearchType.INDICATORS
    assert widget.current_value == ""


@pytest.mark.asyncio
async def test_search_input_compose():
    """Test search input composition."""
    widget = SearchInput()
    components = list(widget.compose())

    # Should have the container structure
    assert len(components) > 0


@pytest.mark.asyncio
async def test_set_value():
    """Test setting search input value."""
    from textual.app import App

    app = App()
    async with app.run_test() as pilot:
        widget = SearchInput()
        await app.mount(widget)

        widget.set_value("test query")
        input_field = widget.query_one("#search-input-field", Input)

        assert input_field.value == "test query"


@pytest.mark.asyncio
async def test_clear():
    """Test clearing search input."""
    from textual.app import App

    app = App()
    async with app.run_test() as pilot:
        widget = SearchInput()
        await app.mount(widget)

        widget.set_value("test query")
        widget.clear()

        input_field = widget.query_one("#search-input-field", Input)
        assert input_field.value == ""


@pytest.mark.asyncio
async def test_set_search_type():
    """Test setting search type."""
    from textual.app import App

    app = App()
    async with app.run_test() as pilot:
        widget = SearchInput()
        await app.mount(widget)

        widget.set_search_type(SearchType.GROUPS)

        assert widget.search_type == SearchType.GROUPS
        select = widget.query_one("#search-type-select", Select)
        assert select.value == SearchType.GROUPS.value


@pytest.mark.asyncio
async def test_history_navigation():
    """Test search history navigation."""
    from textual.app import App

    app = App()
    async with app.run_test() as pilot:
        widget = SearchInput()
        await app.mount(widget)

        # Add some history
        widget._add_to_history("query1")
        widget._add_to_history("query2")
        widget._add_to_history("query3")

        assert len(widget._history) == 3

        # Navigate up
        widget._navigate_history_up()
        assert widget.get_value() == "query3"

        widget._navigate_history_up()
        assert widget.get_value() == "query2"

        # Navigate down
        widget._navigate_history_down()
        assert widget.get_value() == "query3"


def test_is_tql_query():
    """Test TQL query detection."""
    widget = SearchInput()

    assert widget.is_tql_query('typeName in ("Address")')
    assert widget.is_tql_query("rating > 3")
    assert widget.is_tql_query("summary in (\"test\")")
    assert not widget.is_tql_query("192.168.1.1")
    assert not widget.is_tql_query("test@example.com")


def test_no_duplicate_history():
    """Test that consecutive duplicates are not added to history."""
    widget = SearchInput()

    widget._add_to_history("query1")
    widget._add_to_history("query1")

    assert len(widget._history) == 1
```

## Acceptance Criteria

- [ ] SearchInput widget created in `tc_tui/widgets/`
- [ ] Type selector dropdown works (Indicators/Groups/Both)
- [ ] Text input accepts queries
- [ ] Search history navigation with Up/Down arrows
- [ ] SearchSubmitted message emitted on Enter
- [ ] SearchTypeChanged message emitted on type change
- [ ] TQL query detection works
- [ ] Focus management works correctly
- [ ] All tests passing with >80% coverage
- [ ] CSS styling applied
- [ ] Type hints on all public methods
- [ ] Docstrings complete

## Integration Notes

### Dependencies
- **Package 1 (Data Models)**: Uses SearchType enum
- **Package 4 (Utilities)**: Uses detect_indicator_type() function
- **Package 6 (State)**: Will be connected to AppState in screens

### Provides For
- **Package 8 (Screens)**: Will be composed into main screen

### Usage Example

```python
from textual.app import App
from tc_tui.widgets import SearchInput

class MyApp(App):
    def compose(self):
        yield SearchInput()

    def on_search_input_search_submitted(self, message):
        """Handle search submission."""
        query = message.query
        search_type = message.search_type
        # Perform search...
```

## Notes

- Input field focused by default
- `/` key can focus search from anywhere (handled by parent screen)
- History limited to 50 entries
- Consecutive duplicate queries not added to history
- TQL detection is heuristic-based (simple keyword matching)
- Cursor positioned at end when setting value
- CSS can be customized by application

## Time Estimate

- Widget structure: 1 hour
- History navigation: 1 hour
- Event handling: 1 hour
- Tests: 0.5 hours
- Documentation: 0.5 hours

**Total: 3-4 hours**
