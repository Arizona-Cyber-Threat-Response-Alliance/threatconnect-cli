"""Indicator data models."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, ConfigDict
from .common import Tag, Attribute, Association


class Indicator(BaseModel):
    """Represents a ThreatConnect indicator."""

    model_config = ConfigDict(populate_by_name=True)

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
