# Examples

This directory contains comprehensive examples demonstrating the usage of `mimory-mcp-focus` with the Everything MCP Server.

## Prerequisites

Before running the examples, ensure you have:

1. **Node.js and npm** installed
2. **Python 3.10+** installed
3. **Everything MCP Server** installed globally:
   ```bash
   npm install -g @modelcontextprotocol/server-everything@latest
   ```

## Installation

Install the required dependencies:

```bash
# Install the mimory-mcp-focus package
pip install mimory-mcp-focus

# Or install from source
pip install -e .
```

## Examples Overview

### 1. Basic Usage (`basic_usage.py`)

Demonstrates the fundamental features of `FocusClient`:

- Setting up a connection to the Everything MCP Server
- Creating a focused client with tool and parameter restrictions
- Listing available tools (filtered)
- Calling tools with parameter validation
- Error handling for invalid parameters

**Run:**
```bash
python examples/basic_usage.py
```

**Key Features Demonstrated:**
- Tool filtering (`focus_tools`)
- Parameter validation (`focus_params`)
- Range validation (`range:1-20`)
- Error handling with `FocusError`

### 2. Composite Focus (`composite_focus.py`)

Shows advanced usage of `FocusClientComposite`:

- Using composite focus dictionaries
- Global rules that apply to all tools
- Tool-specific rules that override global rules
- Dynamic refocusing
- Complex parameter validation scenarios

**Run:**
```bash
python examples/composite_focus.py
```

**Key Features Demonstrated:**
- Composite focus configuration
- Global vs tool-specific rules
- Dynamic refocusing with `refocus()`
- Strict mode validation

### 3. JWT Integration (`jwt_integration.py`)

Demonstrates JWT-based context extraction:

- Creating JWT tokens with focus context
- Extracting context using `ExtractMCPContextJWT`
- Extracting composite context using `ExtractMCPCompositeContextJWT`
- Using extracted context to create focused clients
- JWT validation and error handling

**Run:**
```bash
python examples/jwt_integration.py
```

**Key Features Demonstrated:**
- JWT token creation and validation
- Context extraction from JWT payloads
- Integration with focused clients
- Security considerations

## Everything MCP Server

The examples use the **Everything MCP Server** which provides:

### Available Tools

- **`echo`**: Simple tool to echo back input messages
  - Input: `message` (string)
  - Returns: Text content with echoed message

- **`add`**: Adds two numbers together
  - Inputs: `a` (number), `b` (number)
  - Returns: Text result of the addition

### Server Configuration

The server is configured with:
- **Transport**: stdio
- **Command**: `npx`
- **Args**: `["-y", "@modelcontextprotocol/server-everything"]`

## Parameter Value Types

The examples demonstrate various parameter value types:

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

All examples demonstrate proper error handling:

```python
from mimory_mcp_focus import FocusError

try:
    result = await focus_client.call_tool("echo", {"message": "forbidden"})
except FocusError as e:
    print(f"Focus error: {e}")
```

Common error scenarios:
- Tool not in allowed list
- Parameter value not allowed
- Missing required parameter in strict mode
- JWT validation failures

## Customization

You can customize the examples by:

1. **Modifying focus rules**: Change the `focus_tools` and `focus_params` to test different scenarios
2. **Adding new tools**: Extend the examples to work with additional MCP tools
3. **JWT customization**: Modify JWT payloads to test different context structures
4. **Error scenarios**: Add more error cases to test edge conditions

## Troubleshooting

### Common Issues

1. **"Command not found: npx"**
   - Ensure Node.js and npm are installed
   - Install the Everything MCP Server: `npm install -g @modelcontextprotocol/server-everything@latest`

2. **"Module not found: mimory_mcp_focus"**
   - Install the package: `pip install mimory-mcp-focus`
   - Or install from source: `pip install -e .`

3. **Connection timeouts**
   - Ensure the Everything MCP Server is properly installed
   - Check that the server command and arguments are correct

4. **JWT validation errors**
   - Ensure JWT tokens are properly formatted
   - Verify JWT keys and algorithms match
   - Check token expiration times

### Debug Mode

Enable debug output by setting environment variables:

```bash
export MCP_DEBUG=1
python examples/basic_usage.py
```

## Contributing

To add new examples:

1. Create a new Python file in the `examples/` directory
2. Follow the naming convention: `descriptive_name.py`
3. Include comprehensive docstrings and comments
4. Add the example to this README
5. Test with the Everything MCP Server

## License

These examples are provided under the same MIT License as the main library.
