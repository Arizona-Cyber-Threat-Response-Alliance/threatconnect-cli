"""Group data models."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from .common import Tag, Attribute, Association


class Group(BaseModel):
    """Represents a ThreatConnect group."""

    model_config = ConfigDict(populate_by_name=True)

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
