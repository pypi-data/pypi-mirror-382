"""Locations resource for viewing facility locations."""

from typing import Any, Dict, Optional

from distru_sdk.resources.base import BaseResource, PaginatedResponse


class LocationsResource(BaseResource):
    """Resource for viewing locations in the Distru API.

    Locations represent physical facilities, warehouses, or stores where
    inventory is stored and transactions occur. Location data is read-only
    via the API.

    Example:
        >>> locations = client.locations.list()
        >>> for location in locations.auto_paginate():
        ...     print(f"{location['name']} - {location['city']}, {location['state']}")
    """

    def list(
        self,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        search: Optional[str] = None,
        state: Optional[str] = None,
        include_inactive: Optional[bool] = None,
        **params: Any,
    ) -> PaginatedResponse[Dict[str, Any]]:
        """List all locations.

        Args:
            page: Page number (default: 1)
            limit: Number of items per page (default: 5000, max: 5000)
            search: Search by location name or address
            state: Filter by US state code (e.g., "CA", "CO")
            include_inactive: Include inactive locations
            **params: Additional query parameters

        Returns:
            Paginated list of locations

        Example:
            >>> # Get all locations
            >>> locations = client.locations.list()
            >>>
            >>> # Search locations
            >>> locations = client.locations.list(search="warehouse")
            >>>
            >>> # Filter by state
            >>> locations = client.locations.list(state="CA")
            >>>
            >>> # Include inactive locations
            >>> locations = client.locations.list(include_inactive=True)
        """
        query_params: Dict[str, Any] = {
            **params,
        }

        if page is not None:
            query_params["page"] = page
        if limit is not None:
            query_params["limit"] = limit
        if search is not None:
            query_params["search"] = search
        if state is not None:
            query_params["state"] = state
        if include_inactive is not None:
            query_params["include_inactive"] = include_inactive

        response_data = self._get("/locations", params=query_params)

        return self._create_paginated_response(
            data=response_data.get("data", []),
            next_page=response_data.get("next_page"),
            params=query_params,
        )

    def get(self, location_id: int) -> Dict[str, Any]:
        """Get a specific location by ID.

        Args:
            location_id: Location ID

        Returns:
            Location data including name, address, and contact information

        Raises:
            NotFoundError: If location not found

        Example:
            >>> location = client.locations.get(5)
            >>> print(f"{location['name']}")
            >>> print(f"{location['street_address']}")
            >>> print(f"{location['city']}, {location['state']} {location['zip']}")
        """
        return self._get(f"/locations/{location_id}")

    def _fetch_next_page(
        self,
        page_identifier: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> PaginatedResponse[Dict[str, Any]]:
        """Fetch next page of locations."""
        next_params = (params or {}).copy()
        next_params["page"] = page_identifier
        return self.list(**next_params)
