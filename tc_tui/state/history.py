"""Search and navigation history management."""

from typing import List, Optional
from collections import deque
from .models import SearchHistoryEntry, NavigationHistoryEntry


class SearchHistory:
    """Manages search history."""

    def __init__(self, max_size: int = 50):
        """Initialize search history.

        Args:
            max_size: Maximum number of history entries to keep
        """
        self.max_size = max_size
        self._history: deque[SearchHistoryEntry] = deque(maxlen=max_size)
        self._current_index: int = -1

    def add(self, entry: SearchHistoryEntry) -> None:
        """Add a new search to history.

        Args:
            entry: Search history entry to add
        """
        # Don't add duplicate consecutive searches
        if self._history and self._history[-1].query == entry.query:
            return

        self._history.append(entry)
        self._current_index = len(self._history) - 1

    def get_previous(self) -> Optional[SearchHistoryEntry]:
        """Get previous search in history.

        Returns:
            Previous search entry or None if at the beginning
        """
        if not self._history or self._current_index <= 0:
            return None

        self._current_index -= 1
        return self._history[self._current_index]

    def get_next(self) -> Optional[SearchHistoryEntry]:
        """Get next search in history.

        Returns:
            Next search entry or None if at the end
        """
        if not self._history or self._current_index >= len(self._history) - 1:
            return None

        self._current_index += 1
        return self._history[self._current_index]

    def get_all(self) -> List[SearchHistoryEntry]:
        """Get all history entries.

        Returns:
            List of all search history entries
        """
        return list(self._history)

    def clear(self) -> None:
        """Clear all history."""
        self._history.clear()
        self._current_index = -1


class NavigationHistory:
    """Manages navigation history for back/forward functionality."""

    def __init__(self, max_size: int = 100):
        """Initialize navigation history.

        Args:
            max_size: Maximum number of history entries to keep
        """
        self.max_size = max_size
        self._history: List[NavigationHistoryEntry] = []
        self._current_index: int = -1

    def push(self, entry: NavigationHistoryEntry) -> None:
        """Push a new navigation entry.

        Args:
            entry: Navigation history entry to add
        """
        # Remove any forward history when pushing new entry
        if self._current_index < len(self._history) - 1:
            self._history = self._history[: self._current_index + 1]

        self._history.append(entry)

        # Maintain max size
        if len(self._history) > self.max_size:
            self._history.pop(0)
        else:
            self._current_index += 1

    def can_go_back(self) -> bool:
        """Check if can navigate back.

        Returns:
            True if can go back, False otherwise
        """
        return self._current_index > 0

    def can_go_forward(self) -> bool:
        """Check if can navigate forward.

        Returns:
            True if can go forward, False otherwise
        """
        return self._current_index < len(self._history) - 1

    def go_back(self) -> Optional[NavigationHistoryEntry]:
        """Navigate to previous entry.

        Returns:
            Previous navigation entry or None
        """
        if not self.can_go_back():
            return None

        self._current_index -= 1
        return self._history[self._current_index]

    def go_forward(self) -> Optional[NavigationHistoryEntry]:
        """Navigate to next entry.

        Returns:
            Next navigation entry or None
        """
        if not self.can_go_forward():
            return None

        self._current_index += 1
        return self._history[self._current_index]

    def current(self) -> Optional[NavigationHistoryEntry]:
        """Get current navigation entry.

        Returns:
            Current navigation entry or None
        """
        if self._current_index < 0 or self._current_index >= len(self._history):
            return None
        return self._history[self._current_index]

    def clear(self) -> None:
        """Clear all history."""
        self._history.clear()
        self._current_index = -1
