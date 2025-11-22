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
