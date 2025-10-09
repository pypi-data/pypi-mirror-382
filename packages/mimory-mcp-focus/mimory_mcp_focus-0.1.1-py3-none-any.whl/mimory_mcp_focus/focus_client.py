from typing import Any, Dict, Iterable, Optional, List, Union
from pydantic import BaseModel, ValidationError

from mcp import ClientSession
from mcp.types import CallToolResult, TextContent

import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError, InvalidSignatureError

# Define the raw simple focus schema
# Needs to accept both string and list values for focus_params
class RawSimpleFocus(BaseModel):
    focus_tools: List[str]
    focus_params: Dict[str, Union[str, List[str]]]
    strict: bool = False

# Define the fixed simple focus schema
class SimpleFocus(BaseModel):
    focus_tools: List[str]
    focus_params: Dict[str, List[str]]
    strict: bool = False

# Define the composite focus schema
class CompositeFocus(BaseModel):
    focus: Dict[str, Dict[str, List[str]]]
    strict: bool = False

#
# Start of internal functions to validate schemas and check values
#

def _check_focus_schema(focus: Any, focus_type: str) -> None:
    """
    Check that the focus schema matches the focus_type.

    Args:
        focus: The focus schema to validate
        focus_type: The type of focus schema to validate

    Raises:
        ValueError: If the focus schema is invalid or the focus type is invalid
    """
    try:
        if focus_type == "simple":
            SimpleFocus(**focus)
        elif focus_type == "composite":
            CompositeFocus(**focus)
        else:
            raise ValueError(f"Invalid focus type: {focus_type}")
    except ValidationError as e:
        raise ValueError(f"Invalid focus schema: {e}")

def _normalize_focus_params(focus_params: Dict[str, Union[str, List[str]]]) -> Dict[str, List[str]]:
    """
    Normalize focus_params by splitting comma-separated values and ensuring all values are lists.

    Args:
        focus_params: The focus_params to normalize

    Returns:
        The normalized focus_params
    """
    normalized = {}
    for param, values in focus_params.items():
        if isinstance(values, str):
            # Split comma-separated values
            normalized[param] = [v.strip() for v in values.split(',')]
        else:
            normalized[param] = list(values)
    return normalized

def _check_range_value(value: Any, range_str: str) -> bool:
    """
    Check if a value falls within the specified range (inclusive).

    Args:
        value: The value to check
        range_str: The range string to check

    Returns:
        True if the value falls within the specified range, False otherwise
    """
    try:
        if not range_str.startswith('range:'):
            return False
        range_part = range_str[6:]  # Remove 'range:' prefix
        if '-' not in range_part:
            return False
        start_str, end_str = range_part.split('-', 1)
        start_val = float(start_str)
        end_val = float(end_str)
        val = float(value)
        return start_val <= val <= end_val
    except (ValueError, AttributeError):
        return False

def _check_value_allowed(value: Any, allowed_values: List[str]) -> bool:
    """
    Check if a value is allowed according to the focus rules.

    Args:
        value: The value to check
        allowed_values: The allowed values to check against

    Returns:
        True if the value is allowed, False otherwise
    """
    for allowed in allowed_values:
        if allowed == "*":
            return True
        if allowed.startswith('range:'):
            if _check_range_value(value, allowed):
                return True
        elif str(value) == str(allowed):
            return True
    return False

#
#  Start of tool argument focus checks
#

def check_tool_args_focus(tool: str, args: Dict[str, Any], focus: Any, focus_type: str):
    """
    Check tool arguments against the focus based using the appropriate focus method.

    Args:
        tool: The tool to check
        args: The arguments to check
        focus: The focus to check against
        focus_type: The type of focus to check
        strict: Whether to check strictly

    Raises:
        ValueError: If the focus type is invalid
        Passes up any other errors from _check_focus_schema, _check_tool_args_focus_simple, or _check_tool_args_focus_composite
    """
    # First check that focus schema matches focus_type
    _check_focus_schema(focus, focus_type)

    # If schema matches, run the appropriate focus check
    # If focus_type is not a valid type, raise an error.  
    # Should never happen as _check_focus_schema will raise an error if the schema is invalid.
    if focus_type == "simple":
        # Extract focus_tools, focus_params, strict from focus
        focus_tools = focus.get("focus_tools")
        focus_params = focus.get("focus_params")
        strict = focus.get("strict")

        # Run the appropriate focus check
        _check_tool_args_focus_simple(tool, args, focus_tools, focus_params, strict)
    elif focus_type == "composite":
        # Extract focus_tools, focus_params, strict from focus
        focus = focus.get("focus")
        strict = focus.get("strict")

        # Run the appropriate focus check
        _check_tool_args_focus_composite(tool, args, focus, strict)
    else:
        raise ValueError(f"Invalid focus type: {focus_type}")

def _check_tool_args_focus_simple(tool: str, args: Dict[str, Any], focus_tools: List[str], focus_params: Dict[str, List[str]], strict: bool):
    """Check arguments using simple focus method (focus_tools + focus_params).

    Args:
        tool: The tool to check
        args: The arguments to check
        focus_tools: The focus_tools to check against
        focus_params: The focus_params to check against
        strict: Whether to check strictly

    Raises:
        ValueError: If the tool is not in the allowed focus_tools list
        ValueError: If the parameters do not match the allowed focus context
        ValueError: If a parameter is missing from the focus context and strict mode is enabled
    """
    # Check if tool is allowed
    if "*" not in focus_tools and tool not in focus_tools:
        raise ValueError(f"Tool {tool} is not in the allowed focus_tools list.")
    
    # Check each parameter
    for param, val in args.items():
        if param in focus_params:
            if not _check_value_allowed(val, focus_params[param]):
                raise ValueError(f"Parameter {param}: {val} does not match allowed focus context.")
        elif strict:
            raise ValueError(f"Parameter {param}: missing from focus context and strict mode is enabled.")

def _check_tool_args_focus_composite(tool: str, args: Dict[str, Any], focus: Dict[str, Dict[str, List[str]]], strict: bool):
    """
    Check arguments using composite focus method (direct focus dict).

    Args:
        tool: The tool to check
        args: The arguments to check
        focus: The focus to check against
        strict: Whether to check strictly

    Raises:
        ValueError: If the tool is not in the focus context
        ValueError: If the parameters do not match the allowed focus context
        ValueError: If a parameter is missing from the focus context and strict mode is enabled
    """
    # Get effective focus rules (combine * and specific tool)
    effective = {**focus.get("*", {}), **focus.get(tool, {})}
    
    if (focus.get(tool) is None) and (focus.get("*") is None):
        raise ValueError(f"Tool {tool} is not in the focus context.")
    
    for param, val in args.items():
        if param in effective:
            if not _check_value_allowed(val, effective[param]):
                raise ValueError(f"Parameter {param}: {val} does not match allowed focus context.")
        elif strict:
            raise ValueError(f"Parameter {param}: missing from focus context and strict mode is enabled.")

#
#  Start of tool list focus checks
#

def filter_tools_focus(tools: List[Any], focus: Any, focus_type: str) -> List[Any]:
    """
    Filter tools based on the focus and focus_type.

    Args:
        tools: The tools to filter
        focus: The focus to filter against
        focus_type: The type of focus to filter
    
    Returns:
        The filtered tools

    Raises:
        ValueError: If the focus type is invalid
    """
    # First check that focus schema matches focus_type
    _check_focus_schema(focus, focus_type)

    # If schema matches, run the appropriate filter
    # If focus_type is not a valid type, raise an error.  
    # Should never happen as _check_focus_schema will raise an error if the schema is invalid.
    if focus_type == "simple":
        # Extract focus_tools from focus
        focus_tools = focus.get("focus_tools")

        # Run the appropriate filter
        return _filter_tools_focus_simple(tools, focus_tools)
    elif focus_type == "composite":
        # Extract focus from focus
        focus = focus.get("focus")

        # Run the appropriate filter
        return _filter_tools_focus_composite(tools, focus)
    else:
        raise ValueError(f"Invalid focus type: {focus_type}")

def _filter_tools_focus_simple(tools: List[Any], focus_tools: List[str]) -> List[Any]:
    """
    Filter tools based on simple focus list.

    Args:
        tools: The tools to filter
        focus_tools: The focus_tools to filter against

    Returns:
        The filtered tools
    """
    if "*" in focus_tools:
        return tools
    return [tool for tool in tools if tool.name in focus_tools]

def _filter_tools_focus_composite(tools: List[Any], focus: Dict[str, Dict[str, List[str]]]) -> List[Any]:
    """
    Filter tools based on focus composite dict.

    Args:
        tools: The tools to filter
        focus: The focus to filter against

    Returns:
        The filtered tools
    """
    if "*" in focus:
        return tools
    return [tool for tool in tools if tool.name in focus]

#
#  Class for FocusedClientSession
#  Wraps a ClientSession and applies focus restrictions to the list_tools and call_tool methods
#
class FocusedClientSession:
    """
    Class that focuses a ClientSession using focus and focus_type.

    Args:
        session: The ClientSession to wrap
        focus: The focus to filter against
        focus_type: The type of focus to filter

    Raises:
        ValueError: If the focus type is invalid
    """
    def __init__(
        self,
        session: ClientSession,
        focus: Dict[str, Any],
        focus_type: str
    ):
        self.session = session
        
        # Set the focus and focus_type
        if focus_type == 'simple':
            # Validate the focus schema
            SimpleFocus(**focus)

            self.focus = focus
            self.focus_type = 'simple'
        elif focus_type == 'composite':
            # Validate the focus schema
            CompositeFocus(**focus)

            self.focus = focus
            self.focus_type = 'composite'
        else:
            raise ValueError(f"Invalid focus type: {focus_type}")
    
    def __getattr__(self, name):
        """Proxy all other method calls to the underlying session."""
        return getattr(self.session, name)
    
    def refocus(
        self, 
        focus: Dict[str, Any], 
        focus_type: str
    ):
        """
        Refocus the client with new focus and focus_type.

        Args:
            focus: The focus to filter against
            focus_type: The type of focus to filter

        Raises:
            ValueError: If the focus type is invalid
        """
        # refocus via focus_type
        if focus_type == 'simple':
            # Validate the focus schema
            SimpleFocus(**focus)

            # Update the focus and focus_type
            self.focus = focus
            self.focus_type = 'simple'
        elif focus_type == 'composite':
            # Validate the focus schema
            CompositeFocus(**focus)

            # Update the focus and focus_type
            self.focus = focus
            self.focus_type = 'composite'
        else:
            raise ValueError(f"Invalid focus type: {focus_type}")
        
    async def list_tools(self, cursor: str | None = None):
        """List tools with focus restrictions."""
        tools_result = await self.session.list_tools(cursor=cursor)

        # Filter the tools list while preserving the ListToolsResult structure
        filtered_tools = filter_tools_focus(tools_result.tools, self.focus, self.focus_type)
        
        # Create a new ListToolsResult with filtered tools
        return type(tools_result)(
            tools=filtered_tools,
            meta=tools_result.meta,
            nextCursor=tools_result.nextCursor
        )

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any], **kwargs):
        """Call a tool with focus restrictions."""
        try:
            check_tool_args_focus(tool_name, arguments or {}, self.focus, self.focus_type)
        except Exception as e:
            # Use repr() to get the exception type and any message
            error_msg = repr(e) if str(e) else f"{type(e).__name__}()"
            error_msg = "FocusError: " + error_msg
            return CallToolResult(
                content=[TextContent(type="text", text=error_msg)],
                isError=True
            )
        
        return await self.session.call_tool(tool_name, arguments, **kwargs)


def focus_client_simple(
    session: ClientSession,
    focus_tools: Optional[List[str]] = None,
    focus_params: Optional[Dict[str, Union[str, List[str]]]] = None,
    strict: bool = False,
) -> FocusedClientSession:
    """
    Standard focus client using focus_tools and focus_params.

    Args:
        session: The ClientSession to wrap
        focus_tools: The focus_tools to filter against
        focus_params: The focus_params to filter against
        strict: Whether to check strictly

    Returns:
        The focused client
    """

    # If focus_tools and focus_params are not provided, use a default simple focus
    # This is equivalent to allowing all tools and all parameters
    if focus_tools is None:
        focus_tools = ["*"]
    if focus_params is None:
        focus_params = {}
    
    # Validate the focus object against the raw schema
    RawSimpleFocus(
        focus_tools=focus_tools,
        focus_params=focus_params,
        strict=strict
    )
    # Noramlize the focus params if it passes the schema validation
    focus_params = _normalize_focus_params(focus_params)

    # Create the focus object
    session_focus = {
        "focus_tools": focus_tools,
        "focus_params": focus_params,
        "strict": strict
    }

    return FocusedClientSession(
        session=session,
        focus=session_focus,
        focus_type="simple"
    )

def refocus_client_simple(
    session: FocusedClientSession,
    focus_tools: List[str],
    focus_params: Dict[str, Union[str, List[str]]],
    strict: bool
) -> None:
    """
    Refocus the client with new focus_tools and focus_params.

    Args:
        session: The client to refocus
        focus_tools: The focus_tools to filter against
        focus_params: The focus_params to filter against
        strict: Whether to check strictly
    """
    # Create and validate the focus object against the schema
    RawSimpleFocus(
        focus_tools=focus_tools,
        focus_params=focus_params,
        strict=strict
    )
    focus_params = _normalize_focus_params(focus_params)

    # Create the focus object
    new_focus = {
        "focus_tools": focus_tools,
        "focus_params": focus_params,
        "strict": strict
    }

    # Refocus the client
    session.refocus(new_focus, 'simple')


def focus_client_composite(
    session: ClientSession,
    focus: Optional[Dict[str, Dict[str, List[str]]]] = None,
    strict: bool = False,
) -> FocusedClientSession:
    """
    Composite focus client using direct focus dictionary.

    Args:
        session: The ClientSession to wrap
        focus: The focus to filter against
        strict: Whether to check strictly

    Returns:
        The focused client
    """

    # If focus is not provided, use a default composite focus
    # This is equivalent to allowing all tools and all parameters
    if focus is None:
        focus = {
            "*": {
                "*" : ["*"]
            }
        }

    # Validate the focus object against the schema
    CompositeFocus(
        focus=focus,
        strict=strict
    )

    # Create the focus object
    session_focus = {
        "focus": focus,
        "strict": strict
    }

    return FocusedClientSession(
        session=session,
        focus=session_focus,
        focus_type="composite"
    )

def refocus_client_composite(
    session: FocusedClientSession,
    focus: Dict[str, Dict[str, List[str]]],
    strict: bool
) -> None:
    """
    Refocus the client with new focus and strict mode.

    Args:
        session: The client to refocus
        focus: The focus to filter against
        strict: Whether to check strictly
    """
    CompositeFocus(
        focus=focus,
        strict=strict
    )

    # Create the focus object
    new_focus = {
        "focus": focus,
        "strict": strict
    }

    # Refocus the client
    session.refocus(new_focus, 'composite')
#
#  Start of JWT extraction functions
#

def extract_mcp_context_jwt(
    jwt_token: str,
    jwt_key: str,
    jwt_signing_algorithm: str,
    parameter_field: str = 'context',
    tool_field: str = 'tools',
    strict: bool = False
) -> Dict[str, Any]:
    """
    Extract context parameters and tools allowed from a JWT token.
    
    Args:
        jwt_token: The JWT token to extract context from
        jwt_key: The symmetric key for symmetric algorithms or PEM public key for asymmetric algorithms
        jwt_signing_algorithm: The JWT signing algorithm (e.g., 'HS256', 'RS256')
        parameter_field: The field name in the JWT containing context parameters (default: 'context')
        tool_field: The field name in the JWT containing allowed tools (default: 'tools')
        strict: Whether to raise errors for missing fields (default: False)
    
    Returns:
        Dict containing 'context_params' and 'tools_allowed' keys
        
    Raises:
        ValueError: If JWT validation fails or required fields are missing in strict mode
    """
    try:
        # Decode and verify the JWT
        payload = jwt.decode(
            jwt_token,
            jwt_key,
            algorithms=[jwt_signing_algorithm],
            options={"verify_exp": True, "verify_signature": True}
        )
        
        # Extract context parameters
        context_params: Dict[str, Union[str, List[str]]] = {}
        if parameter_field in payload:
            context_value = payload[parameter_field]
            if isinstance(context_value, dict):
                context_params = context_value
            else:
                raise ValueError(f"Parameter field '{parameter_field}' is not a valid object")
        elif strict:
            raise ValueError(f"Parameter field '{parameter_field}' not found in JWT and strict mode is enabled")
        
        # Extract tools allowed
        tools_allowed: List[str] = ['*']
        if tool_field in payload:
            tools_value = payload[tool_field]
            if isinstance(tools_value, list):
                tools_allowed = tools_value
            else:
                raise ValueError(f"Tool field '{tool_field}' is not a valid array")
        elif strict:
            raise ValueError(f"Tool field '{tool_field}' not found in JWT and strict mode is enabled")
        
        return context_params, tools_allowed
        
    except ExpiredSignatureError:
        raise ValueError("JWT token has expired")
    except InvalidSignatureError:
        raise ValueError("JWT signature verification failed")
    except InvalidTokenError as e:
        raise ValueError(f"JWT validation failed: {str(e)}")
    except Exception as e:
        raise ValueError(f"JWT validation failed: {str(e)}")


def extract_mcp_composite_context_jwt(
    jwt_token: str,
    jwt_key: str,
    jwt_signing_algorithm: str,
    composite_context_field: str
) -> Dict[str, Dict[str, List[str]]]:
    """
    Extract composite context object from a JWT token.
    
    Args:
        jwt_token: The JWT token to extract context from
        jwt_key: The symmetric key for symmetric algorithms or PEM public key for asymmetric algorithms
        jwt_signing_algorithm: The JWT signing algorithm (e.g., 'HS256', 'RS256')
        composite_context_field: The field name in the JWT containing the composite context (required)
    
    Returns:
        The composite context object
        
    Raises:
        ValueError: If JWT validation fails or composite context field is missing
    """
    if not composite_context_field:
        raise ValueError("composite_context_field is required")
    
    try:
        # Decode and verify the JWT
        payload = jwt.decode(
            jwt_token,
            jwt_key,
            algorithms=[jwt_signing_algorithm],
            options={"verify_exp": True, "verify_signature": True}
        )
        
        # Extract composite context
        if composite_context_field not in payload:
            raise ValueError(f"Composite context field '{composite_context_field}' not found in JWT")
        
        composite_value = payload[composite_context_field]
        if not isinstance(composite_value, dict):
            raise ValueError(f"Composite context field '{composite_context_field}' is not a valid object")
        
        return composite_value
        
    except ExpiredSignatureError:
        raise ValueError("JWT token has expired")
    except InvalidSignatureError:
        raise ValueError("JWT signature verification failed")
    except InvalidTokenError as e:
        raise ValueError(f"JWT validation failed: {str(e)}")
    except Exception as e:
        raise ValueError(f"JWT validation failed: {str(e)}")
