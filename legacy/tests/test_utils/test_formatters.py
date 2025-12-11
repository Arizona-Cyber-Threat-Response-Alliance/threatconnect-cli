"""Tests for formatters."""

import pytest
from datetime import datetime
from tc_tui.utils import Formatters
from rich.text import Text


def test_format_date_from_string():
    """Test date formatting from string."""
    date_str = "2024-01-15T14:32:10Z"
    result = Formatters.format_date(date_str)

    assert "January 15, 2024" in result


def test_format_date_from_datetime():
    """Test date formatting from datetime object."""
    date_obj = datetime(2024, 1, 15, 14, 32, 10)
    result = Formatters.format_date(date_obj)

    assert "January 15, 2024" in result


def test_format_date_invalid():
    """Test date formatting with invalid input."""
    result = Formatters.format_date(12345)
    assert result == "N/A"


def test_format_date_invalid_string():
    """Test date formatting with invalid date string."""
    result = Formatters.format_date("invalid-date")
    assert result == "invalid-date"


def test_format_rating():
    """Test rating formatting."""
    result = Formatters.format_rating(3.5)

    assert "⭐" in result
    assert "3.5" in result


def test_format_confidence():
    """Test confidence formatting."""
    result = Formatters.format_confidence(85)
    assert "85%" in result
    assert "🟡" in result


def test_format_file_size():
    """Test file size formatting."""
    assert Formatters.format_file_size(500) == "500 B"
    assert Formatters.format_file_size(1500) == "1.5 KB"
    assert Formatters.format_file_size(1500000) == "1.4 MB"
    assert Formatters.format_file_size(1500000000) == "1.4 GB"


def test_format_hash():
    """Test hash formatting."""
    long_hash = "5d41402abc4b2a76b9719d911017c592abcd1234"
    result = Formatters.format_hash(long_hash, 16)
    assert result == "5d41402abc4b2a76..."
    assert len(result) == 19  # 16 chars + "..."


def test_format_hash_short():
    """Test hash formatting with short hash."""
    short_hash = "5d41402a"
    result = Formatters.format_hash(short_hash, 16)
    assert result == short_hash  # Should not be truncated


def test_format_list():
    """Test list formatting."""
    items = ["item1", "item2", "item3"]
    result = Formatters.format_list(items, max_items=3)
    assert result == "item1, item2, item3"


def test_format_list_truncated():
    """Test list formatting with truncation."""
    items = ["item1", "item2", "item3", "item4", "item5"]
    result = Formatters.format_list(items, max_items=3)
    assert "item1, item2, item3" in result
    assert "2 more" in result


def test_format_list_empty():
    """Test list formatting with empty list."""
    result = Formatters.format_list([])
    assert result == "None"


def test_colorize_by_rating_critical():
    """Test colorize by rating - critical."""
    result = Formatters.colorize_by_rating("test", 4.5)
    assert isinstance(result, Text)
    assert str(result) == "test"


def test_colorize_by_rating_high():
    """Test colorize by rating - high."""
    result = Formatters.colorize_by_rating("test", 3.5)
    assert isinstance(result, Text)


def test_colorize_by_rating_medium():
    """Test colorize by rating - medium."""
    result = Formatters.colorize_by_rating("test", 2.5)
    assert isinstance(result, Text)


def test_colorize_by_rating_low():
    """Test colorize by rating - low."""
    result = Formatters.colorize_by_rating("test", 1.5)
    assert isinstance(result, Text)


def test_colorize_by_rating_none():
    """Test colorize by rating - no rating."""
    result = Formatters.colorize_by_rating("test", 0.5)
    assert isinstance(result, Text)


def test_colorize_by_confidence_high():
    """Test colorize by confidence - high."""
    result = Formatters.colorize_by_confidence("test", 95)
    assert isinstance(result, Text)


def test_colorize_by_confidence_medium():
    """Test colorize by confidence - medium."""
    result = Formatters.colorize_by_confidence("test", 75)
    assert isinstance(result, Text)


def test_colorize_by_confidence_low_medium():
    """Test colorize by confidence - low-medium."""
    result = Formatters.colorize_by_confidence("test", 55)
    assert isinstance(result, Text)


def test_colorize_by_confidence_low():
    """Test colorize by confidence - low."""
    result = Formatters.colorize_by_confidence("test", 30)
    assert isinstance(result, Text)


def test_truncate():
    """Test text truncation."""
    text = "This is a very long string that needs to be truncated"
    result = Formatters.truncate(text, 20)

    assert len(result) <= 20
    assert result.endswith("...")


def test_truncate_short_text():
    """Test truncate with text shorter than max length."""
    text = "short"
    result = Formatters.truncate(text, 20)
    assert result == text
