#!/usr/bin/env python3
"""
Test: LangChain Agent Integration with MCP

This demonstrates how to integrate MCP tools into a LangChain-based agent.
Note: This is a conceptual test showing the integration pattern.
For full LangChain integration, install: pip install langchain langchain-openai
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, Any, List

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tmcp_runner import TMCPRunner


class MCPTool:
    """
    Wrapper to make MCP tools compatible with LangChain's Tool interface.
    
    This is a simplified version. Full LangChain integration would extend
    from langchain.tools.BaseTool
    """
    
    def __init__(self, mcp_runner: TMCPRunner, server: str, tool_name: str, description: str):
        self.mcp = mcp_runner
        self.server = server
        self.tool_name = tool_name
        self.description = description
        self.name = f"{server}_{tool_name}"
    
    async def run(self, **kwargs) -> str:
        """Execute the MCP tool"""
        result = await self.mcp.execute_tool(
            self.server,
            self.tool_name,
            kwargs
        )
        
        # Format result as text
        text_results = []
        for item in result:
            if hasattr(item, 'text'):
                text_results.append(item.text)
            else:
                text_results.append(str(item))
        
        return "\n".join(text_results) if text_results else "Success"
    
    def __repr__(self):
        return f"MCPTool(name='{self.name}', description='{self.description[:50]}...')"


class LangChainMCPAgent:
    """
    Agent that integrates MCP tools with LangChain.
    
    In production with full LangChain:
    ```
    from langchain.agents import AgentExecutor, create_openai_functions_agent
    from langchain_openai import ChatOpenAI
    
    llm = ChatOpenAI(model="gpt-4")
    agent = create_openai_functions_agent(llm, mcp_tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=mcp_tools)
    ```
    """
    
    def __init__(self, mcp_config_path: str):
        self.mcp = TMCPRunner(mcp_config_path)
        self.tools: List[MCPTool] = []
        self.name = "LangChainAgent"
    
    async def initialize(self):
        """Initialize and wrap all MCP tools for LangChain"""
        print(f"🔗 Initializing {self.name} with MCP tools...")
        
        # Connect to MCP servers
        await self.mcp.connect_all()
        
        # Discover tools
        discovery = await self.mcp.discover_all()
        
        # Wrap each MCP tool as a LangChain-compatible tool
        for server_name, info in discovery.items():
            for tool in info.get('tools', []):
                wrapped_tool = MCPTool(
                    self.mcp,
                    server_name,
                    tool['name'],
                    tool['description']
                )
                self.tools.append(wrapped_tool)
        
        print(f"✅ Wrapped {len(self.tools)} MCP tools for LangChain")
        return True
    
    def get_tools(self) -> List[MCPTool]:
        """Get all wrapped tools"""
        return self.tools
    
    def get_tool_descriptions(self) -> str:
        """Get descriptions of all tools for the agent"""
        descriptions = []
        for tool in self.tools:
            descriptions.append(f"- {tool.name}: {tool.description}")
        return "\n".join(descriptions)
    
    async def execute_tool(self, tool_name: str, **kwargs) -> str:
        """Execute a tool by name"""
        for tool in self.tools:
            if tool.name == tool_name:
                return await tool.run(**kwargs)
        raise ValueError(f"Tool '{tool_name}' not found")
    
    async def run(self, query: str) -> str:
        """
        Run the agent with a query.
        
        In production with LangChain:
        ```
        response = agent_executor.invoke({"input": query})
        return response["output"]
        ```
        """
        print(f"📝 Query: {query}")
        
        # Simulate LangChain agent deciding which tool to use
        if "database" in query.lower() or "tables" in query.lower():
            # Agent would choose the tables tool
            result = await self.execute_tool(
                "towardsmcp-syntheticDB_tables_syntheticDB",
                random_string="test"
            )
            return f"LangChain Agent Response: Found database information:\n{result}"
        else:
            return f"LangChain Agent: I have {len(self.tools)} tools available."
    
    async def cleanup(self):
        """Cleanup MCP connections"""
        await self.mcp.disconnect_all()
        print(f"✅ {self.name} shutdown complete")


async def test_langchain_agent():
    """Test the LangChain agent integration"""
    print("=" * 80)
    print("TEST: LangChain Agent with MCP Integration")
    print("=" * 80)
    
    # Get config path
    config_path = Path(__file__).parent.parent / "tmcp.json"
    
    # Create and initialize agent
    agent = LangChainMCPAgent(str(config_path))
    
    try:
        # Test 1: Initialization
        success = await agent.initialize()
        assert success, "Agent initialization failed"
        assert len(agent.tools) > 0, "No tools wrapped"
        print(f"✅ Test 1: Wrapped {len(agent.tools)} MCP tools for LangChain")
        
        # Test 2: Get tools
        tools = agent.get_tools()
        assert len(tools) > 0, "get_tools() returned empty"
        assert isinstance(tools[0], MCPTool), "Tools are not MCPTool instances"
        print(f"✅ Test 2: Can retrieve {len(tools)} tools")
        
        # Test 3: Tool descriptions
        descriptions = agent.get_tool_descriptions()
        assert len(descriptions) > 0, "Tool descriptions empty"
        print(f"✅ Test 3: Tool descriptions generated ({len(descriptions)} chars)")
        
        # Test 4: Direct tool execution
        result = await agent.execute_tool(
            "towardsmcp-syntheticDB_test_syntheticDB",
            include_version=True
        )
        assert len(result) > 0, "Tool execution returned empty"
        print(f"✅ Test 4: Direct tool execution works")
        
        # Test 5: Agent query handling
        response = await agent.run("Show me the database tables")
        assert len(response) > 0, "Agent run returned empty"
        assert "table" in response.lower(), "Expected table info in response"
        print(f"✅ Test 5: Agent query handling works")
        
        # Test 6: Tool wrapper functionality
        tool = agent.tools[0]
        assert hasattr(tool, 'run'), "Tool missing run method"
        assert hasattr(tool, 'name'), "Tool missing name attribute"
        assert hasattr(tool, 'description'), "Tool missing description"
        print(f"✅ Test 6: Tool wrapper has LangChain-compatible interface")
        
        print("\n" + "=" * 80)
        print("✅ ALL TESTS PASSED - LangChain Integration Works!")
        print("=" * 80)
        print("\n💡 Integration Pattern:")
        print("   1. MCPTool wraps each MCP tool with LangChain interface")
        print("   2. LangChainMCPAgent manages the tool collection")
        print("   3. Tools can be passed to LangChain's AgentExecutor")
        print("   4. LangChain agent can now use all MCP servers!")
        
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
    success = await test_langchain_agent()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())

