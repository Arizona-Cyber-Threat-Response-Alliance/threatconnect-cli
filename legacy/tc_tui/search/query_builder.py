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
            'rating >= 3.0 and confidence >= 80'
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
