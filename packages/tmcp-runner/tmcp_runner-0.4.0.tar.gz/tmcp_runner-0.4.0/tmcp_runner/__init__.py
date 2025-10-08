"""
tmcp_runner

A universal Python library for integrating MCP (Model Context Protocol) capabilities
into your applications. Uses the official Anthropic MCP SDK to connect to MCP servers,
discover resources, and execute tools - just like Claude Desktop and Cursor do internally.

Usage:
    from tmcp_runner import TMCPRunner
    
    runner = TMCPRunner("path/to/mcp_config.json")
    await runner.connect_all()
    # Your app now has access to all configured MCP servers
"""

from .runner import TMCPRunner, MCPClient

__version__ = "0.4.0"
__all__ = ["TMCPRunner", "MCPClient"]
