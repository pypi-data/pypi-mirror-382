"""MCP Server implementation using FastMCP framework."""

import logging
import signal
import sys
from datetime import UTC, datetime
from typing import Any

import httpx
from fastmcp import FastMCP

from cakemail_mcp import __version__
from cakemail_mcp.config import get_config
from cakemail_mcp.errors import MCPError, create_error_response, find_similar_paths
from cakemail_mcp.openapi_repository import OpenAPIRepository

logger = logging.getLogger(__name__)


class CakemailMCPServer:
    """Cakemail API MCP Server.

    Exposes Cakemail API documentation to AI agents via Model Context Protocol.
    """

    def __init__(self) -> None:
        """Initialize the MCP server."""
        self.config = get_config()
        self.openapi_repo = OpenAPIRepository(self.config.openapi_spec_path)

        # Load OpenAPI spec
        try:
            openapi_spec = self.openapi_repo.load()

            # Extract base URL from the spec if available
            base_url = self._get_base_url_from_spec(openapi_spec)

            # Create HTTP client for API calls
            self.http_client = httpx.AsyncClient(
                base_url=base_url,
                timeout=30.0,
                follow_redirects=True,
            )

            # Create lightweight FastMCP server (no auto-generated tools)
            self.mcp = FastMCP(
                name="Cakemail API",
                version=__version__,
            )

            logger.info(
                f"Successfully loaded OpenAPI spec with "
                f"{len(openapi_spec.get('paths', {}))} paths"
            )
        except Exception as e:
            logger.error(f"Failed to load OpenAPI spec: {e}")
            raise

        # Register custom tools
        self._register_health_check_tool()
        self._register_endpoint_discovery_tool()
        self._register_endpoint_detail_tool()
        self._register_auth_documentation_tool()
        self._register_api_call_tool()

        self._setup_signal_handlers()

    def _get_base_url_from_spec(self, spec: dict[str, Any]) -> str:
        """Extract base URL from OpenAPI specification.

        Args:
            spec: The OpenAPI specification

        Returns:
            Base URL for the API
        """
        # OpenAPI 3.x uses 'servers' array
        if "servers" in spec and spec["servers"]:
            url: str = spec["servers"][0].get("url", "https://api.cakemail.com")
            return url

        # Fallback to Cakemail API default
        return "https://api.cakemail.com"

    def _register_health_check_tool(self) -> None:
        """Register a custom health check MCP tool."""

        @self.mcp.tool()
        def cakemail_health() -> dict[str, Any]:
            """Check if Cakemail MCP server is operational.

            Returns:
                Health status information including server version and endpoint count
            """
            endpoint_count = len(self.openapi_repo.spec.get("paths", {}))  # type: ignore

            return {
                "status": "ok",
                "serverVersion": __version__,
                "endpointCount": endpoint_count,
                "timestamp": datetime.now(UTC).isoformat(),
            }

    def _register_endpoint_discovery_tool(self) -> None:
        """Register endpoint discovery MCP tool."""

        @self.mcp.tool()
        def cakemail_list_endpoints(tag: str | None = None) -> list[dict[str, Any]] | dict[str, Any]:
            """List all available Cakemail API endpoints.

            Args:
                tag: Optional tag to filter endpoints (e.g., "Account", "Campaigns")

            Returns:
                List of endpoints with path, method, summary, tags, and operationId,
                or error response if spec cannot be loaded
            """
            spec = self.openapi_repo.spec
            if not spec:
                return create_error_response(
                    "OpenAPI specification not loaded",
                    MCPError.SPEC_LOAD_ERROR,
                )

            endpoints: list[dict[str, Any]] = []
            paths = spec.get("paths", {})

            for path, path_item in paths.items():
                for method, operation in path_item.items():
                    # Skip non-HTTP methods (like 'parameters', 'servers', etc.)
                    if method not in ["get", "post", "put", "patch", "delete", "options", "head"]:
                        continue

                    if not isinstance(operation, dict):
                        continue

                    operation_tags = operation.get("tags", [])

                    # Apply tag filter if provided
                    if tag and tag not in operation_tags:
                        continue

                    endpoints.append(
                        {
                            "path": path,
                            "method": method.upper(),
                            "summary": operation.get("summary", ""),
                            "tags": operation_tags,
                            "operationId": operation.get("operationId", ""),
                        }
                    )

            # Sort by path, then by method
            endpoints.sort(key=lambda e: (e["path"], e["method"]))

            return endpoints

    def _register_endpoint_detail_tool(self) -> None:
        """Register endpoint detail query MCP tool."""

        @self.mcp.tool()
        def cakemail_get_endpoint(path: str, method: str) -> dict[str, Any]:
            """Get detailed specification for a specific Cakemail API endpoint.

            Args:
                path: API endpoint path (e.g., "/campaigns/{id}")
                method: HTTP method (e.g., "GET", "POST")

            Returns:
                Detailed endpoint specification with parameters, request body, and responses,
                or error response if endpoint not found
            """
            # Validate parameters
            if not path:
                return create_error_response(
                    "Path parameter is required",
                    MCPError.MISSING_PARAMETER,
                    {"parameter": "path"},
                )

            if not method:
                return create_error_response(
                    "Method parameter is required",
                    MCPError.MISSING_PARAMETER,
                    {"parameter": "method"},
                )

            spec = self.openapi_repo.spec
            if not spec:
                return create_error_response(
                    "OpenAPI specification not loaded",
                    MCPError.SPEC_LOAD_ERROR,
                )

            paths = spec.get("paths", {})
            path_item = paths.get(path)

            if not path_item:
                # Find similar paths
                available_paths = list(paths.keys())
                suggestions = find_similar_paths(path, available_paths)

                return create_error_response(
                    f"Endpoint not found: {path}",
                    MCPError.ENDPOINT_NOT_FOUND,
                    {
                        "path": path,
                        "method": method,
                        "suggestions": suggestions,
                    },
                    {"requested_path": path, "requested_method": method},
                )

            operation = path_item.get(method.lower())
            if not operation or not isinstance(operation, dict):
                available_methods = [
                    m.upper()
                    for m in path_item
                    if m in ["get", "post", "put", "patch", "delete", "options", "head"]
                ]

                return create_error_response(
                    f"Method {method.upper()} not found for path {path}",
                    MCPError.ENDPOINT_NOT_FOUND,
                    {
                        "path": path,
                        "method": method.upper(),
                        "availableMethods": available_methods,
                    },
                    {"requested_path": path, "requested_method": method},
                )

            # Extract parameters
            parameters = []
            for param in operation.get("parameters", []):
                parameters.append(
                    {
                        "name": param.get("name"),
                        "in": param.get("in"),
                        "required": param.get("required", False),
                        "type": param.get("schema", {}).get("type"),
                        "description": param.get("description", ""),
                        "example": param.get("example"),
                    }
                )

            # Extract request body
            request_body = None
            if "requestBody" in operation:
                req_body = operation["requestBody"]
                content = req_body.get("content", {})
                request_body = {
                    "required": req_body.get("required", False),
                    "description": req_body.get("description", ""),
                    "contentTypes": list(content.keys()),
                    "schema": {},
                }

                # Get first content type schema
                if content:
                    first_content = next(iter(content.values()))
                    request_body["schema"] = first_content.get("schema", {})

            # Extract responses
            responses = {}
            for status_code, response in operation.get("responses", {}).items():
                content = response.get("content", {})
                responses[status_code] = {
                    "description": response.get("description", ""),
                    "contentTypes": list(content.keys()),
                    "schema": {},
                }

                # Get first content type schema
                if content:
                    first_content = next(iter(content.values()))
                    responses[status_code]["schema"] = first_content.get("schema", {})

            return {
                "path": path,
                "method": method.upper(),
                "summary": operation.get("summary", ""),
                "description": operation.get("description", ""),
                "operationId": operation.get("operationId", ""),
                "tags": operation.get("tags", []),
                "parameters": parameters,
                "requestBody": request_body,
                "responses": responses,
            }

    def _register_auth_documentation_tool(self) -> None:
        """Register authentication documentation MCP tool."""

        @self.mcp.tool()
        def cakemail_get_auth() -> dict[str, Any]:
            """Get Cakemail API authentication documentation.

            Returns:
                Authentication requirements and configuration details,
                or error response if spec cannot be loaded
            """
            spec = self.openapi_repo.spec
            if not spec:
                return create_error_response(
                    "OpenAPI specification not loaded",
                    MCPError.SPEC_LOAD_ERROR,
                )

            components = spec.get("components", {})
            security_schemes = components.get("securitySchemes", {})

            schemes = []
            for scheme_name, scheme_data in security_schemes.items():
                scheme_info: dict[str, Any] = {
                    "name": scheme_name,
                    "type": scheme_data.get("type"),
                    "description": scheme_data.get("description", ""),
                }

                # Extract type-specific details
                if scheme_data.get("type") == "http":
                    scheme_info["scheme"] = scheme_data.get("scheme")
                    scheme_info["bearerFormat"] = scheme_data.get("bearerFormat")

                elif scheme_data.get("type") == "apiKey":
                    scheme_info["in"] = scheme_data.get("in")
                    scheme_info["name"] = scheme_data.get("name")

                elif scheme_data.get("type") == "oauth2":
                    flows = scheme_data.get("flows", {})
                    scheme_info["flows"] = {}

                    for flow_type, flow_data in flows.items():
                        scheme_info["flows"][flow_type] = {
                            "tokenUrl": flow_data.get("tokenUrl"),
                            "authorizationUrl": flow_data.get("authorizationUrl"),
                            "refreshUrl": flow_data.get("refreshUrl"),
                            "scopes": flow_data.get("scopes", {}),
                        }

                schemes.append(scheme_info)

            return {
                "schemes": schemes,
                "baseUrl": self._get_base_url_from_spec(spec),
            }

    def _register_api_call_tool(self) -> None:
        """Register API call execution MCP tool."""

        @self.mcp.tool()
        async def cakemail_call_api(
            path: str,
            method: str,
            headers: dict[str, str] | None = None,
            query_params: dict[str, Any] | None = None,
            body: dict[str, Any] | None = None,
        ) -> dict[str, Any]:
            """Execute a Cakemail API call.

            Args:
                path: API endpoint path (e.g., "/campaigns/{id}"). Use actual values for path parameters.
                method: HTTP method (GET, POST, PUT, PATCH, DELETE)
                headers: Optional HTTP headers (e.g., {"Authorization": "Bearer token"})
                query_params: Optional query parameters
                body: Optional request body for POST/PUT/PATCH requests

            Returns:
                API response with status, headers, and body

            Example:
                cakemail_call_api(
                    path="/campaigns/123",
                    method="GET",
                    headers={"Authorization": "Bearer YOUR_TOKEN"}
                )
            """
            # Validate inputs
            if not path:
                return create_error_response(
                    "Path parameter is required",
                    MCPError.MISSING_PARAMETER,
                    {"parameter": "path"},
                )

            if not method:
                return create_error_response(
                    "Method parameter is required",
                    MCPError.MISSING_PARAMETER,
                    {"parameter": "method"},
                )

            method = method.upper()
            if method not in ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"]:
                return create_error_response(
                    f"Invalid HTTP method: {method}",
                    MCPError.MISSING_PARAMETER,
                    {"validMethods": ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"]},
                )

            try:
                # Prepare request
                request_headers = headers or {}
                request_params = query_params or {}
                request_body = body

                # Make the API call
                response = await self.http_client.request(
                    method=method,
                    url=path,
                    headers=request_headers,
                    params=request_params,
                    json=request_body if request_body else None,
                )

                # Parse response
                response_body = None
                try:
                    response_body = response.json()
                except Exception:
                    # Not JSON, return as text
                    response_body = response.text

                return {
                    "success": True,
                    "status": response.status_code,
                    "statusText": response.reason_phrase,
                    "headers": dict(response.headers),
                    "body": response_body,
                }

            except httpx.HTTPStatusError as e:
                return {
                    "success": False,
                    "status": e.response.status_code,
                    "statusText": e.response.reason_phrase,
                    "error": str(e),
                    "body": e.response.text,
                }
            except Exception as e:
                return create_error_response(
                    f"API call failed: {str(e)}",
                    MCPError.SPEC_LOAD_ERROR,
                    {"path": path, "method": method, "error": str(e)},
                )

    def _setup_signal_handlers(self) -> None:
        """Set up graceful shutdown on SIGINT and SIGTERM."""

        def signal_handler(signum: int, _frame: Any) -> None:
            logger.info(f"Received signal {signum}, shutting down gracefully...")
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    def run(self) -> None:
        """Start the MCP server and listen for stdio requests.

        Logs startup information and enters the main server loop.
        """
        logger.info(
            f"Starting Cakemail MCP Server v{__version__} "
            f"(OpenAPI spec: {self.config.openapi_spec_path})"
        )

        try:
            # Run the FastMCP server (blocks until shutdown)
            self.mcp.run()
        except Exception as e:
            logger.error(f"Unhandled exception in MCP server: {e}", exc_info=True)
            sys.exit(1)
