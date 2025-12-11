"""State management models."""

from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field


class SearchType(str, Enum):
    """Type of search being performed."""

    INDICATORS = "indicators"
    GROUPS = "groups"
    BOTH = "both"


class ViewMode(str, Enum):
    """Current view mode in the UI."""

    SEARCH = "search"
    RESULTS = "results"
    DETAIL = "detail"
    HELP = "help"
    SETTINGS = "settings"


class FilterState(BaseModel):
    """Current filter settings."""

    search_type: SearchType = SearchType.INDICATORS
    owner: Optional[str] = None
    min_rating: float = 0.0
    max_rating: float = 5.0
    min_confidence: int = 0
    max_confidence: int = 100
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    tags: List[str] = Field(default_factory=list)
    types: List[str] = Field(default_factory=list)  # Specific indicator/group types

    def is_filtered(self) -> bool:
        """Check if any filters are active."""
        return (
            self.owner is not None
            or self.min_rating > 0.0
            or self.max_rating < 5.0
            or self.min_confidence > 0
            or self.max_confidence < 100
            or self.date_from is not None
            or self.date_to is not None
            or len(self.tags) > 0
            or len(self.types) > 0
        )


class PaginationState(BaseModel):
    """Current pagination state."""

    current_page: int = 0
    page_size: int = 100
    total_results: int = 0
    has_next_page: bool = False
    has_previous_page: bool = False

    @property
    def total_pages(self) -> int:
        """Calculate total number of pages."""
        if self.total_results == 0:
            return 0
        return (self.total_results + self.page_size - 1) // self.page_size

    @property
    def result_start(self) -> int:
        """Get the starting index for the current page."""
        return self.current_page * self.page_size

    @property
    def result_end(self) -> int:
        """Get the ending index for the current page."""
        return min((self.current_page + 1) * self.page_size, self.total_results)


class SearchHistoryEntry(BaseModel):
    """Single search history entry."""

    query: str
    search_type: SearchType
    timestamp: datetime = Field(default_factory=datetime.now)
    result_count: int = 0


class NavigationHistoryEntry(BaseModel):
    """Single navigation history entry."""

    view_mode: ViewMode
    item_id: Optional[int] = None
    item_type: Optional[str] = None  # "Indicator" or "Group"
    timestamp: datetime = Field(default_factory=datetime.now)
