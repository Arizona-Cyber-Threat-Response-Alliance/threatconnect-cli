"""State management module."""

from .manager import AppState
from .models import (
    SearchType,
    ViewMode,
    FilterState,
    PaginationState,
    SearchHistoryEntry,
    NavigationHistoryEntry,
)
from .history import SearchHistory, NavigationHistory

__all__ = [
    "AppState",
    "SearchType",
    "ViewMode",
    "FilterState",
    "PaginationState",
    "SearchHistoryEntry",
    "NavigationHistoryEntry",
    "SearchHistory",
    "NavigationHistory",
]
