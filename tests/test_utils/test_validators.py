"""Tests for validators."""

import pytest
from tc_tui.utils import Validators


def test_is_ipv4():
    """Test IPv4 validation."""
    assert Validators.is_ipv4("192.168.1.1") is True
    assert Validators.is_ipv4("256.1.1.1") is False
    assert Validators.is_ipv4("not-an-ip") is False


def test_is_email():
    """Test email validation."""
    assert Validators.is_email("test@example.com") is True
    assert Validators.is_email("not-an-email") is False


def test_is_md5():
    """Test MD5 validation."""
    assert Validators.is_md5("5d41402abc4b2a76b9719d911017c592") is True
    assert Validators.is_md5("not-a-hash") is False


def test_detect_indicator_type():
    """Test indicator type detection."""
    assert Validators.detect_indicator_type("192.168.1.1") == "Address"
    assert Validators.detect_indicator_type("test@example.com") == "EmailAddress"
    assert Validators.detect_indicator_type("5d41402abc4b2a76b9719d911017c592") == "File"
    assert Validators.detect_indicator_type("example.com") == "Host"
