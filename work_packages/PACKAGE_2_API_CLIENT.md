# Work Package 2: API Client

**Module**: `tc_tui/api/`
**Priority**: High (Foundation)
**Estimated Time**: 6-8 hours
**Dependencies**: Module 1 (Data Models), Module 3 (Configuration)
**Can Start**: After models are defined (can use interface stubs initially)
**Assignable To**: Agent with Python/HTTP/Auth experience

## Objective

Create the API client for ThreatConnect with HMAC authentication, proper error handling, and typed responses using Pydantic models.

## Deliverables

### Files to Create

```
tc_tui/api/
├── __init__.py          # Public exports
├── client.py            # Base HTTP client
├── auth.py              # HMAC authentication
├── indicators.py        # Indicator API methods
├── groups.py            # Group API methods
└── exceptions.py        # Custom exceptions
```

### 1. `tc_tui/api/exceptions.py`

Define custom exceptions:

```python
"""API exception classes."""


class ThreatConnectAPIError(Exception):
    """Base exception for API errors."""

    def __init__(self, message: str, status_code: int = None, response_body: str = None):
        self.message = message
        self.status_code = status_code
        self.response_body = response_body
        super().__init__(self.message)


class AuthenticationError(ThreatConnectAPIError):
    """Raised when authentication fails."""
    pass


class RateLimitError(ThreatConnectAPIError):
    """Raised when rate limit is exceeded."""
    pass


class NotFoundError(ThreatConnectAPIError):
    """Raised when resource is not found."""
    pass


class ValidationError(ThreatConnectAPIError):
    """Raised when request validation fails."""
    pass


class NetworkError(ThreatConnectAPIError):
    """Raised when network operation fails."""
    pass
```

### 2. `tc_tui/api/auth.py`

Implement HMAC-SHA256 authentication:

```python
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
```

### 3. `tc_tui/api/client.py`

Base HTTP client:

```python
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
```

### 4. `tc_tui/api/indicators.py`

Indicator API methods:

```python
"""Indicator API endpoints."""

from typing import List, Optional
import urllib.parse

from ..models import Indicator, SearchResult, PaginationInfo
from .client import ThreatConnectClient


class IndicatorsAPI:
    """API methods for indicators."""

    def __init__(self, client: ThreatConnectClient):
        """Initialize with base client."""
        self.client = client

    async def search(
        self,
        tql: Optional[str] = None,
        result_start: int = 0,
        result_limit: int = 100,
        owner: Optional[str] = None,
        include_tags: bool = False,
        include_attributes: bool = False
    ) -> SearchResult:
        """
        Search indicators.

        Args:
            tql: TQL query string
            result_start: Starting index for pagination
            result_limit: Number of results to return
            owner: Owner name to filter by
            include_tags: Include tags in response
            include_attributes: Include attributes in response

        Returns:
            SearchResult with indicators
        """
        params = {
            "resultStart": result_start,
            "resultLimit": result_limit
        }

        if tql:
            params["tql"] = tql

        if owner:
            params["owner"] = owner

        if include_tags:
            params["includeTags"] = "true"

        if include_attributes:
            params["includeAttributes"] = "true"

        # Make API call
        response = self.client.get("/indicators", params=params)

        # Parse response
        indicators = [Indicator(**item) for item in response.get("data", [])]

        # Build pagination info
        total = response.get("count", 0)
        page_size = result_limit
        current_page = result_start // page_size if page_size > 0 else 0
        total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0

        pagination = PaginationInfo(
            count=total,
            current_page=current_page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=result_start + result_limit < total,
            has_previous=result_start > 0
        )

        return SearchResult(
            data=indicators,
            pagination=pagination,
            search_type="indicators",
            query=tql or ""
        )

    async def get_by_id(
        self,
        indicator_id: int,
        include_tags: bool = True,
        include_attributes: bool = True
    ) -> Indicator:
        """
        Get indicator by ID.

        Args:
            indicator_id: Indicator ID
            include_tags: Include tags in response
            include_attributes: Include attributes in response

        Returns:
            Indicator object
        """
        params = {}

        if include_tags:
            params["includeTags"] = "true"

        if include_attributes:
            params["includeAttributes"] = "true"

        response = self.client.get(f"/indicators/{indicator_id}", params=params)

        return Indicator(**response.get("data", {}))

    async def get_associations(
        self,
        indicator_id: int,
        association_type: Optional[str] = None
    ) -> List:
        """
        Get indicator associations.

        Args:
            indicator_id: Indicator ID
            association_type: Type of associations ("groups" or "indicators")

        Returns:
            List of associations
        """
        if association_type:
            endpoint = f"/indicators/{indicator_id}/{association_type}"
        else:
            endpoint = f"/indicators/{indicator_id}/associations"

        response = self.client.get(endpoint)

        return response.get("data", [])
```

### 5. `tc_tui/api/groups.py`

Group API methods:

```python
"""Group API endpoints."""

from typing import List, Optional

from ..models import Group, SearchResult, PaginationInfo
from .client import ThreatConnectClient


class GroupsAPI:
    """API methods for groups."""

    def __init__(self, client: ThreatConnectClient):
        """Initialize with base client."""
        self.client = client

    async def search(
        self,
        tql: Optional[str] = None,
        result_start: int = 0,
        result_limit: int = 100,
        owner: Optional[str] = None,
        include_tags: bool = False,
        include_attributes: bool = False
    ) -> SearchResult:
        """
        Search groups.

        Args:
            tql: TQL query string
            result_start: Starting index for pagination
            result_limit: Number of results to return
            owner: Owner name to filter by
            include_tags: Include tags in response
            include_attributes: Include attributes in response

        Returns:
            SearchResult with groups
        """
        params = {
            "resultStart": result_start,
            "resultLimit": result_limit
        }

        if tql:
            params["tql"] = tql

        if owner:
            params["owner"] = owner

        if include_tags:
            params["includeTags"] = "true"

        if include_attributes:
            params["includeAttributes"] = "true"

        # Make API call
        response = self.client.get("/groups", params=params)

        # Parse response
        groups = [Group(**item) for item in response.get("data", [])]

        # Build pagination info
        total = response.get("count", 0)
        page_size = result_limit
        current_page = result_start // page_size if page_size > 0 else 0
        total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0

        pagination = PaginationInfo(
            count=total,
            current_page=current_page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=result_start + result_limit < total,
            has_previous=result_start > 0
        )

        return SearchResult(
            data=groups,
            pagination=pagination,
            search_type="groups",
            query=tql or ""
        )

    async def get_by_id(
        self,
        group_id: int,
        include_tags: bool = True,
        include_attributes: bool = True
    ) -> Group:
        """Get group by ID."""
        params = {}

        if include_tags:
            params["includeTags"] = "true"

        if include_attributes:
            params["includeAttributes"] = "true"

        response = self.client.get(f"/groups/{group_id}", params=params)

        return Group(**response.get("data", {}))
```

### 6. `tc_tui/api/__init__.py`

Public exports:

```python
"""ThreatConnect API client."""

from .client import ThreatConnectClient
from .indicators import IndicatorsAPI
from .groups import GroupsAPI
from .exceptions import (
    ThreatConnectAPIError,
    AuthenticationError,
    RateLimitError,
    NotFoundError,
    ValidationError,
    NetworkError
)

__all__ = [
    "ThreatConnectClient",
    "IndicatorsAPI",
    "GroupsAPI",
    "ThreatConnectAPIError",
    "AuthenticationError",
    "RateLimitError",
    "NotFoundError",
    "ValidationError",
    "NetworkError",
]
```

## Testing Requirements

### Test File: `tests/test_api/test_auth.py`

```python
"""Tests for HMAC authentication."""

import pytest
from tc_tui.api.auth import HMACAuth


def test_auth_header_generation():
    """Test HMAC signature generation."""
    auth = HMACAuth("test_id", "test_secret")

    auth_header, timestamp = auth.generate_auth_header(
        api_path="/api/v3/indicators",
        http_method="GET",
        timestamp="1234567890"
    )

    assert auth_header.startswith("TC test_id:")
    assert timestamp == "1234567890"


def test_auth_header_with_query_string():
    """Test HMAC signature with query string."""
    auth = HMACAuth("test_id", "test_secret")

    auth_header, timestamp = auth.generate_auth_header(
        api_path="/api/v3/indicators",
        http_method="GET",
        timestamp="1234567890",
        query_string="tql=typeName%20in%20%28%22Address%22%29"
    )

    assert auth_header.startswith("TC test_id:")
    assert ":" in auth_header  # Contains signature
```

### Test File: `tests/test_api/test_client.py`

```python
"""Tests for API client."""

import pytest
from unittest.mock import Mock, patch
from tc_tui.api import ThreatConnectClient, AuthenticationError


@patch('tc_tui.api.client.requests.Session')
def test_client_initialization(mock_session):
    """Test client initialization."""
    client = ThreatConnectClient(
        access_id="test_id",
        secret_key="test_secret",
        instance="mycompany"
    )

    assert client.instance == "mycompany"
    assert client.base_url == "https://mycompany.threatconnect.com/api/v3"


@patch('tc_tui.api.client.requests.Session')
def test_client_handles_401(mock_session):
    """Test client raises AuthenticationError on 401."""
    # Mock response
    mock_response = Mock()
    mock_response.status_code = 401
    mock_response.text = "Unauthorized"

    mock_session_instance = Mock()
    mock_session_instance.request.return_value = mock_response
    mock_session.return_value = mock_session_instance

    client = ThreatConnectClient(
        access_id="test_id",
        secret_key="test_secret",
        instance="mycompany"
    )

    with pytest.raises(AuthenticationError):
        client.get("/indicators")
```

## Acceptance Criteria

- [ ] All API methods implemented with proper type hints
- [ ] HMAC authentication working correctly
- [ ] Error handling for all HTTP status codes
- [ ] Request/response logging implemented
- [ ] All exceptions defined and used appropriately
- [ ] Tests pass with >80% coverage
- [ ] Can successfully make authenticated requests (integration test)
- [ ] Proper timeout handling
- [ ] Query string encoding works correctly

## Integration Points

- **Uses**: Module 1 (Data Models) for request/response types
- **Uses**: Module 3 (Configuration) for credentials
- **Used By**: Module 5 (Search Engine) for API calls

## Notes

- Make all methods `async` for future async support (can be synchronous initially)
- Log all requests at DEBUG level
- Log errors at ERROR level
- Use session for connection pooling
- Handle rate limiting gracefully
- Query string encoding must preserve TQL syntax

## References

- [ThreatConnect API Authentication](https://docs.threatconnect.com/en/latest/rest_api/authentication.html)
- [ThreatConnect API v3 Overview](https://docs.threatconnect.com/en/latest/rest_api/v3/overview.html)
- [Requests Documentation](https://requests.readthedocs.io/)

---

**Status**: Ready to Start
**Branch**: `module/2-api-client`
**Estimated Completion**: 6-8 hours
