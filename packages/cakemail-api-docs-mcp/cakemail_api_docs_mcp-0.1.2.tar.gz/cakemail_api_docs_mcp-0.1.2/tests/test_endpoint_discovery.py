"""Tests for endpoint discovery tool."""

import json
from unittest.mock import MagicMock, patch

import pytest

from cakemail_mcp.server import CakemailMCPServer


@pytest.fixture
def endpoints_spec():
    """OpenAPI spec with multiple endpoints for testing."""
    return {
        "openapi": "3.0.0",
        "info": {"title": "Test API", "version": "1.0.0"},
        "paths": {
            "/account": {
                "get": {
                    "summary": "Get account information",
                    "operationId": "getAccount",
                    "tags": ["Account"],
                    "responses": {"200": {"description": "Success"}},
                }
            },
            "/campaigns": {
                "get": {
                    "summary": "List campaigns",
                    "operationId": "listCampaigns",
                    "tags": ["Campaigns"],
                    "responses": {"200": {"description": "Success"}},
                },
                "post": {
                    "summary": "Create campaign",
                    "operationId": "createCampaign",
                    "tags": ["Campaigns"],
                    "responses": {"201": {"description": "Created"}},
                },
            },
            "/users/{id}": {
                "get": {
                    "summary": "Get user by ID",
                    "operationId": "getUser",
                    "tags": ["Users"],
                    "responses": {"200": {"description": "Success"}},
                },
                "delete": {
                    "summary": "Delete user",
                    "operationId": "deleteUser",
                    "tags": ["Users"],
                    "responses": {"204": {"description": "No content"}},
                },
            },
        },
        "servers": [{"url": "https://api.example.com"}],
    }


def test_list_all_endpoints(monkeypatch, tmp_path, endpoints_spec):
    """Test listing all endpoints without filter."""
    spec_file = tmp_path / "openapi.json"
    spec_file.write_text(json.dumps(endpoints_spec))

    monkeypatch.setenv("OPENAPI_SPEC_PATH", str(spec_file))

    with patch("cakemail_mcp.server.FastMCP") as mock_fastmcp:
        mock_mcp_instance = MagicMock()
        mock_fastmcp.from_openapi.return_value = mock_mcp_instance

        # Capture the decorated function
        registered_tools = {}

        def tool_decorator():
            def decorator(func):
                registered_tools[func.__name__] = func
                return func

            return decorator

        mock_mcp_instance.tool = tool_decorator

        CakemailMCPServer()

        # Call the endpoint discovery function
        list_func = registered_tools.get("cakemail_list_endpoints")
        assert list_func is not None

        endpoints = list_func()

        # Should have 5 endpoints total (GET /account, GET /campaigns, POST /campaigns, GET /users/{id}, DELETE /users/{id})
        assert len(endpoints) == 5

        # Verify structure
        assert all("path" in e for e in endpoints)
        assert all("method" in e for e in endpoints)
        assert all("summary" in e for e in endpoints)
        assert all("tags" in e for e in endpoints)
        assert all("operationId" in e for e in endpoints)

        # Verify sorting (by path, then method)
        paths = [e["path"] for e in endpoints]
        assert paths == ["/account", "/campaigns", "/campaigns", "/users/{id}", "/users/{id}"]

        # Verify methods for /campaigns are sorted
        campaign_endpoints = [e for e in endpoints if e["path"] == "/campaigns"]
        assert campaign_endpoints[0]["method"] == "GET"
        assert campaign_endpoints[1]["method"] == "POST"


def test_list_endpoints_with_tag_filter(monkeypatch, tmp_path, endpoints_spec):
    """Test filtering endpoints by tag."""
    spec_file = tmp_path / "openapi.json"
    spec_file.write_text(json.dumps(endpoints_spec))

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

        list_func = registered_tools.get("cakemail_list_endpoints")

        # Filter by "Campaigns" tag
        endpoints = list_func(tag="Campaigns")

        assert len(endpoints) == 2
        assert all(e["path"] == "/campaigns" for e in endpoints)
        assert all("Campaigns" in e["tags"] for e in endpoints)

        # Filter by "Users" tag
        endpoints = list_func(tag="Users")

        assert len(endpoints) == 2
        assert all(e["path"] == "/users/{id}" for e in endpoints)
        assert all("Users" in e["tags"] for e in endpoints)


def test_list_endpoints_no_matching_tag(monkeypatch, tmp_path, endpoints_spec):
    """Test that non-matching tag returns empty array."""
    spec_file = tmp_path / "openapi.json"
    spec_file.write_text(json.dumps(endpoints_spec))

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

        list_func = registered_tools.get("cakemail_list_endpoints")

        # Filter by non-existent tag
        endpoints = list_func(tag="NonExistent")

        assert endpoints == []


def test_list_endpoints_empty_spec(monkeypatch, tmp_path):
    """Test listing endpoints with empty paths."""
    empty_spec = {
        "openapi": "3.0.0",
        "info": {"title": "Empty API", "version": "1.0.0"},
        "paths": {},
    }

    spec_file = tmp_path / "openapi.json"
    spec_file.write_text(json.dumps(empty_spec))

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

        list_func = registered_tools.get("cakemail_list_endpoints")
        endpoints = list_func()

        assert endpoints == []


def test_endpoint_fields(monkeypatch, tmp_path, endpoints_spec):
    """Test that all required fields are present in endpoint objects."""
    spec_file = tmp_path / "openapi.json"
    spec_file.write_text(json.dumps(endpoints_spec))

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

        list_func = registered_tools.get("cakemail_list_endpoints")
        endpoints = list_func()

        # Check first endpoint structure
        endpoint = endpoints[0]

        assert endpoint["path"] == "/account"
        assert endpoint["method"] == "GET"
        assert endpoint["summary"] == "Get account information"
        assert endpoint["tags"] == ["Account"]
        assert endpoint["operationId"] == "getAccount"
