#!/usr/bin/env python3
"""
Basic usage example of FocusClientSession with the Everything MCP Server.

This example demonstrates:
- Setting up a connection to the Everything MCP Server
- Creating a FocusClientSession with tool and parameter restrictions
- Listing available tools (filtered)
- Calling tools with parameter validation
- Error handling for invalid parameters
"""

import asyncio
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mimory_mcp_focus import focus_client_simple, refocus_client_simple

async def main():
    """Main example function."""
    print("🚀 Starting Basic FocusClientSession Example")
    print("=" * 50)
    
    # Create MCP server parameters for Everything MCP Server
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-everything"]
    )
    
    try:
        # Connect to MCP server
        print("📡 Connecting to Everything MCP Server...")
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                print("✅ Connected successfully!")
                
                # Create focused client with restrictions
                print("\n🔒 Creating FocusClientSession with restrictions...")
                try:
                    focus_client = focus_client_simple(
                        session=session,
                        focus_tools=["echo", "add"],  # Only allow these tools
                        focus_params={
                            "message": ["hello", "world", "test"],  # Only allow these messages
                            "a": ["1", "2", "3", "5", "10"],       # Only allow these values for 'a'
                            "b": ["range:1-20"]                    # Allow any number between 1-20
                        },
                        strict=False  # Don't require all parameters to be in focus_params
                    )
                except Exception as e:
                    print(f"❌ Failed to create FocusClientSession: {e}")
                    sys.exit(1)
                print("✅ FocusClientSession created with restrictions:")
                print("   - Allowed tools: echo, add")
                print("   - Allowed messages: hello, world, test")
                print("   - Allowed 'a' values: 1, 2, 3, 5, 10")
                print("   - Allowed 'b' values: range 1-20")
                
                # List available tools (filtered)
                print("\n📋 Listing available tools (filtered)...")
                try:
                    tools_result = await focus_client.list_tools()
                    print(f"✅ Available tools: {[tool.name for tool in tools_result.tools]}")
                except Exception as e:
                    print(f"❌ Failed to list tools: {e}")
                
                # Test echo tool with valid parameters
                print("\n🔊 Testing echo tool with valid parameters...")
                test_messages = ["hello", "world", "test"]
                for message in test_messages:
                    result = await focus_client.call_tool("echo", {"message": message})
                    if result.isError:
                        print(f"   ❌ Echo '{message}' failed: {result.content[0].text}")
                    else:
                        print(f"   ✅ Echo '{message}': {result.content[0].text}")
                
                # Test echo tool with invalid parameters
                print("\n🚫 Testing echo tool with invalid parameters...")
                invalid_messages = ["forbidden", "blocked", "unauthorized"]
                for message in invalid_messages:
                    result = await focus_client.call_tool("echo", {"message": message})
                    if result.isError:
                        print(f"   ✅ Echo '{message}' correctly blocked: {result.content[0].text}")
                    else:
                        print(f"   ❌ Echo '{message}' unexpectedly succeeded: {result.content[0].text}")
                
                # Test add tool with valid parameters
                print("\n➕ Testing add tool with valid parameters...")
                test_cases = [
                    {"a": 1, "b": 5},
                    {"a": 2, "b": 10},
                    {"a": 3, "b": 15},
                    {"a": 5, "b": 20}
                ]
                for args in test_cases:
                    result = await focus_client.call_tool("add", args)
                    if result.isError:
                        print(f"   ❌ Add {args} failed: {result.content[0].text}")
                    else:
                        print(f"   ✅ Add {args['a']} + {args['b']}: {result.content[0].text}")
                
                # Test add tool with invalid parameters
                print("\n🚫 Testing add tool with invalid parameters...")
                invalid_cases = [
                    {"a": 4, "b": 5},    # a=4 not in allowed list
                    {"a": 1, "b": 25},   # b=25 outside range
                    {"a": 6, "b": 30}    # both invalid
                ]
                for args in invalid_cases:
                    result = await focus_client.call_tool("add", args)
                    if result.isError:
                        print(f"   ✅ Add {args} correctly blocked: {result.content[0].text}")
                    else:
                        print(f"   ❌ Add {args} unexpectedly succeeded: {result.content[0].text}")
                
                # Test calling a blocked tool
                print("\n🚫 Testing blocked tool access...")
                result = await focus_client.call_tool("blocked_tool", {})
                if result.isError:
                    print(f"   ✅ Blocked tool correctly blocked: {result.content[0].text}")
                else:
                    print(f"   ❌ Blocked tool unexpectedly succeeded: {result}")
                
                print("\n🎉 Basic usage example completed successfully!")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
