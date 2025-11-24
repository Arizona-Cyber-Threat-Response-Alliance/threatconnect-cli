"""Tests for status bar widget."""

import pytest
from textual.app import App
from textual.widgets import Static

from tc_tui.widgets import StatusBar
from tc_tui.state import ViewMode


@pytest.mark.asyncio
async def test_status_bar_initialization():
    """Test status bar initializes correctly."""
    widget = StatusBar()

    assert widget.current_page == 0
    assert widget.total_pages == 0
    assert widget.total_results == 0
    assert widget.view_mode == ViewMode.SEARCH
    assert widget.is_loading is False


@pytest.mark.asyncio
async def test_set_pagination():
    """Test setting pagination information."""
    app = App()
    async with app.run_test() as pilot:
        widget = StatusBar()
        await app.mount(widget)

        widget.set_pagination(
            current_page=2,
            total_pages=10,
            total_results=500
        )

        assert widget.current_page == 2
        assert widget.total_pages == 10
        assert widget.total_results == 500


@pytest.mark.asyncio
async def test_set_loading():
    """Test setting loading state."""
    app = App()
    async with app.run_test() as pilot:
        widget = StatusBar()
        await app.mount(widget)

        widget.set_loading(True, "Searching...")
        assert widget.is_loading is True
        assert widget.status_message == "Searching..."

        widget.set_loading(False)
        assert widget.is_loading is False


@pytest.mark.asyncio
async def test_set_error():
    """Test setting error message."""
    app = App()
    async with app.run_test() as pilot:
        widget = StatusBar()
        await app.mount(widget)

        widget.set_error("Connection failed")
        assert widget.error_message == "Connection failed"

        widget.set_error(None)
        assert widget.error_message is None


@pytest.mark.asyncio
async def test_set_status():
    """Test setting status message."""
    app = App()
    async with app.run_test() as pilot:
        widget = StatusBar()
        await app.mount(widget)

        widget.set_status("Search completed")
        assert widget.status_message == "Search completed"


@pytest.mark.asyncio
async def test_clear_messages():
    """Test clearing all messages."""
    app = App()
    async with app.run_test() as pilot:
        widget = StatusBar()
        await app.mount(widget)

        widget.set_status("Test status")
        widget.set_error("Test error")
        widget.set_loading(True)

        widget.clear_messages()

        assert widget.status_message is None
        assert widget.error_message is None
        assert widget.is_loading is False


@pytest.mark.asyncio
async def test_view_mode_hints():
    """Test keyboard hints change with view mode."""
    app = App()
    async with app.run_test() as pilot:
        widget = StatusBar()
        await app.mount(widget)

        # Test each view mode
        widget.set_view_mode(ViewMode.SEARCH)
        hints = widget._get_keyboard_hints()
        assert "Search" in hints

        widget.set_view_mode(ViewMode.RESULTS)
        hints = widget._get_keyboard_hints()
        assert "Navigate" in hints

        widget.set_view_mode(ViewMode.DETAIL)
        hints = widget._get_keyboard_hints()
        assert "Back" in hints


@pytest.mark.asyncio
async def test_connection_status():
    """Test showing connection status."""
    app = App()
    async with app.run_test() as pilot:
        widget = StatusBar()
        await app.mount(widget)

        widget.show_connection_status(True, "test-instance")
        assert "Connected to test-instance" in widget.status_message

        widget.show_connection_status(False)
        assert widget.error_message == "Not connected"


def test_keyboard_hints_content():
    """Test keyboard hints for different view modes."""
    widget = StatusBar()

    # Search mode
    widget.view_mode = ViewMode.SEARCH
    hints = widget._get_keyboard_hints()
    assert "?" in hints  # Help
    assert "q" in hints  # Quit

    # Results mode
    widget.view_mode = ViewMode.RESULTS
    hints = widget._get_keyboard_hints()
    assert "↑" in hints or "Navigate" in hints
    assert "Enter" in hints

    # Detail mode
    widget.view_mode = ViewMode.DETAIL
    hints = widget._get_keyboard_hints()
    assert "Esc" in hints or "Back" in hints
