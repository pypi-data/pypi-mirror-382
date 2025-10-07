# OdooPyClient

Python client library for Odoo using the requests library and JSON-RPC.

## Quick Start

```python
from odoo_client import OdooPyClient

# Connect to Odoo
odoo = OdooPyClient(
    host='http://localhost',
    port=8069,
    database='odoo',
    username='admin',
    password='admin'
)

# Authenticate
odoo.authenticate()

# Search and read records
products = odoo.search_read(
    model='product.product',
    domain=[['sale_ok', '=', True]],
    fields=['name', 'lst_price'],
    limit=10
)

# Create a record
partner_id = odoo.create(
    model='res.partner',
    values={'name': 'John Doe', 'email': 'john@example.com'}
)

# Update a record
odoo.update(
    model='res.partner',
    ids=partner_id,
    values={'phone': '+1234567890'}
)

# Delete a record
odoo.delete(model='res.partner', ids=partner_id)
```

## Installation

Install from PyPI:

```bash
pip install odoo-pyclient
```

Or install from source:

```bash
git clone https://github.com/mohamed-helmy/OdooPyClient.git
cd OdooPyClient
pip install -r requirements.txt
```

## Usage

Please refer to the Odoo [API documentation](https://www.odoo.com/documentation/16.0/developer/reference/backend/orm.html) if you need help structuring your database queries.

### Creating Odoo connection instance

Before executing any kind of query operations, a connection instance must be established either with a username/password or with a previously retrieved session id.

```python
from odoo_client import OdooPyClient

odoo = OdooPyClient(
    host='http://localhost',
    port=8069,  # Defaults to 80 if not specified
    database='your_database_name',
    username='your_username',  # Optional if using a stored session_id
    password='your_password',  # Optional if using a stored session_id
    session_id='your_session_id',  # Optional if using username/password
    context={'lang': 'en_US'},  # Optional - context like language
)
```

### authenticate

Authenticate with the Odoo server. Returns user data including a session id which can be stored for future connections and session persistence.

```python
try:
    result = odoo.authenticate()
    print(f"Session ID: {odoo.session_id}")
    print(f"User ID: {result.get('uid')}")
except Exception as e:
    print(f"Authentication failed: {e}")
```

### read

Receives an Odoo database model string and parameters containing the IDs you want to read and the fields you want to retrieve from each result.

Returns a list of results matching the array of IDs provided in the parameters.

```python
# Read partner from server
result = odoo.read(
    model='res.partner',
    ids=[1, 2, 3, 4, 5],
    fields=['name']
)
```

### search_read

Just like the read method, this one receives a model string and parameters. With this method the parameters may include a domain list for filtering purposes (with filter statements similar to SQL's WHERE), limit and offset values for pagination and an order property which can be set to specific fields.

Returns a list of results matching the parameters provided.

```python
result = odoo.search_read(
    model='product.product',
    domain=[['list_price', '>', '50'], ['list_price', '<', '65']],
    fields=['name', 'list_price', 'items'],
    order='list_price DESC',
    limit=5,
    offset=0
)
```

### create

Receives a model string and a values dictionary with properties corresponding to the fields you want to write in the row.

**Example: Create a sale order with order lines**

```python
# Get a customer
partners = odoo.search_read(
    model='res.partner',
    domain=[['customer_rank', '>', 0]],
    fields=['id', 'name'],
    limit=1
)
partner_id = partners[0]['id']

# Get products
products = odoo.search_read(
    model='product.product',
    domain=[['sale_ok', '=', True]],
    fields=['id', 'name', 'lst_price'],
    limit=2
)

# Create sale order with order lines
sale_order_id = odoo.create(
    model='sale.order',
    values={
        'partner_id': partner_id,
        'order_line': [
            (0, 0, {
                'product_id': products[0]['id'],
                'product_uom_qty': 2,
                'price_unit': products[0]['lst_price'],
            }),
            (0, 0, {
                'product_id': products[1]['id'],
                'product_uom_qty': 3,
                'price_unit': products[1]['lst_price'],
            }),
        ],
    }
)
print(f"Created sale order with ID: {sale_order_id}")
```

### update

Receives a model string, a list of IDs (or single ID) related to the rows you want to update in the database, and a values dictionary with properties corresponding to the fields that are going to be updated.

If you need to update several rows in the database you can take advantage of Python's concurrent features (see `examples/async_usage.py`) to generate and populate updates in parallel.

**Example: Update a sale order**

```python
result = odoo.update(
    model='sale.order',
    ids=sale_order_id,  # or [1, 2, 3] for multiple IDs
    values={
        'client_order_ref': 'PO-2025-001',
        'note': 'Updated order with client reference',
    }
)
print("Sale order updated successfully")
```

### delete

Receives an Odoo database model string and an IDs list (or single ID) corresponding to the rows you want to delete in the database.

**Example: Delete a sale order (after canceling)**

```python
# First, cancel the order (required before deletion)
odoo.rpc_call(
    endpoint='/web/dataset/call_kw',
    params={
        'model': 'sale.order',
        'method': 'action_cancel',
        'args': [[sale_order_id]],
        'kwargs': {'context': odoo.context}
    }
)

# Now delete it
result = odoo.delete(
    model='sale.order',
    ids=sale_order_id
)
print(f"Order {sale_order_id} deleted successfully")
```

### rpc_call (Generic RPC Call)

If you wish to execute a custom RPC call not represented in this library's methods, you can also run a custom call by passing an endpoint string and a params dictionary. This requires understanding how the Odoo Web API works more thoroughly so you can properly structure the function parameters.

**Example 1: Confirm a sale order**

```python
result = odoo.rpc_call(
    endpoint='/web/dataset/call_kw',
    params={
        'model': 'sale.order',
        'method': 'action_confirm',
        'args': [[sale_order_id]],
        'kwargs': {'context': odoo.context}
    }
)
print("Sale order confirmed")
```

**Example 2: Search for confirmed orders**

```python
order_ids = odoo.rpc_call(
    endpoint='/web/dataset/call_kw',
    params={
        'model': 'sale.order',
        'method': 'search',
        'args': [[['state', '=', 'sale']]],
        'kwargs': {
            'limit': 5,
            'order': 'date_order desc',
            'context': odoo.context
        }
    }
)
print(f"Found {len(order_ids)} confirmed sale orders")
```

**Example 3: Count orders by state**

```python
count = odoo.rpc_call(
    endpoint='/web/dataset/call_kw',
    params={
        'model': 'sale.order',
        'method': 'search_count',
        'args': [[['state', '=', 'draft']]],
        'kwargs': {'context': odoo.context}
    }
)
print(f"Draft orders: {count}")
```

## Complete Workflow Example

Here's a complete example showing the full lifecycle of a sale order:

```python
from odoo_client import OdooPyClient

# 1. Connect and authenticate
odoo = OdooPyClient(
    host='http://localhost',
    port=8069,
    database='odoo',
    username='admin',
    password='admin'
)

result = odoo.authenticate()
print(f"Authenticated as user {result['uid']}")

# 2. Create a sale order
partners = odoo.search_read(
    model='res.partner',
    domain=[['customer_rank', '>', 0]],
    fields=['id', 'name'],
    limit=1
)
partner_id = partners[0]['id']

products = odoo.search_read(
    model='product.product',
    domain=[['sale_ok', '=', True]],
    fields=['id', 'name', 'lst_price'],
    limit=2
)

sale_order_id = odoo.create(
    model='sale.order',
    values={
        'partner_id': partner_id,
        'order_line': [
            (0, 0, {
                'product_id': products[0]['id'],
                'product_uom_qty': 2,
                'price_unit': products[0]['lst_price'],
            })
        ]
    }
)
print(f"Created sale order: {sale_order_id}")

# 3. Read the order
order_data = odoo.read(
    model='sale.order',
    ids=[sale_order_id],
    fields=['name', 'partner_id', 'state', 'amount_total']
)
print(f"Order {order_data[0]['name']}: ${order_data[0]['amount_total']}")

# 4. Update the order
odoo.update(
    model='sale.order',
    ids=sale_order_id,
    values={
        'client_order_ref': 'PO-2025-001',
        'note': 'Updated via API'
    }
)
print("Order updated")

# 5. Confirm the order
odoo.rpc_call(
    endpoint='/web/dataset/call_kw',
    params={
        'model': 'sale.order',
        'method': 'action_confirm',
        'args': [[sale_order_id]],
        'kwargs': {'context': odoo.context}
    }
)
print("Order confirmed")

# 6. Search for confirmed orders
order_ids = odoo.rpc_call(
    endpoint='/web/dataset/call_kw',
    params={
        'model': 'sale.order',
        'method': 'search',
        'args': [[['state', '=', 'sale']]],
        'kwargs': {'limit': 5, 'context': odoo.context}
    }
)
print(f"Found {len(order_ids)} confirmed orders")

# 7. Cancel and delete (optional)
odoo.rpc_call(
    endpoint='/web/dataset/call_kw',
    params={
        'model': 'sale.order',
        'method': 'action_cancel',
        'args': [[sale_order_id]],
        'kwargs': {'context': odoo.context}
    }
)

odoo.delete(model='sale.order', ids=sale_order_id)
print("Order deleted")
```

## Features

- ✅ Authentication with username/password or session ID
- ✅ Session management with cookies
- ✅ CRUD operations (Create, Read, Update, Delete)
- ✅ Search and search_read operations
- ✅ Generic RPC call support
- ✅ Context support (language, timezone, etc.)

## Examples

See the `examples/` directory for more detailed usage examples:
- `example.py` - Complete sale order workflow (create, read, update, delete)

## References

- [Odoo ORM API Reference](https://www.odoo.com/documentation/16.0/developer/reference/backend/orm.html)
- [Odoo Web Service External API](https://www.odoo.com/documentation/16.0/developer/reference/external_api.html)

## License

This project is licensed under the MIT License - see the LICENSE file for details.


## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Author

Mohamed Helmy
