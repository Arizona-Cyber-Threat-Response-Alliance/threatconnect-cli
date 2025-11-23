"""Tests for results table widget."""

import pytest
from datetime import datetime
from textual.widgets import DataTable

from tc_tui.widgets import ResultsTable
from tc_tui.models import Indicator, Group


@pytest.fixture
def mock_indicators():
    """Create mock indicators for testing."""
    return [
        Indicator(
            id=1,
            type="Address",
            summary="192.168.1.1",
            dateAdded="2024-01-01T00:00:00Z",
            lastModified="2024-01-01T00:00:00Z",
            ownerId=1,
            ownerName="TestOrg",
            webLink="https://example.com/1",
            rating=3.0,
            confidence=85
        ),
        Indicator(
            id=2,
            type="EmailAddress",
            summary="evil@bad.com",
            dateAdded="2024-01-02T00:00:00Z",
            lastModified="2024-01-02T00:00:00Z",
            ownerId=1,
            ownerName="TestOrg",
            webLink="https://example.com/2",
            rating=4.0,
            confidence=95
        ),
    ]


@pytest.fixture
def mock_groups():
    """Create mock groups for testing."""
    return [
        Group(
            id=1,
            type="Adversary",
            name="APT29",
            dateAdded="2024-01-01T00:00:00Z",
            lastModified="2024-01-01T00:00:00Z",
            ownerId=1,
            ownerName="TestOrg",
            webLink="https://example.com/1"
        ),
        Group(
            id=2,
            type="Campaign",
            name="Operation XYZ",
            dateAdded="2024-01-02T00:00:00Z",
            lastModified="2024-01-02T00:00:00Z",
            ownerId=1,
            ownerName="TestOrg",
            webLink="https://example.com/2"
        ),
    ]


def test_results_table_initialization():
    """Test results table initializes correctly."""
    widget = ResultsTable()

    assert widget.row_count == 0
    assert widget.selected_row == 0
    assert widget.result_type == "indicators"


def test_update_results_indicators(mock_indicators):
    """Test updating table with indicator results."""
    widget = ResultsTable()
    widget.update_results(mock_indicators, result_type="indicators")

    assert widget.row_count == 2
    assert len(widget._items) == 2
    assert widget.result_type == "indicators"


def test_update_results_groups(mock_groups):
    """Test updating table with group results."""
    widget = ResultsTable()
    widget.update_results(mock_groups, result_type="groups")

    assert widget.row_count == 2
    assert widget.result_type == "groups"


def test_clear_results(mock_indicators):
    """Test clearing results from table."""
    widget = ResultsTable()
    widget.update_results(mock_indicators, result_type="indicators")
    assert widget.row_count == 2

    widget.clear()
    assert widget.row_count == 0
    assert len(widget._items) == 0


def test_get_selected_item(mock_indicators):
    """Test getting selected item."""
    widget = ResultsTable()
    widget.update_results(mock_indicators, result_type="indicators")
    widget.selected_row = 1

    item = widget.get_selected_item()
    assert item is not None
    assert item.summary == "evil@bad.com"


def test_sort_by_column(mock_indicators):
    """Test sorting by column."""
    widget = ResultsTable()
    widget.update_results(mock_indicators, result_type="indicators")

    # Sort by type
    widget.sort_by_column("Type", reverse=False)

    # Verify sorting occurred
    assert widget._items[0].type == "Address"


def test_format_indicator_row(mock_indicators):
    """Test formatting indicator row."""
    widget = ResultsTable()
    widget.result_type = "indicators"

    row = widget._format_indicator_row(mock_indicators[0])

    assert len(row) == 7  # 7 columns
    assert row[1] == "Address"  # Type
    assert row[2] == "192.168.1.1"  # Summary


def test_format_group_row(mock_groups):
    """Test formatting group row."""
    widget = ResultsTable()
    widget.result_type = "groups"

    row = widget._format_group_row(mock_groups[0])

    assert len(row) == 6  # 6 columns
    assert row[1] == "Adversary"  # Type
    assert row[2] == "APT29"  # Name


def test_format_mixed_row_indicator(mock_indicators):
    """Test formatting mixed row for indicator."""
    widget = ResultsTable()
    widget.result_type = "mixed"

    row = widget._format_mixed_row(mock_indicators[0])

    assert len(row) == 6
    assert "Address" in row[1]  # Type
    assert row[2] == "192.168.1.1"  # Summary


def test_format_mixed_row_group(mock_groups):
    """Test formatting mixed row for group."""
    widget = ResultsTable()
    widget.result_type = "mixed"

    row = widget._format_mixed_row(mock_groups[0])

    assert len(row) == 6
    assert "Adversary" in row[1]  # Type
    assert row[2] == "APT29"  # Name


def test_get_selected_item_empty():
    """Test getting selected item when table is empty."""
    widget = ResultsTable()

    item = widget.get_selected_item()
    assert item is None


def test_get_selected_item_out_of_bounds(mock_indicators):
    """Test getting selected item with out of bounds index."""
    widget = ResultsTable()
    widget.update_results(mock_indicators, result_type="indicators")
    widget.selected_row = 999

    item = widget.get_selected_item()
    assert item is None


def test_sort_by_date_added(mock_indicators):
    """Test sorting by date added."""
    widget = ResultsTable()
    widget.update_results(mock_indicators, result_type="indicators")

    # Sort by date added (reverse to get newest first)
    widget.sort_by_column("Date Added", reverse=True)

    # Verify sorting occurred
    assert widget._items[0].summary == "evil@bad.com"  # Newer date


def test_sort_by_rating(mock_indicators):
    """Test sorting by rating."""
    widget = ResultsTable()
    widget.update_results(mock_indicators, result_type="indicators")

    # Sort by rating (reverse to get highest first)
    widget.sort_by_column("Rating", reverse=True)

    # Verify sorting occurred
    assert widget._items[0].rating == 4.0  # Higher rating


def test_sort_by_confidence(mock_indicators):
    """Test sorting by confidence."""
    widget = ResultsTable()
    widget.update_results(mock_indicators, result_type="indicators")

    # Sort by confidence (reverse to get highest first)
    widget.sort_by_column("Confidence", reverse=True)

    # Verify sorting occurred
    assert widget._items[0].confidence == 95  # Higher confidence
