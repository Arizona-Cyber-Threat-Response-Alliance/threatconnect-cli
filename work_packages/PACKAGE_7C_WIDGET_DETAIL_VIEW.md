# Work Package 7c: DetailView Widget

**Module**: `tc_tui/widgets/detail_view.py`
**Priority**: Medium (UI Component)
**Estimated Time**: 4-5 hours
**Dependencies**: Package 1 (Data Models), Package 4 (Utilities), Package 6 (State)
**Can Start**: After Packages 1, 4, and 6 complete
**Assignable To**: Any agent with Python/Textual experience

## Objective

Create a detail view widget to display comprehensive information about a selected Indicator or Group, including metadata, tags, attributes, and associations. Support expandable sections and keyboard navigation.

## Deliverables

### Files to Create/Update

```
tc_tui/widgets/
├── __init__.py          # Update with DetailView export
└── detail_view.py       # Detail view widget
```

### 1. `tc_tui/widgets/detail_view.py`

```python
"""Detail view widget for displaying item details."""

from typing import Any, List, Optional, Union
from textual.app import ComposeResult
from textual.widgets import Static, Label, Rule
from textual.containers import Container, Vertical, Horizontal, ScrollableContainer
from textual.message import Message
from textual.reactive import Reactive

from tc_tui.models import Indicator, Group, Tag, Attribute
from tc_tui.utils import Icons, Formatters


class DetailView(ScrollableContainer):
    """Detail view widget for Indicators and Groups.

    Displays comprehensive information including:
    - Basic metadata
    - Description
    - Tags
    - Attributes
    - Associations (if loaded)

    Emits messages for association navigation.
    """

    DEFAULT_CSS = """
    DetailView {
        height: 1fr;
        border: solid $primary;
        padding: 1 2;
    }

    DetailView > .detail-header {
        height: auto;
        margin-bottom: 1;
        padding: 1;
        background: $surface;
    }

    DetailView > .detail-title {
        text-style: bold;
        color: $accent;
        text-align: center;
    }

    DetailView > .detail-section {
        height: auto;
        margin-top: 1;
        margin-bottom: 1;
    }

    DetailView > .detail-section > .section-title {
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }

    DetailView > .detail-section > .section-content {
        padding-left: 2;
    }

    DetailView > .detail-field {
        height: auto;
        margin-bottom: 0;
    }

    DetailView > .detail-field > .field-label {
        color: $text-muted;
        width: 20;
    }

    DetailView > .detail-field > .field-value {
        color: $text;
    }

    DetailView > .tag-container {
        height: auto;
        margin-top: 1;
    }

    DetailView > .tag {
        background: $primary 30%;
        color: $text;
        padding: 0 1;
        margin-right: 1;
    }

    DetailView > .association-item {
        height: auto;
        margin-bottom: 0;
        padding: 0 1;
    }

    DetailView > .association-item:hover {
        background: $accent 20%;
    }

    DetailView > .no-data {
        color: $text-muted;
        text-style: italic;
    }
    """

    # Reactive properties
    item_type: Reactive[str] = Reactive("")  # "Indicator" or "Group"
    has_associations: Reactive[bool] = Reactive(False)

    class AssociationSelected(Message):
        """Message emitted when an association is selected."""

        def __init__(
            self,
            item_id: int,
            item_type: str
        ) -> None:
            """Initialize message.

            Args:
                item_id: ID of the associated item
                item_type: Type of item ("Indicator" or "Group")
            """
            super().__init__()
            self.item_id = item_id
            self.item_type = item_type

    def __init__(self, id: str = "detail-view") -> None:
        """Initialize detail view widget.

        Args:
            id: Widget ID
        """
        super().__init__(id=id)
        self._current_item: Optional[Union[Indicator, Group]] = None
        self._associations: List[Any] = []

    def compose(self) -> ComposeResult:
        """Compose the detail view widget."""
        yield Static("No item selected", classes="no-data", id="detail-placeholder")

    def show_indicator(self, indicator: Indicator) -> None:
        """Display indicator details.

        Args:
            indicator: Indicator to display
        """
        self._current_item = indicator
        self.item_type = "Indicator"

        # Clear existing content
        self.remove_children()

        # Build detail view
        with Vertical():
            # Header with icon and summary
            with Container(classes="detail-header"):
                icon = Icons.get_indicator_icon(indicator.type)
                yield Static(
                    f"{icon} {indicator.type}: {indicator.summary}",
                    classes="detail-title"
                )

            # Basic Information Section
            yield self._build_indicator_basic_info(indicator)

            # Description Section (if present)
            if hasattr(indicator, 'description') and indicator.description:
                yield self._build_description_section(indicator.description)

            # Tags Section (if present)
            if hasattr(indicator, 'tags') and indicator.tags:
                yield self._build_tags_section(indicator.tags)

            # Attributes Section (if present)
            if hasattr(indicator, 'attributes') and indicator.attributes:
                yield self._build_attributes_section(indicator.attributes)

            # Associations Section (if loaded)
            if self.has_associations and self._associations:
                yield self._build_associations_section()

    def show_group(self, group: Group) -> None:
        """Display group details.

        Args:
            group: Group to display
        """
        self._current_item = group
        self.item_type = "Group"

        # Clear existing content
        self.remove_children()

        # Build detail view
        with Vertical():
            # Header with icon and name
            with Container(classes="detail-header"):
                icon = Icons.get_group_icon(group.type)
                yield Static(
                    f"{icon} {group.type}: {group.name}",
                    classes="detail-title"
                )

            # Basic Information Section
            yield self._build_group_basic_info(group)

            # Description Section (if present)
            if hasattr(group, 'description') and group.description:
                yield self._build_description_section(group.description)

            # Tags Section (if present)
            if hasattr(group, 'tags') and group.tags:
                yield self._build_tags_section(group.tags)

            # Attributes Section (if present)
            if hasattr(group, 'attributes') and group.attributes:
                yield self._build_attributes_section(group.attributes)

            # Associations Section (if loaded)
            if self.has_associations and self._associations:
                yield self._build_associations_section()

    def _build_indicator_basic_info(self, indicator: Indicator) -> Container:
        """Build basic information section for indicator.

        Args:
            indicator: Indicator data

        Returns:
            Container with basic info
        """
        with Container(classes="detail-section") as section:
            yield Static("Basic Information", classes="section-title")
            yield Rule()

            with Vertical(classes="section-content"):
                # Type
                yield self._build_field("Type:", indicator.type)

                # Summary
                yield self._build_field("Summary:", indicator.summary or "N/A")

                # Date Added
                date_added = Formatters.format_datetime(indicator.dateAdded)
                yield self._build_field("Date Added:", date_added)

                # Last Modified (if present)
                if hasattr(indicator, 'lastModified') and indicator.lastModified:
                    last_modified = Formatters.format_datetime(indicator.lastModified)
                    yield self._build_field("Last Modified:", last_modified)

                # Rating (if present)
                if hasattr(indicator, 'rating') and indicator.rating is not None:
                    rating = Formatters.format_rating(indicator.rating)
                    yield self._build_field("Rating:", rating)

                # Confidence (if present)
                if hasattr(indicator, 'confidence') and indicator.confidence is not None:
                    confidence = Formatters.format_confidence(indicator.confidence)
                    yield self._build_field("Confidence:", confidence)

                # Owner
                owner = indicator.ownerName if hasattr(indicator, 'ownerName') else "Unknown"
                yield self._build_field("Owner:", owner)

                # Active status (if present)
                if hasattr(indicator, 'active'):
                    status = "Yes" if indicator.active else "No"
                    yield self._build_field("Active:", status)

        return section

    def _build_group_basic_info(self, group: Group) -> Container:
        """Build basic information section for group.

        Args:
            group: Group data

        Returns:
            Container with basic info
        """
        with Container(classes="detail-section") as section:
            yield Static("Basic Information", classes="section-title")
            yield Rule()

            with Vertical(classes="section-content"):
                # Type
                yield self._build_field("Type:", group.type)

                # Name
                yield self._build_field("Name:", group.name or "N/A")

                # Date Added
                date_added = Formatters.format_datetime(group.dateAdded)
                yield self._build_field("Date Added:", date_added)

                # Last Modified (if present)
                if hasattr(group, 'lastModified') and group.lastModified:
                    last_modified = Formatters.format_datetime(group.lastModified)
                    yield self._build_field("Last Modified:", last_modified)

                # Owner
                owner = group.ownerName if hasattr(group, 'ownerName') else "Unknown"
                yield self._build_field("Owner:", owner)

                # Status (if present)
                if hasattr(group, 'status'):
                    yield self._build_field("Status:", group.status)

                # Event Date (for Events)
                if hasattr(group, 'eventDate') and group.eventDate:
                    event_date = Formatters.format_datetime(group.eventDate)
                    yield self._build_field("Event Date:", event_date)

        return section

    def _build_description_section(self, description: str) -> Container:
        """Build description section.

        Args:
            description: Description text

        Returns:
            Container with description
        """
        with Container(classes="detail-section") as section:
            yield Static("Description", classes="section-title")
            yield Rule()
            yield Static(description, classes="section-content")

        return section

    def _build_tags_section(self, tags: List[Tag]) -> Container:
        """Build tags section.

        Args:
            tags: List of tags

        Returns:
            Container with tags
        """
        with Container(classes="detail-section") as section:
            yield Static(f"Tags ({len(tags)})", classes="section-title")
            yield Rule()

            with Horizontal(classes="tag-container"):
                for tag in tags:
                    tag_name = tag.name if hasattr(tag, 'name') else str(tag)
                    yield Label(f"🏷️ {tag_name}", classes="tag")

        return section

    def _build_attributes_section(self, attributes: List[Attribute]) -> Container:
        """Build attributes section.

        Args:
            attributes: List of attributes

        Returns:
            Container with attributes
        """
        with Container(classes="detail-section") as section:
            yield Static(f"Attributes ({len(attributes)})", classes="section-title")
            yield Rule()

            with Vertical(classes="section-content"):
                for attr in attributes:
                    attr_type = attr.type if hasattr(attr, 'type') else "Unknown"
                    attr_value = attr.value if hasattr(attr, 'value') else str(attr)
                    yield self._build_field(f"📎 {attr_type}:", attr_value)

        return section

    def _build_associations_section(self) -> Container:
        """Build associations section.

        Returns:
            Container with associations
        """
        with Container(classes="detail-section") as section:
            yield Static(f"Associations ({len(self._associations)})", classes="section-title")
            yield Rule()

            with Vertical(classes="section-content"):
                for assoc in self._associations:
                    # Format association based on type
                    if hasattr(assoc, 'type'):
                        icon = Icons.get_indicator_icon(assoc.type) if hasattr(assoc, 'summary') else Icons.get_group_icon(assoc.type)
                        name = assoc.summary if hasattr(assoc, 'summary') else assoc.name
                        yield Label(
                            f"{icon} {assoc.type}: {name}",
                            classes="association-item"
                        )

        return section

    def _build_field(self, label: str, value: str) -> Horizontal:
        """Build a field row with label and value.

        Args:
            label: Field label
            value: Field value

        Returns:
            Horizontal container with label and value
        """
        with Horizontal(classes="detail-field") as field:
            yield Static(label, classes="field-label")
            yield Static(value, classes="field-value")

        return field

    def set_associations(self, associations: List[Any]) -> None:
        """Set associations to display.

        Args:
            associations: List of associated Indicators/Groups
        """
        self._associations = associations
        self.has_associations = len(associations) > 0

        # Refresh display if we have a current item
        if self._current_item:
            if self.item_type == "Indicator":
                self.show_indicator(self._current_item)
            else:
                self.show_group(self._current_item)

    def clear(self) -> None:
        """Clear detail view."""
        self._current_item = None
        self._associations = []
        self.has_associations = False
        self.item_type = ""

        self.remove_children()
        self.mount(Static("No item selected", classes="no-data", id="detail-placeholder"))

    def get_current_item(self) -> Optional[Union[Indicator, Group]]:
        """Get currently displayed item.

        Returns:
            Current item or None
        """
        return self._current_item
```

### 2. Update `tc_tui/widgets/__init__.py`

```python
"""TUI widgets module."""

from .search_input import SearchInput
from .results_table import ResultsTable
from .detail_view import DetailView

__all__ = [
    "SearchInput",
    "ResultsTable",
    "DetailView",
]
```

## Testing Requirements

### Test File: `tests/test_widgets/test_detail_view.py`

```python
"""Tests for detail view widget."""

import pytest
from textual.app import App

from tc_tui.widgets import DetailView
from tc_tui.models import Indicator, Group, Tag, Attribute


@pytest.fixture
def mock_indicator():
    """Create mock indicator for testing."""
    return Indicator(
        id=1,
        type="Address",
        summary="192.168.1.1",
        dateAdded="2024-01-01T00:00:00Z",
        lastModified="2024-01-15T00:00:00Z",
        ownerId=1,
        ownerName="TestOrg",
        rating=3.0,
        confidence=85,
        active=True,
        description="Known C2 server"
    )


@pytest.fixture
def mock_group():
    """Create mock group for testing."""
    return Group(
        id=1,
        type="Adversary",
        name="APT29",
        dateAdded="2024-01-01T00:00:00Z",
        lastModified="2024-01-15T00:00:00Z",
        ownerId=1,
        ownerName="TestOrg",
        status="Active",
        description="Advanced Persistent Threat group"
    )


@pytest.mark.asyncio
async def test_detail_view_initialization():
    """Test detail view initializes correctly."""
    widget = DetailView()

    assert widget.item_type == ""
    assert widget.has_associations is False


@pytest.mark.asyncio
async def test_show_indicator(mock_indicator):
    """Test displaying indicator details."""
    app = App()
    async with app.run_test() as pilot:
        widget = DetailView()
        await app.mount(widget)

        widget.show_indicator(mock_indicator)

        assert widget.item_type == "Indicator"
        assert widget.get_current_item() == mock_indicator


@pytest.mark.asyncio
async def test_show_group(mock_group):
    """Test displaying group details."""
    app = App()
    async with app.run_test() as pilot:
        widget = DetailView()
        await app.mount(widget)

        widget.show_group(mock_group)

        assert widget.item_type == "Group"
        assert widget.get_current_item() == mock_group


@pytest.mark.asyncio
async def test_clear_detail_view(mock_indicator):
    """Test clearing detail view."""
    app = App()
    async with app.run_test() as pilot:
        widget = DetailView()
        await app.mount(widget)

        widget.show_indicator(mock_indicator)
        assert widget.item_type == "Indicator"

        widget.clear()
        assert widget.item_type == ""
        assert widget.get_current_item() is None


@pytest.mark.asyncio
async def test_set_associations(mock_indicator):
    """Test setting associations."""
    app = App()
    async with app.run_test() as pilot:
        widget = DetailView()
        await app.mount(widget)

        widget.show_indicator(mock_indicator)

        # Set associations
        associations = [
            {"id": 2, "type": "Host", "summary": "evil.com"},
            {"id": 3, "type": "File", "summary": "malware.exe"}
        ]
        widget.set_associations(associations)

        assert widget.has_associations is True
        assert len(widget._associations) == 2


def test_build_field():
    """Test building field row."""
    widget = DetailView()

    field = widget._build_field("Test Label:", "Test Value")

    # Field should be created (Horizontal container)
    assert field is not None
```

## Acceptance Criteria

- [ ] DetailView widget created in `tc_tui/widgets/`
- [ ] Displays both Indicator and Group details correctly
- [ ] Shows all metadata fields (type, dates, rating, confidence, etc.)
- [ ] Description section displays when present
- [ ] Tags displayed with visual indicators
- [ ] Attributes displayed in organized format
- [ ] Associations displayed when loaded
- [ ] Scrollable container for long content
- [ ] AssociationSelected message emitted on association click
- [ ] All tests passing with >80% coverage
- [ ] Type hints on all public methods
- [ ] Docstrings complete

## Integration Notes

### Dependencies
- **Package 1 (Data Models)**: Uses Indicator, Group, Tag, Attribute models
- **Package 4 (Utilities)**: Uses Icons and Formatters
- **Package 6 (State)**: Will be connected to AppState in screens

### Provides For
- **Package 8 (Screens)**: Will be composed into main screen

### Usage Example

```python
from textual.app import App
from tc_tui.widgets import DetailView

class MyApp(App):
    def compose(self):
        yield DetailView()

    def on_mount(self):
        # Show indicator details
        detail_view = self.query_one(DetailView)
        detail_view.show_indicator(indicator)

    def on_detail_view_association_selected(self, message):
        """Handle association selection."""
        item_id = message.item_id
        item_type = message.item_type
        # Navigate to associated item...
```

## Notes

- Uses ScrollableContainer for handling long content
- Sections are built dynamically based on available data
- Empty sections not displayed
- Icons from Nerd Fonts for visual appeal
- Field labels right-padded for alignment
- Tags displayed as inline labels with icons
- Associations clickable for navigation (future enhancement)
- CSS can be customized by application
- Works within a terminal of minimum 80 columns wide

## Time Estimate

- Widget structure and layout: 1.5 hours
- Indicator detail building: 1 hour
- Group detail building: 1 hour
- Tags/Attributes sections: 0.5 hours
- Associations section: 0.5 hours
- Tests: 1 hour
- Documentation: 0.5 hours

**Total: 4-5 hours**
