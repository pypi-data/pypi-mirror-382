"""Entry point for running the MCP server as a module."""

import logging
import sys

from cakemail_mcp import __version__
from cakemail_mcp.server import CakemailMCPServer


def setup_logging() -> None:
    """Configure logging for the application."""
    from cakemail_mcp.config import get_config

    config = get_config()

    logging.basicConfig(
        level=getattr(logging, config.log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stderr)],
    )


def main() -> None:
    """Main entry point for the MCP server."""
    # Handle --version flag
    if len(sys.argv) > 1 and sys.argv[1] in ["--version", "-v"]:
        print(f"cakemail-api-docs-mcp {__version__}")
        sys.exit(0)

    # Handle --help flag
    if len(sys.argv) > 1 and sys.argv[1] in ["--help", "-h"]:
        print("Cakemail API MCP Server")
        print(f"Version: {__version__}")
        print()
        print("Usage:")
        print("  cakemail-api-docs-mcp              Start the MCP server")
        print("  cakemail-api-docs-mcp --version    Show version")
        print("  cakemail-api-docs-mcp --help       Show this help")
        print()
        print("Environment Variables:")
        print("  OPENAPI_SPEC_PATH   Path or URL to OpenAPI spec (default: ./openapi.json)")
        print("  LOG_LEVEL           Logging level (default: INFO)")
        print()
        print("Documentation: https://github.com/cakemail/cakemail-api-docs-mcp")
        sys.exit(0)

    setup_logging()
    server = CakemailMCPServer()
    server.run()


if __name__ == "__main__":
    main()
