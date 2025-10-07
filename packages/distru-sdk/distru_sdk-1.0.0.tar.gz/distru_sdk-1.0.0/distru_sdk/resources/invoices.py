"""Invoices resource for managing sales invoices."""

from typing import Any, Dict, List, Optional

from distru_sdk.resources.base import BaseResource, PaginatedResponse


class InvoicesResource(BaseResource):
    """Resource for managing invoices in the Distru API.

    Invoices are billing documents generated from orders, containing line items,
    pricing, payment terms, and payment tracking.

    Example:
        >>> invoices = client.invoices.list()
        >>> for invoice in invoices.auto_paginate():
        ...     print(f"Invoice {invoice['invoice_number']} - {invoice['status']}")

        >>> invoice = client.invoices.create(
        ...     order_id="order-uuid-123",
        ...     invoice_date="2025-10-06",
        ...     due_date="2025-11-06"
        ... )
    """

    def list(
        self,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        company_relationship_id: Optional[int] = None,
        order_id: Optional[str] = None,
        status: Optional[str] = None,
        invoice_date_start: Optional[str] = None,
        invoice_date_end: Optional[str] = None,
        due_date_start: Optional[str] = None,
        due_date_end: Optional[str] = None,
        invoice_number: Optional[str] = None,
        **params: Any,
    ) -> PaginatedResponse[Dict[str, Any]]:
        """List all invoices.

        Args:
            page: Page number (default: 1)
            limit: Number of items per page (default: 5000, max: 5000)
            company_relationship_id: Filter by customer company relationship ID
            order_id: Filter by order UUID
            status: Filter by invoice status (e.g., "unpaid", "paid", "overdue")
            invoice_date_start: Filter by invoice date start (ISO format)
            invoice_date_end: Filter by invoice date end (ISO format)
            due_date_start: Filter by due date start (ISO format)
            due_date_end: Filter by due date end (ISO format)
            invoice_number: Filter by invoice number
            **params: Additional query parameters

        Returns:
            Paginated list of invoices

        Example:
            >>> # Get all invoices
            >>> invoices = client.invoices.list()
            >>>
            >>> # Filter by customer
            >>> invoices = client.invoices.list(company_relationship_id=123)
            >>>
            >>> # Filter by status
            >>> invoices = client.invoices.list(status="unpaid")
            >>>
            >>> # Filter by date range
            >>> invoices = client.invoices.list(
            ...     invoice_date_start="2025-01-01",
            ...     invoice_date_end="2025-12-31"
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
        if order_id is not None:
            query_params["order_id"] = order_id
        if status is not None:
            query_params["status"] = status
        if invoice_date_start is not None:
            query_params["invoice_date_start"] = invoice_date_start
        if invoice_date_end is not None:
            query_params["invoice_date_end"] = invoice_date_end
        if due_date_start is not None:
            query_params["due_date_start"] = due_date_start
        if due_date_end is not None:
            query_params["due_date_end"] = due_date_end
        if invoice_number is not None:
            query_params["invoice_number"] = invoice_number

        response_data = self._get("/invoices", params=query_params)

        return self._create_paginated_response(
            data=response_data.get("data", []),
            next_page=response_data.get("next_page"),
            params=query_params,
        )

    def get(self, invoice_id: str) -> Dict[str, Any]:
        """Get a specific invoice by ID.

        Args:
            invoice_id: Invoice UUID

        Returns:
            Invoice data with line items and payment information

        Raises:
            NotFoundError: If invoice not found

        Example:
            >>> invoice = client.invoices.get("invoice-uuid-123")
            >>> print(f"Invoice {invoice['invoice_number']} total: {invoice['total']}")
        """
        return self._get(f"/invoices/{invoice_id}")

    def create(
        self,
        order_id: str,
        invoice_date: str,
        due_date: str,
        invoice_number: Optional[str] = None,
        status: Optional[str] = None,
        invoice_items: Optional[List[Dict[str, Any]]] = None,
        notes: Optional[str] = None,
        custom_data: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Create a new invoice.

        Args:
            order_id: Order UUID (required)
            invoice_date: Invoice date in ISO format (required)
            due_date: Payment due date in ISO format (required)
            invoice_number: Invoice number (auto-generated if not provided)
            status: Invoice status
            invoice_items: List of invoice items (typically populated from order)
            notes: Notes to appear on invoice
            custom_data: Custom data dictionary
            **kwargs: Additional invoice fields

        Returns:
            Created invoice data

        Raises:
            ValidationError: If validation fails

        Example:
            >>> invoice = client.invoices.create(
            ...     order_id="order-uuid-123",
            ...     invoice_date="2025-10-06",
            ...     due_date="2025-11-06",
            ...     notes="Net 30 terms"
            ... )
        """
        invoice_data: Dict[str, Any] = {
            "order_id": order_id,
            "invoice_date": invoice_date,
            "due_date": due_date,
            **kwargs,
        }

        if invoice_number is not None:
            invoice_data["invoice_number"] = invoice_number
        if status is not None:
            invoice_data["status"] = status
        if invoice_items is not None:
            invoice_data["invoice_items"] = invoice_items
        if notes is not None:
            invoice_data["notes"] = notes
        if custom_data is not None:
            invoice_data["custom_data"] = custom_data

        return self._post("/invoices", json={"invoice": invoice_data})

    def update(
        self,
        invoice_id: str,
        invoice_date: Optional[str] = None,
        due_date: Optional[str] = None,
        status: Optional[str] = None,
        notes: Optional[str] = None,
        custom_data: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Update an existing invoice.

        Args:
            invoice_id: Invoice UUID
            invoice_date: Invoice date
            due_date: Payment due date
            status: Invoice status
            notes: Notes to appear on invoice
            custom_data: Custom data dictionary
            **kwargs: Additional fields to update

        Returns:
            Updated invoice data

        Raises:
            NotFoundError: If invoice not found
            ValidationError: If validation fails

        Example:
            >>> invoice = client.invoices.update(
            ...     "invoice-uuid-123",
            ...     status="paid",
            ...     notes="Payment received"
            ... )
        """
        update_data: Dict[str, Any] = {**kwargs}

        if invoice_date is not None:
            update_data["invoice_date"] = invoice_date
        if due_date is not None:
            update_data["due_date"] = due_date
        if status is not None:
            update_data["status"] = status
        if notes is not None:
            update_data["notes"] = notes
        if custom_data is not None:
            update_data["custom_data"] = custom_data

        return self._patch(f"/invoices/{invoice_id}", json={"invoice": update_data})

    def delete(self, invoice_id: str) -> None:
        """Delete an invoice.

        Args:
            invoice_id: Invoice UUID

        Raises:
            NotFoundError: If invoice not found
            ValidationError: If invoice cannot be deleted (e.g., has payments)

        Example:
            >>> client.invoices.delete("invoice-uuid-123")
        """
        self._delete(f"/invoices/{invoice_id}")

    def add_payment(
        self,
        invoice_id: str,
        amount: str,
        payment_date: str,
        payment_method: Optional[str] = None,
        notes: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Add a payment to an invoice.

        Args:
            invoice_id: Invoice UUID
            amount: Payment amount (required)
            payment_date: Payment date in ISO format (required)
            payment_method: Payment method (e.g., "cash", "check", "credit_card")
            notes: Payment notes
            **kwargs: Additional payment fields

        Returns:
            Updated invoice data with payment information

        Raises:
            NotFoundError: If invoice not found
            ValidationError: If validation fails

        Example:
            >>> invoice = client.invoices.add_payment(
            ...     "invoice-uuid-123",
            ...     amount="150.00",
            ...     payment_date="2025-10-06",
            ...     payment_method="credit_card",
            ...     notes="Visa ending in 1234"
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
            f"/invoices/{invoice_id}/payments",
            json={"payment": payment_data}
        )

    def _fetch_next_page(
        self,
        page_identifier: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> PaginatedResponse[Dict[str, Any]]:
        """Fetch next page of invoices."""
        next_params = (params or {}).copy()
        next_params["page"] = page_identifier
        return self.list(**next_params)
