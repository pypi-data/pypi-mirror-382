# mimory-mcp-focus

A focus-enforcing wrapper for MCP (Model Context Protocol) Python clients that provides fine-grained control over tool access and parameter validation through allowlists and JWT-based context extraction.

## Features

- **Tool Filtering**: Restrict access to specific MCP tools
- **Parameter Focusing**: Enforce allowed values for tool parameters, only handles exact matches, ranges, and * wildcards
- **JWT Integration**: Extract focus context from JWT tokens
- **Flexible Configuration**: Support for both simple and composite focus configurations
- **Range Focusing**: Support for numeric range constraints
- **Strict Mode**: Optional strict parameter validation that requires all passed parameters be included in the focus_params

## Future Work

- **Full MCP Coverage**: Focus all MCP features including resources, prompts, and more
- **Improved Focusing**: Better pattern matching for focus enforcement
- **Easier JWT Integration**: Signed JWTs, even when not used as access tokens, should automatically update the context

## Installation

```bash
pip install mimory-mcp-focus
```

## Quick Start

### Basic Usage with Simple Focus

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mimory_mcp_focus import focus_client_simple

async def main():
    # Create MCP server parameters
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-everything"]
    )
    
    # Connect to MCP server
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Create focused client with restrictions
            focus_client = focus_client_simple(
                session=session,
                focus_tools=["echo", "add"],  # Only allow these tools
                focus_params={
                    "message": ["hello", "world"],  # Only allow these messages
                    "a": ["1", "2", "3"],          # Only allow these values for 'a'
                    "b": ["range:1-10"]            # Allow any number between 1-10
                },
                strict=True  # Require all parameters to be in focus_params
            )
            
            # List available tools (filtered)
            tools = await focus_client.list_tools()
            print(f"Available tools: {[tool.name for tool in tools.tools]}")
            
            # Call allowed tool with valid parameters
            result = await focus_client.call_tool("echo", {"message": "hello"})
            print(f"Echo result: {result.content}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Using Composite Focus

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mimory_mcp_focus import focus_client_composite

async def main():
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-everything"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Create composite focus client
            focus_client = focus_client_composite(
                session=session,
                focus={
                    "echo": {  # Specific rules for echo tool
                        "message": ["hello", "world", "test"]
                    },
                    "add": {  # Specific rules for add tool
                        "a": ["range:1-100"],
                        "b": ["range:1-100"]
                    }
                },
                strict=False
            )
            
            # Use the focused client
            result = await focus_client.call_tool("echo", {"message": "hello"})
            print(f"Result: {result.content}")

if __name__ == "__main__":
    asyncio.run(main())
```

### JWT Context Extraction

```python
from mimory_mcp_focus import extract_mcp_context_jwt, extract_mcp_composite_context_jwt

# Extract simple context from JWT
jwt_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
jwt_key = "your-secret-key"
jwt_algorithm = "HS256"

context_params, tools_allowed = extract_mcp_context_jwt(
    jwt_token=jwt_token,
    jwt_key=jwt_key,
    jwt_signing_algorithm=jwt_algorithm,
    parameter_field="context",
    tool_field="tools",
    strict=True
)

print(f"Context params: {context_params}")
print(f"Tools allowed: {tools_allowed}")

# Extract composite context from JWT
composite_context = extract_mcp_composite_context_jwt(
    jwt_token=jwt_token,
    jwt_key=jwt_key,
    jwt_signing_algorithm=jwt_algorithm,
    composite_context_field="mcp_focus"
)

print(f"Composite context: {composite_context}")
```

### Refocusing a Client

You can change the focus of an existing client without creating a new one:

```python
from mimory_mcp_focus import refocus_client_simple, refocus_client_composite

# Refocus with simple configuration
refocus_client_simple(
    session=focus_client,
    focus_tools=["echo"],  # Now only allow echo
    focus_params={"message": ["hello"]},  # Only allow "hello" messages
    strict=True
)

# Refocus with composite configuration
refocus_client_composite(
    session=focus_client,
    focus={
        "echo": {"message": ["world", "test"]}
    },
    strict=False
)
```

## API Reference

### FocusedClientSession

A focus client that wraps a ClientSession and applies focus restrictions. This is the main class returned by the factory functions.

#### Methods

- `list_tools(cursor: str | None = None)`: List available tools (filtered by focus rules)
- `call_tool(tool_name: str, arguments: Dict[str, Any], **kwargs)`: Call a tool with parameter validation
- `refocus(focus: Dict[str, Any], focus_type: str)`: Update focus configuration
- All other ClientSession methods are proxied through

### focus_client_simple

Factory function that focuses a ClientSession and returns a FocusedClientSession with simple focus configuration.

```python
focus_client_simple(
    session: ClientSession,
    focus_tools: Optional[List[str]] = None,
    focus_params: Optional[Dict[str, Union[str, List[str]]]] = None,
    strict: bool = False
) -> FocusedClientSession
```

**Parameters:**
- `session`: The underlying MCP ClientSession
- `focus_tools`: List of allowed tool names. Use `["*"]` to allow all tools
- `focus_params`: Dictionary mapping parameter names to allowed values
- `strict`: If True, all parameters must be defined in focus_params

### focus_client_composite

Factory function that focuses a ClientSession and returns a FocusedClientSession with composite focus configuration.

```python
focus_client_composite(
    session: ClientSession,
    focus: Optional[Dict[str, Dict[str, List[str]]]] = None,
    strict: bool = False
) -> FocusedClientSession
```

**Parameters:**
- `session`: The underlying MCP ClientSession
- `focus`: Dictionary with tool-specific and global focus rules
- `strict`: If True, all parameters must be defined in focus rules

#### Focus Dictionary Structure

```python
{
    "tool_name": {  # Tool-specific rules
        "param_name": ["allowed_value"]
    }
}
```

### refocus_client_simple

Refocus an existing FocusedClientSession with new simple focus configuration.

```python
refocus_client_simple(
    session: FocusedClientSession,
    focus_tools: List[str],
    focus_params: Dict[str, Union[str, List[str]]],
    strict: bool
) -> None
```

### refocus_client_composite

Refocus an existing FocusedClientSession with new composite focus configuration.

```python
refocus_client_composite(
    session: FocusedClientSession,
    focus: Dict[str, Dict[str, List[str]]],
    strict: bool
) -> None
```

### JWT Extraction Functions

#### extract_mcp_context_jwt

Extract simple context parameters and tools from a JWT token.

```python
extract_mcp_context_jwt(
    jwt_token: str,
    jwt_key: str,
    jwt_signing_algorithm: str,
    parameter_field: str = 'context',
    tool_field: str = 'tools',
    strict: bool = False
) -> Tuple[Dict[str, Union[str, List[str]]], List[str]]
```

**Returns:**
- `focus_params`: Dictionary of context parameters
- `focus_tools`: List of allowed tools

#### extract_mcp_composite_context_jwt

Extract composite context dictionary from a JWT token.

```python
extract_mcp_composite_context_jwt(
    jwt_token: str,
    jwt_key: str,
    jwt_signing_algorithm: str,
    composite_context_field: str
) -> Dict[str, Dict[str, List[str]]]
```

**Returns:**
- `focus_composite`: The composite context dictionary from the JWT

## Parameter Value Types

### String Values
```python
"message": ["hello", "world", "test"]
```

### Numeric Ranges
```python
"number": ["range:1-100"]  # Any number between 1 and 100 (inclusive)
"price": ["range:0.01-999.99"]  # Decimal ranges supported
```

### Wildcard
```python
"any_value": ["*"]  # Allow any value
```

### Comma-separated Strings
```python
"tags": "tag1,tag2,tag3"  # Automatically split into ["tag1", "tag2", "tag3"]
```

## Error Handling

The library returns focus-related errors as `CallToolResult` with `isError=True`.
It raises ValueExceptions and ValidationExceptions depending on internal errors.

```python
result = await focus_client.call_tool("echo", {"message": "forbidden"})
if result.isError:
    print(f"Focus error: {result.content[0].text}")
```

For JWT extraction functions, the library raises `ValueError` for validation failures:

```python
from mimory_mcp_focus import extract_mcp_context_jwt

try:
    context_params, tools_allowed = extract_mcp_context_jwt(
        jwt_token="invalid_token",
        jwt_key="secret",
        jwt_signing_algorithm="HS256"
    )
except ValueError as e:
    print(f"JWT validation error: {e}")
```

Common focus-related error scenarios:
- Tool not in allowed list
- Parameter value not allowed
- Missing required parameter in strict mode

Common exception scenarios:
- Malformed focus_params, focus_tools, or focus fields
- JWT validation failures (expired tokens, invalid signatures, etc.)

## Examples

See the `examples/` directory for complete working examples:

- `basic_usage.py` - Basic FocusClient usage
- `composite_focus.py` - FocusClientComposite usage
- `jwt_integration.py` - JWT context extraction

## Requirements

- Python >= 3.10
- mcp >= 1.14.0
- pyjwt >= 2.10.1

## License

MIT License

## Author

Travis McQueen - oss@mimory.io

## Repository

https://github.com/mimoryinc/mimory-mcp-focus
