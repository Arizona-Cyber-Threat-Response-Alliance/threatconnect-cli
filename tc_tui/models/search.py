"""Search request and response models."""

from enum import Enum
from typing import List, Union, Optional
from pydantic import BaseModel, ConfigDict, Field
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

    model_config = ConfigDict(populate_by_name=True)

    total_results: int = Field(alias="count")
    current_page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool


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
