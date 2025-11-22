"""Tests for formatters."""

import pytest
from datetime import datetime
from tc_tui.utils import Formatters


def test_format_date_from_string():
    """Test date formatting from string."""
    date_str = "2024-01-15T14:32:10Z"
    result = Formatters.format_date(date_str)

    assert "January 15, 2024" in result


def test_format_rating():
    """Test rating formatting."""
    result = Formatters.format_rating(3.5)

    assert "⭐" in result
    assert "3.5" in result


def test_format_file_size():
    """Test file size formatting."""
    assert Formatters.format_file_size(500) == "500 B"
    assert Formatters.format_file_size(1500) == "1.5 KB"
    assert Formatters.format_file_size(1500000) == "1.4 MB"


def test_truncate():
    """Test text truncation."""
    text = "This is a very long string that needs to be truncated"
    result = Formatters.truncate(text, 20)

    assert len(result) <= 20
    assert result.endswith("...")
