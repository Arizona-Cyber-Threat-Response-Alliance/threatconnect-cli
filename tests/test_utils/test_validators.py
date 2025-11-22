"""Tests for validators."""

import pytest
from tc_tui.utils import Validators


def test_is_ipv4():
    """Test IPv4 validation."""
    assert Validators.is_ipv4("192.168.1.1") is True
    assert Validators.is_ipv4("256.1.1.1") is False
    assert Validators.is_ipv4("not-an-ip") is False


def test_is_ipv6():
    """Test IPv6 validation."""
    assert Validators.is_ipv6("2001:0db8:85a3:0000:0000:8a2e:0370:7334") is True
    assert Validators.is_ipv6("::1") is True
    assert Validators.is_ipv6("not-an-ipv6") is False


def test_is_email():
    """Test email validation."""
    assert Validators.is_email("test@example.com") is True
    assert Validators.is_email("not-an-email") is False


def test_is_url():
    """Test URL validation."""
    assert Validators.is_url("https://example.com") is True
    assert Validators.is_url("http://example.com/path") is True
    assert Validators.is_url("ftp://example.com") is True
    assert Validators.is_url("not-a-url") is False


def test_is_md5():
    """Test MD5 validation."""
    assert Validators.is_md5("5d41402abc4b2a76b9719d911017c592") is True
    assert Validators.is_md5("not-a-hash") is False


def test_is_sha1():
    """Test SHA1 validation."""
    assert Validators.is_sha1("356a192b7913b04c54574d18c28d46e6395428ab") is True
    assert Validators.is_sha1("not-a-hash") is False


def test_is_sha256():
    """Test SHA256 validation."""
    assert Validators.is_sha256("e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855") is True
    assert Validators.is_sha256("not-a-hash") is False


def test_is_host():
    """Test hostname validation."""
    assert Validators.is_host("example.com") is True
    assert Validators.is_host("sub.example.com") is True
    assert Validators.is_host("not@hostname") is False


def test_detect_indicator_type():
    """Test indicator type detection."""
    assert Validators.detect_indicator_type("192.168.1.1") == "Address"
    assert Validators.detect_indicator_type("test@example.com") == "EmailAddress"
    assert Validators.detect_indicator_type("5d41402abc4b2a76b9719d911017c592") == "File"
    assert Validators.detect_indicator_type("example.com") == "Host"


def test_detect_indicator_type_sha1():
    """Test SHA1 indicator type detection."""
    assert Validators.detect_indicator_type("356a192b7913b04c54574d18c28d46e6395428ab") == "File"


def test_detect_indicator_type_sha256():
    """Test SHA256 indicator type detection."""
    assert Validators.detect_indicator_type("e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855") == "File"


def test_detect_indicator_type_url():
    """Test URL indicator type detection."""
    assert Validators.detect_indicator_type("https://example.com") == "URL"


def test_detect_indicator_type_ipv6():
    """Test IPv6 indicator type detection."""
    assert Validators.detect_indicator_type("2001:0db8:85a3:0000:0000:8a2e:0370:7334") == "Address"


def test_detect_indicator_type_unknown():
    """Test unknown indicator type detection."""
    assert Validators.detect_indicator_type("random-text-123") is None


def test_is_tql_query():
    """Test TQL query detection."""
    assert Validators.is_tql_query("typeName in ('Address')") is True
    assert Validators.is_tql_query("summary contains 'test'") is True
    assert Validators.is_tql_query("rating > 3") is True
    assert Validators.is_tql_query("confidence > 50 and rating > 2") is True
    assert Validators.is_tql_query("dateAdded > '2024-01-01'") is True
    assert Validators.is_tql_query("simple search term") is False
