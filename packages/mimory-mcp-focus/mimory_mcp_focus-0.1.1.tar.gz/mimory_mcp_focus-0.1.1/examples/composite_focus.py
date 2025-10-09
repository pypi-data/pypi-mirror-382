#!/usr/bin/env python3
"""
Composite focus example using FocusClientComposite with the Everything MCP Server.

This example demonstrates:
- Using FocusClientComposite with a composite focus dictionary
- Global rules that apply to all tools
- Tool-specific rules that override global rules
- Complex parameter validation scenarios
"""

import asyncio
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mimory_mcp_focus import FocusedClientSession, focus_client_composite, refocus_client_composite


async def main():
    """Main example function."""
    print("🚀 Starting Composite Focus Example")
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
                
                # Create composite focus client with complex rules
                print("\n🔒 Creating FocusClientComposite with composite rules...")
                focus_client = focus_client_composite(
                    session=session,
                    focus={
                        # Tool-specific rules for echo
                        "echo": {
                            "message": ["hello", "world", "composite", "test"],
                            "priority": ["low", "medium", "high"],
                            "user_id": ["123", "456", "789"],
                            "session_id": ["range:1000-9999"],
                            "environment": ["dev", "staging", "prod"]
                        },
                        # Tool-specific rules for add
                        "add": {
                            "a": ["range:1-50"],
                            "b": ["range:1-50"],
                            "precision": ["1", "2", "3"],
                            "user_id": ["123", "456", "789"],
                            "session_id": ["range:1000-9999"],
                            "environment": ["dev", "staging", "prod"]
                        }
                    },
                    strict=False
                )
                print("✅ FocusClientComposite created with composite rules:")
                print("   - Global rules: user_id, session_id, environment")
                print("   - Echo-specific: message, priority")
                print("   - Add-specific: a, b, precision")
                
                # List available tools
                print("\n📋 Listing available tools...")
                tools_result = await focus_client.list_tools()
                print(f"✅ Available tools: {[tool.name for tool in tools_result.tools]}")
                
                # Test echo tool with valid parameters
                print("\n🔊 Testing echo tool with valid parameters...")
                echo_test_cases = [
                    {"message": "hello", "user_id": "123", "session_id": "1001"},
                    {"message": "world", "user_id": "456", "session_id": "2000", "priority": "high"},
                    {"message": "composite", "user_id": "789", "session_id": "5000", "environment": "prod"}
                ]
                for args in echo_test_cases:
                    result = await focus_client.call_tool("echo", args)
                    if result.isError:
                        print(f"   ❌ Echo with {args} failed: {result.content[0].text}")
                    else:
                        print(f"   ✅ Echo with {args}: {result.content[0].text}")
                
                # Test echo tool with invalid parameters
                print("\n🚫 Testing echo tool with invalid parameters...")
                invalid_echo_cases = [
                    {"message": "forbidden", "user_id": "123"},  # Invalid message
                    {"message": "hello", "user_id": "999"},      # Invalid user_id
                    {"message": "hello", "session_id": "500"}    # Invalid session_id (too low)
                ]
                for args in invalid_echo_cases:
                    result = await focus_client.call_tool("echo", args)
                    if result.isError:
                        print(f"   ✅ Echo with {args} correctly blocked: {result.content[0].text}")
                    else:
                        print(f"   ❌ Echo with {args} unexpectedly succeeded: {result.content[0].text}")
                
                # Test add tool with valid parameters
                print("\n➕ Testing add tool with valid parameters...")
                add_test_cases = [
                    {"a": 10, "b": 20, "user_id": "123", "session_id": "1001"},
                    {"a": 25, "b": 35, "user_id": "456", "session_id": "2000", "precision": "2"},
                    {"a": 1, "b": 50, "user_id": "789", "session_id": "5000", "environment": "prod"}
                ]
                for args in add_test_cases:
                    result = await focus_client.call_tool("add", args)
                    if result.isError:
                        print(f"   ❌ Add with {args} failed: {result.content[0].text}")
                    else:
                        print(f"   ✅ Add with {args}: {result.content[0].text}")
                
                # Test add tool with invalid parameters
                print("\n🚫 Testing add tool with invalid parameters...")
                invalid_add_cases = [
                    {"a": 60, "b": 20, "user_id": "123"},  # a too high
                    {"a": 10, "b": 60, "user_id": "123"},  # b too high
                    {"a": 10, "b": 20, "user_id": "999"}   # Invalid user_id
                ]
                for args in invalid_add_cases:
                    result = await focus_client.call_tool("add", args)
                    if result.isError:
                        print(f"   ✅ Add with {args} correctly blocked: {result.content[0].text}")
                    else:
                        print(f"   ❌ Add with {args} unexpectedly succeeded: {result.content[0].text}")
                
                # Demonstrate refocusing
                print("\n🔄 Demonstrating refocusing...")
                print("   Updating focus rules to be more restrictive...")
                refocus_client_composite(
                    session=focus_client,
                    focus={
                        "echo": {
                            "message": ["hello"],
                            "user_id": ["123"]  # Only allow "hello" message
                        }
                    },
                    strict=True  # Enable strict mode
                )
                print("   ✅ Refocused with stricter rules")
                
                # Test with new restrictions
                print("\n🧪 Testing with new restrictions...")
                strict_test_cases = [
                    {"message": "hello", "user_id": "123"}  # Should work
                ]
                for args in strict_test_cases:
                    result = await focus_client.call_tool("echo", args)
                    if result.isError:
                        print(f"   ❌ Echo with {args} blocked: {result.content[0].text}")
                    else:
                        print(f"   ✅ Echo with {args}: {result.content[0].text}")
                
                strict_test_cases = [
                    {"message": "world", "user_id": "123"},  # Should fail (invalid message)
                    {"message": "hello", "user_id": "456"}  # Should fail (invalid user)
                ]
                for args in strict_test_cases:
                    result = await focus_client.call_tool("echo", args)
                    if result.isError:
                        print(f"   ✅ Echo with {args} correctly blocked: {result.content[0].text}")
                    else:
                        print(f"   ❌ Echo with {args} unexpectedly succeeded: {result.content[0].text}")
                
                print("\n🎉 Composite focus example completed successfully!")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
