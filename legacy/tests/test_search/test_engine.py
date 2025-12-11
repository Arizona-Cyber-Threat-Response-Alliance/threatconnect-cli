"""Tests for search engine."""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from tc_tui.search import SearchEngine, SearchExecutionError
from tc_tui.models import (
    SearchRequest,
    SearchType,
    SearchFilters,
    SearchResult,
    PaginationInfo,
    Indicator,
    Group
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


@pytest.fixture
def mock_indicator():
    """Create mock indicator."""
    return Indicator(
        id=1,
        type="Address",
        summary="192.168.1.1",
        dateAdded="2024-01-01T00:00:00Z",
        lastModified="2024-01-01T00:00:00Z",
        ownerId=1,
        ownerName="Test",
        webLink="https://test.threatconnect.com/indicators/1"
    )


@pytest.fixture
def mock_group():
    """Create mock group."""
    return Group(
        id=1,
        type="Adversary",
        name="APT29",
        dateAdded="2024-01-01T00:00:00Z",
        lastModified="2024-01-01T00:00:00Z",
        ownerId=1,
        ownerName="Test",
        webLink="https://test.threatconnect.com/groups/1"
    )


@pytest.fixture
def mock_pagination():
    """Create mock pagination info."""
    return PaginationInfo(
        count=10,
        current_page=0,
        page_size=100,
        total_pages=1,
        has_next=False,
        has_previous=False
    )


@pytest.mark.asyncio
async def test_search_indicators(search_engine, mock_indicator, mock_pagination):
    """Test indicator search."""
    # Mock API response
    mock_result = SearchResult(
        data=[mock_indicator],
        pagination=mock_pagination,
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
    assert len(result.data) == 1
    assert result.data[0].summary == "192.168.1.1"
    search_engine.indicators_api.search.assert_called_once()


@pytest.mark.asyncio
async def test_search_groups(search_engine, mock_group, mock_pagination):
    """Test group search."""
    mock_result = SearchResult(
        data=[mock_group],
        pagination=mock_pagination,
        search_type="groups",
        query="APT29"
    )

    search_engine.groups_api.search = AsyncMock(return_value=mock_result)

    # Create request
    request = SearchRequest(
        query="APT29",
        search_type=SearchType.GROUPS
    )

    # Execute search
    result = await search_engine.search(request)

    # Verify
    assert result.search_type == "groups"
    assert len(result.data) == 1
    assert result.data[0].name == "APT29"
    search_engine.groups_api.search.assert_called_once()


@pytest.mark.asyncio
async def test_search_with_filters(search_engine, mock_indicator, mock_pagination):
    """Test search with filters."""
    # Mock API response
    mock_result = SearchResult(
        data=[mock_indicator],
        pagination=mock_pagination,
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

    # Check that the API was called with a TQL query containing filters
    call_args = search_engine.indicators_api.search.call_args
    tql = call_args.kwargs['tql']
    assert "rating >= 3.0" in tql
    assert "confidence >= 80" in tql


@pytest.mark.asyncio
async def test_search_with_tql(search_engine, mock_indicator, mock_pagination):
    """Test search with TQL query."""
    mock_result = SearchResult(
        data=[mock_indicator],
        pagination=mock_pagination,
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
    search_engine.indicators_api.search.assert_called_once()


@pytest.mark.asyncio
async def test_search_with_owner_filter(search_engine, mock_indicator, mock_pagination):
    """Test search with owner filter."""
    mock_result = SearchResult(
        data=[mock_indicator],
        pagination=mock_pagination,
        search_type="indicators",
        query="192.168.1.1"
    )

    search_engine.indicators_api.search = AsyncMock(return_value=mock_result)

    # Create request with owner filter
    filters = SearchFilters(owner="TestOrg")
    request = SearchRequest(
        query="192.168.1.1",
        search_type=SearchType.INDICATORS,
        filters=filters
    )

    # Execute search
    result = await search_engine.search(request)

    # Verify owner was passed to API
    call_args = search_engine.indicators_api.search.call_args
    assert call_args.kwargs['owner'] == "TestOrg"


@pytest.mark.asyncio
async def test_search_pagination(search_engine, mock_indicator):
    """Test search with pagination."""
    pagination = PaginationInfo(
        count=250,
        current_page=2,
        page_size=100,
        total_pages=3,
        has_next=True,
        has_previous=True
    )

    mock_result = SearchResult(
        data=[mock_indicator],
        pagination=pagination,
        search_type="indicators",
        query="test"
    )

    search_engine.indicators_api.search = AsyncMock(return_value=mock_result)

    # Create request for page 2
    request = SearchRequest(
        query="test",
        search_type=SearchType.INDICATORS,
        page=2,
        page_size=100
    )

    # Execute search
    result = await search_engine.search(request)

    # Verify pagination parameters
    call_args = search_engine.indicators_api.search.call_args
    assert call_args.kwargs['result_start'] == 200  # page 2 * page_size 100
    assert call_args.kwargs['result_limit'] == 100


@pytest.mark.asyncio
async def test_search_both(search_engine, mock_indicator, mock_group, mock_pagination):
    """Test combined search for both indicators and groups."""
    # Mock indicator result
    indicator_result = SearchResult(
        data=[mock_indicator],
        pagination=mock_pagination,
        search_type="indicators",
        query="test"
    )

    # Mock group result
    group_result = SearchResult(
        data=[mock_group],
        pagination=mock_pagination,
        search_type="groups",
        query="test"
    )

    search_engine.indicators_api.search = AsyncMock(return_value=indicator_result)
    search_engine.groups_api.search = AsyncMock(return_value=group_result)

    # Create request
    request = SearchRequest(
        query="test",
        search_type=SearchType.BOTH,
        page_size=100
    )

    # Execute search
    result = await search_engine.search(request)

    # Verify both APIs were called
    search_engine.indicators_api.search.assert_called_once()
    search_engine.groups_api.search.assert_called_once()

    # Verify combined results
    assert result.search_type == "both"
    assert len(result.data) == 2
    assert result.pagination.total_results == 20  # 10 + 10 from mock_pagination


@pytest.mark.asyncio
async def test_search_auto_detects_tql(search_engine, mock_indicator, mock_pagination):
    """Test that search auto-detects TQL queries."""
    mock_result = SearchResult(
        data=[mock_indicator],
        pagination=mock_pagination,
        search_type="indicators",
        query="typeName in (\"Address\")"
    )

    search_engine.indicators_api.search = AsyncMock(return_value=mock_result)

    # Create request with TQL-like query but use_tql=False
    request = SearchRequest(
        query='typeName in ("Address")',
        search_type=SearchType.INDICATORS,
        use_tql=False  # Should be auto-detected as TQL
    )

    # Execute search
    result = await search_engine.search(request)

    # Verify
    assert result is not None
    # The query should be passed through as-is since it looks like TQL
    call_args = search_engine.indicators_api.search.call_args
    tql = call_args.kwargs['tql']
    assert "typeName" in tql


@pytest.mark.asyncio
async def test_get_indicator_details(search_engine, mock_indicator):
    """Test getting indicator details."""
    search_engine.indicators_api.get_by_id = AsyncMock(return_value=mock_indicator)
    search_engine.indicators_api.get_associations = AsyncMock(return_value=[])

    # Get details
    result = await search_engine.get_indicator_details(123)

    # Verify
    assert result.id == 1
    assert result.summary == "192.168.1.1"
    search_engine.indicators_api.get_by_id.assert_called_once_with(
        123,
        include_tags=True,
        include_attributes=True
    )


@pytest.mark.asyncio
async def test_get_group_details(search_engine, mock_group):
    """Test getting group details."""
    search_engine.groups_api.get_by_id = AsyncMock(return_value=mock_group)

    # Get details
    result = await search_engine.get_group_details(456)

    # Verify
    assert result.id == 1
    assert result.name == "APT29"
    search_engine.groups_api.get_by_id.assert_called_once_with(
        456,
        include_tags=True,
        include_attributes=True
    )


@pytest.mark.asyncio
async def test_search_handles_api_error(search_engine):
    """Test that search handles API errors gracefully."""
    # Mock API to raise an exception
    search_engine.indicators_api.search = AsyncMock(
        side_effect=Exception("API Error")
    )

    # Create request
    request = SearchRequest(
        query="test",
        search_type=SearchType.INDICATORS
    )

    # Execute search and expect error
    with pytest.raises(SearchExecutionError):
        await search_engine.search(request)


@pytest.mark.asyncio
async def test_search_includes_tags(search_engine, mock_indicator, mock_pagination):
    """Test that search includes tags."""
    mock_result = SearchResult(
        data=[mock_indicator],
        pagination=mock_pagination,
        search_type="indicators",
        query="test"
    )

    search_engine.indicators_api.search = AsyncMock(return_value=mock_result)

    request = SearchRequest(
        query="test",
        search_type=SearchType.INDICATORS
    )

    await search_engine.search(request)

    # Verify that include_tags=True was passed
    call_args = search_engine.indicators_api.search.call_args
    assert call_args.kwargs['include_tags'] is True


@pytest.mark.asyncio
async def test_build_query_simple(search_engine):
    """Test _build_query with simple query."""
    request = SearchRequest(
        query="192.168.1.1",
        search_type=SearchType.INDICATORS,
        use_tql=False
    )

    query = search_engine._build_query(request, SearchType.INDICATORS)

    assert 'summary in ("192.168.1.1")' in query
    assert 'typeName in ("Address")' in query


@pytest.mark.asyncio
async def test_build_query_with_filters(search_engine):
    """Test _build_query with filters."""
    filters = SearchFilters(rating_min=3.0)
    request = SearchRequest(
        query="test",
        search_type=SearchType.INDICATORS,
        filters=filters,
        use_tql=False
    )

    query = search_engine._build_query(request, SearchType.INDICATORS)

    assert "rating >= 3.0" in query
