# Distru Python SDK

Official Python SDK for the [Distru API](https://distru.com) - Cannabis supply chain management platform.

[![PyPI version](https://badge.fury.io/py/distru-sdk.svg)](https://badge.fury.io/py/distru-sdk)
[![Python versions](https://img.shields.io/pypi/pyversions/distru-sdk.svg)](https://pypi.org/project/distru-sdk/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

```bash
pip install distru-sdk
```

## Quick Start

```python
from distru_sdk import DistruClient

# Initialize the client with your API token
client = DistruClient(api_token="your_api_token_here")

# List products
products = client.products.list()
for product in products.auto_paginate():
    print(f"{product['name']} - ${product['sale_price']}")

# Create an order
order = client.orders.create(
    company_relationship_id=123,
    order_date="2025-10-06T12:00:00Z",
    order_items=[
        {
            "product_id": "prod-uuid-123",
            "quantity": 10,
            "unit_price": "15.00"
        }
    ]
)
print(f"Order created: {order['order_number']}")
```

## Authentication

The Distru API uses JWT Bearer token authentication. To get an API token:

1. Log into your Distru account
2. Navigate to **Settings** → **API Keys**
3. Click **Create API Key**
4. Copy the generated token
5. Store it securely (never commit to source control!)

```python
# Initialize client
client = DistruClient(api_token="your_api_token_here")

# Optional: Configure timeout and retries
client = DistruClient(
    api_token="your_api_token_here",
    timeout=60.0,  # Request timeout in seconds
    max_retries=5   # Maximum retry attempts
)
```

## Usage

### Products

```python
# List all products
products = client.products.list()

# Auto-paginate through all results
for product in products.auto_paginate():
    print(product['name'])

# Search products
products = client.products.list(search="Blue Dream")

# Get a specific product
product = client.products.get("prod-uuid-123")

# Create a product
product = client.products.create(
    name="Blue Dream 1g",
    sku="BD-1G",
    unit_type_id=1,
    inventory_tracking_method="BATCH",
    sale_price="15.00",
    wholesale_price="10.00"
)

# Update a product
product = client.products.update(
    "prod-uuid-123",
    sale_price="17.00",
    wholesale_price="11.00"
)

# Delete a product
client.products.delete("prod-uuid-123")
```

### Orders

```python
# List orders
orders = client.orders.list()

# Filter orders
orders = client.orders.list(
    status="Submitted",
    customer_id=123,
    from_date="2025-01-01",
    to_date="2025-12-31"
)

# Get a specific order
order = client.orders.get("order-uuid-123")

# Create an order
order = client.orders.create(
    company_relationship_id=123,
    order_date="2025-10-06T12:00:00Z",
    due_date="2025-10-20T12:00:00Z",
    order_items=[
        {
            "product_id": "prod-uuid-1",
            "quantity": 10,
            "unit_price": "15.00"
        },
        {
            "product_id": "prod-uuid-2",
            "quantity": 5,
            "unit_price": "25.00"
        }
    ]
)
```

### Invoices

```python
# List invoices
invoices = client.invoices.list()

# Filter invoices
invoices = client.invoices.list(
    status="Not Paid",
    customer_id=123
)

# Get a specific invoice
invoice = client.invoices.get(456)

# Create an invoice
invoice = client.invoices.create(
    order_id="order-uuid-123",
    invoice_date="2025-10-06T12:00:00Z",
    due_date="2025-10-20T12:00:00Z",
    invoice_items=[
        {
            "order_item_id": "order-item-uuid-1",
            "quantity": 10
        }
    ]
)

# Add a payment to an invoice
payment = client.invoices.add_payment(
    456,
    amount="150.00",
    payment_date="2025-10-06T12:00:00Z",
    payment_method_id=1
)
```

### Inventory

```python
# Get current inventory
inventory = client.inventory.list()

# Include cost information
inventory = client.inventory.list(include_costs=True)

# Filter by location
inventory = client.inventory.list(location_id=1)

# Filter by product
inventory = client.inventory.list(product_id="prod-uuid-123")
```

### Companies (Customers/Vendors)

```python
# List all companies
companies = client.companies.list()

# Search companies
companies = client.companies.list(search="Acme")

# Filter by state
companies = client.companies.list(us_state="CA")

# Get a specific company
company = client.companies.get(123)
```

### Batches

```python
# List batches
batches = client.batches.list()

# Filter by product
batches = client.batches.list(product_id="prod-uuid-123")

# Create a batch
batch = client.batches.create(
    product_id="prod-uuid-123",
    batch_number="BATCH-001",
    harvest_date="2025-09-01T00:00:00Z",
    expiration_date="2026-09-01T00:00:00Z"
)
```

### Purchases

```python
# List purchases
purchases = client.purchases.list()

# Create a purchase order
purchase = client.purchases.create(
    company_relationship_id=456,
    purchase_date="2025-10-06T12:00:00Z",
    purchase_items=[
        {
            "product_id": "prod-uuid-1",
            "quantity": 100,
            "unit_cost": "8.00"
        }
    ]
)

# Add a payment
payment = client.purchases.add_payment(
    789,
    amount="800.00",
    payment_date="2025-10-06T12:00:00Z"
)
```

## Pagination

All list endpoints return paginated results. The SDK provides helper methods for easy pagination:

### Auto-Pagination

```python
# Automatically fetch all pages
products = client.products.list()
for product in products.auto_paginate():
    print(product['name'])
```

### Manual Pagination

```python
# Iterate page by page
response = client.products.list()
for page in response.iter_pages():
    print(f"Processing page with {len(page)} items")
    for product in page:
        print(product['name'])
```

### Page-by-Page

```python
# Fetch specific pages
page_1 = client.products.list(page=1, limit=100)
page_2 = client.products.list(page=2, limit=100)
```

## Error Handling

The SDK provides specific exception classes for different error types:

```python
from distru_sdk.exceptions import (
    DistruAPIError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    ValidationError,
    RateLimitError,
    ServerError,
    NetworkError,
    TimeoutError,
)

try:
    order = client.orders.get("invalid-uuid")
except NotFoundError as e:
    print(f"Order not found: {e.message}")
except AuthenticationError as e:
    print(f"Invalid API token: {e.message}")
except RateLimitError as e:
    print(f"Rate limited, retry after {e.retry_after} seconds")
except ValidationError as e:
    print(f"Validation error: {e.message}")
    print(f"Details: {e.details}")
except ServerError as e:
    print(f"Server error: {e.message}")
except NetworkError as e:
    print(f"Network error: {e.message}")
except TimeoutError as e:
    print(f"Request timed out: {e.message}")
except DistruAPIError as e:
    print(f"API error: {e.message}")
```

## Webhooks (Beta)

Handle webhook events from Distru:

```python
from distru_sdk.webhooks import WebhookHandler

# Create webhook handler
handler = WebhookHandler()

# Register event handlers
@handler.on('ORDER')
def handle_order_event(event):
    if not event.before_changes:  # New order
        print(f"New order: {event.after_changes['order_number']}")
    elif not event.after_changes:  # Deleted order
        print(f"Order deleted: {event.before_changes['order_number']}")
    else:  # Updated order
        print(f"Order updated: {event.after_changes['order_number']}")

@handler.on('INVOICE')
def handle_invoice_event(event):
    print(f"Invoice event: {event.type}")

# In your web framework (Flask, FastAPI, Django, etc.)
from flask import Flask, request

app = Flask(__name__)

@app.route('/webhooks', methods=['POST'])
def webhook_endpoint():
    payload = request.get_json()
    handler.process(payload)
    return {'status': 'ok'}
```

## Data Consistency

The Distru API uses eventual consistency. Changes may take up to **1 second** to propagate to GET endpoints.

**Best Practices:**
- Use the returned data from create/update operations immediately
- For critical operations, add a small delay before fetching updated data
- Implement idempotency using unique identifiers

```python
import time

# Create an order
order = client.orders.create(...)

# The response contains the created order immediately
print(order['order_number'])  # Available immediately

# If you need to fetch it again, wait briefly
time.sleep(1.5)
order = client.orders.get(order['id'])  # Now guaranteed to be available
```

## Rate Limiting

The SDK automatically handles rate limiting with exponential backoff:

- Automatic retry on 429 (rate limit) and 5xx errors
- Exponential backoff: 1s, 2s, 4s, 8s, 10s (max)
- Maximum 3 retries by default (configurable)
- Respects `Retry-After` headers

```python
# Configure retry behavior
client = DistruClient(
    api_token="your_token",
    max_retries=5,  # Increase max retries
    timeout=60.0     # Increase timeout
)
```

## Advanced Usage

### Context Manager

```python
# Automatically close connection
with DistruClient(api_token="your_token") as client:
    products = client.products.list()
    for product in products.auto_paginate():
        print(product['name'])
# Connection closed automatically
```

### Custom HTTP Client

```python
import httpx

# Use custom httpx client
http_client = httpx.Client(
    timeout=60.0,
    limits=httpx.Limits(max_keepalive_connections=5)
)

client = DistruClient(
    api_token="your_token",
    http_client=http_client
)
```

## Requirements

- Python 3.8+
- httpx >= 0.25.0
- pydantic >= 2.0.0

## Development

### Setup

```bash
# Clone repository
git clone https://github.com/DistruApp/distru-api-sdk.git
cd distru-api-sdk/python

# Install in development mode
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=distru_sdk --cov-report=html

# Run specific test file
pytest tests/test_products.py
```

### Code Quality

```bash
# Format code
black distru_sdk tests

# Sort imports
isort distru_sdk tests

# Type checking
mypy distru_sdk

# Linting
flake8 distru_sdk tests
```

## Support

- **Documentation**: [GitHub Repository](https://github.com/DistruApp/distru-api-sdk)
- **Issues**: [GitHub Issues](https://github.com/DistruApp/distru-api-sdk/issues)
- **Email**: [support@distru.com](mailto:support@distru.com)

## License

MIT License - see [LICENSE](../LICENSE) file for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and changes.
