"""Tests for history management."""

import pytest
from tc_tui.state import (
    SearchHistory,
    NavigationHistory,
    SearchHistoryEntry,
    NavigationHistoryEntry,
    SearchType,
    ViewMode,
)


def test_search_history_add():
    """Test adding searches to history."""
    history = SearchHistory(max_size=10)

    entry1 = SearchHistoryEntry(
        query="test1", search_type=SearchType.INDICATORS, result_count=5
    )
    entry2 = SearchHistoryEntry(
        query="test2", search_type=SearchType.GROUPS, result_count=10
    )

    history.add(entry1)
    history.add(entry2)

    assert len(history.get_all()) == 2


def test_search_history_no_duplicates():
    """Test that consecutive duplicate searches are not added."""
    history = SearchHistory(max_size=10)

    entry1 = SearchHistoryEntry(
        query="test", search_type=SearchType.INDICATORS, result_count=5
    )
    entry2 = SearchHistoryEntry(
        query="test", search_type=SearchType.INDICATORS, result_count=5
    )

    history.add(entry1)
    history.add(entry2)

    assert len(history.get_all()) == 1


def test_search_history_navigation():
    """Test navigating through search history."""
    history = SearchHistory(max_size=10)

    for i in range(5):
        entry = SearchHistoryEntry(
            query=f"test{i}", search_type=SearchType.INDICATORS, result_count=i
        )
        history.add(entry)

    # Navigate backward
    prev = history.get_previous()
    assert prev.query == "test3"

    prev = history.get_previous()
    assert prev.query == "test2"

    # Navigate forward
    next_entry = history.get_next()
    assert next_entry.query == "test3"


def test_search_history_clear():
    """Test clearing search history."""
    history = SearchHistory(max_size=10)

    for i in range(5):
        entry = SearchHistoryEntry(
            query=f"test{i}", search_type=SearchType.INDICATORS, result_count=i
        )
        history.add(entry)

    assert len(history.get_all()) == 5

    history.clear()

    assert len(history.get_all()) == 0


def test_search_history_max_size():
    """Test that history respects max size."""
    history = SearchHistory(max_size=3)

    for i in range(5):
        entry = SearchHistoryEntry(
            query=f"test{i}", search_type=SearchType.INDICATORS, result_count=i
        )
        history.add(entry)

    # Should only have last 3 entries
    assert len(history.get_all()) == 3
    assert history.get_all()[0].query == "test2"


def test_navigation_history_push():
    """Test pushing navigation entries."""
    history = NavigationHistory(max_size=10)

    entry1 = NavigationHistoryEntry(view_mode=ViewMode.RESULTS)
    entry2 = NavigationHistoryEntry(
        view_mode=ViewMode.DETAIL, item_id=123, item_type="Indicator"
    )

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


def test_navigation_history_clear():
    """Test clearing navigation history."""
    history = NavigationHistory(max_size=10)

    for i in range(5):
        entry = NavigationHistoryEntry(view_mode=ViewMode.SEARCH)
        history.push(entry)

    history.clear()

    assert history.current() is None
    assert not history.can_go_back()
    assert not history.can_go_forward()


def test_navigation_history_max_size():
    """Test that navigation history respects max size."""
    history = NavigationHistory(max_size=3)

    for i in range(5):
        entry = NavigationHistoryEntry(view_mode=ViewMode.SEARCH)
        history.push(entry)

    # Current index should be at the end of maintained history
    assert history.can_go_back()
    history.go_back()
    history.go_back()
    # Should not be able to go back more than max_size - 1 times
    assert not history.can_go_back()


def test_search_history_boundary_conditions():
    """Test boundary conditions for search history navigation."""
    history = SearchHistory(max_size=10)

    # Empty history
    assert history.get_previous() is None
    assert history.get_next() is None

    # Single entry
    entry = SearchHistoryEntry(
        query="test", search_type=SearchType.INDICATORS, result_count=1
    )
    history.add(entry)

    assert history.get_previous() is None


def test_navigation_history_boundary_conditions():
    """Test boundary conditions for navigation history."""
    history = NavigationHistory(max_size=10)

    # Empty history
    assert not history.can_go_back()
    assert not history.can_go_forward()
    assert history.go_back() is None
    assert history.go_forward() is None

    # Single entry
    entry = NavigationHistoryEntry(view_mode=ViewMode.SEARCH)
    history.push(entry)

    assert not history.can_go_back()
    assert not history.can_go_forward()
