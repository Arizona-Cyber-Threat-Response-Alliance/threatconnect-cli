"""Data formatting utilities."""

from datetime import datetime
from typing import Union
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
            style = Style(color="grey50", dim=True)  # No rating

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
