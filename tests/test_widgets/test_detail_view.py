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
        webLink="https://app.threatconnect.com/indicators/1",
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
        webLink="https://app.threatconnect.com/groups/1",
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
            type('obj', (object,), {'id': 2, 'type': 'Host', 'summary': 'evil.com'})(),
            type('obj', (object,), {'id': 3, 'type': 'File', 'summary': 'malware.exe'})()
        ]
        widget.set_associations(associations)

        assert widget.has_associations is True
        assert len(widget._associations) == 2


def test_build_field():
    """Test building field row."""
    widget = DetailView()

    # Build field creates a Static widget
    field = widget._build_field("Test Label:", "Test Value")

    # Field should be created (Static widget)
    assert field is not None
    # Verify it's the right type
    from textual.widgets import Static
    assert isinstance(field, Static)
