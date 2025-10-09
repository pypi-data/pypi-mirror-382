#!/usr/bin/env python3
"""
JWT integration example demonstrating context extraction from JWT tokens.

This example demonstrates:
- Creating JWT tokens with focus context
- Extracting context using ExtractMCPContextJWT
- Extracting composite context using ExtractMCPCompositeContextJWT
- Using extracted context to create focused clients
"""

import asyncio
import sys
import jwt
import json
from datetime import datetime, timedelta
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mimory_mcp_focus import (
    FocusedClientSession, 
    focus_client_simple, 
    focus_client_composite, 
    extract_mcp_context_jwt, 
    extract_mcp_composite_context_jwt
)


def sample_jwt_token(jwt_key: str, algorithm: str = "HS256") -> str:
    """Create a sample JWT token with focus context."""
    # Create payload with focus context
    payload = {
        "sub": "user123",
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=1),
        "context": {
            "user_id": ["123", "456"],
            "environment": ["dev", "staging"],
            "session_id": ["range:1000-9999"]
        },
        "tools": ["echo", "add"],
        "mcp_focus": {
            "echo": {
                "message": ["hello", "world", "jwt"],
                "priority": ["low", "medium"],
                "user_id": ["123", "456"],
                "environment": ["dev", "staging"]
            },
            "add": {
                "a": ["range:1-10"],
                "b": ["range:1-10"],
                "user_id": ["123", "456"],
                "environment": ["dev", "staging"]
            }
        }
    }
    
    # Create JWT token
    token = jwt.encode(payload, jwt_key, algorithm=algorithm)
    return token


async def main():
    """Main example function."""
    print("🚀 Starting JWT Integration Example")
    print("=" * 50)
    
    # JWT configuration
    jwt_key = "your-secret-key-for-demo"
    jwt_algorithm = "HS256"
    
    try:
        # Create sample JWT token
        print("🔐 Creating sample JWT token with focus context...")
        jwt_token = sample_jwt_token(jwt_key, jwt_algorithm)
        print(f"✅ JWT token created: {jwt_token[:50]}...")
        
        # Extract simple context from JWT
        print("\n📤 Extracting simple context from JWT...")
        try:
            simple_context_params, simple_context_tools = extract_mcp_context_jwt(
                jwt_token=jwt_token,
                jwt_key=jwt_key,
                jwt_signing_algorithm=jwt_algorithm,
                parameter_field="context",
                tool_field="tools",
                strict=True
            )
            print("✅ Simple context extracted successfully:")
            print(f"   Context params: {simple_context_params}")
            print(f"   Tools allowed: {simple_context_tools}")
        except Exception as e:
            print(f"❌ Failed to extract simple context: {e}")
            return
        
        # Extract composite context from JWT
        print("\n📤 Extracting composite context from JWT...")
        try:
            composite_context = extract_mcp_composite_context_jwt(
                jwt_token=jwt_token,
                jwt_key=jwt_key,
                jwt_signing_algorithm=jwt_algorithm,
                composite_context_field="mcp_focus"
            )
            print("✅ Composite context extracted successfully:")
            print(f"   Composite context: {json.dumps(composite_context, indent=2)}")
        except Exception as e:
            print(f"❌ Failed to extract composite context: {e}")
            return
        
        # Create MCP server parameters
        server_params = StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-everything"]
        )
        
        # Connect to MCP server and test with extracted context
        print("\n📡 Connecting to Everything MCP Server...")
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                print("✅ Connected successfully!")
                
                # Create FocusClient using extracted simple context
                print("\n🔒 Creating FocusClient with extracted simple context...")
                focus_client = focus_client_simple(
                    session=session,
                    focus_tools=simple_context_tools,
                    focus_params=simple_context_params,
                    strict=False
                )
                print("✅ FocusClient created with JWT-extracted context")
                
                # Test the focused client
                print("\n🧪 Testing FocusClient with JWT context...")
                test_cases = [
                    {"message": "hello", "user_id": "123", "environment": "dev"},
                    {"message": "world", "user_id": "456", "environment": "staging"},
                    {"a": 5, "b": 3, "user_id": "123", "environment": "dev"}
                ]
                
                for args in test_cases:
                    tool_name = "echo" if "message" in args else "add"
                    result = await focus_client.call_tool(tool_name, args)
                    if result.isError:
                        print(f"   ❌ {tool_name} with {args} failed: {result.content[0].text}")
                    else:
                        print(f"   ✅ {tool_name} with {args}: {result.content[0].text}")
                
                # Create FocusClientComposite using extracted composite context
                print("\n🔒 Creating FocusClientComposite with extracted composite context...")
                composite_focus_client = focus_client_composite(
                    session=session,
                    focus=composite_context,
                    strict=False
                )
                print("✅ FocusClientComposite created with JWT-extracted composite context")
                
                # Test the composite focused client
                print("\n🧪 Testing FocusClientComposite with JWT context...")
                composite_test_cases = [
                    {"message": "hello", "user_id": "123", "environment": "dev", "priority": "low"},
                    {"message": "world", "user_id": "456", "environment": "staging", "priority": "medium"},
                    {"a": 7, "b": 2, "user_id": "123", "environment": "dev"}
                ]
                
                for args in composite_test_cases:
                    tool_name = "echo" if "message" in args else "add"
                    result = await composite_focus_client.call_tool(tool_name, args)
                    if result.isError:
                        print(f"   ❌ {tool_name} with {args} failed: {result.content[0].text}")
                    else:
                        print(f"   ✅ {tool_name} with {args}: {result.content[0].text}")
                
                # Test with invalid JWT token
                print("\n🚫 Testing with invalid JWT token...")
                invalid_token = "invalid.jwt.token"
                try:
                    invalid_context = extract_mcp_context_jwt(
                        jwt_token=invalid_token,
                        jwt_key=jwt_key,
                        jwt_signing_algorithm=jwt_algorithm
                    )
                    print(f"   ❌ Invalid JWT unexpectedly succeeded: {invalid_context}")
                except Exception as e:
                    print(f"   ✅ Invalid JWT correctly rejected: {e}")
                
                # Test with wrong JWT key
                print("\n🚫 Testing with wrong JWT key...")
                wrong_key = "wrong-secret-key"
                try:
                    wrong_context = extract_mcp_context_jwt(
                        jwt_token=jwt_token,
                        jwt_key=wrong_key,
                        jwt_signing_algorithm=jwt_algorithm
                    )
                    print(f"   ❌ Wrong JWT key unexpectedly succeeded: {wrong_context}")
                except Exception as e:
                    print(f"   ✅ Wrong JWT key correctly rejected: {e}")
                
                print("\n🎉 JWT integration example completed successfully!")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
