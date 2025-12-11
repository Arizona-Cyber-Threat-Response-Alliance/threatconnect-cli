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
