"""Packages resource for viewing inventory packages."""

from typing import Any, Dict, Optional

from distru_sdk.resources.base import BaseResource, PaginatedResponse


class PackagesResource(BaseResource):
    """Resource for viewing packages in the Distru API.

    Packages represent individual inventory units for package-tracked products,
    often corresponding to state compliance tracking tags. Package data is
    read-only via the API and managed through inventory operations.

    Example:
        >>> packages = client.packages.list()
        >>> for package in packages.auto_paginate():
        ...     print(f"{package['tag']} - {package['product_name']}")
        >>>
        >>> # Filter by product
        >>> packages = client.packages.list(product_id="prod-uuid-123")
    """

    def list(
        self,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        product_id: Optional[str] = None,
        batch_id: Optional[str] = None,
        location_id: Optional[int] = None,
        license_id: Optional[int] = None,
        status: Optional[str] = None,
        tag: Optional[str] = None,
        **params: Any,
    ) -> PaginatedResponse[Dict[str, Any]]:
        """List all packages.

        Args:
            page: Page number (default: 1)
            limit: Number of items per page (default: 5000, max: 5000)
            product_id: Filter by product UUID
            batch_id: Filter by batch UUID
            location_id: Filter by location ID
            license_id: Filter by license ID
            status: Filter by package status (e.g., "active", "sold", "destroyed")
            tag: Filter by package tag/identifier
            **params: Additional query parameters

        Returns:
            Paginated list of packages

        Example:
            >>> # Get all packages
            >>> packages = client.packages.list()
            >>>
            >>> # Filter by product
            >>> packages = client.packages.list(product_id="prod-uuid-123")
            >>>
            >>> # Filter by location
            >>> packages = client.packages.list(location_id=5)
            >>>
            >>> # Filter by status
            >>> packages = client.packages.list(status="active")
            >>>
            >>> # Find specific package by tag
            >>> packages = client.packages.list(tag="1A4060300000001000000001")
        """
        query_params: Dict[str, Any] = {
            **params,
        }

        if page is not None:
            query_params["page"] = page
        if limit is not None:
            query_params["limit"] = limit
        if product_id is not None:
            query_params["product_id"] = product_id
        if batch_id is not None:
            query_params["batch_id"] = batch_id
        if location_id is not None:
            query_params["location_id"] = location_id
        if license_id is not None:
            query_params["license_id"] = license_id
        if status is not None:
            query_params["status"] = status
        if tag is not None:
            query_params["tag"] = tag

        response_data = self._get("/packages", params=query_params)

        return self._create_paginated_response(
            data=response_data.get("data", []),
            next_page=response_data.get("next_page"),
            params=query_params,
        )

    def get(self, package_id: str) -> Dict[str, Any]:
        """Get a specific package by ID.

        Args:
            package_id: Package UUID

        Returns:
            Package data including product, batch, and location information

        Raises:
            NotFoundError: If package not found

        Example:
            >>> package = client.packages.get("pkg-uuid-123")
            >>> print(f"Package {package['tag']}: {package['quantity']} units")
        """
        return self._get(f"/packages/{package_id}")

    def _fetch_next_page(
        self,
        page_identifier: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> PaginatedResponse[Dict[str, Any]]:
        """Fetch next page of packages."""
        next_params = (params or {}).copy()
        next_params["page"] = page_identifier
        return self.list(**next_params)
