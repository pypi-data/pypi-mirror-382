"""
Universal MCP Runner using official Anthropic MCP Protocol
Supports stdio, SSE, and HTTP transports like Claude Desktop and Cursor
"""

import json
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from contextlib import asynccontextmanager

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.sse import sse_client
from mcp.types import (
    Tool,
    Resource,
    TextContent,
    ImageContent,
    EmbeddedResource,
)

# Optional: httpx for HTTP transport (not in official SDK yet)
try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False


class MCPClient:
    """
    Individual MCP client for a single server connection.
    Handles initialization, resource discovery, and tool execution.
    """

    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.session: Optional[ClientSession] = None
        self._read_stream = None
        self._write_stream = None
        self._stdio_context = None
        self._sse_context = None
        self._http_client = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()
        
    async def connect(self):
        """Establish connection to MCP server based on transport type"""
        transport_type = self.config.get("transport", "stdio")
        
        if transport_type == "stdio":
            await self._connect_stdio()
        elif transport_type == "sse":
            await self._connect_sse()
        elif transport_type in ("http", "https"):
            await self._connect_http()
        else:
            raise ValueError(f"Unsupported transport type: {transport_type}")
            
    async def _connect_stdio(self):
        """Connect to stdio-based MCP server"""
        command = self.config.get("command")
        args = self.config.get("args", [])
        env = self.config.get("env", {})
        
        if not command:
            raise ValueError(f"Missing 'command' in config for server: {self.name}")
            
        server_params = StdioServerParameters(
            command=command,
            args=args,
            env=env
        )
        
        # Create stdio connection using context manager
        stdio_context = stdio_client(server_params)
        self._read_stream, self._write_stream = await stdio_context.__aenter__()
        self._stdio_context = stdio_context
        
        self.session = ClientSession(self._read_stream, self._write_stream)
        
        # Initialize the session
        await self.session.__aenter__()
        
        # Initialize the MCP server
        await self.session.initialize()
        
    async def _connect_sse(self):
        """Connect to SSE-based MCP server"""
        url = self.config.get("url")
        
        if not url:
            raise ValueError(f"Missing 'url' in config for SSE server: {self.name}")
            
        # Create SSE connection using context manager
        sse_context = sse_client(url)
        self._read_stream, self._write_stream = await sse_context.__aenter__()
        self._sse_context = sse_context
        
        self.session = ClientSession(self._read_stream, self._write_stream)
        
        # Initialize the session
        await self.session.__aenter__()
        
        # Initialize the MCP server
        await self.session.initialize()
    
    async def _connect_http(self):
        """
        Connect to HTTP/HTTPS-based MCP server
        
        Note: HTTP transport is not yet officially supported in the MCP Python SDK.
        This is a placeholder for future implementation or custom HTTP adapters.
        
        For now, consider using SSE transport for HTTP-based servers.
        """
        raise NotImplementedError(
            f"HTTP/HTTPS transport is not yet implemented in the official MCP SDK. "
            f"For HTTP-based servers, please use SSE transport instead by setting "
            f"'transport': 'sse' in your config for server '{self.name}'."
        )
        
    async def disconnect(self):
        """Close the MCP server connection"""
        import asyncio
        
        # Close session first
        if self.session:
            try:
                await self.session.__aexit__(None, None, None)
            except asyncio.CancelledError:
                # Expected during shutdown - ignore
                pass
            except Exception as e:
                # Ignore cancellation and cleanup errors
                if "cancel" not in str(e).lower():
                    print(f"⚠️  Error closing session for {self.name}: {e}")
            finally:
                self.session = None
        
        # Close transport contexts - these manage the underlying processes
        if self._stdio_context:
            try:
                await self._stdio_context.__aexit__(None, None, None)
            except asyncio.CancelledError:
                # Expected during shutdown - ignore
                pass
            except Exception:
                # Silent fail - context cleanup errors are common and harmless
                pass
            finally:
                self._stdio_context = None
        
        if self._sse_context:
            try:
                await self._sse_context.__aexit__(None, None, None)
            except asyncio.CancelledError:
                # Expected during shutdown - ignore
                pass
            except Exception:
                # Silent fail - context cleanup errors are common and harmless
                pass
            finally:
                self._sse_context = None
                
    async def list_tools(self) -> List[Tool]:
        """List all available tools from the MCP server"""
        if not self.session:
            raise RuntimeError(f"Client {self.name} is not connected")
            
        result = await self.session.list_tools()
        return result.tools
        
    async def list_resources(self) -> List[Resource]:
        """List all available resources from the MCP server"""
        if not self.session:
            raise RuntimeError(f"Client {self.name} is not connected")
        
        try:
            result = await self.session.list_resources()
            return result.resources
        except Exception as e:
            # Some servers don't support resources
            if "Unknown method" in str(e) or "resources/list" in str(e):
                return []
            raise
        
    async def read_resource(self, uri: str) -> Union[TextContent, ImageContent, EmbeddedResource]:
        """Read a specific resource by URI"""
        if not self.session:
            raise RuntimeError(f"Client {self.name} is not connected")
            
        result = await self.session.read_resource(uri)
        return result.contents
        
    async def call_tool(self, tool_name: str, arguments: Optional[Dict[str, Any]] = None) -> List[Union[TextContent, ImageContent, EmbeddedResource]]:
        """Execute a tool with given arguments"""
        if not self.session:
            raise RuntimeError(f"Client {self.name} is not connected")
            
        result = await self.session.call_tool(tool_name, arguments or {})
        return result.content
        
    async def list_prompts(self) -> List[Any]:
        """List all available prompts from the MCP server"""
        if not self.session:
            raise RuntimeError(f"Client {self.name} is not connected")
        
        try:
            result = await self.session.list_prompts()
            return result.prompts
        except Exception as e:
            # Some servers don't support prompts
            if "Unknown method" in str(e) or "prompts/list" in str(e):
                return []
            raise


class TMCPRunner:
    """
    Universal MCP Runner - Manages multiple MCP server connections
    Compatible with Claude Desktop and Cursor MCP configurations
    """

    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self.mcp_servers: Dict[str, Dict[str, Any]] = {}
        self.clients: Dict[str, MCPClient] = {}
        self._load_config()

    def _load_config(self):
        """Load MCP configuration from JSON file"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
            
        with open(self.config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        if "mcpServers" not in data:
            raise ValueError("Invalid configuration file (missing 'mcpServers')")
            
        self.mcp_servers = data["mcpServers"]

    def list_servers(self) -> List[str]:
        """List all configured MCP server names"""
        return list(self.mcp_servers.keys())

    async def connect_server(self, server_name: str) -> MCPClient:
        """Connect to a specific MCP server"""
        if server_name not in self.mcp_servers:
            raise ValueError(f"Server '{server_name}' not found in configuration")
            
        if server_name in self.clients:
            return self.clients[server_name]
            
        config = self.mcp_servers[server_name]
        client = MCPClient(server_name, config)
        await client.connect()
        self.clients[server_name] = client
        return client

    async def disconnect_server(self, server_name: str):
        """Disconnect from a specific MCP server"""
        if server_name in self.clients:
            await self.clients[server_name].disconnect()
            del self.clients[server_name]

    async def connect_all(self):
        """Connect to all configured MCP servers"""
        for server_name in self.mcp_servers.keys():
            try:
                await self.connect_server(server_name)
                print(f"✅ Connected to: {server_name}")
            except Exception as e:
                print(f"❌ Failed to connect to {server_name}: {e}")

    async def disconnect_all(self):
        """Disconnect from all MCP servers"""
        for server_name in list(self.clients.keys()):
            await self.disconnect_server(server_name)

    async def discover_all(self) -> Dict[str, Dict[str, Any]]:
        """
        Discover all resources and tools from all connected servers
        Returns a dictionary with server_name as key and discovery info as value
        """
        discovery = {}
        
        for server_name, client in self.clients.items():
            server_info = {
                "tools": [],
                "resources": [],
                "prompts": []
            }
            
            # Try to list tools (most servers support this)
            try:
                tools = await client.list_tools()
                server_info["tools"] = [
                    {"name": t.name, "description": t.description} 
                    for t in tools
                ]
            except Exception as e:
                print(f"⚠️  {server_name}: Cannot list tools - {type(e).__name__}")
            
            # Try to list resources (optional, not all servers support this)
            try:
                resources = await client.list_resources()
                server_info["resources"] = [
                    {"uri": r.uri, "name": r.name, "description": r.description} 
                    for r in resources
                ]
            except Exception:
                # Silent fail - resources are optional
                pass
            
            # Try to list prompts (optional, not all servers support this)
            try:
                prompts = await client.list_prompts()
                server_info["prompts"] = [
                    {"name": p.name, "description": getattr(p, 'description', '')} 
                    for p in prompts
                ]
            except Exception:
                # Silent fail - prompts are optional
                pass
            
            discovery[server_name] = server_info
                
        return discovery

    async def execute_tool(
        self,
        server_name: str,
        tool_name: str,
        arguments: Optional[Dict[str, Any]] = None
    ) -> List[Union[TextContent, ImageContent, EmbeddedResource]]:
        """Execute a tool on a specific server"""
        if server_name not in self.clients:
            await self.connect_server(server_name)
            
        client = self.clients[server_name]
        return await client.call_tool(tool_name, arguments)

    async def read_resource(self, server_name: str, uri: str):
        """Read a resource from a specific server"""
        if server_name not in self.clients:
            await self.connect_server(server_name)
            
        client = self.clients[server_name]
        return await client.read_resource(uri)

    async def run_all(self):
        """
        Connect to all servers and display available resources and tools
        Similar to Claude Desktop's MCP discovery
        """
        print("🚀 Universal MCP Runner - Discovering all servers...\n")
        
        await self.connect_all()
        
        if not self.clients:
            print("⚠️  No servers connected successfully\n")
            return
            
        discovery = await self.discover_all()
        
        print("\n📊 Discovery Results:\n")
        for server_name, info in discovery.items():
            print(f"🔹 Server: {server_name}")
            
            if "error" in info:
                print(f"   ❌ Error: {info['error']}")
                continue
            
            # Display tools
            tools = info.get("tools", [])
            if tools:
                print(f"   🛠️  Tools ({len(tools)}):")
                for tool in tools:
                    desc = tool.get('description', 'No description')
                    print(f"      • {tool['name']}: {desc}")
            else:
                print("   ⚠️  No tools available")
            
            # Display resources (only if found)
            resources = info.get("resources", [])
            if resources:
                print(f"   📦 Resources ({len(resources)}):")
                for resource in resources:
                    desc = resource.get('description', 'No description')
                    print(f"      • {resource.get('name', resource['uri'])}: {desc}")
            
            # Display prompts (only if found)
            prompts = info.get("prompts", [])
            if prompts:
                print(f"   💬 Prompts ({len(prompts)}):")
                for prompt in prompts:
                    desc = prompt.get('description', 'No description')
                    print(f"      • {prompt['name']}: {desc}")
            
            print()
            
        print("✅ Discovery completed\n")
        
        # Keep connections alive
        print("💡 All servers remain connected. Call disconnect_all() when done.\n")
