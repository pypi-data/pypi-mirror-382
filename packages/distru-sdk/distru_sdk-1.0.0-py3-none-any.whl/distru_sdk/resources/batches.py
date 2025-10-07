"""Batches resource for managing product batches."""

from typing import Any, Dict, Optional

from distru_sdk.resources.base import BaseResource, PaginatedResponse


class BatchesResource(BaseResource):
    """Resource for managing batches in the Distru API.

    Batches represent production lots for batch-tracked products, containing
    information about harvest dates, expiration dates, and batch-specific data.

    Example:
        >>> batches = client.batches.list()
        >>> for batch in batches.auto_paginate():
        ...     print(f"{batch['batch_number']} - {batch['product_name']}")

        >>> batch = client.batches.create(
        ...     product_id="prod-uuid-123",
        ...     batch_number="BATCH-2025-001",
        ...     name="Blue Dream Harvest Oct 2025",
        ...     harvest_date="2025-09-15",
        ...     expiration_date="2026-09-15"
        ... )
    """

    def list(
        self,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        product_id: Optional[str] = None,
        batch_number: Optional[str] = None,
        search: Optional[str] = None,
        include_depleted: Optional[bool] = None,
        **params: Any,
    ) -> PaginatedResponse[Dict[str, Any]]:
        """List all batches.

        Args:
            page: Page number (default: 1)
            limit: Number of items per page (default: 5000, max: 5000)
            product_id: Filter by product UUID
            batch_number: Filter by batch number
            search: Search batch names and numbers
            include_depleted: Include batches with zero inventory
            **params: Additional query parameters

        Returns:
            Paginated list of batches

        Example:
            >>> # Get all batches
            >>> batches = client.batches.list()
            >>>
            >>> # Filter by product
            >>> batches = client.batches.list(product_id="prod-uuid-123")
            >>>
            >>> # Search batches
            >>> batches = client.batches.list(search="Blue Dream")
            >>>
            >>> # Include depleted batches
            >>> batches = client.batches.list(include_depleted=True)
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
        if batch_number is not None:
            query_params["batch_number"] = batch_number
        if search is not None:
            query_params["search"] = search
        if include_depleted is not None:
            query_params["include_depleted"] = include_depleted

        response_data = self._get("/batches", params=query_params)

        return self._create_paginated_response(
            data=response_data.get("data", []),
            next_page=response_data.get("next_page"),
            params=query_params,
        )

    def get(self, batch_id: str) -> Dict[str, Any]:
        """Get a specific batch by ID.

        Args:
            batch_id: Batch UUID

        Returns:
            Batch data including inventory levels

        Raises:
            NotFoundError: If batch not found

        Example:
            >>> batch = client.batches.get("batch-uuid-123")
            >>> print(f"Batch {batch['batch_number']}: {batch['quantity']} units")
        """
        return self._get(f"/batches/{batch_id}")

    def create(
        self,
        product_id: str,
        batch_number: str,
        name: Optional[str] = None,
        expiration_date: Optional[str] = None,
        harvest_date: Optional[str] = None,
        manufactured_date: Optional[str] = None,
        thc: Optional[str] = None,
        cbd: Optional[str] = None,
        notes: Optional[str] = None,
        custom_data: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Create a new batch.

        Args:
            product_id: Product UUID (required)
            batch_number: Batch number/identifier (required)
            name: Batch name or description
            expiration_date: Expiration date in ISO format
            harvest_date: Harvest date in ISO format
            manufactured_date: Manufactured date in ISO format
            thc: THC content percentage
            cbd: CBD content percentage
            notes: Internal notes
            custom_data: Custom data dictionary
            **kwargs: Additional batch fields

        Returns:
            Created batch data

        Raises:
            ValidationError: If validation fails

        Example:
            >>> batch = client.batches.create(
            ...     product_id="prod-uuid-123",
            ...     batch_number="BATCH-2025-001",
            ...     name="Blue Dream Harvest Oct 2025",
            ...     harvest_date="2025-09-15",
            ...     expiration_date="2026-09-15",
            ...     thc="24.5",
            ...     cbd="0.8"
            ... )
        """
        batch_data: Dict[str, Any] = {
            "product_id": product_id,
            "batch_number": batch_number,
            **kwargs,
        }

        if name is not None:
            batch_data["name"] = name
        if expiration_date is not None:
            batch_data["expiration_date"] = expiration_date
        if harvest_date is not None:
            batch_data["harvest_date"] = harvest_date
        if manufactured_date is not None:
            batch_data["manufactured_date"] = manufactured_date
        if thc is not None:
            batch_data["thc"] = thc
        if cbd is not None:
            batch_data["cbd"] = cbd
        if notes is not None:
            batch_data["notes"] = notes
        if custom_data is not None:
            batch_data["custom_data"] = custom_data

        return self._post("/batches", json={"batch": batch_data})

    def update(
        self,
        batch_id: str,
        name: Optional[str] = None,
        expiration_date: Optional[str] = None,
        harvest_date: Optional[str] = None,
        manufactured_date: Optional[str] = None,
        thc: Optional[str] = None,
        cbd: Optional[str] = None,
        notes: Optional[str] = None,
        custom_data: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Update an existing batch.

        Args:
            batch_id: Batch UUID
            name: Batch name or description
            expiration_date: Expiration date
            harvest_date: Harvest date
            manufactured_date: Manufactured date
            thc: THC content percentage
            cbd: CBD content percentage
            notes: Internal notes
            custom_data: Custom data dictionary
            **kwargs: Additional fields to update

        Returns:
            Updated batch data

        Raises:
            NotFoundError: If batch not found
            ValidationError: If validation fails

        Example:
            >>> batch = client.batches.update(
            ...     "batch-uuid-123",
            ...     expiration_date="2026-12-31",
            ...     thc="25.2"
            ... )
        """
        update_data: Dict[str, Any] = {**kwargs}

        if name is not None:
            update_data["name"] = name
        if expiration_date is not None:
            update_data["expiration_date"] = expiration_date
        if harvest_date is not None:
            update_data["harvest_date"] = harvest_date
        if manufactured_date is not None:
            update_data["manufactured_date"] = manufactured_date
        if thc is not None:
            update_data["thc"] = thc
        if cbd is not None:
            update_data["cbd"] = cbd
        if notes is not None:
            update_data["notes"] = notes
        if custom_data is not None:
            update_data["custom_data"] = custom_data

        return self._patch(f"/batches/{batch_id}", json={"batch": update_data})

    def delete(self, batch_id: str) -> None:
        """Delete a batch.

        Args:
            batch_id: Batch UUID

        Raises:
            NotFoundError: If batch not found
            ValidationError: If batch cannot be deleted (e.g., has inventory)

        Example:
            >>> client.batches.delete("batch-uuid-123")
        """
        self._delete(f"/batches/{batch_id}")

    def _fetch_next_page(
        self,
        page_identifier: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> PaginatedResponse[Dict[str, Any]]:
        """Fetch next page of batches."""
        next_params = (params or {}).copy()
        next_params["page"] = page_identifier
        return self.list(**next_params)
