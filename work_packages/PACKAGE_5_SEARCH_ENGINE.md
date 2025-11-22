# Work Package 5: Search Engine

**Module**: `tc_tui/search/`
**Priority**: Medium (Business Logic)
**Estimated Time**: 5-6 hours
**Dependencies**: Module 2 (API Client), Module 1 (Data Models)
**Can Start**: After API client is complete
**Assignable To**: Any agent with Python/API experience

## Objective

Create the search engine module that orchestrates searches, builds TQL queries from user input, handles indicator type detection, applies filters, and manages search operations with the ThreatConnect API.

## Deliverables

### Files to Create

```
tc_tui/search/
├── __init__.py          # Public exports
├── engine.py            # Main search orchestrator
├── query_builder.py     # TQL query construction
└── exceptions.py        # Search-specific exceptions
```

### 1. `tc_tui/search/exceptions.py`

Define search-specific exceptions:

```python
"""Search engine exceptions."""


class SearchError(Exception):
    """Base exception for search errors."""
    pass


class InvalidQueryError(SearchError):
    """Raised when query is invalid."""
    pass


class QueryBuildError(SearchError):
    """Raised when TQL query construction fails."""
    pass


class SearchExecutionError(SearchError):
    """Raised when search execution fails."""
    pass
```

### 2. `tc_tui/search/query_builder.py`

TQL query construction:

```python
"""TQL query builder for ThreatConnect searches."""

from typing import List, Optional
import urllib.parse

from ..models import SearchFilters, SearchType
from ..utils import Validators
from .exceptions import QueryBuildError


class TQLQueryBuilder:
    """Builds TQL queries from search parameters."""

    @staticmethod
    def build_simple_query(
        query: str,
        search_type: SearchType = SearchType.INDICATORS,
        auto_detect_type: bool = True
    ) -> str:
        """
        Build simple TQL query for summary search.

        Args:
            query: Search query (indicator value or group name)
            search_type: Type of search to perform
            auto_detect_type: Auto-detect indicator type from query

        Returns:
            TQL query string

        Examples:
            >>> TQLQueryBuilder.build_simple_query("192.168.1.1")
            'typeName in ("Address") and summary in ("192.168.1.1")'

            >>> TQLQueryBuilder.build_simple_query("evil.com", auto_detect_type=True)
            'typeName in ("Host") and summary in ("evil.com")'
        """
        if search_type == SearchType.INDICATORS:
            # Detect indicator type
            indicator_type = None
            if auto_detect_type:
                indicator_type = Validators.detect_indicator_type(query)

            if indicator_type:
                return f'typeName in ("{indicator_type}") and summary in ("{query}")'
            else:
                # Search all indicator types
                return f'summary in ("{query}")'

        elif search_type == SearchType.GROUPS:
            # Search group names
            return f'name in ("{query}")'

        else:  # BOTH
            # Will require separate queries
            raise QueryBuildError(
                "Cannot build single query for BOTH search type. "
                "Use separate queries for indicators and groups."
            )

    @staticmethod
    def build_filtered_query(
        base_query: Optional[str],
        filters: SearchFilters,
        search_type: SearchType = SearchType.INDICATORS
    ) -> str:
        """
        Build TQL query with filters applied.

        Args:
            base_query: Base TQL query or None
            filters: Search filters to apply
            search_type: Type of search

        Returns:
            TQL query string with filters

        Examples:
            >>> filters = SearchFilters(rating_min=3.0, confidence_min=80)
            >>> TQLQueryBuilder.build_filtered_query(None, filters)
            'rating > 3.0 and confidence > 80'
        """
        conditions = []

        # Add base query
        if base_query:
            conditions.append(f"({base_query})")

        # Apply type filters
        if search_type == SearchType.INDICATORS and filters.indicator_types:
            type_list = '", "'.join(filters.indicator_types)
            conditions.append(f'typeName in ("{type_list}")')
        elif search_type == SearchType.GROUPS and filters.group_types:
            type_list = '", "'.join(filters.group_types)
            conditions.append(f'typeName in ("{type_list}")')

        # Apply rating filters
        if filters.rating_min is not None:
            conditions.append(f"rating >= {filters.rating_min}")
        if filters.rating_max is not None:
            conditions.append(f"rating <= {filters.rating_max}")

        # Apply confidence filters
        if filters.confidence_min is not None:
            conditions.append(f"confidence >= {filters.confidence_min}")
        if filters.confidence_max is not None:
            conditions.append(f"confidence <= {filters.confidence_max}")

        # Apply date filters
        if filters.date_added_after:
            conditions.append(f'dateAdded > "{filters.date_added_after}"')
        if filters.date_added_before:
            conditions.append(f'dateAdded < "{filters.date_added_before}"')

        # Apply tag filters
        if filters.tags:
            for tag in filters.tags:
                conditions.append(f'tag in ("{tag}")')

        if not conditions:
            raise QueryBuildError("No query or filters provided")

        # Join all conditions with AND
        return " and ".join(conditions)

    @staticmethod
    def validate_tql(query: str) -> bool:
        """
        Validate TQL query syntax (basic validation).

        Args:
            query: TQL query string

        Returns:
            True if query appears valid

        Raises:
            QueryBuildError: If query is invalid
        """
        if not query or not query.strip():
            raise QueryBuildError("Query cannot be empty")

        # Basic syntax checks
        if query.count('"') % 2 != 0:
            raise QueryBuildError("Unmatched quotes in query")

        if query.count('(') != query.count(')'):
            raise QueryBuildError("Unmatched parentheses in query")

        return True

    @staticmethod
    def encode_for_url(query: str) -> str:
        """
        Encode TQL query for URL parameter.

        Args:
            query: TQL query string

        Returns:
            URL-encoded query string
        """
        return urllib.parse.quote(query)
```

### 3. `tc_tui/search/engine.py`

Main search orchestrator:

```python
"""Search engine for ThreatConnect."""

import logging
from typing import Optional

from ..models import SearchRequest, SearchResult, SearchType
from ..api import ThreatConnectClient, IndicatorsAPI, GroupsAPI
from ..utils import Validators
from .query_builder import TQLQueryBuilder
from .exceptions import SearchError, InvalidQueryError, SearchExecutionError

logger = logging.getLogger(__name__)


class SearchEngine:
    """Orchestrates searches across ThreatConnect API."""

    def __init__(self, client: ThreatConnectClient):
        """
        Initialize search engine.

        Args:
            client: ThreatConnect API client
        """
        self.client = client
        self.indicators_api = IndicatorsAPI(client)
        self.groups_api = GroupsAPI(client)
        self.query_builder = TQLQueryBuilder()

    async def search(self, request: SearchRequest) -> SearchResult:
        """
        Execute search based on request.

        Args:
            request: Search request with query and parameters

        Returns:
            SearchResult with data and pagination

        Raises:
            SearchError: If search fails
        """
        logger.info(
            f"Executing {request.search_type} search: "
            f"query='{request.query}', page={request.page}, "
            f"use_tql={request.use_tql}"
        )

        try:
            if request.search_type == SearchType.BOTH:
                return await self._search_both(request)
            elif request.search_type == SearchType.INDICATORS:
                return await self._search_indicators(request)
            elif request.search_type == SearchType.GROUPS:
                return await self._search_groups(request)
            else:
                raise InvalidQueryError(f"Unknown search type: {request.search_type}")

        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise SearchExecutionError(f"Search execution failed: {e}") from e

    async def _search_indicators(self, request: SearchRequest) -> SearchResult:
        """
        Search indicators.

        Args:
            request: Search request

        Returns:
            SearchResult with indicators
        """
        # Build TQL query
        tql = self._build_query(request, SearchType.INDICATORS)

        logger.debug(f"Indicator TQL: {tql}")

        # Calculate pagination
        result_start = request.page * request.page_size
        result_limit = request.page_size

        # Get owner from filters
        owner = None
        if request.filters and request.filters.owner:
            owner = request.filters.owner

        # Execute search
        result = await self.indicators_api.search(
            tql=tql,
            result_start=result_start,
            result_limit=result_limit,
            owner=owner,
            include_tags=True,
            include_attributes=False
        )

        return result

    async def _search_groups(self, request: SearchRequest) -> SearchResult:
        """
        Search groups.

        Args:
            request: Search request

        Returns:
            SearchResult with groups
        """
        # Build TQL query
        tql = self._build_query(request, SearchType.GROUPS)

        logger.debug(f"Group TQL: {tql}")

        # Calculate pagination
        result_start = request.page * request.page_size
        result_limit = request.page_size

        # Get owner from filters
        owner = None
        if request.filters and request.filters.owner:
            owner = request.filters.owner

        # Execute search
        result = await self.groups_api.search(
            tql=tql,
            result_start=result_start,
            result_limit=result_limit,
            owner=owner,
            include_tags=True,
            include_attributes=False
        )

        return result

    async def _search_both(self, request: SearchRequest) -> SearchResult:
        """
        Search both indicators and groups.

        Args:
            request: Search request

        Returns:
            SearchResult with combined results

        Note:
            This executes two separate searches and combines results.
            Pagination applies to combined results.
        """
        # Create separate requests
        indicators_request = SearchRequest(
            query=request.query,
            search_type=SearchType.INDICATORS,
            filters=request.filters,
            page=request.page,
            page_size=request.page_size // 2,  # Split page size
            use_tql=request.use_tql
        )

        groups_request = SearchRequest(
            query=request.query,
            search_type=SearchType.GROUPS,
            filters=request.filters,
            page=request.page,
            page_size=request.page_size // 2,  # Split page size
            use_tql=request.use_tql
        )

        # Execute both searches
        indicators_result = await self._search_indicators(indicators_request)
        groups_result = await self._search_groups(groups_request)

        # Combine results
        combined_data = indicators_result.data + groups_result.data

        # Combine pagination info
        total_results = (
            indicators_result.pagination.total_results +
            groups_result.pagination.total_results
        )

        from ..models import PaginationInfo

        combined_pagination = PaginationInfo(
            count=total_results,
            current_page=request.page,
            page_size=request.page_size,
            total_pages=(total_results + request.page_size - 1) // request.page_size,
            has_next=indicators_result.pagination.has_next or groups_result.pagination.has_next,
            has_previous=request.page > 0
        )

        return SearchResult(
            data=combined_data,
            pagination=combined_pagination,
            search_type="both",
            query=request.query
        )

    def _build_query(self, request: SearchRequest, search_type: SearchType) -> str:
        """
        Build TQL query from request.

        Args:
            request: Search request
            search_type: Type of search (overrides request.search_type)

        Returns:
            TQL query string
        """
        # If user provided TQL directly
        if request.use_tql:
            query = request.query
            self.query_builder.validate_tql(query)
        else:
            # Check if query looks like TQL
            if Validators.is_tql_query(request.query):
                query = request.query
                self.query_builder.validate_tql(query)
            else:
                # Build simple query
                query = self.query_builder.build_simple_query(
                    request.query,
                    search_type=search_type,
                    auto_detect_type=True
                )

        # Apply filters if present
        if request.filters:
            query = self.query_builder.build_filtered_query(
                base_query=query,
                filters=request.filters,
                search_type=search_type
            )

        return query

    async def get_indicator_details(
        self,
        indicator_id: int,
        include_associations: bool = True
    ):
        """
        Get detailed information about an indicator.

        Args:
            indicator_id: Indicator ID
            include_associations: Include associated groups/indicators

        Returns:
            Indicator with details and associations
        """
        indicator = await self.indicators_api.get_by_id(
            indicator_id,
            include_tags=True,
            include_attributes=True
        )

        if include_associations:
            # Get associations
            associations = await self.indicators_api.get_associations(indicator_id)
            # Note: associations would need to be added to the Indicator model
            # For now, just return the indicator
            pass

        return indicator

    async def get_group_details(
        self,
        group_id: int,
        include_associations: bool = True
    ):
        """
        Get detailed information about a group.

        Args:
            group_id: Group ID
            include_associations: Include associated indicators/groups

        Returns:
            Group with details and associations
        """
        group = await self.groups_api.get_by_id(
            group_id,
            include_tags=True,
            include_attributes=True
        )

        return group
```

### 4. `tc_tui/search/__init__.py`

Public exports:

```python
"""Search engine module."""

from .engine import SearchEngine
from .query_builder import TQLQueryBuilder
from .exceptions import (
    SearchError,
    InvalidQueryError,
    QueryBuildError,
    SearchExecutionError
)

__all__ = [
    "SearchEngine",
    "TQLQueryBuilder",
    "SearchError",
    "InvalidQueryError",
    "QueryBuildError",
    "SearchExecutionError",
]
```

## Testing Requirements

### Test File: `tests/test_search/test_query_builder.py`

```python
"""Tests for TQL query builder."""

import pytest
from tc_tui.search import TQLQueryBuilder, QueryBuildError
from tc_tui.models import SearchFilters, SearchType


def test_build_simple_ipv4_query():
    """Test building query for IPv4 address."""
    query = TQLQueryBuilder.build_simple_query("192.168.1.1")

    assert 'typeName in ("Address")' in query
    assert 'summary in ("192.168.1.1")' in query


def test_build_simple_email_query():
    """Test building query for email address."""
    query = TQLQueryBuilder.build_simple_query("evil@bad.com")

    assert 'typeName in ("EmailAddress")' in query
    assert 'summary in ("evil@bad.com")' in query


def test_build_simple_host_query():
    """Test building query for hostname."""
    query = TQLQueryBuilder.build_simple_query("evil.com")

    assert 'typeName in ("Host")' in query
    assert 'summary in ("evil.com")' in query


def test_build_simple_hash_query():
    """Test building query for file hash."""
    query = TQLQueryBuilder.build_simple_query(
        "5d41402abc4b2a76b9719d911017c592"
    )

    assert 'typeName in ("File")' in query


def test_build_query_without_type_detection():
    """Test building query without type detection."""
    query = TQLQueryBuilder.build_simple_query(
        "something",
        auto_detect_type=False
    )

    assert 'summary in ("something")' in query
    assert "typeName" not in query


def test_build_filtered_query_with_rating():
    """Test building query with rating filter."""
    filters = SearchFilters(rating_min=3.0, rating_max=5.0)

    query = TQLQueryBuilder.build_filtered_query(
        base_query='typeName in ("Address")',
        filters=filters
    )

    assert "rating >= 3.0" in query
    assert "rating <= 5.0" in query
    assert 'typeName in ("Address")' in query


def test_build_filtered_query_with_confidence():
    """Test building query with confidence filter."""
    filters = SearchFilters(confidence_min=80, confidence_max=100)

    query = TQLQueryBuilder.build_filtered_query(
        base_query=None,
        filters=filters
    )

    assert "confidence >= 80" in query
    assert "confidence <= 100" in query


def test_build_filtered_query_with_dates():
    """Test building query with date filters."""
    filters = SearchFilters(
        date_added_after="2024-01-01",
        date_added_before="2024-12-31"
    )

    query = TQLQueryBuilder.build_filtered_query(
        base_query=None,
        filters=filters
    )

    assert 'dateAdded > "2024-01-01"' in query
    assert 'dateAdded < "2024-12-31"' in query


def test_build_filtered_query_with_types():
    """Test building query with type filters."""
    filters = SearchFilters(indicator_types=["Address", "Host"])

    query = TQLQueryBuilder.build_filtered_query(
        base_query=None,
        filters=filters,
        search_type=SearchType.INDICATORS
    )

    assert 'typeName in ("Address", "Host")' in query


def test_build_filtered_query_with_tags():
    """Test building query with tag filters."""
    filters = SearchFilters(tags=["malware", "c2"])

    query = TQLQueryBuilder.build_filtered_query(
        base_query=None,
        filters=filters
    )

    assert 'tag in ("malware")' in query
    assert 'tag in ("c2")' in query


def test_validate_tql_valid_query():
    """Test TQL validation with valid query."""
    query = 'typeName in ("Address") and summary in ("192.168.1.1")'

    assert TQLQueryBuilder.validate_tql(query) is True


def test_validate_tql_unmatched_quotes():
    """Test TQL validation with unmatched quotes."""
    query = 'typeName in ("Address) and summary in ("test")'

    with pytest.raises(QueryBuildError, match="Unmatched quotes"):
        TQLQueryBuilder.validate_tql(query)


def test_validate_tql_unmatched_parentheses():
    """Test TQL validation with unmatched parentheses."""
    query = 'typeName in ("Address") and (summary in ("test")'

    with pytest.raises(QueryBuildError, match="Unmatched parentheses"):
        TQLQueryBuilder.validate_tql(query)


def test_validate_tql_empty_query():
    """Test TQL validation with empty query."""
    with pytest.raises(QueryBuildError, match="cannot be empty"):
        TQLQueryBuilder.validate_tql("")


def test_encode_for_url():
    """Test URL encoding of TQL query."""
    query = 'typeName in ("Address")'
    encoded = TQLQueryBuilder.encode_for_url(query)

    assert "%" in encoded  # Should be URL encoded
    assert '"' not in encoded  # Quotes should be encoded
```

### Test File: `tests/test_search/test_engine.py`

```python
"""Tests for search engine."""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from tc_tui.search import SearchEngine
from tc_tui.models import (
    SearchRequest,
    SearchType,
    SearchFilters,
    SearchResult,
    PaginationInfo
)


@pytest.fixture
def mock_client():
    """Create mock ThreatConnect client."""
    client = Mock()
    client.instance = "test"
    return client


@pytest.fixture
def search_engine(mock_client):
    """Create search engine with mock client."""
    return SearchEngine(mock_client)


@pytest.mark.asyncio
async def test_search_indicators(search_engine, mock_client):
    """Test indicator search."""
    # Mock API response
    mock_result = SearchResult(
        data=[],
        pagination=PaginationInfo(
            count=0,
            current_page=0,
            page_size=100,
            total_pages=0,
            has_next=False,
            has_previous=False
        ),
        search_type="indicators",
        query="192.168.1.1"
    )

    search_engine.indicators_api.search = AsyncMock(return_value=mock_result)

    # Create request
    request = SearchRequest(
        query="192.168.1.1",
        search_type=SearchType.INDICATORS
    )

    # Execute search
    result = await search_engine.search(request)

    # Verify
    assert result.search_type == "indicators"
    search_engine.indicators_api.search.assert_called_once()


@pytest.mark.asyncio
async def test_search_with_filters(search_engine):
    """Test search with filters."""
    # Mock API response
    mock_result = SearchResult(
        data=[],
        pagination=PaginationInfo(
            count=0,
            current_page=0,
            page_size=100,
            total_pages=0,
            has_next=False,
            has_previous=False
        ),
        search_type="indicators",
        query="192.168.1.1"
    )

    search_engine.indicators_api.search = AsyncMock(return_value=mock_result)

    # Create request with filters
    filters = SearchFilters(rating_min=3.0, confidence_min=80)
    request = SearchRequest(
        query="192.168.1.1",
        search_type=SearchType.INDICATORS,
        filters=filters
    )

    # Execute search
    result = await search_engine.search(request)

    # Verify
    assert result is not None
    search_engine.indicators_api.search.assert_called_once()


@pytest.mark.asyncio
async def test_search_with_tql(search_engine):
    """Test search with TQL query."""
    mock_result = SearchResult(
        data=[],
        pagination=PaginationInfo(
            count=0,
            current_page=0,
            page_size=100,
            total_pages=0,
            has_next=False,
            has_previous=False
        ),
        search_type="indicators",
        query='typeName in ("Address")'
    )

    search_engine.indicators_api.search = AsyncMock(return_value=mock_result)

    # Create request with TQL
    request = SearchRequest(
        query='typeName in ("Address") and rating > 3',
        search_type=SearchType.INDICATORS,
        use_tql=True
    )

    # Execute search
    result = await search_engine.search(request)

    # Verify
    assert result is not None


@pytest.mark.asyncio
async def test_search_groups(search_engine):
    """Test group search."""
    mock_result = SearchResult(
        data=[],
        pagination=PaginationInfo(
            count=0,
            current_page=0,
            page_size=100,
            total_pages=0,
            has_next=False,
            has_previous=False
        ),
        search_type="groups",
        query="APT"
    )

    search_engine.groups_api.search = AsyncMock(return_value=mock_result)

    # Create request
    request = SearchRequest(
        query="APT",
        search_type=SearchType.GROUPS
    )

    # Execute search
    result = await search_engine.search(request)

    # Verify
    assert result.search_type == "groups"
    search_engine.groups_api.search.assert_called_once()


@pytest.mark.asyncio
async def test_get_indicator_details(search_engine):
    """Test getting indicator details."""
    from tc_tui.models import Indicator

    mock_indicator = Indicator(
        id=123,
        type="Address",
        summary="192.168.1.1",
        dateAdded="2024-01-01T00:00:00Z",
        ownerId=1,
        ownerName="Test"
    )

    search_engine.indicators_api.get_by_id = AsyncMock(return_value=mock_indicator)

    # Get details
    result = await search_engine.get_indicator_details(123)

    # Verify
    assert result.id == 123
    assert result.summary == "192.168.1.1"
```

## Acceptance Criteria

- [ ] All search methods implemented with proper type hints
- [ ] TQL query builder handles all filter types
- [ ] Auto-detection of indicator types working
- [ ] Simple queries and TQL queries both supported
- [ ] Pagination parameters calculated correctly
- [ ] Combined search (BOTH) works correctly
- [ ] Error handling for invalid queries
- [ ] Tests pass with >85% coverage
- [ ] Async methods work correctly
- [ ] Query validation prevents injection

## Integration Points

- **Uses**: Module 2 (API Client) for making API calls
- **Uses**: Module 1 (Data Models) for request/response types
- **Uses**: Module 4 (Utilities) for validators and type detection
- **Used By**: Module 7 (Widgets) for executing searches
- **Used By**: Module 8 (Screens) for search orchestration

## Notes

- All API methods use async/await pattern for future async support
- Query builder validates TQL syntax before submission
- Search engine logs all queries at DEBUG level
- Support for both simple (summary) and advanced (TQL) searches
- Auto-detection uses validators from utilities module
- Combined search splits page size between indicators and groups

## References

- [TQL Documentation](https://knowledge.threatconnect.com/docs/threatconnect-query-language-tql)
- [TQL Operators](https://knowledge.threatconnect.com/docs/tql-operators-and-parameters)
- [API v3 Filter Results](https://docs.threatconnect.com/en/latest/rest_api/v3/filter_results.html)

## Examples

### Simple Search

```python
from tc_tui.search import SearchEngine
from tc_tui.models import SearchRequest, SearchType

# Create search request
request = SearchRequest(
    query="192.168.1.1",
    search_type=SearchType.INDICATORS
)

# Execute search
result = await engine.search(request)
print(f"Found {result.pagination.total_results} indicators")
```

### Search with Filters

```python
from tc_tui.models import SearchFilters

# Create filters
filters = SearchFilters(
    rating_min=3.0,
    confidence_min=80,
    tags=["malware"]
)

# Create request
request = SearchRequest(
    query="evil.com",
    search_type=SearchType.INDICATORS,
    filters=filters
)

result = await engine.search(request)
```

### TQL Search

```python
# Direct TQL query
request = SearchRequest(
    query='typeName in ("Address", "Host") and rating > 3 and dateAdded > "2024-01-01"',
    search_type=SearchType.INDICATORS,
    use_tql=True
)

result = await engine.search(request)
```

---

**Status**: Ready to Start
**Branch**: `module/5-search-engine`
**Estimated Completion**: 5-6 hours
