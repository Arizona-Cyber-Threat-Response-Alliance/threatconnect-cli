"""Tests for search models."""

import pytest
from tc_tui.models import SearchRequest, SearchType, SearchFilters, PaginationInfo, SearchResult, Indicator


def test_search_request_creation():
    """Test creating a search request."""
    request = SearchRequest(
        query="192.168.1.1",
        search_type=SearchType.INDICATORS,
        page=0,
        page_size=100
    )

    assert request.query == "192.168.1.1"
    assert request.search_type == SearchType.INDICATORS
    assert request.page == 0
    assert request.page_size == 100
    assert request.use_tql is False


def test_search_request_with_filters():
    """Test search request with filters."""
    filters = SearchFilters(
        rating_min=3.0,
        confidence_min=80,
        tags=["malware", "c2"]
    )

    request = SearchRequest(
        query='typeName in ("Address")',
        search_type=SearchType.INDICATORS,
        filters=filters,
        use_tql=True
    )

    assert request.filters.rating_min == 3.0
    assert request.filters.confidence_min == 80
    assert len(request.filters.tags) == 2


def test_pagination_info():
    """Test pagination info."""
    pagination = PaginationInfo(
        count=250,
        current_page=1,
        page_size=100,
        total_pages=3,
        has_next=True,
        has_previous=False
    )

    assert pagination.total_results == 250
    assert pagination.current_page == 1
    assert pagination.total_pages == 3
    assert pagination.has_next is True
    assert pagination.has_previous is False


def test_search_type_enum():
    """Test search type enum."""
    assert SearchType.INDICATORS == "indicators"
    assert SearchType.GROUPS == "groups"
    assert SearchType.BOTH == "both"


def test_search_filters_defaults():
    """Test search filters with defaults."""
    filters = SearchFilters()

    assert filters.owner is None
    assert filters.rating_min is None
    assert filters.rating_max is None
    assert filters.confidence_min is None
    assert filters.confidence_max is None
    assert filters.tags == []
    assert filters.indicator_types == []
    assert filters.group_types == []


def test_search_result_with_indicators():
    """Test search result with indicators."""
    indicator_data = {
        "id": 1,
        "type": "Address",
        "summary": "192.168.1.1",
        "rating": 3.0,
        "confidence": 85,
        "dateAdded": "2024-01-15T14:32:10Z",
        "lastModified": "2025-11-22T09:15:43Z",
        "ownerName": "MyOrg",
        "ownerId": 1,
        "webLink": "https://example.com"
    }

    pagination = PaginationInfo(
        count=1,
        current_page=0,
        page_size=100,
        total_pages=1,
        has_next=False,
        has_previous=False
    )

    result = SearchResult(
        data=[Indicator(**indicator_data)],
        pagination=pagination,
        search_type=SearchType.INDICATORS,
        query="192.168.1.1"
    )

    assert len(result.data) == 1
    assert len(result.indicators) == 1
    assert len(result.groups) == 0
    assert result.query == "192.168.1.1"


def test_search_request_page_validation():
    """Test that page must be >= 0."""
    with pytest.raises(ValueError):
        SearchRequest(
            query="test",
            search_type=SearchType.INDICATORS,
            page=-1
        )


def test_search_request_page_size_validation():
    """Test that page_size must be between 1 and 10000."""
    with pytest.raises(ValueError):
        SearchRequest(
            query="test",
            search_type=SearchType.INDICATORS,
            page_size=0
        )

    with pytest.raises(ValueError):
        SearchRequest(
            query="test",
            search_type=SearchType.INDICATORS,
            page_size=10001
        )


def test_search_filters_rating_validation():
    """Test that rating min/max must be between 0 and 5."""
    with pytest.raises(ValueError):
        SearchFilters(rating_min=6.0)

    with pytest.raises(ValueError):
        SearchFilters(rating_max=-1.0)


def test_search_filters_confidence_validation():
    """Test that confidence min/max must be between 0 and 100."""
    with pytest.raises(ValueError):
        SearchFilters(confidence_min=101)

    with pytest.raises(ValueError):
        SearchFilters(confidence_max=-1)
