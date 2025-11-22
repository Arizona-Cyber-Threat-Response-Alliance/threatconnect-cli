"""Common data models shared across the application."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class Tag(BaseModel):
    """Represents a ThreatConnect tag."""

    name: str
    description: Optional[str] = None


class Attribute(BaseModel):
    """Represents a ThreatConnect attribute."""

    model_config = ConfigDict(populate_by_name=True)

    id: int
    type: str
    value: str
    date_added: datetime = Field(alias="dateAdded")
    last_modified: datetime = Field(alias="lastModified")


class Association(BaseModel):
    """Represents an association between objects."""

    model_config = ConfigDict(populate_by_name=True)

    id: int
    type: str  # "Indicator" or "Group"
    object_type: str = Field(alias="objectType")  # Specific type (Address, Adversary, etc.)
    summary: Optional[str] = None  # For indicators
    name: Optional[str] = None  # For groups


class Owner(BaseModel):
    """Represents a ThreatConnect owner/organization."""

    id: int
    name: str
    type: str
