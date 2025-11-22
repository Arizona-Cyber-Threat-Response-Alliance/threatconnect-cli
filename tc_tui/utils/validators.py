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
