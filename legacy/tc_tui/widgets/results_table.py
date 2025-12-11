"""Results table widget for displaying search results."""

from typing import Any, List, Optional, Union
from textual.app import ComposeResult
from textual.widgets import DataTable, Static
from textual.message import Message
from textual.reactive import Reactive
from textual.containers import Container

from tc_tui.models import Indicator, Group
from tc_tui.utils import IconMapper, Formatters


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
        try:
            table = self.query_one("#results-datatable", DataTable)
            table.clear(columns=True)

            table.add_column("", width=3)  # Icon
            table.add_column("Type", width=15)
            table.add_column("Summary", width=40)
            table.add_column("Rating", width=10)
            table.add_column("Confidence", width=12)
            table.add_column("Date Added", width=20)
            table.add_column("Owner", width=20)
        except Exception:
            # Widget not yet mounted
            pass

    def _setup_group_columns(self) -> None:
        """Set up columns for group results."""
        try:
            table = self.query_one("#results-datatable", DataTable)
            table.clear(columns=True)

            table.add_column("", width=3)  # Icon
            table.add_column("Type", width=15)
            table.add_column("Name", width=40)
            table.add_column("Date Added", width=20)
            table.add_column("Owner", width=20)
            table.add_column("Status", width=15)
        except Exception:
            # Widget not yet mounted
            pass

    def _setup_mixed_columns(self) -> None:
        """Set up columns for mixed indicator/group results."""
        try:
            table = self.query_one("#results-datatable", DataTable)
            table.clear(columns=True)

            table.add_column("", width=3)  # Icon
            table.add_column("Type", width=15)
            table.add_column("Summary/Name", width=40)
            table.add_column("Rating/Status", width=15)
            table.add_column("Date Added", width=20)
            table.add_column("Owner", width=20)
        except Exception:
            # Widget not yet mounted
            pass

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

        # Update header (if widget is mounted)
        try:
            header = self.query_one("#results-header", Static)
            header.update(f"Results ({len(items)})")
        except Exception:
            # Widget not yet mounted, skip header update
            pass

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
        try:
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
        except Exception:
            # Widget not yet mounted
            pass

    def _format_indicator_row(self, indicator: Indicator) -> List[str]:
        """Format indicator data for table row.

        Args:
            indicator: Indicator to format

        Returns:
            List of formatted cell values
        """
        icon = IconMapper.get_indicator_icon(indicator.type)
        type_name = indicator.type
        summary = indicator.summary or ""

        # Format rating with stars
        rating = Formatters.format_rating(
            indicator.rating if hasattr(indicator, 'rating') else 0.0
        )

        # Format confidence as percentage
        confidence = Formatters.format_confidence(
            indicator.confidence if hasattr(indicator, 'confidence') else 0
        )

        # Format date
        date_added = Formatters.format_date(indicator.date_added, "%Y-%m-%d %H:%M")

        # Owner name
        owner = indicator.owner_name if hasattr(indicator, 'owner_name') else ""

        return [icon, type_name, summary, rating, confidence, date_added, owner]

    def _format_group_row(self, group: Group) -> List[str]:
        """Format group data for table row.

        Args:
            group: Group to format

        Returns:
            List of formatted cell values
        """
        icon = IconMapper.get_group_icon(group.type)
        type_name = group.type
        name = group.name or ""

        # Format date
        date_added = Formatters.format_date(group.date_added, "%Y-%m-%d %H:%M")

        # Owner name
        owner = group.owner_name if hasattr(group, 'owner_name') else ""

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
            icon = IconMapper.get_indicator_icon(item.type)
            type_name = f"📊 {item.type}"
            summary = item.summary or ""
            rating_status = Formatters.format_rating(
                item.rating if hasattr(item, 'rating') else 0.0
            )
        else:
            icon = IconMapper.get_group_icon(item.type)
            type_name = f"📁 {item.type}"
            summary = item.name or ""
            rating_status = item.status if hasattr(item, 'status') else "Active"

        date_added = Formatters.format_date(item.date_added, "%Y-%m-%d %H:%M")
        owner = item.owner_name if hasattr(item, 'owner_name') else ""

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
        try:
            table = self.query_one("#results-datatable", DataTable)
            table.clear()
        except Exception:
            # Widget not yet mounted
            pass

        self._items = []
        self.row_count = 0
        self.selected_row = 0

        try:
            header = self.query_one("#results-header", Static)
            header.update("Results (0)")
        except Exception:
            # Widget not yet mounted
            pass

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
            self._items.sort(key=lambda x: x.date_added or "", reverse=reverse)
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
