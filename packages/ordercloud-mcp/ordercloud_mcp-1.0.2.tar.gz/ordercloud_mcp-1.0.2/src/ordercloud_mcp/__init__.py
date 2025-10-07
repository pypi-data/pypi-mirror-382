"""OrderCloud MCP - MCP server for Order Cloud API integration."""

__version__ = "1.0.0"

from ordercloud_mcp.server import mcp, main

__all__ = ["mcp", "main"]