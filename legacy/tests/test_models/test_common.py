"""Tests for common models."""

import pytest
from datetime import datetime
from tc_tui.models import Tag, Attribute, Association, Owner


def test_tag_creation():
    """Test creating a tag."""
    tag = Tag(name="malware", description="Malicious software")

    assert tag.name == "malware"
    assert tag.description == "Malicious software"


def test_tag_without_description():
    """Test creating a tag without description."""
    tag = Tag(name="c2")

    assert tag.name == "c2"
    assert tag.description is None


def test_attribute_creation():
    """Test creating an attribute."""
    data = {
        "id": 1,
        "type": "Source",
        "value": "OSINT",
        "dateAdded": "2024-01-15T14:32:10Z",
        "lastModified": "2025-11-22T09:15:43Z"
    }

    attribute = Attribute(**data)

    assert attribute.id == 1
    assert attribute.type == "Source"
    assert attribute.value == "OSINT"
    assert attribute.date_added is not None
    assert attribute.last_modified is not None


def test_attribute_field_aliases():
    """Test that attribute field aliases work."""
    data = {
        "id": 1,
        "type": "Source",
        "value": "OSINT",
        "dateAdded": "2024-01-15T14:32:10Z",
        "lastModified": "2025-11-22T09:15:43Z"
    }

    attribute = Attribute(**data)

    # Should be accessible via Python snake_case names
    assert attribute.date_added is not None
    assert attribute.last_modified is not None


def test_association_indicator():
    """Test creating an association for an indicator."""
    data = {
        "id": 123,
        "type": "Indicator",
        "objectType": "Address",
        "summary": "192.168.1.1"
    }

    association = Association(**data)

    assert association.id == 123
    assert association.type == "Indicator"
    assert association.object_type == "Address"
    assert association.summary == "192.168.1.1"
    assert association.name is None


def test_association_group():
    """Test creating an association for a group."""
    data = {
        "id": 456,
        "type": "Group",
        "objectType": "Incident",
        "name": "Network Intrusion"
    }

    association = Association(**data)

    assert association.id == 456
    assert association.type == "Group"
    assert association.object_type == "Incident"
    assert association.name == "Network Intrusion"
    assert association.summary is None


def test_owner_creation():
    """Test creating an owner."""
    owner = Owner(id=1, name="MyOrganization", type="Organization")

    assert owner.id == 1
    assert owner.name == "MyOrganization"
    assert owner.type == "Organization"


def test_association_field_alias():
    """Test that association field alias works."""
    data = {
        "id": 123,
        "type": "Indicator",
        "objectType": "Address",
        "summary": "192.168.1.1"
    }

    association = Association(**data)

    # Should be accessible via Python snake_case name
    assert association.object_type == "Address"
