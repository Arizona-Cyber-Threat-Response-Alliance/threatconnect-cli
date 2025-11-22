"""Tests for group models."""

import pytest
from datetime import datetime
from tc_tui.models import Group, GroupType


def test_group_creation():
    """Test creating a group."""
    data = {
        "id": 67890,
        "type": "Incident",
        "name": "Network Intrusion",
        "dateAdded": "2024-01-20T10:00:00Z",
        "lastModified": "2024-01-25T15:30:00Z",
        "ownerName": "MyOrganization",
        "ownerId": 1,
        "webLink": "https://example.com"
    }

    group = Group(**data)

    assert group.id == 67890
    assert group.type == "Incident"
    assert group.name == "Network Intrusion"
    assert group.owner_name == "MyOrganization"
    assert group.owner_id == 1


def test_group_with_event_fields():
    """Test group with event-specific fields."""
    data = {
        "id": 1,
        "type": "Event",
        "name": "Security Event",
        "dateAdded": "2024-01-20T10:00:00Z",
        "lastModified": "2024-01-25T15:30:00Z",
        "ownerName": "MyOrg",
        "ownerId": 1,
        "webLink": "https://example.com",
        "eventDate": "2024-01-18T00:00:00Z",
        "status": "Open"
    }

    group = Group(**data)

    assert group.type == "Event"
    assert group.event_date is not None
    assert group.status == "Open"


def test_group_with_document_fields():
    """Test group with document-specific fields."""
    data = {
        "id": 1,
        "type": "Document",
        "name": "Malware Analysis Report",
        "dateAdded": "2024-01-20T10:00:00Z",
        "lastModified": "2024-01-25T15:30:00Z",
        "ownerName": "MyOrg",
        "ownerId": 1,
        "webLink": "https://example.com",
        "fileName": "report.pdf",
        "fileSize": 1048576,
        "fileType": "PDF"
    }

    group = Group(**data)

    assert group.type == "Document"
    assert group.file_name == "report.pdf"
    assert group.file_size == 1048576
    assert group.file_type == "PDF"


def test_group_with_email_fields():
    """Test group with email-specific fields."""
    data = {
        "id": 1,
        "type": "Email",
        "name": "Phishing Email",
        "dateAdded": "2024-01-20T10:00:00Z",
        "lastModified": "2024-01-25T15:30:00Z",
        "ownerName": "MyOrg",
        "ownerId": 1,
        "webLink": "https://example.com",
        "subject": "Important Security Update",
        "from": "attacker@evil.com",
        "to": "victim@company.com",
        "header": "Received: from evil.com...",
        "body": "Click this link..."
    }

    group = Group(**data)

    assert group.type == "Email"
    assert group.subject == "Important Security Update"
    assert group.from_address == "attacker@evil.com"
    assert group.to_address == "victim@company.com"


def test_group_with_tags_and_attributes():
    """Test group with tags and attributes."""
    data = {
        "id": 1,
        "type": "Incident",
        "name": "Network Intrusion",
        "dateAdded": "2024-01-20T10:00:00Z",
        "lastModified": "2024-01-25T15:30:00Z",
        "ownerName": "MyOrg",
        "ownerId": 1,
        "webLink": "https://example.com",
        "tags": [
            {"name": "apt"},
            {"name": "intrusion"}
        ],
        "attributes": [
            {
                "id": 1,
                "type": "Description",
                "value": "Advanced persistent threat",
                "dateAdded": "2024-01-20T10:00:00Z",
                "lastModified": "2024-01-20T10:00:00Z"
            }
        ]
    }

    group = Group(**data)

    assert len(group.tags) == 2
    assert group.tags[0].name == "apt"
    assert len(group.attributes) == 1
    assert group.attributes[0].type == "Description"


def test_group_type_constants():
    """Test group type constants."""
    assert GroupType.ADVERSARY == "Adversary"
    assert GroupType.CAMPAIGN == "Campaign"
    assert GroupType.DOCUMENT == "Document"
    assert GroupType.EMAIL == "Email"
    assert GroupType.EVENT == "Event"
    assert GroupType.INCIDENT == "Incident"
    assert GroupType.INTRUSION_SET == "Intrusion Set"
    assert GroupType.REPORT == "Report"
    assert GroupType.SIGNATURE == "Signature"
    assert GroupType.THREAT == "Threat"


def test_group_field_aliases():
    """Test that field aliases work correctly."""
    data = {
        "id": 1,
        "type": "Incident",
        "name": "Test Incident",
        "dateAdded": "2024-01-20T10:00:00Z",  # API format
        "lastModified": "2024-01-25T15:30:00Z",  # API format
        "ownerName": "MyOrg",  # API format
        "ownerId": 1,
        "webLink": "https://example.com"
    }

    group = Group(**data)

    # Should be accessible via Python snake_case names
    assert group.date_added is not None
    assert group.last_modified is not None
    assert group.owner_name == "MyOrg"
    assert group.owner_id == 1
    assert group.web_link == "https://example.com"


def test_group_with_signature_fields():
    """Test group with signature-specific fields."""
    data = {
        "id": 1,
        "type": "Signature",
        "name": "Malware Signature",
        "dateAdded": "2024-01-20T10:00:00Z",
        "lastModified": "2024-01-25T15:30:00Z",
        "ownerName": "MyOrg",
        "ownerId": 1,
        "webLink": "https://example.com",
        "signatureType": "YARA"
    }

    group = Group(**data)

    assert group.type == "Signature"
    assert group.signature_type == "YARA"
