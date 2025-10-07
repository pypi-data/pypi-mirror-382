# Cakemail API MCP Server

A Model Context Protocol (MCP) server that exposes Cakemail's email marketing API documentation to AI agents, eliminating hallucination and enabling accurate code generation.

## Overview

The Cakemail API MCP Server provides AI coding assistants (Claude, Cursor, GitHub Copilot) with direct access to authoritative Cakemail API specifications. Instead of guessing endpoint URLs, parameters, and authentication details, AI agents can query the MCP server for exact specifications from Cakemail's OpenAPI documentation.

## Features

- **Zero-hallucination guarantee**: AI agents get facts from OpenAPI spec, not statistical guesses
- **Real-time API documentation**: Always reflects the latest API state
- **Seamless integration**: Works with Claude Desktop, Cursor, and other MCP-compatible tools
- **Fast queries**: <500ms response time for spec lookups

## Installation

### ⭐ Easiest Method (Recommended)

**One command to install with Claude Code/Desktop:**

```bash
# Using npx (works for everyone!)
claude mcp add cakemail-api-docs -- npx cakemail-api-docs

# Or using uvx (Python developers)
claude mcp add cakemail-api-docs -- uvx cakemail-api-docs-mcp
```

That's it! No manual configuration needed.

### Alternative Methods

**Method 1: Using npm**
```bash
npm install -g cakemail-api-docs
claude mcp add cakemail-api-docs cakemail-api-docs
```

**Method 2: Using pip**
```bash
pip install cakemail-api-docs-mcp
claude mcp add cakemail-api-docs cakemail-api-docs-mcp
```

**Method 3: From source (for development)**
```bash
git clone https://github.com/cakemail/cakemail-api-documentation-mcp.git
cd cakemail-api-documentation-mcp
uv pip install -e ".[dev]"
```

See [INSTALLATION.md](./INSTALLATION.md) for detailed installation options.

## Quick Start

### Using with Claude Desktop

After running `claude mcp add`, restart Claude Desktop. You should see a 🔌 icon indicating the server is connected.

**Test it:**
- "Can you check the health of the Cakemail MCP server?"
- "List all Cakemail API endpoints"
- "Show me how to authenticate with the Cakemail API"

### Manual Configuration

If not using `claude mcp add`, edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "cakemail": {
      "command": "cakemail-api-docs-mcp",
      "env": {
        "OPENAPI_SPEC_PATH": "https://api.cakemail.dev/openapi.json"
      }
    }
  }
}
```

### Running Standalone

```bash
cakemail-api-docs-mcp
```

Or using Python module:

```bash
python -m cakemail_mcp
```

### Integrating with Claude Desktop

Add to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "cakemail": {
      "command": "cakemail-api-docs-mcp",
      "env": {
        "OPENAPI_SPEC_PATH": "/path/to/cakemail/openapi.json"
      }
    }
  }
}
```

## Development

### Setup

```bash
# Clone repository
git clone https://github.com/cakemail/cakemail-api-docs-mcp.git
cd cakemail-api-docs-mcp

# Install with development dependencies
uv pip install -e .[dev]
```

### Running Tests

```bash
pytest
```

### Code Quality

```bash
# Format code
black src tests

# Lint
ruff check src tests

# Type check
mypy src
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! Please see our [contributing guidelines](CONTRIBUTING.md) for details.

## Support

- [Documentation](https://github.com/cakemail/cakemail-api-docs-mcp#readme)
- [Issue Tracker](https://github.com/cakemail/cakemail-api-docs-mcp/issues)
- [Cakemail API Documentation](https://docs.cakemail.com)
