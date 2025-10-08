"""
Tests for Universal MCP Runner
"""

import pytest
import asyncio
import json
from pathlib import Path
from tmcp_runner import TMCPRunner, MCPClient


def test_invalid_config(tmp_path):
    """Test that invalid config raises ValueError"""
    invalid = tmp_path / "bad.json"
    invalid.write_text('{"foo": "bar"}')
    with pytest.raises(ValueError):
        TMCPRunner(str(invalid))


def test_missing_config():
    """Test that missing config file raises FileNotFoundError"""
    with pytest.raises(FileNotFoundError):
        TMCPRunner("nonexistent.json")


def test_valid_config_loading(tmp_path):
    """Test that valid config loads successfully"""
    config = tmp_path / "test.json"
    config_data = {
        "mcpServers": {
            "test-server": {
                "command": "echo",
                "args": ["hello"],
                "transport": "stdio"
            }
        }
    }
    config.write_text(json.dumps(config_data))
    
    runner = TMCPRunner(str(config))
    assert runner.list_servers() == ["test-server"]


def test_list_servers(tmp_path):
    """Test listing configured servers"""
    config = tmp_path / "test.json"
    config_data = {
        "mcpServers": {
            "server1": {"command": "cmd1", "transport": "stdio"},
            "server2": {"command": "cmd2", "transport": "stdio"},
            "server3": {"command": "cmd3", "transport": "stdio"}
        }
    }
    config.write_text(json.dumps(config_data))
    
    runner = TMCPRunner(str(config))
    servers = runner.list_servers()
    
    assert len(servers) == 3
    assert "server1" in servers
    assert "server2" in servers
    assert "server3" in servers


@pytest.mark.asyncio
async def test_connect_nonexistent_server(tmp_path):
    """Test that connecting to nonexistent server raises ValueError"""
    config = tmp_path / "test.json"
    config_data = {"mcpServers": {}}
    config.write_text(json.dumps(config_data))
    
    runner = TMCPRunner(str(config))
    
    with pytest.raises(ValueError, match="not found in configuration"):
        await runner.connect_server("nonexistent")


@pytest.mark.asyncio
async def test_mcp_client_invalid_transport():
    """Test that invalid transport type raises ValueError"""
    config = {
        "command": "test",
        "transport": "invalid"
    }
    
    client = MCPClient("test", config)
    
    with pytest.raises(ValueError, match="Unsupported transport type"):
        await client.connect()


@pytest.mark.asyncio
async def test_mcp_client_missing_command():
    """Test that missing command raises ValueError for stdio"""
    config = {
        "transport": "stdio"
    }
    
    client = MCPClient("test", config)
    
    with pytest.raises(ValueError, match="Missing 'command'"):
        await client.connect()


@pytest.mark.asyncio
async def test_mcp_client_missing_url_for_sse():
    """Test that missing URL raises ValueError for SSE"""
    config = {
        "transport": "sse"
    }
    
    client = MCPClient("test", config)
    
    with pytest.raises(ValueError, match="Missing 'url'"):
        await client.connect()


def test_client_operations_without_connection():
    """Test that operations fail when client is not connected"""
    config = {"command": "test", "transport": "stdio"}
    client = MCPClient("test", config)
    
    # These should raise RuntimeError since client is not connected
    with pytest.raises(RuntimeError, match="not connected"):
        asyncio.run(client.list_tools())
    
    with pytest.raises(RuntimeError, match="not connected"):
        asyncio.run(client.list_resources())
    
    with pytest.raises(RuntimeError, match="not connected"):
        asyncio.run(client.call_tool("test", {}))


@pytest.mark.asyncio
async def test_disconnect_all(tmp_path):
    """Test that disconnect_all works correctly"""
    config = tmp_path / "test.json"
    config_data = {
        "mcpServers": {
            "test-server": {
                "command": "echo",
                "args": ["hello"],
                "transport": "stdio"
            }
        }
    }
    config.write_text(json.dumps(config_data))
    
    runner = TMCPRunner(str(config))
    
    # Should not raise any errors even with no connections
    await runner.disconnect_all()
    
    assert len(runner.clients) == 0


# Integration test markers for tests that need actual MCP servers
@pytest.mark.integration
@pytest.mark.asyncio
async def test_real_mcp_server_connection():
    """
    Integration test with a real MCP server (requires actual server to be available)
    This test is skipped by default - run with: pytest -m integration
    """
    # This would test with a real MCP server
    # For now, we'll skip this in regular test runs
    pytest.skip("Integration tests require real MCP server setup")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
