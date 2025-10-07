"""Tests for error handling in MCP tools."""

import json
from unittest.mock import MagicMock, patch

import pytest

from cakemail_mcp.errors import MCPError, create_error_response, find_similar_paths
from cakemail_mcp.server import CakemailMCPServer


@pytest.fixture
def sample_spec():
    """Sample OpenAPI spec for error testing."""
    return {
        "openapi": "3.0.0",
        "info": {"title": "Test API", "version": "1.0.0"},
        "paths": {
            "/users/{id}": {
                "get": {
                    "summary": "Get user",
                    "operationId": "getUser",
                    "tags": ["Users"],
                    "responses": {"200": {"description": "Success"}},
                }
            },
            "/campaigns": {
                "get": {
                    "summary": "List campaigns",
                    "operationId": "listCampaigns",
                    "tags": ["Campaigns"],
                    "responses": {"200": {"description": "Success"}},
                }
            },
        },
        "servers": [{"url": "https://api.example.com"}],
        "components": {
            "securitySchemes": {
                "oauth2": {
                    "type": "oauth2",
                    "description": "OAuth2 authentication",
                    "flows": {
                        "password": {
                            "tokenUrl": "https://api.example.com/token",
                            "scopes": {"read": "Read access"},
                        }
                    },
                }
            }
        },
    }


def test_create_error_response():
    """Test error response creation."""
    error = create_error_response(
        "Test error",
        MCPError.MISSING_PARAMETER,
        {"param": "test"},
        {"context": "testing"},
    )

    assert error["error"] == "Test error"
    assert error["code"] == MCPError.MISSING_PARAMETER
    assert error["details"]["param"] == "test"


def test_create_error_response_no_details():
    """Test error response without details."""
    error = create_error_response("Simple error", MCPError.SPEC_LOAD_ERROR)

    assert error["error"] == "Simple error"
    assert error["code"] == MCPError.SPEC_LOAD_ERROR
    assert "details" not in error


def test_find_similar_paths():
    """Test path similarity matching."""
    available = ["/users/{id}", "/users/{id}/posts", "/campaigns", "/accounts"]

    # Test exact partial match
    suggestions = find_similar_paths("/users/123", available)
    assert "/users/{id}" in suggestions

    # Test no match
    suggestions = find_similar_paths("/nonexistent/path", available)
    assert len(suggestions) == 0

    # Test multiple matches
    suggestions = find_similar_paths("/users/123/posts/456", available)
    assert "/users/{id}/posts" in suggestions


def test_find_similar_paths_with_limit():
    """Test path similarity with result limit."""
    available = ["/a", "/a/b", "/a/b/c", "/a/b/c/d"]

    suggestions = find_similar_paths("/a/b/c/d/e", available, limit=2)
    assert len(suggestions) <= 2


def test_endpoint_detail_missing_path(monkeypatch, tmp_path, sample_spec):
    """Test get_endpoint with missing path parameter."""
    spec_file = tmp_path / "openapi.json"
    spec_file.write_text(json.dumps(sample_spec))

    monkeypatch.setenv("OPENAPI_SPEC_PATH", str(spec_file))

    with patch("cakemail_mcp.server.FastMCP") as mock_fastmcp:
        mock_mcp_instance = MagicMock()
        mock_fastmcp.from_openapi.return_value = mock_mcp_instance

        registered_tools = {}

        def tool_decorator():
            def decorator(func):
                registered_tools[func.__name__] = func
                return func

            return decorator

        mock_mcp_instance.tool = tool_decorator

        CakemailMCPServer()

        get_func = registered_tools.get("cakemail_get_endpoint")
        result = get_func(path="", method="GET")

        assert "error" in result
        assert result["code"] == MCPError.MISSING_PARAMETER
        assert result["details"]["parameter"] == "path"


def test_endpoint_detail_missing_method(monkeypatch, tmp_path, sample_spec):
    """Test get_endpoint with missing method parameter."""
    spec_file = tmp_path / "openapi.json"
    spec_file.write_text(json.dumps(sample_spec))

    monkeypatch.setenv("OPENAPI_SPEC_PATH", str(spec_file))

    with patch("cakemail_mcp.server.FastMCP") as mock_fastmcp:
        mock_mcp_instance = MagicMock()
        mock_fastmcp.from_openapi.return_value = mock_mcp_instance

        registered_tools = {}

        def tool_decorator():
            def decorator(func):
                registered_tools[func.__name__] = func
                return func

            return decorator

        mock_mcp_instance.tool = tool_decorator

        CakemailMCPServer()

        get_func = registered_tools.get("cakemail_get_endpoint")
        result = get_func(path="/users/{id}", method="")

        assert "error" in result
        assert result["code"] == MCPError.MISSING_PARAMETER
        assert result["details"]["parameter"] == "method"


def test_endpoint_detail_path_not_found(monkeypatch, tmp_path, sample_spec):
    """Test get_endpoint with non-existent path."""
    spec_file = tmp_path / "openapi.json"
    spec_file.write_text(json.dumps(sample_spec))

    monkeypatch.setenv("OPENAPI_SPEC_PATH", str(spec_file))

    with patch("cakemail_mcp.server.FastMCP") as mock_fastmcp:
        mock_mcp_instance = MagicMock()
        mock_fastmcp.from_openapi.return_value = mock_mcp_instance

        registered_tools = {}

        def tool_decorator():
            def decorator(func):
                registered_tools[func.__name__] = func
                return func

            return decorator

        mock_mcp_instance.tool = tool_decorator

        CakemailMCPServer()

        get_func = registered_tools.get("cakemail_get_endpoint")
        result = get_func(path="/nonexistent", method="GET")

        assert "error" in result
        assert result["code"] == MCPError.ENDPOINT_NOT_FOUND
        assert "suggestions" in result["details"]


def test_endpoint_detail_method_not_found(monkeypatch, tmp_path, sample_spec):
    """Test get_endpoint with invalid method for path."""
    spec_file = tmp_path / "openapi.json"
    spec_file.write_text(json.dumps(sample_spec))

    monkeypatch.setenv("OPENAPI_SPEC_PATH", str(spec_file))

    with patch("cakemail_mcp.server.FastMCP") as mock_fastmcp:
        mock_mcp_instance = MagicMock()
        mock_fastmcp.from_openapi.return_value = mock_mcp_instance

        registered_tools = {}

        def tool_decorator():
            def decorator(func):
                registered_tools[func.__name__] = func
                return func

            return decorator

        mock_mcp_instance.tool = tool_decorator

        CakemailMCPServer()

        get_func = registered_tools.get("cakemail_get_endpoint")
        result = get_func(path="/users/{id}", method="POST")

        assert "error" in result
        assert result["code"] == MCPError.ENDPOINT_NOT_FOUND
        assert "availableMethods" in result["details"]
        assert "GET" in result["details"]["availableMethods"]


def test_list_endpoints_spec_not_loaded(monkeypatch, tmp_path):
    """Test list_endpoints when spec cannot be loaded."""
    spec_file = tmp_path / "openapi.json"
    spec_file.write_text(json.dumps({"openapi": "3.0.0"}))

    monkeypatch.setenv("OPENAPI_SPEC_PATH", str(spec_file))

    with patch("cakemail_mcp.server.FastMCP") as mock_fastmcp:
        mock_mcp_instance = MagicMock()
        mock_fastmcp.from_openapi.return_value = mock_mcp_instance

        registered_tools = {}

        def tool_decorator():
            def decorator(func):
                registered_tools[func.__name__] = func
                return func

            return decorator

        mock_mcp_instance.tool = tool_decorator

        server = CakemailMCPServer()
        # Simulate spec not loaded
        server.openapi_repo._spec = None

        list_func = registered_tools.get("cakemail_list_endpoints")
        result = list_func()

        assert "error" in result
        assert result["code"] == MCPError.SPEC_LOAD_ERROR


def test_get_auth_spec_not_loaded(monkeypatch, tmp_path):
    """Test get_auth when spec cannot be loaded."""
    spec_file = tmp_path / "openapi.json"
    spec_file.write_text(json.dumps({"openapi": "3.0.0"}))

    monkeypatch.setenv("OPENAPI_SPEC_PATH", str(spec_file))

    with patch("cakemail_mcp.server.FastMCP") as mock_fastmcp:
        mock_mcp_instance = MagicMock()
        mock_fastmcp.from_openapi.return_value = mock_mcp_instance

        registered_tools = {}

        def tool_decorator():
            def decorator(func):
                registered_tools[func.__name__] = func
                return func

            return decorator

        mock_mcp_instance.tool = tool_decorator

        server = CakemailMCPServer()
        # Simulate spec not loaded
        server.openapi_repo._spec = None

        get_auth_func = registered_tools.get("cakemail_get_auth")
        result = get_auth_func()

        assert "error" in result
        assert result["code"] == MCPError.SPEC_LOAD_ERROR


def test_get_endpoint_spec_not_loaded(monkeypatch, tmp_path):
    """Test get_endpoint when spec cannot be loaded."""
    spec_file = tmp_path / "openapi.json"
    spec_file.write_text(json.dumps({"openapi": "3.0.0"}))

    monkeypatch.setenv("OPENAPI_SPEC_PATH", str(spec_file))

    with patch("cakemail_mcp.server.FastMCP") as mock_fastmcp:
        mock_mcp_instance = MagicMock()
        mock_fastmcp.from_openapi.return_value = mock_mcp_instance

        registered_tools = {}

        def tool_decorator():
            def decorator(func):
                registered_tools[func.__name__] = func
                return func

            return decorator

        mock_mcp_instance.tool = tool_decorator

        server = CakemailMCPServer()
        # Simulate spec not loaded
        server.openapi_repo._spec = None

        get_func = registered_tools.get("cakemail_get_endpoint")
        result = get_func(path="/users/{id}", method="GET")

        assert "error" in result
        assert result["code"] == MCPError.SPEC_LOAD_ERROR
