"""Resource modules for Distru API endpoints."""

from distru_sdk.resources.base import BaseResource, PaginatedResponse
from distru_sdk.resources.products import ProductsResource
from distru_sdk.resources.orders import OrdersResource
from distru_sdk.resources.invoices import InvoicesResource
from distru_sdk.resources.companies import CompaniesResource
from distru_sdk.resources.inventory import InventoryResource
from distru_sdk.resources.batches import BatchesResource
from distru_sdk.resources.packages import PackagesResource
from distru_sdk.resources.purchases import PurchasesResource
from distru_sdk.resources.contacts import ContactsResource
from distru_sdk.resources.locations import LocationsResource

__all__ = [
    "BaseResource",
    "PaginatedResponse",
    "ProductsResource",
    "OrdersResource",
    "InvoicesResource",
    "CompaniesResource",
    "InventoryResource",
    "BatchesResource",
    "PackagesResource",
    "PurchasesResource",
    "ContactsResource",
    "LocationsResource",
]
