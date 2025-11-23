# Work Package 7b: ResultsTable Widget

**Module**: `tc_tui/widgets/results_table.py`
**Priority**: Medium (UI Component)
**Estimated Time**: 4-5 hours
**Dependencies**: Package 1 (Data Models), Package 4 (Utilities), Package 6 (State)
**Can Start**: After Packages 1, 4, and 6 complete
**Assignable To**: Any agent with Python/Textual experience

## Objective

Create a results table widget using Textual's DataTable to display search results (Indicators and Groups) with sorting, selection, and visual styling. Support keyboard navigation, column sorting, and highlighting of selected rows.

## Deliverables

### Files to Create/Update

```
tc_tui/widgets/
├── __init__.py          # Update with ResultsTable export
└── results_table.py     # Results table widget
```

### 1. `tc_tui/widgets/results_table.py`

```python
"""Results table widget for displaying search results."""

from typing import Any, List, Optional, Union
from textual.app import ComposeResult
from textual.widgets import DataTable, Static
from textual.message import Message
from textual.reactive import Reactive
from textual.containers import Container

from tc_tui.models import Indicator, Group
from tc_tui.utils import Icons, Formatters


class ResultsTable(Container):
    """Table widget for displaying search results.

    Supports both Indicators and Groups with appropriate columns.
    Emits RowSelected message when a row is selected.
    """

    DEFAULT_CSS = """
    ResultsTable {
        height: 1fr;
        border: solid $primary;
    }

    ResultsTable > .results-header {
        height: 1;
        background: $surface;
        color: $text;
        padding: 0 1;
        text-style: bold;
    }

    ResultsTable > DataTable {
        height: 1fr;
    }

    ResultsTable > DataTable:focus {
        border: solid $accent;
    }

    ResultsTable > DataTable > .datatable--cursor {
        background: $accent 20%;
    }

    ResultsTable > DataTable > .datatable--header {
        text-style: bold;
        background: $surface;
    }

    /* Rating-based row coloring */
    ResultsTable .rating-high {
        color: $error;
    }

    ResultsTable .rating-medium {
        color: $warning;
    }

    ResultsTable .rating-low {
        color: $success;
    }
    """

    # Reactive properties
    row_count: Reactive[int] = Reactive(0)
    selected_row: Reactive[int] = Reactive(0)
    result_type: Reactive[str] = Reactive("indicators")  # "indicators", "groups", or "mixed"

    class RowSelected(Message):
        """Message emitted when a row is selected."""

        def __init__(self, row_index: int, item: Union[Indicator, Group]) -> None:
            """Initialize message.

            Args:
                row_index: Index of selected row
                item: The selected Indicator or Group
            """
            super().__init__()
            self.row_index = row_index
            self.item = item

    class RowActivated(Message):
        """Message emitted when a row is activated (Enter key)."""

        def __init__(self, row_index: int, item: Union[Indicator, Group]) -> None:
            """Initialize message.

            Args:
                row_index: Index of activated row
                item: The activated Indicator or Group
            """
            super().__init__()
            self.row_index = row_index
            self.item = item

    def __init__(self, id: str = "results-table") -> None:
        """Initialize results table widget.

        Args:
            id: Widget ID
        """
        super().__init__(id=id)
        self._items: List[Union[Indicator, Group]] = []
        self._sort_column: Optional[str] = None
        self._sort_reverse: bool = False

    def compose(self) -> ComposeResult:
        """Compose the results table widget."""
        yield Static("Results (0)", classes="results-header", id="results-header")
        yield DataTable(id="results-datatable", cursor_type="row", zebra_stripes=True)

    def on_mount(self) -> None:
        """Handle widget mount."""
        table = self.query_one("#results-datatable", DataTable)
        table.focus()

        # Set up default columns for indicators
        self._setup_indicator_columns()

    def _setup_indicator_columns(self) -> None:
        """Set up columns for indicator results."""
        table = self.query_one("#results-datatable", DataTable)
        table.clear(columns=True)

        table.add_column("", width=3)  # Icon
        table.add_column("Type", width=15)
        table.add_column("Summary", width=40)
        table.add_column("Rating", width=10)
        table.add_column("Confidence", width=12)
        table.add_column("Date Added", width=20)
        table.add_column("Owner", width=20)

    def _setup_group_columns(self) -> None:
        """Set up columns for group results."""
        table = self.query_one("#results-datatable", DataTable)
        table.clear(columns=True)

        table.add_column("", width=3)  # Icon
        table.add_column("Type", width=15)
        table.add_column("Name", width=40)
        table.add_column("Date Added", width=20)
        table.add_column("Owner", width=20)
        table.add_column("Status", width=15)

    def _setup_mixed_columns(self) -> None:
        """Set up columns for mixed indicator/group results."""
        table = self.query_one("#results-datatable", DataTable)
        table.clear(columns=True)

        table.add_column("", width=3)  # Icon
        table.add_column("Type", width=15)
        table.add_column("Summary/Name", width=40)
        table.add_column("Rating/Status", width=15)
        table.add_column("Date Added", width=20)
        table.add_column("Owner", width=20)

    def update_results(
        self,
        items: List[Union[Indicator, Group]],
        result_type: str = "indicators"
    ) -> None:
        """Update table with new results.

        Args:
            items: List of indicators or groups
            result_type: Type of results ("indicators", "groups", or "mixed")
        """
        self._items = items
        self.result_type = result_type
        self.row_count = len(items)

        # Update header
        header = self.query_one("#results-header", Static)
        header.update(f"Results ({len(items)})")

        # Set up appropriate columns
        if result_type == "indicators":
            self._setup_indicator_columns()
        elif result_type == "groups":
            self._setup_group_columns()
        else:
            self._setup_mixed_columns()

        # Populate table
        self._populate_table()

    def _populate_table(self) -> None:
        """Populate table with current items."""
        table = self.query_one("#results-datatable", DataTable)
        table.clear()

        for item in self._items:
            if self.result_type == "indicators":
                row = self._format_indicator_row(item)
            elif self.result_type == "groups":
                row = self._format_group_row(item)
            else:
                row = self._format_mixed_row(item)

            table.add_row(*row)

    def _format_indicator_row(self, indicator: Indicator) -> List[str]:
        """Format indicator data for table row.

        Args:
            indicator: Indicator to format

        Returns:
            List of formatted cell values
        """
        icon = Icons.get_indicator_icon(indicator.type)
        type_name = indicator.type
        summary = indicator.summary or ""

        # Format rating with stars
        rating = Formatters.format_rating(
            indicator.rating if hasattr(indicator, 'rating') else None
        )

        # Format confidence as percentage
        confidence = Formatters.format_confidence(
            indicator.confidence if hasattr(indicator, 'confidence') else None
        )

        # Format date
        date_added = Formatters.format_datetime(indicator.dateAdded)

        # Owner name
        owner = indicator.ownerName if hasattr(indicator, 'ownerName') else ""

        return [icon, type_name, summary, rating, confidence, date_added, owner]

    def _format_group_row(self, group: Group) -> List[str]:
        """Format group data for table row.

        Args:
            group: Group to format

        Returns:
            List of formatted cell values
        """
        icon = Icons.get_group_icon(group.type)
        type_name = group.type
        name = group.name or ""

        # Format date
        date_added = Formatters.format_datetime(group.dateAdded)

        # Owner name
        owner = group.ownerName if hasattr(group, 'ownerName') else ""

        # Status
        status = group.status if hasattr(group, 'status') else "Active"

        return [icon, type_name, name, date_added, owner, status]

    def _format_mixed_row(self, item: Union[Indicator, Group]) -> List[str]:
        """Format mixed indicator/group data for table row.

        Args:
            item: Indicator or Group to format

        Returns:
            List of formatted cell values
        """
        is_indicator = hasattr(item, 'summary')

        if is_indicator:
            icon = Icons.get_indicator_icon(item.type)
            type_name = f"📊 {item.type}"
            summary = item.summary or ""
            rating_status = Formatters.format_rating(
                item.rating if hasattr(item, 'rating') else None
            )
        else:
            icon = Icons.get_group_icon(item.type)
            type_name = f"📁 {item.type}"
            summary = item.name or ""
            rating_status = item.status if hasattr(item, 'status') else "Active"

        date_added = Formatters.format_datetime(item.dateAdded)
        owner = item.ownerName if hasattr(item, 'ownerName') else ""

        return [icon, type_name, summary, rating_status, date_added, owner]

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection in data table.

        Args:
            event: Row selected event
        """
        if event.cursor_row < len(self._items):
            self.selected_row = event.cursor_row
            item = self._items[event.cursor_row]
            self.post_message(self.RowSelected(event.cursor_row, item))

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        """Handle row highlighting in data table.

        Args:
            event: Row highlighted event
        """
        if event.cursor_row < len(self._items):
            self.selected_row = event.cursor_row
            item = self._items[event.cursor_row]
            # Don't post RowSelected on highlight, only on actual selection

    def on_key(self, event) -> None:
        """Handle key events.

        Args:
            event: Key event
        """
        table = self.query_one("#results-datatable", DataTable)

        if event.key == "enter":
            # Activate current row
            if self.selected_row < len(self._items):
                item = self._items[self.selected_row]
                self.post_message(self.RowActivated(self.selected_row, item))
                event.prevent_default()

        elif event.key == "g":
            # Jump to top
            table.cursor_coordinate = (0, 0)
            event.prevent_default()

        elif event.key == "G":
            # Jump to bottom
            if self.row_count > 0:
                table.cursor_coordinate = (self.row_count - 1, 0)
            event.prevent_default()

    def get_selected_item(self) -> Optional[Union[Indicator, Group]]:
        """Get currently selected item.

        Returns:
            Selected item or None
        """
        if 0 <= self.selected_row < len(self._items):
            return self._items[self.selected_row]
        return None

    def clear(self) -> None:
        """Clear all results from table."""
        table = self.query_one("#results-datatable", DataTable)
        table.clear()
        self._items = []
        self.row_count = 0
        self.selected_row = 0

        header = self.query_one("#results-header", Static)
        header.update("Results (0)")

    def focus_table(self) -> None:
        """Focus the data table."""
        table = self.query_one("#results-datatable", DataTable)
        table.focus()

    def sort_by_column(self, column_name: str, reverse: bool = False) -> None:
        """Sort table by column.

        Args:
            column_name: Name of column to sort by
            reverse: Sort in reverse order
        """
        self._sort_column = column_name
        self._sort_reverse = reverse

        # Sort items based on column
        if column_name == "Type":
            self._items.sort(key=lambda x: x.type, reverse=reverse)
        elif column_name == "Summary" or column_name == "Name":
            self._items.sort(
                key=lambda x: getattr(x, 'summary', getattr(x, 'name', '')),
                reverse=reverse
            )
        elif column_name == "Date Added":
            self._items.sort(key=lambda x: x.dateAdded or "", reverse=reverse)
        elif column_name == "Rating":
            self._items.sort(
                key=lambda x: getattr(x, 'rating', 0) or 0,
                reverse=reverse
            )
        elif column_name == "Confidence":
            self._items.sort(
                key=lambda x: getattr(x, 'confidence', 0) or 0,
                reverse=reverse
            )

        # Repopulate table with sorted data
        self._populate_table()
```

### 2. Update `tc_tui/widgets/__init__.py`

```python
"""TUI widgets module."""

from .search_input import SearchInput
from .results_table import ResultsTable

__all__ = [
    "SearchInput",
    "ResultsTable",
]
```

## Testing Requirements

### Test File: `tests/test_widgets/test_results_table.py`

```python
"""Tests for results table widget."""

import pytest
from datetime import datetime
from textual.app import App
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
            ownerId=1,
            ownerName="TestOrg",
            rating=3.0,
            confidence=85
        ),
        Indicator(
            id=2,
            type="EmailAddress",
            summary="evil@bad.com",
            dateAdded="2024-01-02T00:00:00Z",
            ownerId=1,
            ownerName="TestOrg",
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
            ownerId=1,
            ownerName="TestOrg"
        ),
        Group(
            id=2,
            type="Campaign",
            name="Operation XYZ",
            dateAdded="2024-01-02T00:00:00Z",
            ownerId=1,
            ownerName="TestOrg"
        ),
    ]


@pytest.mark.asyncio
async def test_results_table_initialization():
    """Test results table initializes correctly."""
    widget = ResultsTable()

    assert widget.row_count == 0
    assert widget.selected_row == 0
    assert widget.result_type == "indicators"


@pytest.mark.asyncio
async def test_update_results_indicators(mock_indicators):
    """Test updating table with indicator results."""
    app = App()
    async with app.run_test() as pilot:
        widget = ResultsTable()
        await app.mount(widget)

        widget.update_results(mock_indicators, result_type="indicators")

        assert widget.row_count == 2
        assert len(widget._items) == 2
        assert widget.result_type == "indicators"


@pytest.mark.asyncio
async def test_update_results_groups(mock_groups):
    """Test updating table with group results."""
    app = App()
    async with app.run_test() as pilot:
        widget = ResultsTable()
        await app.mount(widget)

        widget.update_results(mock_groups, result_type="groups")

        assert widget.row_count == 2
        assert widget.result_type == "groups"


@pytest.mark.asyncio
async def test_clear_results(mock_indicators):
    """Test clearing results from table."""
    app = App()
    async with app.run_test() as pilot:
        widget = ResultsTable()
        await app.mount(widget)

        widget.update_results(mock_indicators, result_type="indicators")
        assert widget.row_count == 2

        widget.clear()
        assert widget.row_count == 0
        assert len(widget._items) == 0


@pytest.mark.asyncio
async def test_get_selected_item(mock_indicators):
    """Test getting selected item."""
    app = App()
    async with app.run_test() as pilot:
        widget = ResultsTable()
        await app.mount(widget)

        widget.update_results(mock_indicators, result_type="indicators")
        widget.selected_row = 1

        item = widget.get_selected_item()
        assert item is not None
        assert item.summary == "evil@bad.com"


@pytest.mark.asyncio
async def test_sort_by_column(mock_indicators):
    """Test sorting by column."""
    app = App()
    async with app.run_test() as pilot:
        widget = ResultsTable()
        await app.mount(widget)

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
```

## Acceptance Criteria

- [ ] ResultsTable widget created in `tc_tui/widgets/`
- [ ] DataTable component properly integrated
- [ ] Supports both Indicator and Group display
- [ ] Column sorting works correctly
- [ ] Row selection with keyboard navigation (↑/↓, g/G)
- [ ] RowSelected and RowActivated messages emitted
- [ ] Visual styling with rating-based colors
- [ ] Header shows result count
- [ ] All tests passing with >80% coverage
- [ ] Type hints on all public methods
- [ ] Docstrings complete

## Integration Notes

### Dependencies
- **Package 1 (Data Models)**: Uses Indicator and Group models
- **Package 4 (Utilities)**: Uses Icons and Formatters
- **Package 6 (State)**: Will be connected to AppState in screens

### Provides For
- **Package 8 (Screens)**: Will be composed into main screen

### Usage Example

```python
from textual.app import App
from tc_tui.widgets import ResultsTable

class MyApp(App):
    def compose(self):
        yield ResultsTable()

    def on_mount(self):
        # Update with search results
        table = self.query_one(ResultsTable)
        table.update_results(indicators, result_type="indicators")

    def on_results_table_row_activated(self, message):
        """Handle row activation (Enter key)."""
        item = message.item
        # Show detail view...
```

## Notes

- Table uses Textual's DataTable component for performance
- Zebra striping enabled for better readability
- Cursor type set to "row" for full row selection
- Icons from Nerd Fonts for visual indicators
- Rating-based color coding (high=red, medium=yellow, low=green)
- Sorting is in-memory, does not re-query API
- Mixed mode supports displaying both indicators and groups
- Column widths optimized for 120-column terminal

## Time Estimate

- Widget structure and columns: 1.5 hours
- Data formatting and display: 1.5 hours
- Keyboard navigation and events: 1 hour
- Sorting functionality: 0.5 hours
- Tests: 1 hour
- Documentation: 0.5 hours

**Total: 4-5 hours**
