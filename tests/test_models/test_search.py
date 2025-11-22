"""Tests for search models."""

import pytest
from tc_tui.models import SearchRequest, SearchType, SearchFilters, PaginationInfo


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
    """Test SearchType enum values."""
    assert SearchType.INDICATORS == "indicators"
    assert SearchType.GROUPS == "groups"
    assert SearchType.BOTH == "both"
