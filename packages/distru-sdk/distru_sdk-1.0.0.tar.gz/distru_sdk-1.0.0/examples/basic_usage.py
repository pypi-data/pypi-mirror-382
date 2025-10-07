"""Basic usage examples for the Distru Python SDK."""

import os
from distru_sdk import DistruClient
from distru_sdk.exceptions import (
    NotFoundError,
    ValidationError,
    RateLimitError,
    DistruAPIError,
)

# Initialize the client
api_token = os.environ.get("DISTRU_API_TOKEN")
if not api_token:
    raise ValueError("DISTRU_API_TOKEN environment variable not set")

client = DistruClient(api_token=api_token)


def list_products_example():
    """Example: List and iterate through products."""
    print("\n=== Listing Products ===")

    # Get first page of products
    products = client.products.list(limit=10)

    print(f"Found {len(products)} products on first page")

    # Iterate through first page
    for product in products:
        print(f"- {product['name']} (SKU: {product.get('sku', 'N/A')})")

    # Auto-paginate through all products
    print("\nAuto-paginating through all products...")
    count = 0
    for product in client.products.list().auto_paginate():
        count += 1
        if count <= 5:  # Show first 5
            print(f"- {product['name']}")

    print(f"Total products: {count}")


def search_products_example():
    """Example: Search for products."""
    print("\n=== Searching Products ===")

    # Search by name
    results = client.products.list(search="Dream")

    print(f"Found {len(results)} products matching 'Dream'")
    for product in results:
        print(f"- {product['name']}")


def create_product_example():
    """Example: Create a new product."""
    print("\n=== Creating Product ===")

    try:
        product = client.products.create(
            name="Example Product 1g",
            sku="EX-1G",
            unit_type_id=1,
            inventory_tracking_method="BATCH",
            description="An example product for testing",
            sale_price="15.00",
            wholesale_price="10.00",
        )

        print(f"Created product: {product['name']}")
        print(f"Product ID: {product['id']}")
        return product["id"]

    except ValidationError as e:
        print(f"Validation error: {e.message}")
        print(f"Details: {e.details}")
        return None


def get_product_example(product_id):
    """Example: Get a specific product."""
    print("\n=== Getting Product ===")

    try:
        product = client.products.get(product_id)
        print(f"Product: {product['name']}")
        print(f"SKU: {product.get('sku')}")
        print(f"Price: ${product.get('sale_price')}")

    except NotFoundError:
        print(f"Product {product_id} not found")


def list_orders_example():
    """Example: List orders with filters."""
    print("\n=== Listing Orders ===")

    # List recent orders
    orders = client.orders.list(limit=5)

    print(f"Found {len(orders)} orders")
    for order in orders:
        print(f"- {order['order_number']} - Status: {order['status']}")

    # Filter by status
    submitted_orders = client.orders.list(status="Submitted")
    print(f"\nFound {len(submitted_orders)} submitted orders")


def create_order_example(customer_id, product_id):
    """Example: Create a sales order."""
    print("\n=== Creating Order ===")

    try:
        order = client.orders.create(
            company_relationship_id=customer_id,
            order_date="2025-10-06T12:00:00Z",
            due_date="2025-10-20T12:00:00Z",
            status="Draft",
            order_items=[
                {
                    "product_id": product_id,
                    "quantity": 10,
                    "unit_price": "15.00",
                }
            ],
        )

        print(f"Created order: {order['order_number']}")
        print(f"Order ID: {order['id']}")
        print(f"Total: ${order.get('total', '0.00')}")
        return order["id"]

    except ValidationError as e:
        print(f"Validation error: {e.message}")
        return None


def list_inventory_example():
    """Example: Get current inventory."""
    print("\n=== Listing Inventory ===")

    # Get inventory with costs
    inventory = client.inventory.list(include_costs=True, limit=10)

    print(f"Found {len(inventory)} inventory items")
    for item in inventory:
        product_name = item.get("product_name", "Unknown")
        quantity = item.get("quantity", 0)
        cost = item.get("cost_per_unit_actual", "N/A")
        print(f"- {product_name}: {quantity} units (Cost: ${cost})")


def list_companies_example():
    """Example: List companies (customers/vendors)."""
    print("\n=== Listing Companies ===")

    # List all companies
    companies = client.companies.list(limit=10)

    print(f"Found {len(companies)} companies")
    for company in companies:
        name = company.get("name", "Unknown")
        state = company.get("us_state", "N/A")
        print(f"- {name} ({state})")

    # Search for specific company
    results = client.companies.list(search="Acme")
    print(f"\nFound {len(results)} companies matching 'Acme'")


def create_invoice_example(order_id):
    """Example: Create an invoice."""
    print("\n=== Creating Invoice ===")

    try:
        invoice = client.invoices.create(
            order_id=order_id,
            invoice_date="2025-10-06T12:00:00Z",
            due_date="2025-10-20T12:00:00Z",
            invoice_items=[
                {
                    "order_item_id": "order-item-uuid",  # Replace with actual
                    "quantity": 10,
                }
            ],
        )

        print(f"Created invoice: {invoice['invoice_number']}")
        print(f"Invoice ID: {invoice['id']}")
        print(f"Total: ${invoice.get('total', '0.00')}")
        return invoice["id"]

    except ValidationError as e:
        print(f"Validation error: {e.message}")
        return None


def error_handling_example():
    """Example: Error handling."""
    print("\n=== Error Handling Examples ===")

    # Handle not found
    try:
        client.products.get("invalid-uuid")
    except NotFoundError as e:
        print(f"✓ Caught NotFoundError: {e.message}")

    # Handle validation errors
    try:
        client.products.create(
            name="",  # Invalid: name required
            unit_type_id=1,
            inventory_tracking_method="BATCH",
        )
    except ValidationError as e:
        print(f"✓ Caught ValidationError: {e.message}")

    # Handle rate limits
    try:
        # This would trigger if rate limited
        pass
    except RateLimitError as e:
        print(f"Rate limited, retry after {e.retry_after} seconds")

    # Generic error handling
    try:
        # Some API call
        pass
    except DistruAPIError as e:
        print(f"API Error [{e.status_code}]: {e.message}")


def pagination_examples():
    """Example: Different pagination patterns."""
    print("\n=== Pagination Examples ===")

    # Method 1: Auto-paginate (easiest)
    print("Method 1: Auto-paginate")
    count = 0
    for product in client.products.list().auto_paginate():
        count += 1
    print(f"Total products (auto-paginate): {count}")

    # Method 2: Iterate pages
    print("\nMethod 2: Iterate pages")
    page_num = 0
    for page in client.products.list(limit=100).iter_pages():
        page_num += 1
        print(f"Page {page_num}: {len(page)} items")
        if page_num >= 3:  # Stop after 3 pages for demo
            break

    # Method 3: Manual pagination
    print("\nMethod 3: Manual pagination")
    response = client.products.list(page=1, limit=100)
    print(f"Page 1: {len(response)} items")

    if response.has_more():
        response = client.products.list(page=2, limit=100)
        print(f"Page 2: {len(response)} items")


def context_manager_example():
    """Example: Using client as context manager."""
    print("\n=== Context Manager Example ===")

    with DistruClient(api_token=api_token) as client:
        products = client.products.list(limit=5)
        print(f"Found {len(products)} products")

    # Client connection is automatically closed


def main():
    """Run all examples."""
    print("=" * 60)
    print("Distru Python SDK - Basic Usage Examples")
    print("=" * 60)

    try:
        # List products
        list_products_example()

        # Search products
        search_products_example()

        # Get first product for other examples
        products = client.products.list(limit=1)
        if len(products) > 0:
            product_id = products[0]["id"]

            # Get specific product
            get_product_example(product_id)

            # List orders
            list_orders_example()

            # Get companies
            companies = client.companies.list(limit=1)
            if len(companies) > 0:
                customer_id = companies[0]["id"]

                # Create order (commented out - modify for your use case)
                # order_id = create_order_example(customer_id, product_id)

        # List inventory
        list_inventory_example()

        # List companies
        list_companies_example()

        # Error handling
        error_handling_example()

        # Pagination
        pagination_examples()

        # Context manager
        context_manager_example()

    except Exception as e:
        print(f"\nError running examples: {e}")
        raise

    print("\n" + "=" * 60)
    print("Examples completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
