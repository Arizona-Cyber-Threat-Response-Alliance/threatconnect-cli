# Work Package 4: Utilities

**Module**: `tc_tui/utils/`
**Priority**: Medium (Foundation)
**Estimated Time**: 3-4 hours
**Dependencies**: Module 1 (Data Models)
**Can Start**: After model interfaces are defined
**Assignable To**: Any agent with Python experience

## Objective

Create utility functions for icon mapping, data formatting, input validation, and caching that will be used throughout the application.

## Deliverables

### Files to Create

```
tc_tui/utils/
├── __init__.py          # Public exports
├── icons.py             # Icon mapping
├── formatters.py        # Data formatters
├── validators.py        # Input validation
└── cache.py             # Caching utilities
```

### 1. `tc_tui/utils/icons.py`

Icon mapping for indicator and group types:

```python
"""Icon mapping for ThreatConnect data types."""

from typing import Dict


class IconMapper:
    """Maps ThreatConnect types to display icons."""

    INDICATOR_ICONS: Dict[str, str] = {
        # Addresses
        "Address": "🌐",

        # Hosts
        "Host": "🖥️",

        # Email
        "EmailAddress": "📧",
        "EmailSubject": "📬",

        # URLs
        "URL": "🔗",

        # Files
        "File": "📄",

        # Network
        "ASN": "🔢",
        "CIDR": "📍",

        # System
        "Mutex": "🔒",
        "Registry Key": "🗝️",
        "RegistryKey": "🗝️",

        # Other
        "User Agent": "🤖",
        "UserAgent": "🤖",

        # Custom/Unknown
        "Custom": "⚙️",
        "Unknown": "❓",
    }

    GROUP_ICONS: Dict[str, str] = {
        "Adversary": "💀",
        "Campaign": "🎯",
        "Document": "📋",
        "Email": "✉️",
        "Event": "📅",
        "Incident": "🚨",
        "Intrusion Set": "🔴",
        "IntrusionSet": "🔴",
        "Report": "📊",
        "Signature": "✍️",
        "Threat": "⚠️",
        "Task": "📝",
        "Unknown": "❓",
    }

    # Rating icons
    RATING_ICON = "⭐"
    NO_RATING_ICON = "☆"

    # Status icons
    ACTIVE_ICON = "✅"
    INACTIVE_ICON = "❌"
    UNKNOWN_STATUS_ICON = "❔"

    # Association icons
    ASSOCIATION_INDICATOR_ICON = "🔗"
    ASSOCIATION_GROUP_ICON = "📁"

    @classmethod
    def get_indicator_icon(cls, indicator_type: str) -> str:
        """
        Get icon for indicator type.

        Args:
            indicator_type: Indicator type name

        Returns:
            Icon emoji/character
        """
        return cls.INDICATOR_ICONS.get(indicator_type, cls.INDICATOR_ICONS["Unknown"])

    @classmethod
    def get_group_icon(cls, group_type: str) -> str:
        """
        Get icon for group type.

        Args:
            group_type: Group type name

        Returns:
            Icon emoji/character
        """
        return cls.GROUP_ICONS.get(group_type, cls.GROUP_ICONS["Unknown"])

    @classmethod
    def get_rating_icon(cls, rating: float, max_rating: float = 5.0) -> str:
        """
        Get star rating display.

        Args:
            rating: Rating value (0-5)
            max_rating: Maximum rating value

        Returns:
            Star rating string
        """
        if rating <= 0:
            return cls.NO_RATING_ICON * int(max_rating)

        filled_stars = int(rating)
        empty_stars = int(max_rating - rating)

        return (cls.RATING_ICON * filled_stars) + (cls.NO_RATING_ICON * empty_stars)

    @classmethod
    def get_active_icon(cls, is_active: bool) -> str:
        """
        Get active/inactive icon.

        Args:
            is_active: Whether item is active

        Returns:
            Status icon
        """
        return cls.ACTIVE_ICON if is_active else cls.INACTIVE_ICON

    @classmethod
    def get_confidence_icon(cls, confidence: int) -> str:
        """
        Get confidence level icon.

        Args:
            confidence: Confidence percentage (0-100)

        Returns:
            Icon representing confidence level
        """
        if confidence >= 90:
            return "🟢"  # High confidence
        elif confidence >= 70:
            return "🟡"  # Medium confidence
        elif confidence >= 50:
            return "🟠"  # Low-medium confidence
        else:
            return "🔴"  # Low confidence
```

### 2. `tc_tui/utils/formatters.py`

Data formatting utilities:

```python
"""Data formatting utilities."""

from datetime import datetime
from typing import Optional, Union
from rich.text import Text
from rich.style import Style


class Formatters:
    """Data formatting utilities."""

    @staticmethod
    def format_date(
        date_input: Union[str, datetime],
        format_string: str = "%B %d, %Y %H:%M:%S"
    ) -> str:
        """
        Format datetime to readable string.

        Args:
            date_input: ISO date string or datetime object
            format_string: strftime format string

        Returns:
            Formatted date string
        """
        if isinstance(date_input, str):
            try:
                # Parse ISO format
                date_obj = datetime.fromisoformat(date_input.replace('Z', '+00:00'))
            except ValueError:
                return date_input  # Return as-is if can't parse
        elif isinstance(date_input, datetime):
            date_obj = date_input
        else:
            return "N/A"

        return date_obj.strftime(format_string)

    @staticmethod
    def format_rating(rating: float, max_rating: float = 5.0) -> str:
        """
        Format rating as stars with numeric value.

        Args:
            rating: Rating value
            max_rating: Maximum rating

        Returns:
            Formatted rating string
        """
        from .icons import IconMapper

        stars = IconMapper.get_rating_icon(rating, max_rating)
        return f"{stars} ({rating:.1f}/{max_rating})"

    @staticmethod
    def format_confidence(confidence: int) -> str:
        """
        Format confidence with icon.

        Args:
            confidence: Confidence percentage

        Returns:
            Formatted confidence string
        """
        from .icons import IconMapper

        icon = IconMapper.get_confidence_icon(confidence)
        return f"{icon} {confidence}%"

    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """
        Format file size in human-readable format.

        Args:
            size_bytes: Size in bytes

        Returns:
            Formatted size string (e.g., "1.5 MB")
        """
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"

    @staticmethod
    def format_hash(hash_value: str, length: int = 16) -> str:
        """
        Truncate hash for display.

        Args:
            hash_value: Hash string
            length: Number of characters to show

        Returns:
            Truncated hash with ellipsis
        """
        if len(hash_value) <= length:
            return hash_value

        return f"{hash_value[:length]}..."

    @staticmethod
    def format_list(items: list, separator: str = ", ", max_items: int = 3) -> str:
        """
        Format list with truncation.

        Args:
            items: List of items
            separator: Separator between items
            max_items: Maximum items to show

        Returns:
            Formatted list string
        """
        if not items:
            return "None"

        if len(items) <= max_items:
            return separator.join(str(item) for item in items)

        shown_items = separator.join(str(item) for item in items[:max_items])
        remaining = len(items) - max_items

        return f"{shown_items}, and {remaining} more"

    @staticmethod
    def colorize_by_rating(text: str, rating: float) -> Text:
        """
        Colorize text based on rating.

        Args:
            text: Text to colorize
            rating: Rating value (0-5)

        Returns:
            Rich Text object with color
        """
        if rating >= 4:
            style = Style(color="red", bold=True)  # Critical
        elif rating >= 3:
            style = Style(color="yellow", bold=True)  # High
        elif rating >= 2:
            style = Style(color="orange1")  # Medium
        elif rating >= 1:
            style = Style(color="green")  # Low
        else:
            style = Style(color="dim")  # No rating

        return Text(text, style=style)

    @staticmethod
    def colorize_by_confidence(text: str, confidence: int) -> Text:
        """
        Colorize text based on confidence.

        Args:
            text: Text to colorize
            confidence: Confidence percentage

        Returns:
            Rich Text object with color
        """
        if confidence >= 90:
            style = Style(color="green", bold=True)
        elif confidence >= 70:
            style = Style(color="yellow")
        elif confidence >= 50:
            style = Style(color="orange1")
        else:
            style = Style(color="red")

        return Text(text, style=style)

    @staticmethod
    def truncate(text: str, max_length: int = 50, suffix: str = "...") -> str:
        """
        Truncate text to max length.

        Args:
            text: Text to truncate
            max_length: Maximum length
            suffix: Suffix to add if truncated

        Returns:
            Truncated text
        """
        if len(text) <= max_length:
            return text

        return text[:max_length - len(suffix)] + suffix
```

### 3. `tc_tui/utils/validators.py`

Input validation utilities:

```python
"""Input validation utilities."""

import re
from typing import Optional


class Validators:
    """Input validation utilities."""

    # Regex patterns from original code
    IPV4_PATTERN = r"\b(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"
    IPV6_PATTERN = r"(?<![a-zA-Z0-9:])(?:(?:(?:[a-fA-F0-9]{1,4}:){7}[a-fA-F0-9]{1,4})|(?:(?=(?:[a-fA-F0-9]{0,4}:){0,7}[a-fA-F0-9]{0,4})(?:(?:[a-fA-F0-9]{1,4}:){1,7}|:)(?:(?::[a-fA-F0-9]{1,4}){1,7}|:)))(?![a-zA-Z0-9:])"
    EMAIL_PATTERN = r"(?i)[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])"
    URL_PATTERN = r"\b(?:(?:https?|s?ftp|tcp|file)://)(?:(?:\b(?=.{4,253})(?:(?:[a-z0-9_-]{1,63}\.){0,124}(?:(?!-)[-a-z0-9]{1,63}(?<!-)\.){0,125}(?![-0-9])[-a-z0-9]{2,24}(?<![-0-9]))\b|\b(?:(?:(?:[0-9]|[1-8][0-9]|9[0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}(?:[0-9]|[1-8][0-9]|9[0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))\b)(?::(?:[1-9]|[1-8][0-9]|9[0-9]|[1-8][0-9]{2}|9[0-8][0-9]|99[0-9]|[1-8][0-9]{3}|9[0-8][0-9]{2}|99[0-8][0-9]|999[0-9]|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5]))?\b)(?:/[-a-zA-Z0-9_.~%!$&'()*+,;=:@]*)*(?:\?[-a-zA-Z0-9_.~%!$&'()*+,;=:@/?]*#?)?(?:\#[-a-zA-Z0-9_.~%!$&'()*+,;=:@/?]+)?"
    MD5_PATTERN = r"\b([a-fA-F\d]{32})\b"
    SHA1_PATTERN = r"\b([a-fA-F\d]{40})\b"
    SHA256_PATTERN = r"\b([a-fA-F\d]{64})\b"
    HOST_PATTERN = r"(?i)\b((?:(?!-)[a-zA-Z0-9-]{1,63}(?<!-)\.)+(?!apk|apt|arpa|asp|bat|bdoda|bin|bsspx|cer|cfg|cgi|class|close|cpl|cpp|crl|css|dll|doc|docx|dyn|exe|fl|gz|hlp|htm|html|ico|ini|ioc|jar|jpg|js|jxr|lco|lnk|loader|log|lxdns|mdb|mp4|odt|pcap|pdb|pdf|php|plg|plist|png|ppt|pptx|quit|rar|rtf|scr|sleep|ssl|torproject|tmp|txt|vbp|vbs|w32|wav|xls|xlsx|xml|xpi|dat($|\r\n)|gif($|\r\n)|xn$)(?:xn--[a-zA-Z0-9]{2,22}|[a-zA-Z]{2,13}))(?!.*@)"

    @classmethod
    def is_ipv4(cls, value: str) -> bool:
        """Check if value is IPv4 address."""
        return bool(re.match(cls.IPV4_PATTERN, value))

    @classmethod
    def is_ipv6(cls, value: str) -> bool:
        """Check if value is IPv6 address."""
        return bool(re.match(cls.IPV6_PATTERN, value))

    @classmethod
    def is_email(cls, value: str) -> bool:
        """Check if value is email address."""
        return bool(re.match(cls.EMAIL_PATTERN, value))

    @classmethod
    def is_url(cls, value: str) -> bool:
        """Check if value is URL."""
        return bool(re.match(cls.URL_PATTERN, value))

    @classmethod
    def is_md5(cls, value: str) -> bool:
        """Check if value is MD5 hash."""
        return bool(re.match(cls.MD5_PATTERN, value))

    @classmethod
    def is_sha1(cls, value: str) -> bool:
        """Check if value is SHA1 hash."""
        return bool(re.match(cls.SHA1_PATTERN, value))

    @classmethod
    def is_sha256(cls, value: str) -> bool:
        """Check if value is SHA256 hash."""
        return bool(re.match(cls.SHA256_PATTERN, value))

    @classmethod
    def is_host(cls, value: str) -> bool:
        """Check if value is hostname."""
        return bool(re.match(cls.HOST_PATTERN, value))

    @classmethod
    def detect_indicator_type(cls, value: str) -> Optional[str]:
        """
        Auto-detect indicator type from value.

        Args:
            value: Indicator value

        Returns:
            Indicator type name or None if unknown
        """
        # Order matters - check more specific patterns first
        if cls.is_sha256(value):
            return "File"
        elif cls.is_sha1(value):
            return "File"
        elif cls.is_md5(value):
            return "File"
        elif cls.is_url(value):
            return "URL"
        elif cls.is_email(value):
            return "EmailAddress"
        elif cls.is_ipv6(value):
            return "Address"
        elif cls.is_ipv4(value):
            return "Address"
        elif cls.is_host(value):
            return "Host"
        else:
            return None

    @classmethod
    def is_tql_query(cls, query: str) -> bool:
        """
        Check if query appears to be TQL.

        Args:
            query: Query string

        Returns:
            True if appears to be TQL
        """
        # Simple heuristic: contains TQL keywords
        tql_keywords = ["typeName", "summary", "rating", "confidence", " in ", " and ", " or ", "dateAdded"]
        query_lower = query.lower()

        return any(keyword.lower() in query_lower for keyword in tql_keywords)
```

### 4. `tc_tui/utils/cache.py`

Simple caching utility:

```python
"""Caching utilities."""

import time
from typing import Any, Optional, Dict, Tuple
from collections import OrderedDict


class TTLCache:
    """Simple time-to-live cache."""

    def __init__(self, ttl_seconds: int = 300, max_size: int = 1000):
        """
        Initialize TTL cache.

        Args:
            ttl_seconds: Time to live in seconds
            max_size: Maximum number of entries
        """
        self.ttl_seconds = ttl_seconds
        self.max_size = max_size
        self._cache: OrderedDict[str, Tuple[Any, float]] = OrderedDict()

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        if key not in self._cache:
            return None

        value, timestamp = self._cache[key]

        # Check if expired
        if time.time() - timestamp > self.ttl_seconds:
            del self._cache[key]
            return None

        # Move to end (LRU)
        self._cache.move_to_end(key)

        return value

    def set(self, key: str, value: Any) -> None:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
        """
        # Remove oldest entry if at max size
        if len(self._cache) >= self.max_size:
            self._cache.popitem(last=False)

        self._cache[key] = (value, time.time())

    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()

    def remove(self, key: str) -> None:
        """Remove specific cache entry."""
        if key in self._cache:
            del self._cache[key]

    def cleanup_expired(self) -> int:
        """
        Remove all expired entries.

        Returns:
            Number of entries removed
        """
        now = time.time()
        expired_keys = [
            key for key, (_, timestamp) in self._cache.items()
            if now - timestamp > self.ttl_seconds
        ]

        for key in expired_keys:
            del self._cache[key]

        return len(expired_keys)

    def size(self) -> int:
        """Get current cache size."""
        return len(self._cache)
```

### 5. `tc_tui/utils/__init__.py`

Public exports:

```python
"""Utility functions."""

from .icons import IconMapper
from .formatters import Formatters
from .validators import Validators
from .cache import TTLCache

__all__ = [
    "IconMapper",
    "Formatters",
    "Validators",
    "TTLCache",
]
```

## Testing Requirements

### Test File: `tests/test_utils/test_formatters.py`

```python
"""Tests for formatters."""

import pytest
from datetime import datetime
from tc_tui.utils import Formatters


def test_format_date_from_string():
    """Test date formatting from string."""
    date_str = "2024-01-15T14:32:10Z"
    result = Formatters.format_date(date_str)

    assert "January 15, 2024" in result


def test_format_rating():
    """Test rating formatting."""
    result = Formatters.format_rating(3.5)

    assert "⭐" in result
    assert "3.5" in result


def test_format_file_size():
    """Test file size formatting."""
    assert Formatters.format_file_size(500) == "500 B"
    assert Formatters.format_file_size(1500) == "1.5 KB"
    assert Formatters.format_file_size(1500000) == "1.4 MB"


def test_truncate():
    """Test text truncation."""
    text = "This is a very long string that needs to be truncated"
    result = Formatters.truncate(text, 20)

    assert len(result) <= 20
    assert result.endswith("...")
```

### Test File: `tests/test_utils/test_validators.py`

```python
"""Tests for validators."""

import pytest
from tc_tui.utils import Validators


def test_is_ipv4():
    """Test IPv4 validation."""
    assert Validators.is_ipv4("192.168.1.1") is True
    assert Validators.is_ipv4("256.1.1.1") is False
    assert Validators.is_ipv4("not-an-ip") is False


def test_is_email():
    """Test email validation."""
    assert Validators.is_email("test@example.com") is True
    assert Validators.is_email("not-an-email") is False


def test_is_md5():
    """Test MD5 validation."""
    assert Validators.is_md5("5d41402abc4b2a76b9719d911017c592") is True
    assert Validators.is_md5("not-a-hash") is False


def test_detect_indicator_type():
    """Test indicator type detection."""
    assert Validators.detect_indicator_type("192.168.1.1") == "Address"
    assert Validators.detect_indicator_type("test@example.com") == "EmailAddress"
    assert Validators.detect_indicator_type("5d41402abc4b2a76b9719d911017c592") == "File"
    assert Validators.detect_indicator_type("example.com") == "Host"
```

## Acceptance Criteria

- [ ] All utility functions implemented with type hints
- [ ] Icon mapping covers all indicator and group types
- [ ] Formatters handle edge cases (None, empty, invalid dates)
- [ ] Validators correctly identify indicator types
- [ ] Cache implements TTL and LRU eviction
- [ ] All tests pass with >85% coverage
- [ ] No external dependencies except Rich
- [ ] Utilities are stateless (except cache)

## Integration Points

- **Used By**: Module 1 (Data Models) for get_icon() methods
- **Used By**: Module 7 (Widgets) for display formatting
- **Used By**: Module 5 (Search Engine) for type detection

## Notes

- Icons use Unicode emoji for wide compatibility
- Formatters use Rich library for color support
- Validators preserve original regex patterns from tc-indicator.py
- Cache is simple in-memory implementation (consider redis for production)

## References

- [Rich Documentation](https://rich.readthedocs.io/)
- Original `tc-indicator.py` for regex patterns

---

**Status**: Ready to Start
**Branch**: `module/4-utilities`
**Estimated Completion**: 3-4 hours
