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
