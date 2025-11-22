"""Tests for icon mapping."""

import pytest
from tc_tui.utils import IconMapper


def test_get_indicator_icon():
    """Test indicator icon mapping."""
    assert IconMapper.get_indicator_icon("Address") == "🌐"
    assert IconMapper.get_indicator_icon("Host") == "🖥️"
    assert IconMapper.get_indicator_icon("EmailAddress") == "📧"
    assert IconMapper.get_indicator_icon("Unknown Type") == "❓"


def test_get_group_icon():
    """Test group icon mapping."""
    assert IconMapper.get_group_icon("Adversary") == "💀"
    assert IconMapper.get_group_icon("Campaign") == "🎯"
    assert IconMapper.get_group_icon("Incident") == "🚨"
    assert IconMapper.get_group_icon("Unknown Type") == "❓"


def test_get_rating_icon():
    """Test rating icon generation."""
    # Full rating
    result = IconMapper.get_rating_icon(5.0)
    assert result == "⭐⭐⭐⭐⭐"

    # Partial rating
    result = IconMapper.get_rating_icon(3.0)
    assert result == "⭐⭐⭐☆☆"

    # Zero rating
    result = IconMapper.get_rating_icon(0)
    assert result == "☆☆☆☆☆"


def test_get_active_icon():
    """Test active/inactive icon."""
    assert IconMapper.get_active_icon(True) == "✅"
    assert IconMapper.get_active_icon(False) == "❌"


def test_get_confidence_icon():
    """Test confidence level icons."""
    assert IconMapper.get_confidence_icon(95) == "🟢"  # High
    assert IconMapper.get_confidence_icon(75) == "🟡"  # Medium
    assert IconMapper.get_confidence_icon(55) == "🟠"  # Low-medium
    assert IconMapper.get_confidence_icon(30) == "🔴"  # Low
