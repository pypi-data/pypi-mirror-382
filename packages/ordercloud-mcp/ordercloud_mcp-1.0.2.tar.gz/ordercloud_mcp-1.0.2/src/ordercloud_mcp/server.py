from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("OrderCloudMCP")

# Constants
API_BASE = "http://localhost:3300/api/v1"
USER_AGENT = "ordercloud-mcp/1.0"

async def make_request(
    method: str, endpoint: str, params: dict[str, Any] | None = None, body: dict[str, Any] | None = None
) -> dict[str, Any] | None:
    """Generic HTTP request helper for Order Cloud API."""
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    
    # Add Content-Type header for POST/PUT requests
    if body is not None:
        headers["Content-Type"] = "application/json"
    
    url = f"{API_BASE}{endpoint}"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(method, url, headers=headers, params=params, json=body, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"HTTP error {e.response.status_code}: {e.response.text}")
            return None
        except Exception as e:
            print(f"Request error: {e}")
            return None

def format_order(order: dict) -> str:
    """Format a single order into readable text."""
    items = order.get("order_items", [])
    items_str = "\n".join(
        f"- Product: {item['product_id']} (qty: {item['quantity']}, price: ${item['price']})" 
        for item in items
    )
    
    # Format dates nicely
    created_on = order.get('created_on', 'N/A')
    if created_on != 'N/A':
        created_at = created_on.replace('T', ' ').replace('Z', '').split('.')[0]
    else:
        created_at = 'N/A'
    
    return f"""Order ID: {order.get('id')}
Customer ID: {order.get('customer_id')}
Prescription ID: {order.get('prescription_id')}
Active: {order.get('is_active')}
Payment Done: {order.get('is_payment_done')}
Total Amount: ${order.get('total_amount')}
Created: {created_at}
Items:
{items_str if items_str else '  No items'}
"""

@mcp.tool()
async def get_order(order_id: str) -> str:
    """
    Retrieve a single order by ID with all its details including items, events, and CSR actions.
    
    Args:
        order_id: UUID of the order to retrieve
    """
    data = await make_request("GET", f"/order/{order_id}")
    if not data or not data.get("success"):
        return f"❌ Unable to fetch order {order_id}. Please check if the order ID is valid."
    
    order = data["data"]
    formatted_order = format_order(order)
    
    # Add events and CSR actions if they exist
    events = order.get("order_events", [])
    csr_actions = order.get("csr_actions", [])
    
    if events:
        events_str = "\n".join(
            f"- {event.get('event_type', 'N/A')} (triggered by: {event.get('triggered_by', 'N/A')})"
            for event in events
        )
        formatted_order += f"\nEvents:\n{events_str}"
    
    if csr_actions:
        actions_str = "\n".join(f"- Action ID: {action.get('id', 'N/A')}" for action in csr_actions)
        formatted_order += f"\nCSR Actions:\n{actions_str}"
    
    return formatted_order

@mcp.tool()
async def list_orders(page: int = 1, limit: int = 10, is_active: bool | None = None) -> str:
    """
    Retrieve all orders with pagination support. Can filter by active status.
    
    Args:
        page: Page number for pagination (default: 1)
        limit: Number of orders per page (default: 10)
        is_active: Filter by active status (true/false/None)
    """
    params: dict[str, Any] = {"page": str(page), "limit": str(limit)}
    if is_active is not None:
        params["isActive"] = str(is_active).lower()
    
    data = await make_request("GET", "/order", params=params)
    if not data or not data.get("success"):
        return "❌ Unable to fetch orders."
    
    orders_data = data["data"]
    orders = orders_data.get("orders", [])
    total = orders_data.get("total", 0)
    current_page = orders_data.get("page", page)
    current_limit = orders_data.get("limit", limit)
    
    if not orders:
        return "📭 No orders found."
    
    header = f"📋 Orders (Page {current_page}, Limit {current_limit}, Total: {total})\n" + "="*60
    orders_list = "\n---\n".join(format_order(order) for order in orders)
    
    return f"{header}\n{orders_list}"

@mcp.tool()
async def create_order(
    customer_id: str,
    prescription_id: str,
    created_by: str,
    order_items: list[dict[str, Any]],
    total_amount: str | None = None,
    is_payment_done: bool = False,
    is_active: bool = True
) -> str:
    """
    Create a new order with items. Automatically generates UUIDs and calculates totals if not provided.
    
    Args:
        customer_id: UUID of the customer
        prescription_id: UUID of the prescription
        created_by: UUID of the user creating the order
        order_items: List of order items with product_id, quantity, price, and created_by
        total_amount: Total amount (calculated if not provided)
        is_payment_done: Payment status (default: False)
        is_active: Active status (default: True)
    """
    order_data = {
        "customer_id": customer_id,
        "prescription_id": prescription_id,
        "created_by": created_by,
        "order_items": order_items,
        "is_payment_done": is_payment_done,
        "is_active": is_active
    }
    
    if total_amount is not None:
        order_data["total_amount"] = total_amount
    
    data = await make_request("POST", "/order", body=order_data)
    if not data or not data.get("success"):
        return "❌ Unable to create order. Please check the request data."
    
    order_info = data["data"]
    order_id = order_info.get("order_id")
    message = order_info.get("message", "Order created successfully!")
    
    return f"✅ {message}\nOrder ID: {order_id}"

@mcp.tool()
async def delete_order(order_id: str, deleted_by: str) -> str:
    """
    Delete an order (soft delete).
    
    Args:
        order_id: UUID of the order to delete
        deleted_by: UUID of the user deleting the order
    """
    params = {"deleted_by": deleted_by}
    data = await make_request("DELETE", f"/order/{order_id}", params=params)
    if not data or not data.get("success"):
        return f"❌ Unable to delete order {order_id}. Please check if the order ID is valid."
    
    return f"🗑️ Order {order_id} has been deleted successfully."

@mcp.tool()
async def get_orders_by_customer(customer_id: str) -> str:
    """
    Get all orders for a specific customer.
    
    Args:
        customer_id: UUID of the customer
    """
    data = await make_request("GET", f"/order/customer/{customer_id}")
    if not data or not data.get("success"):
        return f"❌ Unable to fetch orders for customer {customer_id}."
    
    orders = data["data"]
    if not orders:
        return f"📭 No orders found for customer {customer_id}."
    
    header = f"📋 Orders for Customer: {customer_id}\n" + "="*50
    orders_list = "\n---\n".join(format_order(order) for order in orders)
    
    return f"{header}\n{orders_list}"

@mcp.tool()
async def cancel_order(order_id: str, cancelled_by: str) -> str:
    """
    Cancel an order.
    
    Args:
        order_id: UUID of the order to cancel
        cancelled_by: UUID of the user cancelling the order
    """
    body = {"cancelled_by": cancelled_by}
    data = await make_request("PUT", f"/order/{order_id}/cancel", body=body)
    if not data or not data.get("success"):
        return f"❌ Unable to cancel order {order_id}. Please check if the order ID is valid."
    
    return f"❌ Order {order_id} has been cancelled successfully."

@mcp.tool()
async def add_csr_action(
    order_id: str, 
    csr_id: str, 
    action_type: str, 
    old_values: dict[str, Any], 
    new_values: dict[str, Any], 
    created_by: str
) -> str:
    """
    Add a CSR action to an order.
    
    Args:
        order_id: UUID of the order
        csr_id: UUID of the CSR performing the action
        action_type: Type of action performed
        old_values: Previous values before the change
        new_values: New values after the change
        created_by: UUID of the user creating this record
    """
    action_data = {
        "csr_id": csr_id,
        "action_type": action_type,
        "old_values": old_values,
        "new_values": new_values,
        "created_by": created_by
    }
    
    data = await make_request("POST", f"/csr/order/{order_id}/action", body=action_data)
    if not data or not data.get("success"):
        return f"❌ Unable to add CSR action to order {order_id}."
    
    action_id = data["data"].get("action_id", "Unknown")
    return f"👤 CSR action added successfully to order {order_id}. Action ID: {action_id}"

def main():
    """Entry point for the MCP server."""
    import sys
    
    # Check for transport argument
    transport = "stdio"
    if len(sys.argv) > 1 and sys.argv[1] == "--sse":
        transport = "sse"
    
    mcp.run(transport=transport)

if __name__ == "__main__":
    main()