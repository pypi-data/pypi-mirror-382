"""Purchases resource for managing purchase orders."""

from typing import Any, Dict, List, Optional

from distru_sdk.resources.base import BaseResource, PaginatedResponse


class PurchasesResource(BaseResource):
    """Resource for managing purchases in the Distru API.

    Purchases represent buying transactions from vendors, containing purchase items,
    pricing, and receiving information.

    Example:
        >>> purchases = client.purchases.list()
        >>> for purchase in purchases.auto_paginate():
        ...     print(f"Purchase {purchase['purchase_number']} - {purchase['status']}")

        >>> purchase = client.purchases.create(
        ...     company_relationship_id=456,
        ...     purchase_date="2025-10-06",
        ...     purchase_items=[
        ...         {
        ...             "product_id": "prod-uuid-123",
        ...             "quantity": 100,
        ...             "unit_cost": "5.00"
        ...         }
        ...     ]
        ... )
    """

    def list(
        self,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        company_relationship_id: Optional[int] = None,
        status: Optional[str] = None,
        purchase_date_start: Optional[str] = None,
        purchase_date_end: Optional[str] = None,
        purchase_number: Optional[str] = None,
        **params: Any,
    ) -> PaginatedResponse[Dict[str, Any]]:
        """List all purchases.

        Args:
            page: Page number (default: 1)
            limit: Number of items per page (default: 5000, max: 5000)
            company_relationship_id: Filter by vendor company relationship ID
            status: Filter by purchase status (e.g., "pending", "received", "cancelled")
            purchase_date_start: Filter by purchase date start (ISO format)
            purchase_date_end: Filter by purchase date end (ISO format)
            purchase_number: Filter by purchase number
            **params: Additional query parameters

        Returns:
            Paginated list of purchases

        Example:
            >>> # Get all purchases
            >>> purchases = client.purchases.list()
            >>>
            >>> # Filter by vendor
            >>> purchases = client.purchases.list(company_relationship_id=456)
            >>>
            >>> # Filter by status
            >>> purchases = client.purchases.list(status="pending")
            >>>
            >>> # Filter by date range
            >>> purchases = client.purchases.list(
            ...     purchase_date_start="2025-01-01",
            ...     purchase_date_end="2025-12-31"
            ... )
        """
        query_params: Dict[str, Any] = {
            **params,
        }

        if page is not None:
            query_params["page"] = page
        if limit is not None:
            query_params["limit"] = limit
        if company_relationship_id is not None:
            query_params["company_relationship_id"] = company_relationship_id
        if status is not None:
            query_params["status"] = status
        if purchase_date_start is not None:
            query_params["purchase_date_start"] = purchase_date_start
        if purchase_date_end is not None:
            query_params["purchase_date_end"] = purchase_date_end
        if purchase_number is not None:
            query_params["purchase_number"] = purchase_number

        response_data = self._get("/purchases", params=query_params)

        return self._create_paginated_response(
            data=response_data.get("data", []),
            next_page=response_data.get("next_page"),
            params=query_params,
        )

    def get(self, purchase_id: str) -> Dict[str, Any]:
        """Get a specific purchase by ID.

        Args:
            purchase_id: Purchase UUID

        Returns:
            Purchase data with line items and related information

        Raises:
            NotFoundError: If purchase not found

        Example:
            >>> purchase = client.purchases.get("purchase-uuid-123")
            >>> print(f"Purchase {purchase['purchase_number']} total: {purchase['total']}")
        """
        return self._get(f"/purchases/{purchase_id}")

    def create(
        self,
        company_relationship_id: int,
        purchase_date: str,
        purchase_items: List[Dict[str, Any]],
        purchase_number: Optional[str] = None,
        status: Optional[str] = None,
        expected_delivery_date: Optional[str] = None,
        notes: Optional[str] = None,
        location_id: Optional[int] = None,
        custom_data: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Create a new purchase order.

        Args:
            company_relationship_id: Vendor company relationship ID (required)
            purchase_date: Purchase date in ISO format (required)
            purchase_items: List of purchase items (required), each containing:
                - product_id: Product UUID
                - quantity: Quantity ordered
                - unit_cost: Cost per unit
            purchase_number: Purchase order number (auto-generated if not provided)
            status: Purchase status
            expected_delivery_date: Expected delivery date
            notes: Internal notes
            location_id: Receiving location ID
            custom_data: Custom data dictionary
            **kwargs: Additional purchase fields

        Returns:
            Created purchase data

        Raises:
            ValidationError: If validation fails

        Example:
            >>> purchase = client.purchases.create(
            ...     company_relationship_id=456,
            ...     purchase_date="2025-10-06",
            ...     purchase_items=[
            ...         {
            ...             "product_id": "prod-uuid-123",
            ...             "quantity": 100,
            ...             "unit_cost": "5.00"
            ...         },
            ...         {
            ...             "product_id": "prod-uuid-456",
            ...             "quantity": 50,
            ...             "unit_cost": "8.00"
            ...         }
            ...     ],
            ...     expected_delivery_date="2025-10-13",
            ...     notes="Bulk order for Q4"
            ... )
        """
        purchase_data: Dict[str, Any] = {
            "company_relationship_id": company_relationship_id,
            "purchase_date": purchase_date,
            "purchase_items": purchase_items,
            **kwargs,
        }

        if purchase_number is not None:
            purchase_data["purchase_number"] = purchase_number
        if status is not None:
            purchase_data["status"] = status
        if expected_delivery_date is not None:
            purchase_data["expected_delivery_date"] = expected_delivery_date
        if notes is not None:
            purchase_data["notes"] = notes
        if location_id is not None:
            purchase_data["location_id"] = location_id
        if custom_data is not None:
            purchase_data["custom_data"] = custom_data

        return self._post("/purchases", json={"purchase": purchase_data})

    def update(
        self,
        purchase_id: str,
        purchase_date: Optional[str] = None,
        status: Optional[str] = None,
        expected_delivery_date: Optional[str] = None,
        notes: Optional[str] = None,
        custom_data: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Update an existing purchase order.

        Args:
            purchase_id: Purchase UUID
            purchase_date: Purchase date
            status: Purchase status
            expected_delivery_date: Expected delivery date
            notes: Internal notes
            custom_data: Custom data dictionary
            **kwargs: Additional fields to update

        Returns:
            Updated purchase data

        Raises:
            NotFoundError: If purchase not found
            ValidationError: If validation fails

        Example:
            >>> purchase = client.purchases.update(
            ...     "purchase-uuid-123",
            ...     status="received",
            ...     notes="Received in full"
            ... )
        """
        update_data: Dict[str, Any] = {**kwargs}

        if purchase_date is not None:
            update_data["purchase_date"] = purchase_date
        if status is not None:
            update_data["status"] = status
        if expected_delivery_date is not None:
            update_data["expected_delivery_date"] = expected_delivery_date
        if notes is not None:
            update_data["notes"] = notes
        if custom_data is not None:
            update_data["custom_data"] = custom_data

        return self._patch(f"/purchases/{purchase_id}", json={"purchase": update_data})

    def delete(self, purchase_id: str) -> None:
        """Delete a purchase order.

        Args:
            purchase_id: Purchase UUID

        Raises:
            NotFoundError: If purchase not found
            ValidationError: If purchase cannot be deleted

        Example:
            >>> client.purchases.delete("purchase-uuid-123")
        """
        self._delete(f"/purchases/{purchase_id}")

    def add_payment(
        self,
        purchase_id: str,
        amount: str,
        payment_date: str,
        payment_method: Optional[str] = None,
        notes: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Add a payment to a purchase order.

        Args:
            purchase_id: Purchase UUID
            amount: Payment amount (required)
            payment_date: Payment date in ISO format (required)
            payment_method: Payment method (e.g., "cash", "check", "wire_transfer")
            notes: Payment notes
            **kwargs: Additional payment fields

        Returns:
            Updated purchase data with payment information

        Raises:
            NotFoundError: If purchase not found
            ValidationError: If validation fails

        Example:
            >>> purchase = client.purchases.add_payment(
            ...     "purchase-uuid-123",
            ...     amount="500.00",
            ...     payment_date="2025-10-06",
            ...     payment_method="check",
            ...     notes="Check #1234"
            ... )
        """
        payment_data: Dict[str, Any] = {
            "amount": amount,
            "payment_date": payment_date,
            **kwargs,
        }

        if payment_method is not None:
            payment_data["payment_method"] = payment_method
        if notes is not None:
            payment_data["notes"] = notes

        return self._post(
            f"/purchases/{purchase_id}/payments",
            json={"payment": payment_data}
        )

    def _fetch_next_page(
        self,
        page_identifier: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> PaginatedResponse[Dict[str, Any]]:
        """Fetch next page of purchases."""
        next_params = (params or {}).copy()
        next_params["page"] = page_identifier
        return self.list(**next_params)
