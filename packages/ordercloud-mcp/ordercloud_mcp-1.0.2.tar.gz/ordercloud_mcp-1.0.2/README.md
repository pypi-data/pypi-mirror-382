# OrderCloud MCP

A Model Context Protocol (MCP) server for Order Cloud API integration. This server provides tools for managing orders, customers, and CSR actions through the MCP protocol.

## Features

- 🛒 **Order Management**: Create, read, update, and delete orders
- 📋 **Order Listing**: List orders with pagination and filtering
- 👤 **Customer Orders**: Retrieve all orders for specific customers
- ❌ **Order Cancellation**: Cancel orders with tracking
- 👨‍💼 **CSR Actions**: Track customer service representative actions

## Installation

```bash
pip install ordercloud-mcp
```

## Usage

### As a Standalone Server

Run with stdio transport (default):
```bash
ordercloud-mcp
```

Run with SSE transport:
```bash
ordercloud-mcp --sse
```

### With Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ordercloud": {
      "command": "ordercloud-mcp"
    }
  }
}
```

### Programmatic Usage

```python
from ordercloud_mcp import mcp

# The server will be available for MCP clients
mcp.run(transport='stdio')
```

## Configuration

The server connects to the Order Cloud API at `http://localhost:3300/api/v1` by default. To change this, modify the `API_BASE` constant in your local installation.

## Available Tools

### `get_order`
Retrieve a single order by ID with all details.

**Parameters:**
- `order_id` (str): UUID of the order

### `list_orders`
Retrieve all orders with pagination.

**Parameters:**
- `page` (int): Page number (default: 1)
- `limit` (int): Orders per page (default: 10)
- `is_active` (bool|None): Filter by active status

### `create_order`
Create a new order with items.

**Parameters:**
- `customer_id` (str): Customer UUID
- `prescription_id` (str): Prescription UUID
- `created_by` (str): Creator UUID
- `order_items` (list): List of order items
- `total_amount` (str|None): Total amount
- `is_payment_done` (bool): Payment status
- `is_active` (bool): Active status

### `delete_order`
Soft delete an order.

**Parameters:**
- `order_id` (str): Order UUID
- `deleted_by` (str): Deleter UUID

### `get_orders_by_customer`
Get all orders for a specific customer.

**Parameters:**
- `customer_id` (str): Customer UUID

### `cancel_order`
Cancel an order.

**Parameters:**
- `order_id` (str): Order UUID
- `cancelled_by` (str): Canceller UUID

### `add_csr_action`
Add a CSR action to an order.

**Parameters:**
- `order_id` (str): Order UUID
- `csr_id` (str): CSR UUID
- `action_type` (str): Type of action
- `old_values` (dict): Previous values
- `new_values` (dict): New values
- `created_by` (str): Creator UUID

## Development

### Setup

```bash
git clone https://github.com/yourusername/ordercloud-mcp.git
cd ordercloud-mcp
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black src/
ruff check src/
```

## Requirements

- Python 3.10+
- httpx >= 0.24.0
- mcp >= 1.0.0

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please use the [GitHub Issues](https://github.com/yourusername/ordercloud-mcp/issues) page.