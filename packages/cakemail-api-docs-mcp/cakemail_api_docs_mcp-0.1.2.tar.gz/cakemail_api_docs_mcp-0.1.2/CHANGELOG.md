# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-10-05

### Added

#### Core MCP Server (Epic 1)
- Initial MCP server implementation using FastMCP framework
- OpenAPI specification loading from local files and remote URLs
- Automatic tool generation from OpenAPI spec (217 tools from Cakemail API)
- Health check MCP tool (`cakemail_health`)
- Graceful shutdown handlers (SIGINT, SIGTERM)
- Comprehensive logging with configurable log levels
- CI/CD pipeline with GitHub Actions
- Multi-version Python testing (3.11, 3.12)

#### API Discovery & Documentation (Epic 2)
- Endpoint discovery tool (`cakemail_list_endpoints`) with tag filtering
- Endpoint detail query tool (`cakemail_get_endpoint`) with full spec extraction
- Authentication documentation tool (`cakemail_get_auth`) with OAuth2 support
- Structured error handling with custom error codes:
  - `MISSING_PARAMETER` - Required parameter not provided
  - `INVALID_PARAMETER` - Parameter validation failed
  - `ENDPOINT_NOT_FOUND` - Requested endpoint doesn't exist
  - `SPEC_LOAD_ERROR` - OpenAPI spec failed to load
- Path similarity suggestions for 404 errors
- Available methods suggestions for invalid HTTP methods
- Comprehensive error logging with context

#### Quality & Testing
- 42 unit tests with 100% pass rate
- 77% code coverage (100% on errors.py, config.py, openapi_repository.py)
- Strict type checking with mypy
- Code linting with ruff
- Code formatting with black

#### Documentation
- Comprehensive README with quick start guide
- Installation guide with multiple methods (pip, pipx, uvx, claude mcp add)
- Local testing guide for Claude Desktop integration
- Implementation summary with architecture details
- Error handling and troubleshooting documentation

### Features

- **4 Custom MCP Tools:**
  - `cakemail_health` - Server health and status check
  - `cakemail_list_endpoints` - Discover API endpoints with optional filtering
  - `cakemail_get_endpoint` - Get detailed specifications for any endpoint
  - `cakemail_get_auth` - Authentication requirements and OAuth2 configuration

- **217 Auto-Generated Tools:**
  - Direct invocation of all Cakemail API operations
  - Full parameter and schema support
  - Automatic documentation from OpenAPI

- **Real Cakemail API Integration:**
  - 149 API endpoints from OpenAPI 3.1.0 spec
  - OAuth2 Password Bearer authentication
  - Base URL: https://api.cakemail.dev

### Performance

- OpenAPI spec loading: ~4ms for 149 endpoints
- Tool response time: <50ms (well under 500ms target)
- In-memory caching for optimal performance
- Zero re-parsing on tool calls

### Technical Details

- Python 3.11+ support
- FastMCP 0.2.0+ framework
- Stdio transport for MCP communication
- Repository pattern for data access
- Environment-based configuration

### Installation

Supports multiple installation methods:
- One-command: `claude mcp add cakemail -- uvx cakemail-api-docs-mcp`
- Traditional: `pip install cakemail-api-docs-mcp`
- Development: `uv pip install -e ".[dev]"`

[0.1.0]: https://github.com/cakemail/cakemail-api-docs-mcp/releases/tag/v0.1.0
