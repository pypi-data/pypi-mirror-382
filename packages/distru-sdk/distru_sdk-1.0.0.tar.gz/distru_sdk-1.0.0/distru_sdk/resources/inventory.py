"""Inventory resource for viewing inventory levels."""

from typing import Any, Dict, Optional

from distru_sdk.resources.base import BaseResource, PaginatedResponse


class InventoryResource(BaseResource):
    """Resource for viewing inventory in the Distru API.

    Inventory represents the current stock levels across products, batches,
    packages, and locations. Inventory data is read-only via the API and
    updated through order fulfillment, purchases, and transfers.

    Example:
        >>> inventory = client.inventory.list()
        >>> for item in inventory.auto_paginate():
        ...     print(f"{item['product_name']}: {item['quantity']} units")
        >>>
        >>> # View inventory with costs
        >>> inventory = client.inventory.list(include_costs=True)
    """

    def list(
        self,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        include_costs: Optional[bool] = None,
        product_id: Optional[str] = None,
        location_id: Optional[int] = None,
        batch_id: Optional[str] = None,
        package_id: Optional[str] = None,
        **params: Any,
    ) -> PaginatedResponse[Dict[str, Any]]:
        """List all inventory items.

        Args:
            page: Page number (default: 1)
            limit: Number of items per page (default: 5000, max: 5000)
            include_costs: Include cost information (requires appropriate permissions)
            product_id: Filter by product UUID
            location_id: Filter by location ID
            batch_id: Filter by batch UUID
            package_id: Filter by package UUID
            **params: Additional query parameters

        Returns:
            Paginated list of inventory items

        Example:
            >>> # Get all inventory
            >>> inventory = client.inventory.list()
            >>>
            >>> # Get inventory for specific product
            >>> inventory = client.inventory.list(product_id="prod-uuid-123")
            >>>
            >>> # Get inventory at specific location
            >>> inventory = client.inventory.list(location_id=5)
            >>>
            >>> # Get inventory with cost data
            >>> inventory = client.inventory.list(
            ...     product_id="prod-uuid-123",
            ...     include_costs=True
            ... )
        """
        query_params: Dict[str, Any] = {
            **params,
        }

        if page is not None:
            query_params["page"] = page
        if limit is not None:
            query_params["limit"] = limit
        if include_costs is not None:
            query_params["include_costs"] = include_costs
        if product_id is not None:
            query_params["product_id"] = product_id
        if location_id is not None:
            query_params["location_id"] = location_id
        if batch_id is not None:
            query_params["batch_id"] = batch_id
        if package_id is not None:
            query_params["package_id"] = package_id

        response_data = self._get("/inventory", params=query_params)

        return self._create_paginated_response(
            data=response_data.get("data", []),
            next_page=response_data.get("next_page"),
            params=query_params,
        )

    def get(
        self,
        product_id: Optional[str] = None,
        location_id: Optional[int] = None,
        batch_id: Optional[str] = None,
        package_id: Optional[str] = None,
        include_costs: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Get inventory summary for specific filters.

        This is a convenience method that returns aggregated inventory data
        for the specified filters.

        Args:
            product_id: Product UUID
            location_id: Location ID
            batch_id: Batch UUID
            package_id: Package UUID
            include_costs: Include cost information

        Returns:
            Inventory summary data

        Example:
            >>> # Get inventory for a product at a location
            >>> inventory = client.inventory.get(
            ...     product_id="prod-uuid-123",
            ...     location_id=5
            ... )
        """
        query_params: Dict[str, Any] = {}

        if product_id is not None:
            query_params["product_id"] = product_id
        if location_id is not None:
            query_params["location_id"] = location_id
        if batch_id is not None:
            query_params["batch_id"] = batch_id
        if package_id is not None:
            query_params["package_id"] = package_id
        if include_costs is not None:
            query_params["include_costs"] = include_costs

        return self._get("/inventory", params=query_params)

    def _fetch_next_page(
        self,
        page_identifier: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> PaginatedResponse[Dict[str, Any]]:
        """Fetch next page of inventory."""
        next_params = (params or {}).copy()
        next_params["page"] = page_identifier
        return self.list(**next_params)
