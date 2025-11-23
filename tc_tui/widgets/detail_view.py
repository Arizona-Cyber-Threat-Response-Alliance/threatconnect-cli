"""Detail view widget for displaying item details."""

from typing import Any, List, Optional, Union
from textual.app import ComposeResult
from textual.widgets import Static, Label, Rule
from textual.containers import Container, Vertical, Horizontal, ScrollableContainer
from textual.message import Message
from textual.reactive import Reactive

from tc_tui.models import Indicator, Group, Tag, Attribute
from tc_tui.utils import IconMapper, Formatters


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

    DetailView .detail-header {
        height: auto;
        margin-bottom: 1;
        padding: 1;
        background: $surface;
    }

    DetailView .detail-title {
        text-style: bold;
        color: $accent;
        text-align: center;
    }

    DetailView .detail-section {
        height: auto;
        margin-top: 1;
        margin-bottom: 1;
    }

    DetailView .section-title {
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }

    DetailView .section-content {
        padding-left: 2;
    }

    DetailView .detail-field {
        height: auto;
        margin-bottom: 0;
    }

    DetailView .field-label {
        color: $text-muted;
        width: 20;
    }

    DetailView .field-value {
        color: $text;
    }

    DetailView .tag-container {
        height: auto;
        margin-top: 1;
    }

    DetailView .tag {
        background: $primary 30%;
        color: $text;
        padding: 0 1;
        margin-right: 1;
    }

    DetailView .association-item {
        height: auto;
        margin-bottom: 0;
        padding: 0 1;
    }

    DetailView .association-item:hover {
        background: $accent 20%;
    }

    DetailView .no-data {
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

        # Build and mount all widgets
        icon = IconMapper.get_indicator_icon(indicator.type)
        self.mount(Static(
            f"{icon} {indicator.type}: {indicator.summary}",
            classes="detail-title"
        ))

        # Build basic info widgets
        for widget in self._build_indicator_basic_info(indicator):
            self.mount(widget)

        # Description Section (if present)
        if hasattr(indicator, 'description') and indicator.description:
            for widget in self._build_description_section(indicator.description):
                self.mount(widget)

        # Tags Section (if present)
        if hasattr(indicator, 'tags') and indicator.tags:
            for widget in self._build_tags_section(indicator.tags):
                self.mount(widget)

        # Attributes Section (if present)
        if hasattr(indicator, 'attributes') and indicator.attributes:
            for widget in self._build_attributes_section(indicator.attributes):
                self.mount(widget)

        # Associations Section (if loaded)
        if self.has_associations and self._associations:
            for widget in self._build_associations_section():
                self.mount(widget)

    def show_group(self, group: Group) -> None:
        """Display group details.

        Args:
            group: Group to display
        """
        self._current_item = group
        self.item_type = "Group"

        # Clear existing content
        self.remove_children()

        # Build and mount all widgets
        icon = IconMapper.get_group_icon(group.type)
        self.mount(Static(
            f"{icon} {group.type}: {group.name}",
            classes="detail-title"
        ))

        # Build basic info widgets
        for widget in self._build_group_basic_info(group):
            self.mount(widget)

        # Description Section (if present)
        if hasattr(group, 'description') and group.description:
            for widget in self._build_description_section(group.description):
                self.mount(widget)

        # Tags Section (if present)
        if hasattr(group, 'tags') and group.tags:
            for widget in self._build_tags_section(group.tags):
                self.mount(widget)

        # Attributes Section (if present)
        if hasattr(group, 'attributes') and group.attributes:
            for widget in self._build_attributes_section(group.attributes):
                self.mount(widget)

        # Associations Section (if loaded)
        if self.has_associations and self._associations:
            for widget in self._build_associations_section():
                self.mount(widget)

    def _build_indicator_basic_info(self, indicator: Indicator) -> List:
        """Build basic information section for indicator.

        Args:
            indicator: Indicator data

        Returns:
            List of widgets
        """
        widgets = []
        widgets.append(Static("Basic Information", classes="section-title"))
        widgets.append(Rule())

        # Type
        widgets.append(self._create_field("Type:", indicator.type))

        # Summary
        widgets.append(self._create_field("Summary:", indicator.summary or "N/A"))

        # Date Added
        date_added = Formatters.format_date(indicator.date_added)
        widgets.append(self._create_field("Date Added:", date_added))

        # Last Modified (if present)
        if hasattr(indicator, 'last_modified') and indicator.last_modified:
            last_modified = Formatters.format_date(indicator.last_modified)
            widgets.append(self._create_field("Last Modified:", last_modified))

        # Rating (if present)
        if hasattr(indicator, 'rating') and indicator.rating is not None:
            rating = Formatters.format_rating(indicator.rating)
            widgets.append(self._create_field("Rating:", rating))

        # Confidence (if present)
        if hasattr(indicator, 'confidence') and indicator.confidence is not None:
            confidence = Formatters.format_confidence(indicator.confidence)
            widgets.append(self._create_field("Confidence:", confidence))

        # Owner
        owner = indicator.owner_name if hasattr(indicator, 'owner_name') else "Unknown"
        widgets.append(self._create_field("Owner:", owner))

        # Active status (if present)
        if hasattr(indicator, 'active'):
            status = "Yes" if indicator.active else "No"
            widgets.append(self._create_field("Active:", status))

        return widgets

    def _build_group_basic_info(self, group: Group) -> List:
        """Build basic information section for group.

        Args:
            group: Group data

        Returns:
            List of widgets
        """
        widgets = []
        widgets.append(Static("Basic Information", classes="section-title"))
        widgets.append(Rule())

        # Type
        widgets.append(self._create_field("Type:", group.type))

        # Name
        widgets.append(self._create_field("Name:", group.name or "N/A"))

        # Date Added
        date_added = Formatters.format_date(group.date_added)
        widgets.append(self._create_field("Date Added:", date_added))

        # Last Modified (if present)
        if hasattr(group, 'last_modified') and group.last_modified:
            last_modified = Formatters.format_date(group.last_modified)
            widgets.append(self._create_field("Last Modified:", last_modified))

        # Owner
        owner = group.owner_name if hasattr(group, 'owner_name') else "Unknown"
        widgets.append(self._create_field("Owner:", owner))

        # Status (if present)
        if hasattr(group, 'status'):
            widgets.append(self._create_field("Status:", group.status))

        # Event Date (for Events)
        if hasattr(group, 'event_date') and group.event_date:
            event_date = Formatters.format_date(group.event_date)
            widgets.append(self._create_field("Event Date:", event_date))

        return widgets

    def _build_description_section(self, description: str) -> List:
        """Build description section.

        Args:
            description: Description text

        Returns:
            List of widgets
        """
        widgets = []
        widgets.append(Static("Description", classes="section-title"))
        widgets.append(Rule())
        widgets.append(Static(description, classes="section-content"))
        return widgets

    def _build_tags_section(self, tags: List[Tag]) -> List:
        """Build tags section.

        Args:
            tags: List of tags

        Returns:
            List of widgets
        """
        widgets = []
        widgets.append(Static(f"Tags ({len(tags)})", classes="section-title"))
        widgets.append(Rule())

        # Create horizontal container for tags
        tag_container = Horizontal(classes="tag-container")
        for tag in tags:
            tag_name = tag.name if hasattr(tag, 'name') else str(tag)
            # Create label and add to container's children before mounting
            label = Label(f"🏷️ {tag_name}", classes="tag")
            tag_container._nodes.append(label)

        widgets.append(tag_container)
        return widgets

    def _build_attributes_section(self, attributes: List[Attribute]) -> List:
        """Build attributes section.

        Args:
            attributes: List of attributes

        Returns:
            List of widgets
        """
        widgets = []
        widgets.append(Static(f"Attributes ({len(attributes)})", classes="section-title"))
        widgets.append(Rule())

        for attr in attributes:
            attr_type = attr.type if hasattr(attr, 'type') else "Unknown"
            attr_value = attr.value if hasattr(attr, 'value') else str(attr)
            widgets.append(self._create_field(f"📎 {attr_type}:", attr_value))

        return widgets

    def _build_associations_section(self) -> List:
        """Build associations section.

        Returns:
            List of widgets
        """
        widgets = []
        widgets.append(Static(f"Associations ({len(self._associations)})", classes="section-title"))
        widgets.append(Rule())

        for assoc in self._associations:
            # Format association based on type
            if hasattr(assoc, 'type'):
                icon = IconMapper.get_indicator_icon(assoc.type) if hasattr(assoc, 'summary') else IconMapper.get_group_icon(assoc.type)
                name = assoc.summary if hasattr(assoc, 'summary') else assoc.name
                widgets.append(Label(
                    f"{icon} {assoc.type}: {name}",
                    classes="association-item"
                ))

        return widgets

    def _create_field(self, label: str, value: str) -> Static:
        """Create a field row with label and value.

        Args:
            label: Field label
            value: Field value

        Returns:
            Static widget with formatted field
        """
        # Return a single Static widget with both label and value
        # Using padding to align them
        return Static(f"{label:20s} {value}", classes="detail-field")

    def _build_field(self, label: str, value: str) -> Static:
        """Build a field row with label and value (deprecated, use _create_field).

        Args:
            label: Field label
            value: Field value

        Returns:
            Static widget with field
        """
        return self._create_field(label, value)

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
        self.mount(Static("No item selected", classes="no-data"))

    def get_current_item(self) -> Optional[Union[Indicator, Group]]:
        """Get currently displayed item.

        Returns:
            Current item or None
        """
        return self._current_item
