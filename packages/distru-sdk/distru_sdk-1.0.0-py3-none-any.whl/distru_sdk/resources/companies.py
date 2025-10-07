"""Companies resource for viewing company relationships."""

from typing import Any, Dict, Optional

from distru_sdk.resources.base import BaseResource, PaginatedResponse


class CompaniesResource(BaseResource):
    """Resource for viewing companies in the Distru API.

    Companies represent business relationships including customers, vendors,
    and partners. Company data is primarily managed through the Distru web
    interface, with read-only access via the API.

    Example:
        >>> companies = client.companies.list()
        >>> for company in companies.auto_paginate():
        ...     print(f"{company['name']} - {company['us_state']}")
    """

    def list(
        self,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        search: Optional[str] = None,
        relationship_type: Optional[str] = None,
        us_state: Optional[str] = None,
        include_inactive: Optional[bool] = None,
        **params: Any,
    ) -> PaginatedResponse[Dict[str, Any]]:
        """List all companies.

        Args:
            page: Page number (default: 1)
            limit: Number of items per page (default: 5000, max: 5000)
            search: Search by company name or legal business name
            relationship_type: Filter by relationship type (e.g., "customer", "vendor")
            us_state: Filter by US state code (e.g., "CA", "CO")
            include_inactive: Include inactive company relationships
            **params: Additional query parameters

        Returns:
            Paginated list of companies

        Example:
            >>> # Get all companies
            >>> companies = client.companies.list()
            >>>
            >>> # Search for companies
            >>> companies = client.companies.list(search="Acme")
            >>>
            >>> # Filter by relationship type
            >>> companies = client.companies.list(relationship_type="customer")
            >>>
            >>> # Filter by state
            >>> companies = client.companies.list(us_state="CA")
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
        if relationship_type is not None:
            query_params["relationship_type"] = relationship_type
        if us_state is not None:
            query_params["us_state"] = us_state
        if include_inactive is not None:
            query_params["include_inactive"] = include_inactive

        response_data = self._get("/companies", params=query_params)

        return self._create_paginated_response(
            data=response_data.get("data", []),
            next_page=response_data.get("next_page"),
            params=query_params,
        )

    def get(self, company_id: int) -> Dict[str, Any]:
        """Get a specific company by ID.

        Args:
            company_id: Company relationship ID

        Returns:
            Company data including contact information and addresses

        Raises:
            NotFoundError: If company not found

        Example:
            >>> company = client.companies.get(123)
            >>> print(f"{company['name']} - {company['email']}")
        """
        return self._get(f"/companies/{company_id}")

    def _fetch_next_page(
        self,
        page_identifier: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> PaginatedResponse[Dict[str, Any]]:
        """Fetch next page of companies."""
        next_params = (params or {}).copy()
        next_params["page"] = page_identifier
        return self.list(**next_params)
