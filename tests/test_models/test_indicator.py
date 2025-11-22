"""Tests for indicator models."""

import pytest
from datetime import datetime
from tc_tui.models import Indicator, IndicatorType


def test_indicator_creation():
    """Test creating an indicator."""
    data = {
        "id": 12345,
        "type": "Address",
        "summary": "192.168.1.1",
        "rating": 3.5,
        "confidence": 85,
        "dateAdded": "2024-01-15T14:32:10Z",
        "lastModified": "2025-11-22T09:15:43Z",
        "ownerName": "MyOrg",
        "ownerId": 1,
        "webLink": "https://example.threatconnect.com/...",
        "active": True
    }

    indicator = Indicator(**data)

    assert indicator.id == 12345
    assert indicator.type == "Address"
    assert indicator.summary == "192.168.1.1"
    assert indicator.rating == 3.5
    assert indicator.confidence == 85
    assert indicator.owner_name == "MyOrg"
    assert indicator.active is True


def test_indicator_rating_validation():
    """Test rating must be between 0 and 5."""
    data = {
        "id": 1,
        "type": "Address",
        "summary": "192.168.1.1",
        "rating": 6.0,  # Invalid
        "confidence": 50,
        "dateAdded": "2024-01-15T14:32:10Z",
        "lastModified": "2025-11-22T09:15:43Z",
        "ownerName": "MyOrg",
        "ownerId": 1,
        "webLink": "https://example.com"
    }

    with pytest.raises(ValueError, match="Rating must be between 0 and 5"):
        Indicator(**data)


def test_indicator_confidence_validation():
    """Test confidence must be between 0 and 100."""
    data = {
        "id": 1,
        "type": "Address",
        "summary": "192.168.1.1",
        "rating": 3.0,
        "confidence": 150,  # Invalid
        "dateAdded": "2024-01-15T14:32:10Z",
        "lastModified": "2025-11-22T09:15:43Z",
        "ownerName": "MyOrg",
        "ownerId": 1,
        "webLink": "https://example.com"
    }

    with pytest.raises(ValueError, match="Confidence must be between 0 and 100"):
        Indicator(**data)


def test_indicator_with_tags_and_attributes():
    """Test indicator with tags and attributes."""
    data = {
        "id": 1,
        "type": "Address",
        "summary": "192.168.1.1",
        "rating": 3.0,
        "confidence": 85,
        "dateAdded": "2024-01-15T14:32:10Z",
        "lastModified": "2025-11-22T09:15:43Z",
        "ownerName": "MyOrg",
        "ownerId": 1,
        "webLink": "https://example.com",
        "tags": [
            {"name": "malware"},
            {"name": "c2"}
        ],
        "attributes": [
            {
                "id": 1,
                "type": "Source",
                "value": "OSINT",
                "dateAdded": "2024-01-15T14:32:10Z",
                "lastModified": "2025-11-22T09:15:43Z"
            }
        ]
    }

    indicator = Indicator(**data)

    assert len(indicator.tags) == 2
    assert indicator.tags[0].name == "malware"
    assert len(indicator.attributes) == 1
    assert indicator.attributes[0].type == "Source"


def test_indicator_type_constants():
    """Test indicator type constants."""
    assert IndicatorType.ADDRESS == "Address"
    assert IndicatorType.EMAIL_ADDRESS == "EmailAddress"
    assert IndicatorType.FILE == "File"
    assert IndicatorType.HOST == "Host"
    assert IndicatorType.URL == "URL"


def test_indicator_with_file_hashes():
    """Test indicator with file hash fields."""
    data = {
        "id": 1,
        "type": "File",
        "summary": "malware.exe",
        "rating": 5.0,
        "confidence": 100,
        "dateAdded": "2024-01-15T14:32:10Z",
        "lastModified": "2025-11-22T09:15:43Z",
        "ownerName": "MyOrg",
        "ownerId": 1,
        "webLink": "https://example.com",
        "md5": "d41d8cd98f00b204e9800998ecf8427e",
        "sha1": "da39a3ee5e6b4b0d3255bfef95601890afd80709",
        "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "size": 1024
    }

    indicator = Indicator(**data)

    assert indicator.type == "File"
    assert indicator.md5 == "d41d8cd98f00b204e9800998ecf8427e"
    assert indicator.sha1 == "da39a3ee5e6b4b0d3255bfef95601890afd80709"
    assert indicator.sha256 == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    assert indicator.size == 1024


def test_indicator_field_aliases():
    """Test that field aliases work correctly."""
    data = {
        "id": 1,
        "type": "Address",
        "summary": "192.168.1.1",
        "rating": 3.0,
        "confidence": 85,
        "dateAdded": "2024-01-15T14:32:10Z",  # API format
        "lastModified": "2025-11-22T09:15:43Z",  # API format
        "ownerName": "MyOrg",  # API format
        "ownerId": 1,
        "webLink": "https://example.com"
    }

    indicator = Indicator(**data)

    # Should be accessible via Python snake_case names
    assert indicator.date_added is not None
    assert indicator.last_modified is not None
    assert indicator.owner_name == "MyOrg"
    assert indicator.owner_id == 1
    assert indicator.web_link == "https://example.com"
