"""Search engine for ThreatConnect."""

import logging
from typing import Optional

from ..models import SearchRequest, SearchResult, SearchType, PaginationInfo
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
