"""Contacts resource for viewing company contacts."""

from typing import Any, Dict, Optional

from distru_sdk.resources.base import BaseResource, PaginatedResponse


class ContactsResource(BaseResource):
    """Resource for viewing contacts in the Distru API.

    Contacts represent individuals associated with company relationships,
    including email addresses, phone numbers, and roles. Contact data is
    read-only via the API.

    Example:
        >>> contacts = client.contacts.list()
        >>> for contact in contacts.auto_paginate():
        ...     print(f"{contact['name']} - {contact['email']}")
        >>>
        >>> # Filter by company
        >>> contacts = client.contacts.list(company_relationship_id=123)
    """

    def list(
        self,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        company_relationship_id: Optional[int] = None,
        search: Optional[str] = None,
        **params: Any,
    ) -> PaginatedResponse[Dict[str, Any]]:
        """List all contacts.

        Args:
            page: Page number (default: 1)
            limit: Number of items per page (default: 5000, max: 5000)
            company_relationship_id: Filter by company relationship ID
            search: Search by contact name or email
            **params: Additional query parameters

        Returns:
            Paginated list of contacts

        Example:
            >>> # Get all contacts
            >>> contacts = client.contacts.list()
            >>>
            >>> # Get contacts for a specific company
            >>> contacts = client.contacts.list(company_relationship_id=123)
            >>>
            >>> # Search for contacts
            >>> contacts = client.contacts.list(search="john")
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
        if search is not None:
            query_params["search"] = search

        response_data = self._get("/contacts", params=query_params)

        return self._create_paginated_response(
            data=response_data.get("data", []),
            next_page=response_data.get("next_page"),
            params=query_params,
        )

    def get(self, contact_id: int) -> Dict[str, Any]:
        """Get a specific contact by ID.

        Args:
            contact_id: Contact ID

        Returns:
            Contact data including name, email, phone, and company information

        Raises:
            NotFoundError: If contact not found

        Example:
            >>> contact = client.contacts.get(789)
            >>> print(f"{contact['name']} - {contact['email']}")
        """
        return self._get(f"/contacts/{contact_id}")

    def _fetch_next_page(
        self,
        page_identifier: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> PaginatedResponse[Dict[str, Any]]:
        """Fetch next page of contacts."""
        next_params = (params or {}).copy()
        next_params["page"] = page_identifier
        return self.list(**next_params)
