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


def test_build_simple_group_query():
    """Test building query for groups."""
    query = TQLQueryBuilder.build_simple_query(
        "APT29",
        search_type=SearchType.GROUPS
    )

    assert 'name in ("APT29")' in query


def test_build_both_raises_error():
    """Test that BOTH search type raises error."""
    with pytest.raises(QueryBuildError, match="Cannot build single query"):
        TQLQueryBuilder.build_simple_query(
            "test",
            search_type=SearchType.BOTH
        )


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


def test_build_filtered_query_with_indicator_types():
    """Test building query with indicator type filters."""
    filters = SearchFilters(indicator_types=["Address", "Host"])

    query = TQLQueryBuilder.build_filtered_query(
        base_query=None,
        filters=filters,
        search_type=SearchType.INDICATORS
    )

    assert 'typeName in ("Address", "Host")' in query


def test_build_filtered_query_with_group_types():
    """Test building query with group type filters."""
    filters = SearchFilters(group_types=["Adversary", "Campaign"])

    query = TQLQueryBuilder.build_filtered_query(
        base_query=None,
        filters=filters,
        search_type=SearchType.GROUPS
    )

    assert 'typeName in ("Adversary", "Campaign")' in query


def test_build_filtered_query_with_tags():
    """Test building query with tag filters."""
    filters = SearchFilters(tags=["malware", "c2"])

    query = TQLQueryBuilder.build_filtered_query(
        base_query=None,
        filters=filters
    )

    assert 'tag in ("malware")' in query
    assert 'tag in ("c2")' in query


def test_build_filtered_query_combines_all():
    """Test building query with multiple filters."""
    filters = SearchFilters(
        rating_min=3.0,
        confidence_min=80,
        tags=["malware"]
    )

    query = TQLQueryBuilder.build_filtered_query(
        base_query='summary in ("test")',
        filters=filters
    )

    assert 'summary in ("test")' in query
    assert "rating >= 3.0" in query
    assert "confidence >= 80" in query
    assert 'tag in ("malware")' in query
    assert " and " in query


def test_build_filtered_query_no_filters_raises_error():
    """Test that empty filters raises error."""
    filters = SearchFilters()

    with pytest.raises(QueryBuildError, match="No query or filters"):
        TQLQueryBuilder.build_filtered_query(base_query=None, filters=filters)


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


def test_validate_tql_whitespace_query():
    """Test TQL validation with whitespace query."""
    with pytest.raises(QueryBuildError, match="cannot be empty"):
        TQLQueryBuilder.validate_tql("   ")


def test_encode_for_url():
    """Test URL encoding of TQL query."""
    query = 'typeName in ("Address")'
    encoded = TQLQueryBuilder.encode_for_url(query)

    assert "%" in encoded  # Should be URL encoded
    assert '"' not in encoded  # Quotes should be encoded


def test_encode_for_url_special_chars():
    """Test URL encoding with special characters."""
    query = 'typeName in ("Address") and summary in ("test@example.com")'
    encoded = TQLQueryBuilder.encode_for_url(query)

    assert "@" not in encoded  # @ should be encoded
    assert " " not in encoded  # Spaces should be encoded
