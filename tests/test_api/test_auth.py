"""Tests for HMAC authentication."""

import pytest
from tc_tui.api.auth import HMACAuth


def test_auth_header_generation():
    """Test HMAC signature generation."""
    auth = HMACAuth("test_id", "test_secret")

    auth_header, timestamp = auth.generate_auth_header(
        api_path="/api/v3/indicators",
        http_method="GET",
        timestamp="1234567890"
    )

    assert auth_header.startswith("TC test_id:")
    assert timestamp == "1234567890"


def test_auth_header_with_query_string():
    """Test HMAC signature with query string."""
    auth = HMACAuth("test_id", "test_secret")

    auth_header, timestamp = auth.generate_auth_header(
        api_path="/api/v3/indicators",
        http_method="GET",
        timestamp="1234567890",
        query_string="tql=typeName%20in%20%28%22Address%22%29"
    )

    assert auth_header.startswith("TC test_id:")
    assert ":" in auth_header  # Contains signature


def test_auth_header_auto_timestamp():
    """Test auth header generates timestamp automatically."""
    auth = HMACAuth("test_id", "test_secret")

    auth_header, timestamp = auth.generate_auth_header(
        api_path="/api/v3/indicators",
        http_method="GET"
    )

    assert auth_header.startswith("TC test_id:")
    assert timestamp is not None
    assert timestamp.isdigit()
    assert len(timestamp) == 10  # Unix timestamp


def test_auth_header_different_methods():
    """Test auth headers differ for different HTTP methods."""
    auth = HMACAuth("test_id", "test_secret")

    auth_get, _ = auth.generate_auth_header(
        api_path="/api/v3/indicators",
        http_method="GET",
        timestamp="1234567890"
    )

    auth_post, _ = auth.generate_auth_header(
        api_path="/api/v3/indicators",
        http_method="POST",
        timestamp="1234567890"
    )

    # Different methods should produce different signatures
    assert auth_get != auth_post
