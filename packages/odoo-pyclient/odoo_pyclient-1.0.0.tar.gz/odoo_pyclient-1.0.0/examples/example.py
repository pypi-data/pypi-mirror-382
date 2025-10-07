"""
Basic usage examples for OdooPyClient.
"""

from odoo_client import OdooPyClient

# Create Odoo connection instance
odoo = OdooPyClient(
    host='http://localhost',
    port=8069,
        database='odoo',
        username='admin',
        password='admin',
    # Optional: use session_id instead of username/password
    # session_id='your_session_id',
    # Optional: context for settings like language
    # context={'lang': 'en_US'}
)

# Authenticate
try:
    result = odoo.authenticate()
    print("Authentication successful!")
    print(f"User ID: {result.get('uid')}")
    print(f"Session ID: {odoo.session_id}")
except Exception as e:
    print(f"Authentication failed: {e}")

# Read records
params = {
    'ids': [1, 2, 3, 4, 5],
    'fields': ['name']
}
try:
    result = odoo.read('res.partner', ids=[1, 2, 3, 4, 5], fields=['name'])
    print(f"Read results: {result}")
except Exception as e:
    print(f"Read failed: {e}")

# Search and read records
try:
    result = odoo.search_read(
        model='product.product',
        domain=[['lst_price', '>', '50'], ['lst_price', '<', '65']],
        fields=['name', 'lst_price'],
        order='name DESC',
        limit=5,
        offset=0
    )
    print(f"Search read results: {result}")
except Exception as e:
    print(f"Search read failed: {e}")

print("\n1. Creating a new sale order with order lines...")
try:
    partners = odoo.search_read(
        model='res.partner',
        domain=[['customer_rank', '>', 0]],
        fields=['id', 'name'],
        limit=1
    )
    
    if not partners:
        print("No customers found. Creating a test customer first...")
        partner_id = odoo.create(
            model='res.partner',
            values={
                'name': 'Test Customer',
                'email': 'test@example.com',
                'phone': '+1234567890',
                'customer_rank': 1,
            }
        )
        print(f"Created test customer with ID: {partner_id}")
    else:
        partner_id = partners[0]['id']
        print(f"Using existing customer: {partners[0]['name']} (ID: {partner_id})")

    # Get products to use in order lines
    products = odoo.search_read(
        model='product.product',
        domain=[['sale_ok', '=', True]],
        fields=['id', 'name', 'lst_price'],
        limit=2
    )
    
    
    if products:
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
                    })
                ]
            }
        )
        print(f"Created sale order with ID: {sale_order_id}")
        print(f"  Product 1: {products[0]['name']} (Qty: 2)")
    else:
        print("Cannot create sale order without products.")
        sale_order_id = None
        
except Exception as e:
    print(f"Create sale order failed: {e}")
    sale_order_id = None

# 2. READ: Read the created sale order
if sale_order_id:
    print(f"Reading sale order {sale_order_id}...")
    try:
        order_data = odoo.read(
            model='sale.order',
            ids=[sale_order_id],
            fields=['name', 'partner_id', 'state', 'amount_total', 'order_line']
        )
        if order_data:
            print(f"Order: {order_data[0]['name']}")
            print(f"Partner: {order_data[0]['partner_id'][1]}")
            print(f"State: {order_data[0]['state']}")
            print(f"Total: {order_data[0]['amount_total']}")
    except Exception as e:
        print(f"Read failed: {e}")

# 3. UPDATE: Update the sale order
if sale_order_id:
    print(f"Updating sale order {sale_order_id}...")
    try:
        result = odoo.update(
            model='sale.order',
            ids=sale_order_id,
            values={
                'client_order_ref': 'PO-2025-001',
                'note': 'Updated order with client reference',
            }
        )
        print(f"Updated sale order successfully")
        print(f"- Added client order reference: PO-2025-001")
        print(f"- Added note: Updated order with client reference")
    except Exception as e:
        print(f"Update failed: {e}")

# 4. RPC CALL: Confirm the sale order using action_confirm
if sale_order_id:
    print(f"Confirming sale order {sale_order_id} using RPC call...")
    try:
        result = odoo.rpc_call(
            endpoint='/web/dataset/call_kw',
            params={
                'model': 'sale.order',
                'method': 'action_confirm',
                'args': [[sale_order_id]],
                'kwargs': {'context': odoo.context}
            }
        )
        print(f"Sale order confirmed successfully")
    except Exception as e:
        print(f"Confirm failed: {e}")

# 5. SEARCH: Search for confirmed sale orders using RPC call
print("Searching for confirmed sale orders...")
try:
    # Search for sale orders with state 'sale' (confirmed)
    order_ids = odoo.rpc_call(
        endpoint='/web/dataset/call_kw',
        params={
            'model': 'sale.order',
            'method': 'search',
            'args': [[['state', '=', 'draft']]],
            'kwargs': {
                'limit': 5,
                'order': 'date_order desc',
                'context': odoo.context
            }
        }
    )
    print(f"Found {len(order_ids)} confirmed sale orders")
    
except Exception as e:
    print(f"Search failed: {e}")


# 7. DELETE: Delete the created sale order
if sale_order_id:
    print(f"Delete sale order...")
    try:
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
        print(f"Order {sale_order_id} cancelled")
        
        # Now delete it
        result = odoo.delete(
            model='sale.order',
            ids=sale_order_id
        )
        print(f"Order {sale_order_id} deleted successfully")
    except Exception as e:
        print(f"Delete failed: {e}")
