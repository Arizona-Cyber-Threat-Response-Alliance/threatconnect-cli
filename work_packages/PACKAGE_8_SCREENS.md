# Work Package 8: Screens

**Module**: `tc_tui/screens/`
**Priority**: Medium (UI Integration)
**Estimated Time**: 5-6 hours
**Dependencies**: Package 1 (Data Models), Package 5 (Search Engine), Package 6 (State), Packages 7a-7d (Widgets)
**Can Start**: After all widget packages (7a-7d) complete
**Assignable To**: Any agent with Python/Textual experience

## Objective

Create the screen composition layer that combines all widgets into functional screens. Implement the main screen with search, results, and detail view, plus help and settings screens. Handle widget communication, state management, and keyboard bindings.

## Deliverables

### Files to Create

```
tc_tui/screens/
├── __init__.py          # Public exports
├── main_screen.py       # Main application screen
├── help_screen.py       # Help and keybindings screen
└── settings_screen.py   # Settings configuration screen (optional for Phase 2)
```

### 1. `tc_tui/screens/main_screen.py`

```python
"""Main application screen composing all widgets."""

from typing import Optional
from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Header, Footer
from textual.binding import Binding

from tc_tui.widgets import SearchInput, ResultsTable, DetailView, StatusBar
from tc_tui.state import AppState, ViewMode, SearchType
from tc_tui.search import SearchEngine
from tc_tui.models import SearchRequest


class MainScreen(Screen):
    """Main application screen with search, results, and detail views.

    Layout:
    - Header (title and instance info)
    - SearchInput (collapsible)
    - ResultsTable / DetailView (switchable)
    - StatusBar (always visible)
    """

    BINDINGS = [
        Binding("/", "focus_search", "Focus Search", show=True),
        Binding("escape", "close_detail", "Close Detail", show=False),
        Binding("?", "show_help", "Help", show=True),
        Binding("q", "quit", "Quit", show=True),
        Binding("left", "previous_page", "Previous Page", show=False),
        Binding("right", "next_page", "Next Page", show=False),
        Binding("h", "previous_page", "Previous Page (vim)", show=False),
        Binding("l", "next_page", "Next Page (vim)", show=False),
    ]

    CSS = """
    MainScreen {
        layout: vertical;
    }

    MainScreen > Container {
        height: 1fr;
    }

    MainScreen > .search-container {
        height: auto;
    }

    MainScreen > .content-container {
        height: 1fr;
        layout: vertical;
    }

    MainScreen > .results-container {
        height: 1fr;
    }

    MainScreen > .detail-container {
        height: 1fr;
        display: none;
    }

    MainScreen > .detail-container.visible {
        display: block;
    }

    MainScreen > .results-container.hidden {
        display: none;
    }
    """

    def __init__(
        self,
        app_state: AppState,
        search_engine: SearchEngine,
        instance_name: str = ""
    ) -> None:
        """Initialize main screen.

        Args:
            app_state: Application state manager
            search_engine: Search engine instance
            instance_name: ThreatConnect instance name
        """
        super().__init__()
        self.app_state = app_state
        self.search_engine = search_engine
        self.instance_name = instance_name

    def compose(self) -> ComposeResult:
        """Compose the main screen layout."""
        title = f"ThreatConnect CLI - {self.instance_name}" if self.instance_name else "ThreatConnect CLI"
        yield Header(show_clock=True)

        # Search input section
        with Container(classes="search-container"):
            yield SearchInput()

        # Content area (results or detail view)
        with Container(classes="content-container"):
            with Container(classes="results-container", id="results-container"):
                yield ResultsTable()

            with Container(classes="detail-container", id="detail-container"):
                yield DetailView()

        # Status bar
        yield StatusBar()

    def on_mount(self) -> None:
        """Handle screen mount."""
        # Set up state watchers
        self.watch(self.app_state, "view_mode", self.on_view_mode_changed)
        self.watch(self.app_state, "results", self.on_results_changed)
        self.watch(self.app_state, "selected_item", self.on_selected_item_changed)
        self.watch(self.app_state, "pagination", self.on_pagination_changed)
        self.watch(self.app_state, "is_loading", self.on_loading_changed)
        self.watch(self.app_state, "error_message", self.on_error_changed)
        self.watch(self.app_state, "status_message", self.on_status_changed)

        # Set initial view mode
        self.app_state.set_view_mode(ViewMode.SEARCH)

        # Update status bar
        status_bar = self.query_one(StatusBar)
        status_bar.set_view_mode(ViewMode.SEARCH)
        if self.instance_name:
            status_bar.show_connection_status(True, self.instance_name)

    def on_view_mode_changed(self, view_mode: ViewMode) -> None:
        """Handle view mode changes.

        Args:
            view_mode: New view mode
        """
        results_container = self.query_one("#results-container")
        detail_container = self.query_one("#detail-container")
        status_bar = self.query_one(StatusBar)

        if view_mode == ViewMode.DETAIL:
            # Show detail view, hide results
            results_container.add_class("hidden")
            detail_container.add_class("visible")
        else:
            # Show results, hide detail view
            results_container.remove_class("hidden")
            detail_container.remove_class("visible")

        # Update status bar
        status_bar.set_view_mode(view_mode)

    def on_results_changed(self, results: list) -> None:
        """Handle results changes.

        Args:
            results: New results list
        """
        results_table = self.query_one(ResultsTable)

        # Determine result type based on search type
        result_type = self.app_state.search_type.value

        # Update table
        results_table.update_results(results, result_type=result_type)

        # Update view mode
        if results:
            self.app_state.set_view_mode(ViewMode.RESULTS)

    def on_selected_item_changed(self, item: Optional[any]) -> None:
        """Handle selected item changes.

        Args:
            item: New selected item
        """
        # This will be used when implementing detail view fetching
        pass

    def on_pagination_changed(self, pagination: any) -> None:
        """Handle pagination changes.

        Args:
            pagination: New pagination state
        """
        status_bar = self.query_one(StatusBar)
        status_bar.set_pagination(
            current_page=pagination.current_page,
            total_pages=pagination.total_pages,
            total_results=pagination.total_results
        )

    def on_loading_changed(self, is_loading: bool) -> None:
        """Handle loading state changes.

        Args:
            is_loading: New loading state
        """
        status_bar = self.query_one(StatusBar)
        status_bar.set_loading(is_loading, self.app_state.status_message)

    def on_error_changed(self, error: Optional[str]) -> None:
        """Handle error message changes.

        Args:
            error: New error message
        """
        status_bar = self.query_one(StatusBar)
        status_bar.set_error(error)

    def on_status_changed(self, status: Optional[str]) -> None:
        """Handle status message changes.

        Args:
            status: New status message
        """
        status_bar = self.query_one(StatusBar)
        if not self.app_state.is_loading and not self.app_state.error_message:
            status_bar.set_status(status)

    # Widget message handlers

    def on_search_input_search_submitted(
        self,
        message: SearchInput.SearchSubmitted
    ) -> None:
        """Handle search submission.

        Args:
            message: Search submitted message
        """
        self.run_worker(self.execute_search(message.query, message.search_type))

    def on_search_input_search_type_changed(
        self,
        message: SearchInput.SearchTypeChanged
    ) -> None:
        """Handle search type change.

        Args:
            message: Search type changed message
        """
        self.app_state.set_search_type(message.search_type)

    def on_results_table_row_selected(
        self,
        message: ResultsTable.RowSelected
    ) -> None:
        """Handle row selection in results table.

        Args:
            message: Row selected message
        """
        self.app_state.select_result(message.row_index)

    def on_results_table_row_activated(
        self,
        message: ResultsTable.RowActivated
    ) -> None:
        """Handle row activation (Enter key) in results table.

        Args:
            message: Row activated message
        """
        # Show detail view for the selected item
        detail_view = self.query_one(DetailView)

        # Determine if it's an indicator or group
        if hasattr(message.item, 'summary'):
            detail_view.show_indicator(message.item)
        else:
            detail_view.show_group(message.item)

        self.app_state.show_detail(message.item)

    def on_detail_view_association_selected(
        self,
        message: DetailView.AssociationSelected
    ) -> None:
        """Handle association selection in detail view.

        Args:
            message: Association selected message
        """
        # Navigate to the associated item
        # This would fetch the item and show its details
        # Implementation depends on API methods
        pass

    # Action handlers

    def action_focus_search(self) -> None:
        """Focus the search input."""
        search_input = self.query_one(SearchInput)
        search_input.focus_input()
        self.app_state.set_view_mode(ViewMode.SEARCH)

    def action_close_detail(self) -> None:
        """Close detail view and return to results."""
        if self.app_state.view_mode == ViewMode.DETAIL:
            self.app_state.hide_detail()

    def action_show_help(self) -> None:
        """Show help screen."""
        from .help_screen import HelpScreen
        self.app.push_screen(HelpScreen())

    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()

    def action_previous_page(self) -> None:
        """Navigate to previous page."""
        if self.app_state.pagination.has_previous_page:
            self.app_state.previous_page()
            # Re-execute search with new page
            self.run_worker(self.execute_search(
                self.app_state.current_query,
                self.app_state.search_type
            ))

    def action_next_page(self) -> None:
        """Navigate to next page."""
        if self.app_state.pagination.has_next_page:
            self.app_state.next_page()
            # Re-execute search with new page
            self.run_worker(self.execute_search(
                self.app_state.current_query,
                self.app_state.search_type
            ))

    # Worker methods

    async def execute_search(self, query: str, search_type: SearchType) -> None:
        """Execute search query.

        Args:
            query: Search query
            search_type: Type of search
        """
        try:
            # Set loading state
            self.app_state.set_loading(True, "Searching...")
            self.app_state.set_error(None)

            # Build search request
            request = SearchRequest(
                query=query,
                search_type=search_type,
                page=self.app_state.pagination.current_page,
                page_size=self.app_state.pagination.page_size,
                filters=self.app_state.filters
            )

            # Execute search
            result = await self.search_engine.search(request)

            # Update state with results
            self.app_state.set_results(
                result.data,
                total_count=result.pagination.total_results
            )

            # Add to search history
            self.app_state.add_search_to_history(
                query,
                result_count=result.pagination.total_results
            )

            # Set success message
            self.app_state.set_status(
                f"Found {result.pagination.total_results} results"
            )

        except Exception as e:
            # Set error state
            self.app_state.set_error(f"Search failed: {str(e)}")
            self.app_state.clear_results()

        finally:
            # Clear loading state
            self.app_state.set_loading(False)
```

### 2. `tc_tui/screens/help_screen.py`

```python
"""Help screen displaying keybindings and usage information."""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Static, Footer
from textual.containers import Container, Vertical, ScrollableContainer
from textual.binding import Binding


class HelpScreen(Screen):
    """Help screen with keybindings and usage information."""

    BINDINGS = [
        Binding("escape", "close", "Close", show=True),
        Binding("q", "close", "Close", show=False),
    ]

    CSS = """
    HelpScreen {
        align: center middle;
    }

    HelpScreen > Container {
        width: 80;
        height: auto;
        max-height: 90%;
        border: solid $primary;
        background: $surface;
        padding: 1 2;
    }

    HelpScreen .help-title {
        text-style: bold;
        color: $accent;
        text-align: center;
        margin-bottom: 1;
    }

    HelpScreen .help-section {
        margin-top: 1;
        margin-bottom: 1;
    }

    HelpScreen .section-title {
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }

    HelpScreen .keybinding {
        margin-left: 2;
    }

    HelpScreen .key {
        color: $accent;
        text-style: bold;
    }
    """

    def compose(self) -> ComposeResult:
        """Compose help screen."""
        with ScrollableContainer():
            yield Static("ThreatConnect CLI - Help", classes="help-title")

            # Search Section
            with Container(classes="help-section"):
                yield Static("Search", classes="section-title")
                yield Static("  /           Focus search input", classes="keybinding")
                yield Static("  Enter       Execute search", classes="keybinding")
                yield Static("  ↑ / ↓       Navigate search history", classes="keybinding")

            # Navigation Section
            with Container(classes="help-section"):
                yield Static("Navigation", classes="section-title")
                yield Static("  ↑ / ↓       Navigate results (or k / j)", classes="keybinding")
                yield Static("  g           Jump to top", classes="keybinding")
                yield Static("  G           Jump to bottom", classes="keybinding")
                yield Static("  ← / →       Previous/Next page (or h / l)", classes="keybinding")
                yield Static("  Enter       View details", classes="keybinding")
                yield Static("  Esc         Close detail view", classes="keybinding")

            # General Section
            with Container(classes="help-section"):
                yield Static("General", classes="section-title")
                yield Static("  ?           Show this help", classes="keybinding")
                yield Static("  q           Quit application", classes="keybinding")
                yield Static("  Ctrl+C      Force quit", classes="keybinding")

            # Search Tips Section
            with Container(classes="help-section"):
                yield Static("Search Tips", classes="section-title")
                yield Static("  • Enter indicator value (IP, email, hash, etc.) for auto-detection", classes="keybinding")
                yield Static("  • Use TQL for advanced queries: typeName in (\"Address\") and rating > 3", classes="keybinding")
                yield Static("  • Select search type (Indicators/Groups/Both) before searching", classes="keybinding")

            yield Static("\nPress Esc or q to close", classes="help-title")

    def action_close(self) -> None:
        """Close help screen."""
        self.app.pop_screen()
```

### 3. `tc_tui/screens/__init__.py`

```python
"""Screens module."""

from .main_screen import MainScreen
from .help_screen import HelpScreen

__all__ = [
    "MainScreen",
    "HelpScreen",
]
```

## Testing Requirements

### Test File: `tests/test_screens/test_main_screen.py`

```python
"""Tests for main screen."""

import pytest
from unittest.mock import AsyncMock, Mock
from textual.app import App

from tc_tui.screens import MainScreen
from tc_tui.state import AppState, ViewMode, SearchType
from tc_tui.widgets import SearchInput, ResultsTable, StatusBar, DetailView


@pytest.fixture
def mock_search_engine():
    """Create mock search engine."""
    engine = Mock()
    engine.search = AsyncMock()
    return engine


@pytest.fixture
def app_state():
    """Create app state."""
    return AppState()


@pytest.mark.asyncio
async def test_main_screen_initialization(app_state, mock_search_engine):
    """Test main screen initializes correctly."""
    screen = MainScreen(app_state, mock_search_engine, "test-instance")

    assert screen.app_state == app_state
    assert screen.search_engine == mock_search_engine
    assert screen.instance_name == "test-instance"


@pytest.mark.asyncio
async def test_main_screen_composition(app_state, mock_search_engine):
    """Test main screen composition."""
    app = App()
    async with app.run_test() as pilot:
        screen = MainScreen(app_state, mock_search_engine)
        await app.install_screen(screen, name="main")
        await app.push_screen("main")

        # Verify widgets are present
        assert screen.query_one(SearchInput) is not None
        assert screen.query_one(ResultsTable) is not None
        assert screen.query_one(StatusBar) is not None
        assert screen.query_one(DetailView) is not None


@pytest.mark.asyncio
async def test_view_mode_switching(app_state, mock_search_engine):
    """Test switching between view modes."""
    app = App()
    async with app.run_test() as pilot:
        screen = MainScreen(app_state, mock_search_engine)
        await app.install_screen(screen, name="main")
        await app.push_screen("main")

        # Start in search mode
        assert app_state.view_mode == ViewMode.SEARCH

        # Switch to results
        app_state.set_view_mode(ViewMode.RESULTS)
        await pilot.pause()
        assert app_state.view_mode == ViewMode.RESULTS

        # Switch to detail
        app_state.set_view_mode(ViewMode.DETAIL)
        await pilot.pause()
        assert app_state.view_mode == ViewMode.DETAIL
```

### Test File: `tests/test_screens/test_help_screen.py`

```python
"""Tests for help screen."""

import pytest
from textual.app import App

from tc_tui.screens import HelpScreen


@pytest.mark.asyncio
async def test_help_screen_composition():
    """Test help screen composition."""
    app = App()
    async with app.run_test() as pilot:
        screen = HelpScreen()
        await app.push_screen(screen)

        # Verify screen is displayed
        assert screen is not None


@pytest.mark.asyncio
async def test_help_screen_close():
    """Test closing help screen."""
    app = App()
    async with app.run_test() as pilot:
        screen = HelpScreen()
        await app.push_screen(screen)

        # Press escape to close
        await pilot.press("escape")
        await pilot.pause()

        # Screen should be popped
        # (verification depends on app structure)
```

## Acceptance Criteria

- [ ] MainScreen created in `tc_tui/screens/`
- [ ] All widgets properly composed in layout
- [ ] View mode switching works (search/results/detail)
- [ ] Search execution with loading states
- [ ] Results displayed in table
- [ ] Detail view shown when row activated
- [ ] Pagination navigation (←/→, h/l)
- [ ] Keyboard shortcuts working (/, Esc, ?, q)
- [ ] Status bar updates with state changes
- [ ] HelpScreen displays keybindings
- [ ] State watchers update UI reactively
- [ ] All tests passing with >80% coverage
- [ ] Type hints on all public methods
- [ ] Docstrings complete

## Integration Notes

### Dependencies
- **Package 1 (Data Models)**: Uses SearchRequest, Indicator, Group
- **Package 5 (Search Engine)**: Uses SearchEngine for queries
- **Package 6 (State)**: Uses AppState for state management
- **Packages 7a-7d**: Composes all widgets

### Provides For
- **Package 9 (Main App)**: MainScreen will be the primary app screen

### Usage Example

```python
from textual.app import App
from tc_tui.screens import MainScreen
from tc_tui.state import AppState
from tc_tui.search import SearchEngine

app_state = AppState()
search_engine = SearchEngine(client)

class ThreatConnectApp(App):
    def on_mount(self):
        self.push_screen(MainScreen(app_state, search_engine, "my-instance"))
```

## Notes

- MainScreen uses workers for async search execution
- State watchers automatically update UI when state changes
- Detail view toggles visibility instead of being removed/added
- Keyboard bindings defined at screen level
- Help screen uses ScrollableContainer for long content
- CSS handles layout and visibility toggling
- Error handling in search worker with try/finally
- Pagination reloads search with new page parameters
- All widget messages handled in MainScreen

## Time Estimate

- MainScreen structure and layout: 1.5 hours
- Widget composition and communication: 1.5 hours
- State watchers and handlers: 1 hour
- Search execution worker: 1 hour
- Keyboard bindings: 0.5 hours
- HelpScreen: 0.5 hours
- Tests: 1.5 hours
- Documentation: 0.5 hours

**Total: 5-6 hours**
