# Work Package 1: Data Models

**Module**: `tc_tui/models/`
**Priority**: High (Foundation)
**Estimated Time**: 4-6 hours
**Dependencies**: None
**Can Start**: Immediately
**Assignable To**: Any agent with Python/Pydantic experience

## Objective

Create all Pydantic data models for the application. These models will be used throughout the codebase for type safety, validation, and API response parsing.

## Deliverables

### Files to Create

```
tc_tui/models/
├── __init__.py          # Public exports
├── indicator.py         # Indicator models
├── group.py             # Group models
├── common.py            # Shared models (Tag, Attribute, etc.)
└── search.py            # Search request/response models
```

### 1. `tc_tui/models/common.py`

Define shared models used across indicators and groups:

```python
"""Common data models shared across the application."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class Tag(BaseModel):
    """Represents a ThreatConnect tag."""

    name: str
    description: Optional[str] = None


class Attribute(BaseModel):
    """Represents a ThreatConnect attribute."""

    id: int
    type: str
    value: str
    date_added: datetime = Field(alias="dateAdded")
    last_modified: datetime = Field(alias="lastModified")

    class Config:
        populate_by_name = True


class Association(BaseModel):
    """Represents an association between objects."""

    id: int
    type: str  # "Indicator" or "Group"
    object_type: str = Field(alias="objectType")  # Specific type (Address, Adversary, etc.)
    summary: Optional[str] = None  # For indicators
    name: Optional[str] = None  # For groups

    class Config:
        populate_by_name = True


class Owner(BaseModel):
    """Represents a ThreatConnect owner/organization."""

    id: int
    name: str
    type: str
```

### 2. `tc_tui/models/indicator.py`

Define indicator-specific models:

```python
"""Indicator data models."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from .common import Tag, Attribute, Association


class Indicator(BaseModel):
    """Represents a ThreatConnect indicator."""

    id: int
    type: str
    summary: str
    rating: float = 0.0
    confidence: int = 0
    date_added: datetime = Field(alias="dateAdded")
    last_modified: datetime = Field(alias="lastModified")
    owner_name: str = Field(alias="ownerName")
    owner_id: int = Field(alias="ownerId")
    web_link: str = Field(alias="webLink")

    # Optional fields
    description: Optional[str] = None
    active: bool = True
    source: Optional[str] = None

    # Relationships (loaded separately)
    tags: List[Tag] = Field(default_factory=list)
    attributes: List[Attribute] = Field(default_factory=list)
    associated_groups: List[Association] = Field(default_factory=list, alias="associatedGroups")
    associated_indicators: List[Association] = Field(default_factory=list, alias="associatedIndicators")

    # Type-specific fields (only present for certain types)
    size: Optional[int] = None  # For File indicators
    md5: Optional[str] = None
    sha1: Optional[str] = None
    sha256: Optional[str] = None

    class Config:
        populate_by_name = True

    @field_validator('rating')
    @classmethod
    def validate_rating(cls, v: float) -> float:
        """Ensure rating is between 0 and 5."""
        if not 0 <= v <= 5:
            raise ValueError('Rating must be between 0 and 5')
        return v

    @field_validator('confidence')
    @classmethod
    def validate_confidence(cls, v: int) -> int:
        """Ensure confidence is between 0 and 100."""
        if not 0 <= v <= 100:
            raise ValueError('Confidence must be between 0 and 100')
        return v

    def get_icon(self) -> str:
        """Get icon for this indicator type."""
        from ..utils.icons import IconMapper
        return IconMapper.get_indicator_icon(self.type)


# Indicator type constants
class IndicatorType:
    """Constants for indicator types."""

    ADDRESS = "Address"
    EMAIL_ADDRESS = "EmailAddress"
    FILE = "File"
    HOST = "Host"
    URL = "URL"
    ASN = "ASN"
    CIDR = "CIDR"
    MUTEX = "Mutex"
    REGISTRY_KEY = "Registry Key"
    USER_AGENT = "User Agent"
```

### 3. `tc_tui/models/group.py`

Define group-specific models:

```python
"""Group data models."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from .common import Tag, Attribute, Association


class Group(BaseModel):
    """Represents a ThreatConnect group."""

    id: int
    type: str
    name: str
    date_added: datetime = Field(alias="dateAdded")
    last_modified: datetime = Field(alias="lastModified")
    owner_name: str = Field(alias="ownerName")
    owner_id: int = Field(alias="ownerId")
    web_link: str = Field(alias="webLink")

    # Optional fields
    description: Optional[str] = None

    # Relationships (loaded separately)
    tags: List[Tag] = Field(default_factory=list)
    attributes: List[Attribute] = Field(default_factory=list)
    associated_groups: List[Association] = Field(default_factory=list, alias="associatedGroups")
    associated_indicators: List[Association] = Field(default_factory=list, alias="associatedIndicators")

    # Type-specific fields
    # Event-specific
    event_date: Optional[datetime] = Field(None, alias="eventDate")
    status: Optional[str] = None

    # Document-specific
    file_name: Optional[str] = Field(None, alias="fileName")
    file_size: Optional[int] = Field(None, alias="fileSize")
    file_type: Optional[str] = Field(None, alias="fileType")

    # Email-specific
    subject: Optional[str] = None
    header: Optional[str] = None
    body: Optional[str] = None
    from_address: Optional[str] = Field(None, alias="from")
    to_address: Optional[str] = Field(None, alias="to")

    # Signature-specific
    signature_type: Optional[str] = Field(None, alias="signatureType")

    class Config:
        populate_by_name = True

    def get_icon(self) -> str:
        """Get icon for this group type."""
        from ..utils.icons import IconMapper
        return IconMapper.get_group_icon(self.type)


# Group type constants
class GroupType:
    """Constants for group types."""

    ADVERSARY = "Adversary"
    CAMPAIGN = "Campaign"
    DOCUMENT = "Document"
    EMAIL = "Email"
    EVENT = "Event"
    INCIDENT = "Incident"
    INTRUSION_SET = "Intrusion Set"
    REPORT = "Report"
    SIGNATURE = "Signature"
    THREAT = "Threat"
```

### 4. `tc_tui/models/search.py`

Define search-related models:

```python
"""Search request and response models."""

from enum import Enum
from typing import List, Union, Optional
from pydantic import BaseModel, Field
from .indicator import Indicator
from .group import Group


class SearchType(str, Enum):
    """Type of search to perform."""

    INDICATORS = "indicators"
    GROUPS = "groups"
    BOTH = "both"


class SearchFilters(BaseModel):
    """Filters for search queries."""

    owner: Optional[str] = None
    rating_min: Optional[float] = Field(None, ge=0, le=5)
    rating_max: Optional[float] = Field(None, ge=0, le=5)
    confidence_min: Optional[int] = Field(None, ge=0, le=100)
    confidence_max: Optional[int] = Field(None, ge=0, le=100)
    date_added_after: Optional[str] = None
    date_added_before: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    indicator_types: List[str] = Field(default_factory=list)
    group_types: List[str] = Field(default_factory=list)


class SearchRequest(BaseModel):
    """Request for searching ThreatConnect."""

    query: str
    search_type: SearchType
    filters: Optional[SearchFilters] = None
    page: int = Field(default=0, ge=0)
    page_size: int = Field(default=100, ge=1, le=10000)

    # If True, use query as TQL. If False, treat as summary search
    use_tql: bool = False


class PaginationInfo(BaseModel):
    """Pagination metadata."""

    total_results: int = Field(alias="count")
    current_page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool

    class Config:
        populate_by_name = True


class SearchResult(BaseModel):
    """Result from a search query."""

    data: List[Union[Indicator, Group]]
    pagination: PaginationInfo
    search_type: SearchType
    query: str

    @property
    def indicators(self) -> List[Indicator]:
        """Get only indicators from results."""
        return [item for item in self.data if isinstance(item, Indicator)]

    @property
    def groups(self) -> List[Group]:
        """Get only groups from results."""
        return [item for item in self.data if isinstance(item, Group)]
```

### 5. `tc_tui/models/__init__.py`

Public API exports:

```python
"""Data models for ThreatConnect CLI."""

from .common import Tag, Attribute, Association, Owner
from .indicator import Indicator, IndicatorType
from .group import Group, GroupType
from .search import (
    SearchType,
    SearchFilters,
    SearchRequest,
    SearchResult,
    PaginationInfo
)

__all__ = [
    # Common
    "Tag",
    "Attribute",
    "Association",
    "Owner",

    # Indicators
    "Indicator",
    "IndicatorType",

    # Groups
    "Group",
    "GroupType",

    # Search
    "SearchType",
    "SearchFilters",
    "SearchRequest",
    "SearchResult",
    "PaginationInfo",
]
```

## Testing Requirements

Create `tests/test_models/` with tests for each model:

### Test File: `tests/test_models/test_indicator.py`

```python
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
```

### Test File: `tests/test_models/test_search.py`

```python
"""Tests for search models."""

import pytest
from tc_tui.models import SearchRequest, SearchType, SearchFilters, PaginationInfo


def test_search_request_creation():
    """Test creating a search request."""
    request = SearchRequest(
        query="192.168.1.1",
        search_type=SearchType.INDICATORS,
        page=0,
        page_size=100
    )

    assert request.query == "192.168.1.1"
    assert request.search_type == SearchType.INDICATORS
    assert request.page == 0
    assert request.page_size == 100
    assert request.use_tql is False


def test_search_request_with_filters():
    """Test search request with filters."""
    filters = SearchFilters(
        rating_min=3.0,
        confidence_min=80,
        tags=["malware", "c2"]
    )

    request = SearchRequest(
        query='typeName in ("Address")',
        search_type=SearchType.INDICATORS,
        filters=filters,
        use_tql=True
    )

    assert request.filters.rating_min == 3.0
    assert request.filters.confidence_min == 80
    assert len(request.filters.tags) == 2


def test_pagination_info():
    """Test pagination info."""
    pagination = PaginationInfo(
        count=250,
        current_page=1,
        page_size=100,
        total_pages=3,
        has_next=True,
        has_previous=False
    )

    assert pagination.total_results == 250
    assert pagination.current_page == 1
    assert pagination.total_pages == 3
    assert pagination.has_next is True
    assert pagination.has_previous is False
```

## Acceptance Criteria

- [ ] All model files created with complete type hints
- [ ] Pydantic models handle API response field aliases correctly (dateAdded → date_added)
- [ ] Validation logic works for rating (0-5) and confidence (0-100)
- [ ] Models can serialize to/from JSON
- [ ] All tests pass with >90% coverage
- [ ] Docstrings on all public classes and methods
- [ ] No dependencies on other modules (except utils for icons, which is a soft dependency)
- [ ] `__init__.py` exports all public models

## Mock Data for Other Teams

Create `tests/fixtures/mock_data.py`:

```python
"""Mock data for testing."""

MOCK_INDICATOR_RESPONSE = {
    "id": 12345,
    "type": "Address",
    "summary": "192.168.1.1",
    "rating": 3.5,
    "confidence": 85,
    "dateAdded": "2024-01-15T14:32:10Z",
    "lastModified": "2025-11-22T09:15:43Z",
    "ownerName": "MyOrganization",
    "ownerId": 1,
    "webLink": "https://example.threatconnect.com/auth/indicators/details/address.xhtml?address=192.168.1.1",
    "description": "Known C2 server for malware family XYZ",
    "active": True,
    "tags": [
        {"name": "malware"},
        {"name": "c2"},
        {"name": "apt29"}
    ],
    "attributes": [
        {
            "id": 1,
            "type": "Source",
            "value": "OSINT Report #1234",
            "dateAdded": "2024-01-15T14:32:10Z",
            "lastModified": "2024-01-15T14:32:10Z"
        }
    ]
}

MOCK_GROUP_RESPONSE = {
    "id": 67890,
    "type": "Incident",
    "name": "Network Intrusion January 2024",
    "dateAdded": "2024-01-20T10:00:00Z",
    "lastModified": "2024-01-25T15:30:00Z",
    "ownerName": "MyOrganization",
    "ownerId": 1,
    "webLink": "https://example.threatconnect.com/auth/incident/incident.xhtml?incident=67890",
    "description": "Detected network intrusion via C2 communication",
    "eventDate": "2024-01-18T00:00:00Z",
    "status": "Open"
}
```

## Notes

- Use Pydantic V2 syntax
- All datetime fields should be parsed automatically by Pydantic
- Field aliases handle API response format (camelCase) to Python convention (snake_case)
- Models should be frozen after creation when possible for immutability
- Keep models pure data structures - no business logic

## References

- [Pydantic V2 Documentation](https://docs.pydantic.dev/latest/)
- [ThreatConnect API v3 Indicators](https://docs.threatconnect.com/en/latest/rest_api/v3/indicators/indicators.html)
- [ThreatConnect API v3 Groups](https://docs.threatconnect.com/en/latest/rest_api/v3/groups/groups.html)

---

**Status**: Ready to Start
**Branch**: `module/1-data-models`
**Estimated Completion**: 4-6 hours
