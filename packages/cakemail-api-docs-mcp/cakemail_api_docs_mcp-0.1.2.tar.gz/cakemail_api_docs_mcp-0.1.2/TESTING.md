# Testing the Cakemail MCP Server Locally

## Prerequisites

1. **Claude Desktop** installed on macOS
2. **Python 3.11+** installed
3. **UV package manager** installed (`curl -LsSf https://astral.sh/uv/install.sh | sh`)

## Setup Steps

### 1. Install the MCP Server in Development Mode

```bash
cd /Users/francoislane/dev/cakemail-api-mcp
uv pip install -e ".[dev]"
```

### 2. Configure Claude Desktop

Edit your Claude Desktop configuration file:

```bash
# Open the config file
code ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

Add the following configuration:

```json
{
  "mcpServers": {
    "cakemail": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/Users/francoislane/dev/cakemail-api-mcp",
        "python",
        "-m",
        "cakemail_mcp"
      ],
      "env": {
        "OPENAPI_SPEC_PATH": "/Users/francoislane/dev/cakemail-api-mcp/openapi.json",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

**Alternative (if globally installed):**

```json
{
  "mcpServers": {
    "cakemail": {
      "command": "python3",
      "args": ["-m", "cakemail_mcp"],
      "env": {
        "OPENAPI_SPEC_PATH": "/Users/francoislane/dev/cakemail-api-mcp/openapi.json",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### 3. Restart Claude Desktop

**Important:** Completely quit and restart Claude Desktop for the configuration to take effect:

1. Quit Claude Desktop (Cmd+Q)
2. Relaunch Claude Desktop

### 4. Verify the Connection

In Claude Desktop, you should see a small 🔌 icon in the input area indicating MCP servers are connected.

## Testing the Tools

### Test 1: Health Check

Ask Claude:
```
Can you check the health of the Cakemail MCP server?
```

Expected response should include:
- Status: "ok"
- Server version: "0.1.0"
- Endpoint count: 149
- Timestamp

### Test 2: List Endpoints

Ask Claude:
```
List all Cakemail API endpoints tagged with "Campaigns"
```

Expected: Array of campaign-related endpoints

### Test 3: Get Endpoint Details

Ask Claude:
```
Get the details for the GET /campaigns/{campaign_id} endpoint
```

Expected: Complete endpoint specification with parameters, responses, and schemas

### Test 4: Authentication Info

Ask Claude:
```
What authentication does the Cakemail API use?
```

Expected: OAuth2 configuration with token URL and scopes

### Test 5: Error Handling

Ask Claude:
```
Get details for a non-existent endpoint: /fake/endpoint with GET method
```

Expected: Error response with suggestions for similar paths

## Troubleshooting

### Server Not Connecting

**Check logs:**
```bash
# Check Claude Desktop logs
tail -f ~/Library/Logs/Claude/mcp*.log
```

**Test server manually:**
```bash
cd /Users/francoislane/dev/cakemail-api-mcp
uv run python -m cakemail_mcp
```

You should see:
```
INFO:cakemail_mcp:Starting Cakemail MCP Server v0.1.0 (OpenAPI spec: /path/to/openapi.json)
INFO:cakemail_mcp:Successfully loaded OpenAPI spec with 149 paths
```

Press Ctrl+C to stop.

### OpenAPI Spec Not Found

Make sure the `OPENAPI_SPEC_PATH` in your config points to the correct location:

```bash
ls -la /Users/francoislane/dev/cakemail-api-mcp/openapi.json
```

### Permission Issues

Ensure the script is executable:

```bash
chmod +x /Users/francoislane/dev/cakemail-api-mcp/src/cakemail_mcp/__main__.py
```

### UV Not Found

Install UV:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then restart your terminal.

## Debugging

### Enable Debug Logging

Update your Claude Desktop config to set `LOG_LEVEL` to `DEBUG`:

```json
{
  "mcpServers": {
    "cakemail": {
      "command": "uv",
      "args": ["run", "--directory", "/Users/francoislane/dev/cakemail-api-mcp", "python", "-m", "cakemail_mcp"],
      "env": {
        "OPENAPI_SPEC_PATH": "/Users/francoislane/dev/cakemail-api-mcp/openapi.json",
        "LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

### Test with MCP Inspector

Install the MCP Inspector for interactive debugging:

```bash
npx @modelcontextprotocol/inspector uv run --directory /Users/francoislane/dev/cakemail-api-mcp python -m cakemail_mcp
```

This opens a web UI at http://localhost:5173 where you can:
- See all available tools
- Call tools interactively
- View request/response data
- Debug connection issues

## Advanced Testing

### Test Custom Code Generation

Ask Claude:
```
Write Python code to list all campaigns using the Cakemail API
```

Claude should use the MCP tools to discover the correct endpoint and generate accurate code.

### Test Error Recovery

Ask Claude:
```
I want to use the endpoint /campaings (typo) to get campaigns
```

Claude should use the error handling to suggest the correct path `/campaigns`.

## Expected Behavior

When working correctly:
- Claude will use `cakemail_list_endpoints`, `cakemail_get_endpoint`, `cakemail_get_auth`, and `cakemail_health` tools
- Claude will generate accurate API code without hallucinating endpoints
- Claude will provide correct authentication information
- Errors will include helpful suggestions

## Next Steps

Once local testing is complete:
1. Test with real API integration
2. Validate OAuth2 authentication flow
3. Test all 149 endpoints
4. Prepare for PyPI publication
