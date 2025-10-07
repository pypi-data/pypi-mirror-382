"""Base resource class for all API resources."""

from typing import TYPE_CHECKING, Any, Dict, Generic, Iterator, List, Optional, TypeVar

if TYPE_CHECKING:
    from distru_sdk.client import DistruClient

T = TypeVar("T")


class PaginatedResponse(Generic[T]):
    """Response object for paginated API results.

    Provides helper methods for iterating through paginated results.

    Example:
        >>> response = client.products.list()
        >>> for product in response.auto_paginate():
        ...     print(product.name)
    """

    def __init__(
        self,
        data: List[T],
        next_page: Optional[str],
        resource: "BaseResource",
        request_params: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize paginated response.

        Args:
            data: List of items in current page
            next_page: URL or page identifier for next page (None if no more pages)
            resource: Resource instance for fetching additional pages
            request_params: Original request parameters
        """
        self.data = data
        self.next_page = next_page
        self._resource = resource
        self._request_params = request_params or {}

    def __iter__(self) -> Iterator[T]:
        """Iterate over items in current page."""
        return iter(self.data)

    def __len__(self) -> int:
        """Return number of items in current page."""
        return len(self.data)

    def __getitem__(self, index: int) -> T:
        """Get item by index from current page."""
        return self.data[index]

    def has_more(self) -> bool:
        """Check if there are more pages available.

        Returns:
            True if there are more pages to fetch
        """
        return self.next_page is not None

    def auto_paginate(self) -> Iterator[T]:
        """Automatically fetch all pages and yield items.

        Yields:
            Items from all pages

        Example:
            >>> for product in response.auto_paginate():
            ...     print(product.name)
        """
        # Yield items from current page
        for item in self.data:
            yield item

        # Fetch and yield from subsequent pages
        current_response = self
        while current_response.has_more():
            # Get next page URL or extract page number
            if current_response.next_page:
                if current_response.next_page.startswith("http"):
                    # Full URL provided
                    next_response = self._resource._fetch_next_page_url(current_response.next_page)
                else:
                    # Page identifier provided (e.g., page number)
                    next_response = self._resource._fetch_next_page(
                        current_response.next_page, self._request_params
                    )

                for item in next_response.data:
                    yield item

                current_response = next_response
            else:
                break

    def iter_pages(self) -> Iterator["PaginatedResponse[T]"]:
        """Iterate through pages of results.

        Yields:
            PaginatedResponse objects for each page

        Example:
            >>> for page in response.iter_pages():
            ...     print(f"Page has {len(page)} items")
            ...     for item in page:
            ...         print(item.name)
        """
        yield self

        current_response = self
        while current_response.has_more():
            if current_response.next_page:
                if current_response.next_page.startswith("http"):
                    next_response = self._resource._fetch_next_page_url(current_response.next_page)
                else:
                    next_response = self._resource._fetch_next_page(
                        current_response.next_page, self._request_params
                    )
                yield next_response
                current_response = next_response
            else:
                break


class BaseResource:
    """Base class for all API resource endpoints."""

    def __init__(self, client: "DistruClient") -> None:
        """Initialize resource with client.

        Args:
            client: DistruClient instance
        """
        self._client = client

    def _get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Make a GET request.

        Args:
            path: API endpoint path
            params: Query parameters

        Returns:
            Response JSON data
        """
        response = self._client.request("GET", path, params=params)
        return response.json()

    def _post(
        self,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Make a POST request.

        Args:
            path: API endpoint path
            json: Request body
            params: Query parameters

        Returns:
            Response JSON data
        """
        response = self._client.request("POST", path, json=json, params=params)
        return response.json()

    def _patch(
        self,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Make a PATCH request.

        Args:
            path: API endpoint path
            json: Request body
            params: Query parameters

        Returns:
            Response JSON data
        """
        response = self._client.request("PATCH", path, json=json, params=params)
        return response.json()

    def _delete(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Make a DELETE request.

        Args:
            path: API endpoint path
            params: Query parameters

        Returns:
            Response JSON data (if any)
        """
        response = self._client.request("DELETE", path, params=params)
        if response.status_code == 204:  # No content
            return None
        return response.json() if response.content else None

    def _create_paginated_response(
        self,
        data: List[Any],
        next_page: Optional[str],
        params: Optional[Dict[str, Any]] = None,
    ) -> PaginatedResponse[Any]:
        """Create a paginated response object.

        Args:
            data: List of items
            next_page: Next page URL or identifier
            params: Original request parameters

        Returns:
            PaginatedResponse instance
        """
        return PaginatedResponse(
            data=data,
            next_page=next_page,
            resource=self,
            request_params=params,
        )

    def _fetch_next_page(
        self,
        page_identifier: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> PaginatedResponse[Any]:
        """Fetch next page using page identifier.

        Args:
            page_identifier: Page number or identifier
            params: Request parameters

        Returns:
            PaginatedResponse for the next page
        """
        # This should be overridden by subclasses that support pagination
        raise NotImplementedError("Pagination not implemented for this resource")

    def _fetch_next_page_url(self, url: str) -> PaginatedResponse[Any]:
        """Fetch next page using full URL.

        Args:
            url: Full URL for next page

        Returns:
            PaginatedResponse for the next page
        """
        response_data = self._get(url)
        return self._create_paginated_response(
            data=response_data.get("data", []),
            next_page=response_data.get("next_page"),
        )
