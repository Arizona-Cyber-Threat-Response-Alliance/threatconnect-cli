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


def test_clear_results():
    """Test clearing results."""
    state = AppState()
    state.set_results([1, 2, 3], total_count=3)

    state.clear_results()

    assert len(state.results) == 0
    assert state.selected_index == 0
    assert state.selected_item is None
    assert state.pagination.total_results == 0


def test_set_search_type():
    """Test setting search type."""
    state = AppState()

    state.set_search_type(SearchType.GROUPS)

    assert state.search_type == SearchType.GROUPS
    assert state.filters.search_type == SearchType.GROUPS


def test_view_mode():
    """Test setting view mode."""
    state = AppState()

    state.set_view_mode(ViewMode.RESULTS)
    assert state.view_mode == ViewMode.RESULTS

    state.set_view_mode(ViewMode.DETAIL)
    assert state.view_mode == ViewMode.DETAIL


def test_detail_view():
    """Test detail view operations."""
    state = AppState()
    mock_item = {"id": 123, "summary": "test"}

    state.show_detail(mock_item)

    assert state.detail_item == mock_item
    assert state.view_mode == ViewMode.DETAIL

    state.hide_detail()

    assert state.detail_item is None
    assert state.view_mode == ViewMode.RESULTS


def test_get_state_summary():
    """Test getting state summary."""
    state = AppState()
    state.set_query("test")
    state.set_results([1, 2, 3], total_count=3)

    summary = state.get_state_summary()

    assert summary["current_query"] == "test"
    assert summary["result_count"] == 3
    assert summary["current_page"] == 0
    assert summary["has_filters"] is False


def test_goto_page():
    """Test going to specific page."""
    state = AppState()
    state.set_results([1, 2, 3], total_count=300)

    state.goto_page(1)
    assert state.pagination.current_page == 1

    state.goto_page(2)
    assert state.pagination.current_page == 2

    # Invalid page should not change current page
    state.goto_page(100)
    assert state.pagination.current_page == 2
