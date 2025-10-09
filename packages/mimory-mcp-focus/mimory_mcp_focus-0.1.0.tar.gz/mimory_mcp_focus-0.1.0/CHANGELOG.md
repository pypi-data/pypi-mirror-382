# Changelog

All notable changes to this project will be documented in this file.

### Added
- Initial release of mimory-mcp-focus
- FocusClient for basic tool and parameter filtering
- FocusClientComposite for composite focus configurations
- JWT context extraction functions
- Comprehensive examples and documentation
- Support for range validation (`range:min-max`)
- Support for wildcard values (`*`)
- Strict mode for parameter validation
- Dynamic refocusing capabilities

### Features
- **Tool Filtering**: Restrict access to specific MCP tools
- **Parameter Validation**: Enforce allowed values for tool parameters
- **JWT Integration**: Extract focus context from JWT tokens
- **Flexible Configuration**: Support for both simple and composite focus configurations
- **Range Validation**: Support for numeric range constraints
- **Strict Mode**: Optional strict parameter validation

### Dependencies
- mcp >= 1.14.0
- pyjwt >= 2.10.1

## [0.0.1] - 2025-10-07

### Added
- Small scale release to ensure functionality
- Basic focus client functionality
- JWT context extraction
- Comprehensive examples

## [0.1.0] - 2025-10-08

### Added
- Initial public release.
