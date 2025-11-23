# Work Package 6: State Manager

**Module**: `tc_tui/state/`
**Priority**: Medium (Required for UI)
**Estimated Time**: 4-5 hours
**Dependencies**: Package 1 (Data Models)
**Can Start**: After Package 1 complete
**Assignable To**: Any agent with Python/Textual experience

## Objective

Create a centralized state management system for the TUI application using Textual's reactive system. This will manage all application state including search results, selections, filters, navigation history, and UI state.

## Deliverables

### Files to Create

```
tc_tui/state/
├── __init__.py          # Public exports
├── manager.py           # Main state manager
├── models.py            # State-specific models
└── history.py           # Search/navigation history
```

### 1. `tc_tui/state/models.py`

Define state-specific data models:

```python
"""State management models."""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Any
from pydantic import BaseModel, Field


class SearchType(str, Enum):
    """Type of search being performed."""

    INDICATORS = "indicators"
    GROUPS = "groups"
    BOTH = "both"


class ViewMode(str, Enum):
    """Current view mode in the UI."""

    SEARCH = "search"
    RESULTS = "results"
    DETAIL = "detail"
    HELP = "help"
    SETTINGS = "settings"


class FilterState(BaseModel):
    """Current filter settings."""

    search_type: SearchType = SearchType.INDICATORS
    owner: Optional[str] = None
    min_rating: float = 0.0
    max_rating: float = 5.0
    min_confidence: int = 0
    max_confidence: int = 100
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    tags: List[str] = Field(default_factory=list)
    types: List[str] = Field(default_factory=list)  # Specific indicator/group types

    def is_filtered(self) -> bool:
        """Check if any filters are active."""
        return (
            self.owner is not None
            or self.min_rating > 0.0
            or self.max_rating < 5.0
            or self.min_confidence > 0
            or self.max_confidence < 100
            or self.date_from is not None
            or self.date_to is not None
            or len(self.tags) > 0
            or len(self.types) > 0
        )


class PaginationState(BaseModel):
    """Current pagination state."""

    current_page: int = 0
    page_size: int = 100
    total_results: int = 0
    has_next_page: bool = False
    has_previous_page: bool = False

    @property
    def total_pages(self) -> int:
        """Calculate total number of pages."""
        if self.total_results == 0:
            return 0
        return (self.total_results + self.page_size - 1) // self.page_size

    @property
    def result_start(self) -> int:
        """Get the starting index for the current page."""
        return self.current_page * self.page_size

    @property
    def result_end(self) -> int:
        """Get the ending index for the current page."""
        return min((self.current_page + 1) * self.page_size, self.total_results)


class SearchHistoryEntry(BaseModel):
    """Single search history entry."""

    query: str
    search_type: SearchType
    timestamp: datetime = Field(default_factory=datetime.now)
    result_count: int = 0


class NavigationHistoryEntry(BaseModel):
    """Single navigation history entry."""

    view_mode: ViewMode
    item_id: Optional[int] = None
    item_type: Optional[str] = None  # "Indicator" or "Group"
    timestamp: datetime = Field(default_factory=datetime.now)
```

### 2. `tc_tui/state/history.py`

Implement search and navigation history management:

```python
"""Search and navigation history management."""

from typing import List, Optional
from collections import deque
from .models import SearchHistoryEntry, NavigationHistoryEntry


class SearchHistory:
    """Manages search history."""

    def __init__(self, max_size: int = 50):
        """Initialize search history.

        Args:
            max_size: Maximum number of history entries to keep
        """
        self.max_size = max_size
        self._history: deque[SearchHistoryEntry] = deque(maxlen=max_size)
        self._current_index: int = -1

    def add(self, entry: SearchHistoryEntry) -> None:
        """Add a new search to history.

        Args:
            entry: Search history entry to add
        """
        # Don't add duplicate consecutive searches
        if self._history and self._history[-1].query == entry.query:
            return

        self._history.append(entry)
        self._current_index = len(self._history) - 1

    def get_previous(self) -> Optional[SearchHistoryEntry]:
        """Get previous search in history.

        Returns:
            Previous search entry or None if at the beginning
        """
        if not self._history or self._current_index <= 0:
            return None

        self._current_index -= 1
        return self._history[self._current_index]

    def get_next(self) -> Optional[SearchHistoryEntry]:
        """Get next search in history.

        Returns:
            Next search entry or None if at the end
        """
        if not self._history or self._current_index >= len(self._history) - 1:
            return None

        self._current_index += 1
        return self._history[self._current_index]

    def get_all(self) -> List[SearchHistoryEntry]:
        """Get all history entries.

        Returns:
            List of all search history entries
        """
        return list(self._history)

    def clear(self) -> None:
        """Clear all history."""
        self._history.clear()
        self._current_index = -1


class NavigationHistory:
    """Manages navigation history for back/forward functionality."""

    def __init__(self, max_size: int = 100):
        """Initialize navigation history.

        Args:
            max_size: Maximum number of history entries to keep
        """
        self.max_size = max_size
        self._history: List[NavigationHistoryEntry] = []
        self._current_index: int = -1

    def push(self, entry: NavigationHistoryEntry) -> None:
        """Push a new navigation entry.

        Args:
            entry: Navigation history entry to add
        """
        # Remove any forward history when pushing new entry
        if self._current_index < len(self._history) - 1:
            self._history = self._history[:self._current_index + 1]

        self._history.append(entry)

        # Maintain max size
        if len(self._history) > self.max_size:
            self._history.pop(0)
        else:
            self._current_index += 1

    def can_go_back(self) -> bool:
        """Check if can navigate back.

        Returns:
            True if can go back, False otherwise
        """
        return self._current_index > 0

    def can_go_forward(self) -> bool:
        """Check if can navigate forward.

        Returns:
            True if can go forward, False otherwise
        """
        return self._current_index < len(self._history) - 1

    def go_back(self) -> Optional[NavigationHistoryEntry]:
        """Navigate to previous entry.

        Returns:
            Previous navigation entry or None
        """
        if not self.can_go_back():
            return None

        self._current_index -= 1
        return self._history[self._current_index]

    def go_forward(self) -> Optional[NavigationHistoryEntry]:
        """Navigate to next entry.

        Returns:
            Next navigation entry or None
        """
        if not self.can_go_forward():
            return None

        self._current_index += 1
        return self._history[self._current_index]

    def current(self) -> Optional[NavigationHistoryEntry]:
        """Get current navigation entry.

        Returns:
            Current navigation entry or None
        """
        if self._current_index < 0 or self._current_index >= len(self._history):
            return None
        return self._history[self._current_index]

    def clear(self) -> None:
        """Clear all history."""
        self._history.clear()
        self._current_index = -1
```

### 3. `tc_tui/state/manager.py`

Implement the main state manager with Textual reactive variables:

```python
"""Main application state manager."""

from typing import Optional, List, Any, Dict
from textual.reactive import Reactive
from textual.app import ComposeResult
from textual.widget import Widget

from tc_tui.models import Indicator, Group, SearchResult
from .models import (
    SearchType,
    ViewMode,
    FilterState,
    PaginationState,
    SearchHistoryEntry,
    NavigationHistoryEntry,
)
from .history import SearchHistory, NavigationHistory


class AppState(Widget):
    """Central application state manager using Textual reactive system.

    This widget doesn't render anything but manages all application state
    using Textual's reactive system for automatic UI updates.
    """

    # View state
    view_mode: Reactive[ViewMode] = Reactive(ViewMode.SEARCH)
    is_loading: Reactive[bool] = Reactive(False)
    error_message: Reactive[Optional[str]] = Reactive(None)
    status_message: Reactive[Optional[str]] = Reactive(None)

    # Search state
    current_query: Reactive[str] = Reactive("")
    search_type: Reactive[SearchType] = Reactive(SearchType.INDICATORS)

    # Results state
    results: Reactive[List[Any]] = Reactive([])  # List[Indicator | Group]
    selected_index: Reactive[int] = Reactive(0)
    selected_item: Reactive[Optional[Any]] = Reactive(None)  # Indicator | Group | None

    # Filter state
    filters: Reactive[FilterState] = Reactive(FilterState())

    # Pagination state
    pagination: Reactive[PaginationState] = Reactive(PaginationState())

    # Detail view state
    detail_item: Reactive[Optional[Any]] = Reactive(None)  # Indicator | Group | None
    detail_associations: Reactive[List[Any]] = Reactive([])
    show_associations: Reactive[bool] = Reactive(False)

    def __init__(self):
        """Initialize the state manager."""
        super().__init__()
        self.search_history = SearchHistory()
        self.navigation_history = NavigationHistory()

    def compose(self) -> ComposeResult:
        """Compose method required by Widget (returns nothing)."""
        return []

    # Search operations

    def set_query(self, query: str) -> None:
        """Set the current search query.

        Args:
            query: Search query string
        """
        self.current_query = query

    def set_search_type(self, search_type: SearchType) -> None:
        """Set the search type.

        Args:
            search_type: Type of search (indicators, groups, or both)
        """
        self.search_type = search_type
        self.filters = FilterState(search_type=search_type)

    def add_search_to_history(self, query: str, result_count: int) -> None:
        """Add a search to history.

        Args:
            query: The search query
            result_count: Number of results returned
        """
        entry = SearchHistoryEntry(
            query=query,
            search_type=self.search_type,
            result_count=result_count,
        )
        self.search_history.add(entry)

    # Results operations

    def set_results(self, results: List[Any], total_count: int) -> None:
        """Set search results.

        Args:
            results: List of indicators or groups
            total_count: Total number of results (for pagination)
        """
        self.results = results
        self.selected_index = 0

        # Update pagination
        pagination = PaginationState(
            current_page=self.pagination.current_page,
            page_size=self.pagination.page_size,
            total_results=total_count,
        )
        pagination.has_next_page = pagination.current_page < pagination.total_pages - 1
        pagination.has_previous_page = pagination.current_page > 0
        self.pagination = pagination

        # Update selected item
        if results:
            self.selected_item = results[0]
        else:
            self.selected_item = None

    def clear_results(self) -> None:
        """Clear search results."""
        self.results = []
        self.selected_index = 0
        self.selected_item = None
        self.pagination = PaginationState()

    def select_result(self, index: int) -> None:
        """Select a result by index.

        Args:
            index: Index of the result to select
        """
        if 0 <= index < len(self.results):
            self.selected_index = index
            self.selected_item = self.results[index]

    def select_next(self) -> None:
        """Select the next result."""
        if self.selected_index < len(self.results) - 1:
            self.select_result(self.selected_index + 1)

    def select_previous(self) -> None:
        """Select the previous result."""
        if self.selected_index > 0:
            self.select_result(self.selected_index - 1)

    # Pagination operations

    def next_page(self) -> None:
        """Move to next page."""
        if self.pagination.has_next_page:
            new_pagination = self.pagination.model_copy()
            new_pagination.current_page += 1
            self.pagination = new_pagination

    def previous_page(self) -> None:
        """Move to previous page."""
        if self.pagination.has_previous_page:
            new_pagination = self.pagination.model_copy()
            new_pagination.current_page -= 1
            self.pagination = new_pagination

    def goto_page(self, page_number: int) -> None:
        """Go to a specific page.

        Args:
            page_number: Page number (0-indexed)
        """
        if 0 <= page_number < self.pagination.total_pages:
            new_pagination = self.pagination.model_copy()
            new_pagination.current_page = page_number
            self.pagination = new_pagination

    # Filter operations

    def set_filters(self, filters: FilterState) -> None:
        """Set filter state.

        Args:
            filters: New filter state
        """
        self.filters = filters

    def reset_filters(self) -> None:
        """Reset filters to default."""
        self.filters = FilterState(search_type=self.search_type)

    # Detail view operations

    def show_detail(self, item: Any) -> None:
        """Show detail view for an item.

        Args:
            item: Indicator or Group to show details for
        """
        self.detail_item = item
        self.view_mode = ViewMode.DETAIL

        # Add to navigation history
        item_type = "Indicator" if hasattr(item, "summary") else "Group"
        entry = NavigationHistoryEntry(
            view_mode=ViewMode.DETAIL,
            item_id=item.id,
            item_type=item_type,
        )
        self.navigation_history.push(entry)

    def hide_detail(self) -> None:
        """Hide detail view."""
        self.detail_item = None
        self.detail_associations = []
        self.view_mode = ViewMode.RESULTS

    def set_detail_associations(self, associations: List[Any]) -> None:
        """Set associations for the current detail item.

        Args:
            associations: List of associated items
        """
        self.detail_associations = associations
        self.show_associations = True

    # View mode operations

    def set_view_mode(self, mode: ViewMode) -> None:
        """Set the current view mode.

        Args:
            mode: New view mode
        """
        self.view_mode = mode

    # Loading and error state

    def set_loading(self, loading: bool, message: Optional[str] = None) -> None:
        """Set loading state.

        Args:
            loading: Whether app is loading
            message: Optional loading message
        """
        self.is_loading = loading
        if loading and message:
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

    # Navigation operations

    def go_back(self) -> Optional[NavigationHistoryEntry]:
        """Navigate back in history.

        Returns:
            Previous navigation entry or None
        """
        return self.navigation_history.go_back()

    def go_forward(self) -> Optional[NavigationHistoryEntry]:
        """Navigate forward in history.

        Returns:
            Next navigation entry or None
        """
        return self.navigation_history.go_forward()

    def can_go_back(self) -> bool:
        """Check if can navigate back.

        Returns:
            True if can go back, False otherwise
        """
        return self.navigation_history.can_go_back()

    def can_go_forward(self) -> bool:
        """Check if can navigate forward.

        Returns:
            True if can go forward, False otherwise
        """
        return self.navigation_history.can_go_forward()

    # Utility methods

    def reset(self) -> None:
        """Reset all state to initial values."""
        self.view_mode = ViewMode.SEARCH
        self.is_loading = False
        self.error_message = None
        self.status_message = None
        self.current_query = ""
        self.search_type = SearchType.INDICATORS
        self.clear_results()
        self.reset_filters()
        self.hide_detail()

    def get_state_summary(self) -> Dict[str, Any]:
        """Get a summary of current state for debugging.

        Returns:
            Dictionary with current state values
        """
        return {
            "view_mode": self.view_mode,
            "is_loading": self.is_loading,
            "current_query": self.current_query,
            "search_type": self.search_type,
            "result_count": len(self.results),
            "selected_index": self.selected_index,
            "current_page": self.pagination.current_page,
            "total_pages": self.pagination.total_pages,
            "has_filters": self.filters.is_filtered(),
        }
```

### 4. `tc_tui/state/__init__.py`

Export public API:

```python
"""State management module."""

from .manager import AppState
from .models import (
    SearchType,
    ViewMode,
    FilterState,
    PaginationState,
    SearchHistoryEntry,
    NavigationHistoryEntry,
)
from .history import SearchHistory, NavigationHistory

__all__ = [
    "AppState",
    "SearchType",
    "ViewMode",
    "FilterState",
    "PaginationState",
    "SearchHistoryEntry",
    "NavigationHistoryEntry",
    "SearchHistory",
    "NavigationHistory",
]
```

## Testing Requirements

### Test File: `tests/test_state/test_manager.py`

```python
"""Tests for state manager."""

import pytest
from tc_tui.state import AppState, ViewMode, SearchType, FilterState


def test_state_initialization():
    """Test state manager initializes with correct defaults."""
    state = AppState()

    assert state.view_mode == ViewMode.SEARCH
    assert state.is_loading is False
    assert state.current_query == ""
    assert state.search_type == SearchType.INDICATORS
    assert len(state.results) == 0
    assert state.selected_index == 0


def test_set_query():
    """Test setting search query."""
    state = AppState()
    state.set_query("test query")

    assert state.current_query == "test query"


def test_set_results():
    """Test setting search results."""
    state = AppState()
    mock_results = [{"id": 1}, {"id": 2}, {"id": 3}]

    state.set_results(mock_results, total_count=10)

    assert len(state.results) == 3
    assert state.selected_index == 0
    assert state.selected_item == mock_results[0]
    assert state.pagination.total_results == 10


def test_select_result():
    """Test selecting a result by index."""
    state = AppState()
    mock_results = [{"id": 1}, {"id": 2}, {"id": 3}]
    state.set_results(mock_results, total_count=3)

    state.select_result(1)

    assert state.selected_index == 1
    assert state.selected_item == mock_results[1]


def test_select_next_previous():
    """Test navigating between results."""
    state = AppState()
    mock_results = [{"id": 1}, {"id": 2}, {"id": 3}]
    state.set_results(mock_results, total_count=3)

    state.select_next()
    assert state.selected_index == 1

    state.select_next()
    assert state.selected_index == 2

    state.select_next()  # Should not go beyond end
    assert state.selected_index == 2

    state.select_previous()
    assert state.selected_index == 1


def test_pagination():
    """Test pagination operations."""
    state = AppState()
    state.set_results([1, 2, 3], total_count=300)

    assert state.pagination.total_pages == 3
    assert state.pagination.current_page == 0

    state.next_page()
    assert state.pagination.current_page == 1

    state.previous_page()
    assert state.pagination.current_page == 0


def test_filters():
    """Test filter operations."""
    state = AppState()

    assert not state.filters.is_filtered()

    filters = FilterState(min_rating=3.0)
    state.set_filters(filters)

    assert state.filters.is_filtered()
    assert state.filters.min_rating == 3.0

    state.reset_filters()
    assert not state.filters.is_filtered()


def test_loading_state():
    """Test loading state management."""
    state = AppState()

    state.set_loading(True, "Searching...")
    assert state.is_loading is True
    assert state.status_message == "Searching..."

    state.set_loading(False)
    assert state.is_loading is False
    assert state.status_message is None


def test_error_state():
    """Test error state management."""
    state = AppState()

    state.set_error("Connection failed")
    assert state.error_message == "Connection failed"

    state.set_error(None)
    assert state.error_message is None


def test_reset():
    """Test resetting state."""
    state = AppState()

    # Modify state
    state.set_query("test")
    state.set_results([1, 2, 3], total_count=3)
    state.set_error("error")

    # Reset
    state.reset()

    assert state.current_query == ""
    assert len(state.results) == 0
    assert state.error_message is None
    assert state.view_mode == ViewMode.SEARCH
```

### Test File: `tests/test_state/test_history.py`

```python
"""Tests for history management."""

import pytest
from tc_tui.state import SearchHistory, NavigationHistory, SearchHistoryEntry, NavigationHistoryEntry, SearchType, ViewMode


def test_search_history_add():
    """Test adding searches to history."""
    history = SearchHistory(max_size=10)

    entry1 = SearchHistoryEntry(query="test1", search_type=SearchType.INDICATORS, result_count=5)
    entry2 = SearchHistoryEntry(query="test2", search_type=SearchType.GROUPS, result_count=10)

    history.add(entry1)
    history.add(entry2)

    assert len(history.get_all()) == 2


def test_search_history_no_duplicates():
    """Test that consecutive duplicate searches are not added."""
    history = SearchHistory(max_size=10)

    entry1 = SearchHistoryEntry(query="test", search_type=SearchType.INDICATORS, result_count=5)
    entry2 = SearchHistoryEntry(query="test", search_type=SearchType.INDICATORS, result_count=5)

    history.add(entry1)
    history.add(entry2)

    assert len(history.get_all()) == 1


def test_search_history_navigation():
    """Test navigating through search history."""
    history = SearchHistory(max_size=10)

    for i in range(5):
        entry = SearchHistoryEntry(query=f"test{i}", search_type=SearchType.INDICATORS, result_count=i)
        history.add(entry)

    # Navigate backward
    prev = history.get_previous()
    assert prev.query == "test3"

    prev = history.get_previous()
    assert prev.query == "test2"

    # Navigate forward
    next_entry = history.get_next()
    assert next_entry.query == "test3"


def test_navigation_history_push():
    """Test pushing navigation entries."""
    history = NavigationHistory(max_size=10)

    entry1 = NavigationHistoryEntry(view_mode=ViewMode.RESULTS)
    entry2 = NavigationHistoryEntry(view_mode=ViewMode.DETAIL, item_id=123, item_type="Indicator")

    history.push(entry1)
    history.push(entry2)

    assert history.current().view_mode == ViewMode.DETAIL


def test_navigation_history_back_forward():
    """Test back/forward navigation."""
    history = NavigationHistory(max_size=10)

    entry1 = NavigationHistoryEntry(view_mode=ViewMode.SEARCH)
    entry2 = NavigationHistoryEntry(view_mode=ViewMode.RESULTS)
    entry3 = NavigationHistoryEntry(view_mode=ViewMode.DETAIL)

    history.push(entry1)
    history.push(entry2)
    history.push(entry3)

    assert history.can_go_back()
    assert not history.can_go_forward()

    back = history.go_back()
    assert back.view_mode == ViewMode.RESULTS

    assert history.can_go_forward()
    forward = history.go_forward()
    assert forward.view_mode == ViewMode.DETAIL


def test_navigation_history_clear_forward():
    """Test that pushing clears forward history."""
    history = NavigationHistory(max_size=10)

    for i in range(5):
        entry = NavigationHistoryEntry(view_mode=ViewMode.SEARCH)
        history.push(entry)

    # Go back twice
    history.go_back()
    history.go_back()

    # Push new entry should clear forward history
    new_entry = NavigationHistoryEntry(view_mode=ViewMode.DETAIL)
    history.push(new_entry)

    assert not history.can_go_forward()
```

## Acceptance Criteria

- [ ] All files created in `tc_tui/state/`
- [ ] State manager uses Textual's reactive system
- [ ] All state operations work correctly
- [ ] Search and navigation history implemented
- [ ] Filter state management works
- [ ] Pagination state tracks correctly
- [ ] All tests passing with >80% coverage
- [ ] Type hints on all public methods
- [ ] Docstrings complete

## Integration Notes

### Dependencies
- **Package 1 (Data Models)**: Uses Indicator, Group, SearchResult models

### Provides For
- **Package 7 (Widgets)**: All widgets will watch reactive state variables
- **Package 8 (Screens)**: Screens will compose widgets and manage state
- **Package 9 (Main App)**: App will instantiate AppState and pass to screens

### Usage Example

```python
from textual.app import App
from tc_tui.state import AppState, ViewMode

class ThreatConnectApp(App):
    def __init__(self):
        super().__init__()
        self.state = AppState()

    def on_mount(self):
        # Watch state changes
        self.watch(self.state, "view_mode", self.on_view_mode_changed)
        self.watch(self.state, "results", self.on_results_changed)

    def on_view_mode_changed(self, view_mode: ViewMode):
        """Handle view mode changes."""
        if view_mode == ViewMode.RESULTS:
            self.show_results_screen()
        elif view_mode == ViewMode.DETAIL:
            self.show_detail_screen()
```

## Notes

- The AppState extends Widget but doesn't render anything - it's purely for state management
- Textual's reactive system automatically notifies watchers when state changes
- History management is separate from reactive state for performance
- All state changes should go through AppState methods, not direct assignment
- State should be the single source of truth for the entire UI

## Time Estimate

- Models: 1 hour
- History management: 1.5 hours
- State manager: 2 hours
- Tests: 1 hour
- Documentation: 0.5 hours

**Total: 4-5 hours**
