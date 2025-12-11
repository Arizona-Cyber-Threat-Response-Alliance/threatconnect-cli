"""Main application state manager."""

from typing import Optional, List, Any, Dict
from textual.reactive import Reactive
from textual.app import ComposeResult
from textual.widget import Widget

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
            new_pagination.has_next_page = (
                new_pagination.current_page < new_pagination.total_pages - 1
            )
            new_pagination.has_previous_page = new_pagination.current_page > 0
            self.pagination = new_pagination

    def previous_page(self) -> None:
        """Move to previous page."""
        if self.pagination.has_previous_page:
            new_pagination = self.pagination.model_copy()
            new_pagination.current_page -= 1
            new_pagination.has_next_page = (
                new_pagination.current_page < new_pagination.total_pages - 1
            )
            new_pagination.has_previous_page = new_pagination.current_page > 0
            self.pagination = new_pagination

    def goto_page(self, page_number: int) -> None:
        """Go to a specific page.

        Args:
            page_number: Page number (0-indexed)
        """
        if 0 <= page_number < self.pagination.total_pages:
            new_pagination = self.pagination.model_copy()
            new_pagination.current_page = page_number
            new_pagination.has_next_page = (
                new_pagination.current_page < new_pagination.total_pages - 1
            )
            new_pagination.has_previous_page = new_pagination.current_page > 0
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
        # Handle both dict and object-like items
        item_id = item.get("id") if isinstance(item, dict) else getattr(item, "id", None)

        if item_id is not None:
            entry = NavigationHistoryEntry(
                view_mode=ViewMode.DETAIL,
                item_id=item_id,
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
        self.is_loading = False
        self.error_message = None
        self.status_message = None
        self.current_query = ""
        self.search_type = SearchType.INDICATORS
        self.clear_results()
        self.reset_filters()
        self.hide_detail()
        self.view_mode = ViewMode.SEARCH

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
