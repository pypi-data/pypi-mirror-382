"""Main client for the Distru API."""

import time
from typing import Any, Dict, Optional
from urllib.parse import urljoin

import httpx

from distru_sdk import exceptions
from distru_sdk.resources import (
    ProductsResource,
    OrdersResource,
    InvoicesResource,
    CompaniesResource,
    InventoryResource,
    BatchesResource,
    PackagesResource,
    PurchasesResource,
    ContactsResource,
    LocationsResource,
)

__version__ = "1.0.0"


class DistruClient:
    """Client for interacting with the Distru API.

    The client handles authentication, retries, rate limiting, and provides
    access to all API resources.

    Example:
        >>> client = DistruClient(api_token="your_api_token")
        >>> products = client.products.list()
        >>> for product in products.auto_paginate():
        ...     print(product.name)
    """

    DEFAULT_BASE_URL = "https://app.distru.com/public/v1"
    DEFAULT_TIMEOUT = 30.0
    DEFAULT_MAX_RETRIES = 3

    def __init__(
        self,
        api_token: str,
        base_url: Optional[str] = None,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        http_client: Optional[httpx.Client] = None,
    ) -> None:
        """Initialize the Distru API client.

        Args:
            api_token: Your Distru API token (Bearer token)
            base_url: Base URL for the API (defaults to production)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts for failed requests
            http_client: Optional custom httpx.Client instance

        Raises:
            ValueError: If api_token is empty or None
        """
        if not api_token:
            raise ValueError("api_token is required")

        self.api_token = api_token
        self.base_url = (base_url or self.DEFAULT_BASE_URL).rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries

        # Create HTTP client
        if http_client:
            self._http_client = http_client
            self._owns_http_client = False
        else:
            self._http_client = httpx.Client(
                base_url=self.base_url,
                timeout=timeout,
                headers=self._get_default_headers(),
            )
            self._owns_http_client = True

        # Initialize resource endpoints
        self.products = ProductsResource(self)
        self.orders = OrdersResource(self)
        self.invoices = InvoicesResource(self)
        self.companies = CompaniesResource(self)
        self.inventory = InventoryResource(self)
        self.batches = BatchesResource(self)
        self.packages = PackagesResource(self)
        self.purchases = PurchasesResource(self)
        self.contacts = ContactsResource(self)
        self.locations = LocationsResource(self)

    def _get_default_headers(self) -> Dict[str, str]:
        """Get default headers for API requests."""
        return {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": f"distru-python-sdk/{__version__}",
        }

    def request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """Make an HTTP request with retry logic.

        Args:
            method: HTTP method (GET, POST, etc.)
            path: API endpoint path
            params: Query parameters
            json: JSON request body
            **kwargs: Additional arguments passed to httpx

        Returns:
            httpx.Response object

        Raises:
            AuthenticationError: On 401 responses
            AuthorizationError: On 403 responses
            NotFoundError: On 404 responses
            ValidationError: On 422 responses
            RateLimitError: On 429 responses (after retries exhausted)
            ServerError: On 5xx responses (after retries exhausted)
            NetworkError: On network/connection errors (after retries exhausted)
            TimeoutError: On request timeouts (after retries exhausted)
        """
        url = path if path.startswith("http") else urljoin(self.base_url + "/", path.lstrip("/"))

        retries = 0
        last_exception: Optional[Exception] = None

        while retries <= self.max_retries:
            try:
                response = self._http_client.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json,
                    **kwargs,
                )

                # Handle successful responses
                if response.status_code < 400:
                    return response

                # Handle error responses
                self._handle_error_response(response)

                # If we get here, check if we should retry
                if self._should_retry(response.status_code) and retries < self.max_retries:
                    delay = self._get_retry_delay(retries, response)
                    time.sleep(delay)
                    retries += 1
                    continue

                # No retry, raise the error
                self._handle_error_response(response)

            except (httpx.NetworkError, httpx.ConnectError) as e:
                last_exception = e
                if retries < self.max_retries:
                    delay = self._exponential_backoff(retries)
                    time.sleep(delay)
                    retries += 1
                    continue
                raise exceptions.NetworkError(
                    f"Network error: {str(e)}", original_error=e
                ) from e

            except httpx.TimeoutException as e:
                last_exception = e
                if retries < self.max_retries:
                    delay = self._exponential_backoff(retries)
                    time.sleep(delay)
                    retries += 1
                    continue
                raise exceptions.TimeoutError(
                    f"Request timed out after {self.timeout}s", timeout=self.timeout
                ) from e

        # Should never reach here, but just in case
        if last_exception:
            raise exceptions.NetworkError(
                "Max retries exceeded", original_error=last_exception
            ) from last_exception

        raise exceptions.DistruAPIError("Max retries exceeded")

    def _should_retry(self, status_code: int) -> bool:
        """Determine if request should be retried based on status code.

        Args:
            status_code: HTTP status code

        Returns:
            True if request should be retried
        """
        # Retry on rate limits and server errors
        return status_code == 429 or status_code >= 500

    def _get_retry_delay(self, retry_count: int, response: httpx.Response) -> float:
        """Get delay before retrying request.

        Args:
            retry_count: Current retry attempt number
            response: Response object

        Returns:
            Delay in seconds
        """
        # Check for Retry-After header
        retry_after = response.headers.get("Retry-After")
        if retry_after:
            try:
                return float(retry_after)
            except ValueError:
                pass

        # Use exponential backoff
        return self._exponential_backoff(retry_count)

    def _exponential_backoff(self, retry_count: int) -> float:
        """Calculate exponential backoff delay.

        Args:
            retry_count: Current retry attempt number

        Returns:
            Delay in seconds
        """
        # 2^retry_count, max 10 seconds
        return min(2**retry_count, 10.0)

    def _handle_error_response(self, response: httpx.Response) -> None:
        """Handle error responses from the API.

        Args:
            response: Response object

        Raises:
            AuthenticationError: On 401
            AuthorizationError: On 403
            NotFoundError: On 404
            ValidationError: On 422
            RateLimitError: On 429
            ServerError: On 5xx
            DistruAPIError: On other errors
        """
        status_code = response.status_code

        # Try to parse error response
        try:
            error_data = response.json()
            error_message = error_data.get("error") or error_data.get("message") or str(error_data)
        except Exception:
            error_message = response.text or f"HTTP {status_code} error"

        # Raise specific exceptions
        if status_code == 401:
            raise exceptions.AuthenticationError(error_message, response_data=error_data if 'error_data' in locals() else None)
        elif status_code == 403:
            raise exceptions.AuthorizationError(error_message, response_data=error_data if 'error_data' in locals() else None)
        elif status_code == 404:
            raise exceptions.NotFoundError(error_message, response_data=error_data if 'error_data' in locals() else None)
        elif status_code == 422:
            raise exceptions.ValidationError(error_message, response_data=error_data if 'error_data' in locals() else None)
        elif status_code == 429:
            retry_after = response.headers.get("Retry-After")
            retry_after_int = int(retry_after) if retry_after and retry_after.isdigit() else None
            raise exceptions.RateLimitError(
                error_message,
                retry_after=retry_after_int,
                response_data=error_data if 'error_data' in locals() else None,
            )
        elif status_code >= 500:
            raise exceptions.ServerError(
                error_message,
                status_code=status_code,
                response_data=error_data if 'error_data' in locals() else None,
            )
        else:
            raise exceptions.DistruAPIError(
                error_message,
                status_code=status_code,
                response_data=error_data if 'error_data' in locals() else None,
            )

    def close(self) -> None:
        """Close the HTTP client connection."""
        if self._owns_http_client:
            self._http_client.close()

    def __enter__(self) -> "DistruClient":
        """Context manager entry."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Context manager exit."""
        self.close()

    def __del__(self) -> None:
        """Cleanup on deletion."""
        if hasattr(self, "_owns_http_client") and self._owns_http_client:
            try:
                self._http_client.close()
            except Exception:
                pass
