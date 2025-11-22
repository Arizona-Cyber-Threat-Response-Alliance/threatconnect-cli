"""ThreatConnect HMAC authentication."""

import hmac
import hashlib
import base64
import time
from typing import Tuple


class HMACAuth:
    """Handle ThreatConnect HMAC authentication."""

    def __init__(self, access_id: str, secret_key: str):
        """
        Initialize HMAC authenticator.

        Args:
            access_id: ThreatConnect API access ID
            secret_key: ThreatConnect API secret key
        """
        self.access_id = access_id
        self.secret_key = secret_key

    def generate_auth_header(
        self,
        api_path: str,
        http_method: str,
        timestamp: str = None,
        query_string: str = ""
    ) -> Tuple[str, str]:
        """
        Generate Authorization header and timestamp.

        Args:
            api_path: API endpoint path (e.g., "/api/v3/indicators")
            http_method: HTTP method (GET, POST, etc.)
            timestamp: Unix timestamp (generated if not provided)
            query_string: URL query string (without leading ?)

        Returns:
            Tuple of (authorization_header, timestamp)
        """
        if timestamp is None:
            timestamp = str(int(time.time()))

        # Construct message to sign
        if query_string:
            message = f"{api_path}?{query_string}:{http_method}:{timestamp}"
        else:
            message = f"{api_path}:{http_method}:{timestamp}"

        # Calculate HMAC-SHA256 signature
        signature = base64.b64encode(
            hmac.new(
                self.secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
        ).decode()

        # Construct authorization header
        auth_header = f"TC {self.access_id}:{signature}"

        return auth_header, timestamp
