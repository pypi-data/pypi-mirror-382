"""Distru API SDK for Python.

Official Python client library for the Distru API - Cannabis supply chain management platform.

Basic usage:
    >>> from distru_sdk import DistruClient
    >>> client = DistruClient(api_token="your_api_token_here")
    >>> products = client.products.list()
    >>> for product in products.auto_paginate():
    ...     print(f"{product.name} - {product.sku}")

For more information, see https://github.com/DistruApp/distru-api-sdk
"""

__version__ = "1.0.0"
__author__ = "Distru Inc."
__email__ = "support@distru.com"
__license__ = "MIT"

from distru_sdk.client import DistruClient
from distru_sdk.exceptions import (
    DistruAPIError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    ValidationError,
    RateLimitError,
    ServerError,
)

__all__ = [
    "DistruClient",
    "DistruAPIError",
    "AuthenticationError",
    "AuthorizationError",
    "NotFoundError",
    "ValidationError",
    "RateLimitError",
    "ServerError",
    "__version__",
]
