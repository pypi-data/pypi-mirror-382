#!/usr/bin/env python3
"""
Test: Pydantic AI Agent Integration with MCP

This demonstrates how to integrate MCP tools into a Pydantic AI agent.
Uses Pydantic for type-safe tool definitions and validation.
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tmcp_runner import TMCPRunner


class ToolDefinition(BaseModel):
    """Type-safe tool definition using Pydantic"""
    name: str = Field(..., description="Tool identifier")
    server: str = Field(..., description="MCP server name")
    tool_name: str = Field(..., description="Tool name on server")
    description: str = Field(..., description="What the tool does")
    
    class Config:
        frozen = True


class ToolExecutionResult(BaseModel):
    """Type-safe result from tool execution"""
    success: bool = Field(..., description="Whether execution succeeded")
    output: str = Field(..., description="Tool output or error message")
    tool_name: str = Field(..., description="Name of tool that was executed")


class AgentState(BaseModel):
    """Type-safe agent state"""
    initialized: bool = False
    tools_count: int = 0
    active_servers: List[str] = []


class PydanticAIAgent:
    """
    Type-safe AI agent using Pydantic for validation.
    
    Benefits:
    - Type checking at runtime
    - Automatic validation of tool definitions
    - Clear data structures
    - Easy serialization
    """
    
    def __init__(self, mcp_config_path: str):
        self.mcp = TMCPRunner(mcp_config_path)
        self.tools: Dict[str, ToolDefinition] = {}
        self.state = AgentState()
        self.name = "PydanticAgent"
    
    async def initialize(self) -> bool:
        """Initialize agent with type-safe tool discovery"""
        print(f"🔍 Initializing {self.name} with type-safe MCP tools...")
        
        # Connect to MCP servers
        await self.mcp.connect_all()
        
        # Discover tools
        discovery = await self.mcp.discover_all()
        
        # Create type-safe tool definitions
        active_servers = []
        for server_name, info in discovery.items():
            if 'error' not in info:
                active_servers.append(server_name)
                
            for tool in info.get('tools', []):
                tool_id = f"{server_name}.{tool['name']}"
                
                # Create validated ToolDefinition
                tool_def = ToolDefinition(
                    name=tool_id,
                    server=server_name,
                    tool_name=tool['name'],
                    description=tool['description']
                )
                
                self.tools[tool_id] = tool_def
        
        # Update state
        self.state = AgentState(
            initialized=True,
            tools_count=len(self.tools),
            active_servers=active_servers
        )
        
        print(f"✅ Initialized with {self.state.tools_count} type-safe tools")
        print(f"   Active servers: {', '.join(self.state.active_servers)}")
        
        return True
    
    def get_tool_definition(self, tool_id: str) -> Optional[ToolDefinition]:
        """Get type-safe tool definition"""
        return self.tools.get(tool_id)
    
    def list_tools(self) -> List[ToolDefinition]:
        """Get all tool definitions"""
        return list(self.tools.values())
    
    async def execute_tool(
        self, 
        tool_id: str, 
        arguments: Dict[str, Any]
    ) -> ToolExecutionResult:
        """
        Execute tool with type-safe result.
        
        Returns ToolExecutionResult with validated structure.
        """
        print(f"🔧 Executing: {tool_id}")
        
        # Get tool definition
        tool_def = self.get_tool_definition(tool_id)
        if not tool_def:
            return ToolExecutionResult(
                success=False,
                output=f"Tool '{tool_id}' not found",
                tool_name=tool_id
            )
        
        try:
            # Execute via MCP
            result = await self.mcp.execute_tool(
                tool_def.server,
                tool_def.tool_name,
                arguments
            )
            
            # Format output
            text_results = []
            for item in result:
                if hasattr(item, 'text'):
                    text_results.append(item.text)
                else:
                    text_results.append(str(item))
            
            output = "\n".join(text_results) if text_results else "Success"
            
            return ToolExecutionResult(
                success=True,
                output=output,
                tool_name=tool_id
            )
            
        except Exception as e:
            return ToolExecutionResult(
                success=False,
                output=f"Error: {str(e)}",
                tool_name=tool_id
            )
    
    def get_state(self) -> AgentState:
        """Get current agent state"""
        return self.state
    
    def export_tools_schema(self) -> List[Dict[str, Any]]:
        """Export tools as JSON schema (for OpenAI function calling, etc.)"""
        return [tool.model_dump() for tool in self.tools.values()]
    
    async def cleanup(self):
        """Cleanup MCP connections"""
        await self.mcp.disconnect_all()
        print(f"✅ {self.name} shutdown complete")


async def test_pydantic_agent():
    """Test the Pydantic AI agent"""
    print("=" * 80)
    print("TEST: Pydantic AI Agent with Type-Safe MCP Integration")
    print("=" * 80)
    
    # Get config path
    config_path = Path(__file__).parent.parent / "tmcp.json"
    
    # Create and initialize agent
    agent = PydanticAIAgent(str(config_path))
    
    try:
        # Test 1: Initialization
        success = await agent.initialize()
        assert success, "Agent initialization failed"
        assert agent.state.initialized, "Agent state not initialized"
        assert agent.state.tools_count > 0, "No tools discovered"
        print(f"✅ Test 1: Agent initialized with {agent.state.tools_count} tools")
        
        # Test 2: State validation
        state = agent.get_state()
        assert isinstance(state, AgentState), "State is not AgentState instance"
        assert state.initialized == True, "State not properly set"
        assert len(state.active_servers) > 0, "No active servers in state"
        print(f"✅ Test 2: Agent state is type-safe ({len(state.active_servers)} servers)")
        
        # Test 3: Tool definitions are Pydantic models
        tools = agent.list_tools()
        assert len(tools) > 0, "No tools returned"
        assert isinstance(tools[0], ToolDefinition), "Tools are not ToolDefinition instances"
        assert tools[0].name is not None, "Tool name is None"
        assert tools[0].description is not None, "Tool description is None"
        print(f"✅ Test 3: Tool definitions are type-safe Pydantic models")
        
        # Test 4: Get specific tool definition
        tool_def = agent.get_tool_definition("towardsmcp-syntheticDB.test_syntheticDB")
        if tool_def:
            assert isinstance(tool_def, ToolDefinition), "Retrieved tool is not ToolDefinition"
            assert tool_def.server == "towardsmcp-syntheticDB", "Tool server mismatch"
            print(f"✅ Test 4: Can retrieve specific tool definitions")
        else:
            print(f"⚠️  Test 4: Skipped (test tool not available)")
        
        # Test 5: Tool execution with type-safe result
        result = await agent.execute_tool(
            "towardsmcp-syntheticDB.test_syntheticDB",
            {"include_version": True}
        )
        assert isinstance(result, ToolExecutionResult), "Result is not ToolExecutionResult"
        assert result.tool_name == "towardsmcp-syntheticDB.test_syntheticDB", "Tool name mismatch"
        assert hasattr(result, 'success'), "Result missing success field"
        assert hasattr(result, 'output'), "Result missing output field"
        print(f"✅ Test 5: Tool execution returns type-safe result")
        
        # Test 6: Schema export
        schema = agent.export_tools_schema()
        assert isinstance(schema, list), "Schema export not a list"
        assert len(schema) > 0, "Schema export empty"
        assert isinstance(schema[0], dict), "Schema items not dicts"
        assert 'name' in schema[0], "Schema missing 'name' field"
        print(f"✅ Test 6: Can export tool schema ({len(schema)} tools)")
        
        # Test 7: Pydantic validation
        try:
            # This should work
            valid_tool = ToolDefinition(
                name="test.tool",
                server="test",
                tool_name="tool",
                description="Test tool"
            )
            assert valid_tool.name == "test.tool", "Validation failed"
            print(f"✅ Test 7: Pydantic validation works")
        except Exception as e:
            print(f"❌ Test 7 Failed: {e}")
            raise
        
        print("\n" + "=" * 80)
        print("✅ ALL TESTS PASSED - Pydantic AI Integration Works!")
        print("=" * 80)
        print("\n💡 Type Safety Benefits:")
        print("   • ToolDefinition: Validated tool metadata")
        print("   • ToolExecutionResult: Type-safe results")
        print("   • AgentState: Validated agent state")
        print("   • Automatic JSON serialization")
        print("   • Runtime type checking")
        
        return True
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await agent.cleanup()


async def main():
    """Run the test"""
    success = await test_pydantic_agent()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())

