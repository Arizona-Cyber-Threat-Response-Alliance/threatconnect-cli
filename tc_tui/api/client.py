"""Base ThreatConnect API client."""

import requests
from typing import Dict, Any, Optional
from urllib.parse import urlencode
import logging

from .auth import HMACAuth
from .exceptions import (
    ThreatConnectAPIError,
    AuthenticationError,
    RateLimitError,
    NotFoundError,
    NetworkError
)

logger = logging.getLogger(__name__)


class ThreatConnectClient:
    """Base client for ThreatConnect API."""

    def __init__(
        self,
        access_id: str,
        secret_key: str,
        instance: str,
        api_version: str = "v3"
    ):
        """
        Initialize ThreatConnect client.

        Args:
            access_id: API access ID
            secret_key: API secret key
            instance: Instance name (e.g., "mycompany")
            api_version: API version ("v3" or "v2")
        """
        self.instance = instance
        self.base_url = f"https://{instance}.threatconnect.com/api/{api_version}"
        self.auth = HMACAuth(access_id, secret_key)
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "Content-Type": "application/json"
        })

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make authenticated request to ThreatConnect API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (e.g., "/indicators")
            params: Query parameters
            data: Request body data

        Returns:
            Parsed JSON response

        Raises:
            ThreatConnectAPIError: On API errors
        """
        # Build full URL
        url = f"{self.base_url}{endpoint}"

        # Build query string
        query_string = ""
        if params:
            query_string = urlencode(params, safe='(),')

        # Generate auth header
        auth_header, timestamp = self.auth.generate_auth_header(
            api_path=f"/api/v3{endpoint}",
            http_method=method,
            query_string=query_string
        )

        # Add auth headers
        headers = {
            "Authorization": auth_header,
            "Timestamp": timestamp
        }

        # Make request
        try:
            logger.debug(f"{method} {url}?{query_string}")

            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=data,
                headers=headers,
                timeout=30
            )

            # Handle errors
            if response.status_code == 401:
                raise AuthenticationError(
                    "Authentication failed",
                    status_code=401,
                    response_body=response.text
                )
            elif response.status_code == 404:
                raise NotFoundError(
                    "Resource not found",
                    status_code=404,
                    response_body=response.text
                )
            elif response.status_code == 429:
                raise RateLimitError(
                    "Rate limit exceeded",
                    status_code=429,
                    response_body=response.text
                )
            elif response.status_code >= 400:
                raise ThreatConnectAPIError(
                    f"API error: {response.status_code}",
                    status_code=response.status_code,
                    response_body=response.text
                )

            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Network error: {e}")
            raise NetworkError(str(e))

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make GET request."""
        return self._make_request("GET", endpoint, params=params)

    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make POST request."""
        return self._make_request("POST", endpoint, data=data)

    def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make PUT request."""
        return self._make_request("PUT", endpoint, data=data)

    def delete(self, endpoint: str) -> Dict[str, Any]:
        """Make DELETE request."""
        return self._make_request("DELETE", endpoint)
