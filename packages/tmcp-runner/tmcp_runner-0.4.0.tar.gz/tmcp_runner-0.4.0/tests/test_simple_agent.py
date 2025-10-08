#!/usr/bin/env python3
"""
Test: Simple AI Agent Integration with MCP

This demonstrates the most basic pattern for integrating MCP tools into an AI agent.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tmcp_runner import TMCPRunner


class SimpleAIAgent:
    """
    A minimal AI agent that can discover and use MCP tools.
    
    In production, you'd integrate with your LLM (GPT-4, Claude, etc.)
    """
    
    def __init__(self, mcp_config_path: str):
        self.mcp = TMCPRunner(mcp_config_path)
        self.tools = {}
        self.name = "SimpleAgent"
    
    async def initialize(self):
        """Initialize agent with MCP tools"""
        print(f"🤖 Initializing {self.name}...")
        
        # Connect to all MCP servers
        await self.mcp.connect_all()
        
        # Discover available tools
        discovery = await self.mcp.discover_all()
        
        # Build tool catalog
        for server_name, info in discovery.items():
            for tool in info.get('tools', []):
                tool_id = f"{server_name}.{tool['name']}"
                self.tools[tool_id] = {
                    'server': server_name,
                    'name': tool['name'],
                    'description': tool['description']
                }
        
        print(f"✅ Agent initialized with {len(self.tools)} tools from {len(discovery)} servers")
        return True
    
    def get_tools_for_llm(self) -> str:
        """
        Format tools for LLM system prompt.
        
        In production, send this to your LLM so it knows what tools are available.
        """
        tools_text = "You have access to these tools:\n\n"
        for tool_id, info in self.tools.items():
            tools_text += f"- {tool_id}\n"
            tools_text += f"  Description: {info['description']}\n\n"
        return tools_text
    
    async def execute_tool(self, tool_id: str, arguments: dict) -> str:
        """
        Execute a specific MCP tool.
        
        Call this when your LLM decides to use a tool.
        """
        if tool_id not in self.tools:
            return f"Error: Unknown tool '{tool_id}'"
        
        tool = self.tools[tool_id]
        print(f"🔧 Executing: {tool_id}")
        
        try:
            result = await self.mcp.execute_tool(
                tool['server'],
                tool['name'],
                arguments
            )
            
            # Format result for LLM
            text_results = []
            for item in result:
                if hasattr(item, 'text'):
                    text_results.append(item.text)
                else:
                    text_results.append(str(item))
            
            return "\n".join(text_results) if text_results else "Success"
            
        except Exception as e:
            return f"Error executing tool: {str(e)}"
    
    async def handle_query(self, user_query: str) -> str:
        """
        Handle a user query.
        
        In production:
        1. Send query + available tools to your LLM
        2. LLM decides which tool to use
        3. Execute the tool
        4. Send result back to LLM
        5. LLM generates final response
        """
        print(f"\n📝 User Query: {user_query}")
        
        # Simulate LLM decision (in production, your LLM does this)
        if "database" in user_query.lower() or "tables" in user_query.lower():
            # LLM decided to check database tables
            result = await self.execute_tool(
                "towardsmcp-syntheticDB.tables_syntheticDB",
                {"random_string": "test"}
            )
            return f"I found information about the database:\n{result}"
        else:
            return f"I have {len(self.tools)} tools available. Ask me about the database!"
    
    async def cleanup(self):
        """Cleanup MCP connections"""
        await self.mcp.disconnect_all()
        print(f"✅ {self.name} shutdown complete")


async def test_simple_agent():
    """Test the simple agent"""
    print("=" * 80)
    print("TEST: Simple AI Agent with MCP")
    print("=" * 80)
    
    # Get config path
    config_path = Path(__file__).parent.parent / "tmcp.json"
    
    # Create and initialize agent
    agent = SimpleAIAgent(str(config_path))
    
    try:
        # Initialize
        success = await agent.initialize()
        assert success, "Agent initialization failed"
        assert len(agent.tools) > 0, "No tools discovered"
        print(f"✅ Test 1: Agent discovered {len(agent.tools)} tools")
        
        # Test tool listing
        tools_text = agent.get_tools_for_llm()
        assert len(tools_text) > 0, "Tool listing failed"
        print(f"✅ Test 2: Tool listing works ({len(tools_text)} chars)")
        
        # Test query handling
        response = await agent.handle_query("Show me database tables")
        assert len(response) > 0, "Query handling failed"
        assert "table" in response.lower(), "Expected table information in response"
        print(f"✅ Test 3: Query handling works")
        
        # Test direct tool execution
        result = await agent.execute_tool(
            "towardsmcp-syntheticDB.test_syntheticDB",
            {"include_version": True}
        )
        assert "error" not in result.lower() or "success" in result.lower(), "Tool execution failed"
        print(f"✅ Test 4: Direct tool execution works")
        
        print("\n" + "=" * 80)
        print("✅ ALL TESTS PASSED - Simple Agent Integration Works!")
        print("=" * 80)
        
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
    success = await test_simple_agent()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())

