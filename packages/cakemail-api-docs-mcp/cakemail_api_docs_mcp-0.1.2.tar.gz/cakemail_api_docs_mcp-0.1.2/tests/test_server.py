"""Tests for MCP server initialization."""

import signal
from unittest.mock import MagicMock, patch

import pytest

from cakemail_mcp.server import CakemailMCPServer


@pytest.fixture
def sample_openapi_spec():
    """Sample OpenAPI specification for testing."""
    return {
        "openapi": "3.0.0",
        "info": {"title": "Test API", "version": "1.0.0"},
        "paths": {"/test": {"get": {"responses": {"200": {}}}}},
        "servers": [{"url": "https://api.example.com"}],
    }


def test_server_initialization(monkeypatch, tmp_path, sample_openapi_spec):
    """Test that server initializes correctly."""
    import json

    spec_file = tmp_path / "openapi.json"
    spec_file.write_text(json.dumps(sample_openapi_spec))

    monkeypatch.setenv("OPENAPI_SPEC_PATH", str(spec_file))
    monkeypatch.setenv("LOG_LEVEL", "INFO")

    with patch("cakemail_mcp.server.FastMCP") as mock_fastmcp:
        mock_fastmcp.from_openapi.return_value = MagicMock()

        server = CakemailMCPServer()

        assert server.config is not None
        assert server.mcp is not None
        assert server.openapi_repo is not None
        mock_fastmcp.from_openapi.assert_called_once()


def test_server_signal_handlers(monkeypatch, tmp_path, sample_openapi_spec):
    """Test that signal handlers are set up correctly."""
    import json

    spec_file = tmp_path / "openapi.json"
    spec_file.write_text(json.dumps(sample_openapi_spec))

    monkeypatch.setenv("OPENAPI_SPEC_PATH", str(spec_file))

    with (
        patch("cakemail_mcp.server.FastMCP") as mock_fastmcp,
        patch("signal.signal") as mock_signal,
    ):
        mock_fastmcp.from_openapi.return_value = MagicMock()

        _ = CakemailMCPServer()

        # Verify SIGINT and SIGTERM handlers were registered
        calls = mock_signal.call_args_list
        signal_numbers = [call[0][0] for call in calls]

        assert signal.SIGINT in signal_numbers
        assert signal.SIGTERM in signal_numbers


def test_server_run(monkeypatch, tmp_path, sample_openapi_spec):
    """Test that server run method calls FastMCP.run()."""
    import json

    spec_file = tmp_path / "openapi.json"
    spec_file.write_text(json.dumps(sample_openapi_spec))

    monkeypatch.setenv("OPENAPI_SPEC_PATH", str(spec_file))

    with patch("cakemail_mcp.server.FastMCP") as mock_fastmcp:
        mock_mcp_instance = MagicMock()
        mock_fastmcp.from_openapi.return_value = mock_mcp_instance

        server = CakemailMCPServer()
        server.run()

        mock_mcp_instance.run.assert_called_once()


def test_server_run_exception_handling(monkeypatch, tmp_path, sample_openapi_spec):
    """Test that server handles exceptions during run."""
    import json

    spec_file = tmp_path / "openapi.json"
    spec_file.write_text(json.dumps(sample_openapi_spec))

    monkeypatch.setenv("OPENAPI_SPEC_PATH", str(spec_file))

    with patch("cakemail_mcp.server.FastMCP") as mock_fastmcp:
        mock_mcp_instance = MagicMock()
        mock_mcp_instance.run.side_effect = RuntimeError("Test error")
        mock_fastmcp.from_openapi.return_value = mock_mcp_instance

        server = CakemailMCPServer()

        with pytest.raises(SystemExit) as exc_info:
            server.run()

        assert exc_info.value.code == 1


def test_server_config_loading(monkeypatch, tmp_path, sample_openapi_spec):
    """Test that server loads configuration correctly."""
    import json

    spec_file = tmp_path / "custom_spec.json"
    spec_file.write_text(json.dumps(sample_openapi_spec))

    monkeypatch.setenv("OPENAPI_SPEC_PATH", str(spec_file))
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")

    with patch("cakemail_mcp.server.FastMCP") as mock_fastmcp:
        mock_fastmcp.from_openapi.return_value = MagicMock()

        server = CakemailMCPServer()

        assert server.config.openapi_spec_path == str(spec_file)
        assert server.config.log_level == "DEBUG"


def test_server_base_url_extraction(monkeypatch, tmp_path):
    """Test that server extracts base URL from OpenAPI spec."""
    import json

    spec_with_server = {
        "openapi": "3.0.0",
        "info": {"title": "Test API", "version": "1.0.0"},
        "paths": {},
        "servers": [{"url": "https://custom.api.com"}],
    }

    spec_file = tmp_path / "openapi.json"
    spec_file.write_text(json.dumps(spec_with_server))

    monkeypatch.setenv("OPENAPI_SPEC_PATH", str(spec_file))

    with (
        patch("cakemail_mcp.server.FastMCP") as mock_fastmcp,
        patch("cakemail_mcp.server.httpx.AsyncClient") as mock_client,
    ):
        mock_fastmcp.from_openapi.return_value = MagicMock()

        _ = CakemailMCPServer()

        # Verify AsyncClient was created with the correct base URL
        mock_client.assert_called_once()
        assert mock_client.call_args[1]["base_url"] == "https://custom.api.com"


def test_health_check_tool_registration(monkeypatch, tmp_path, sample_openapi_spec):
    """Test that custom tools are registered."""
    import json

    spec_file = tmp_path / "openapi.json"
    spec_file.write_text(json.dumps(sample_openapi_spec))

    monkeypatch.setenv("OPENAPI_SPEC_PATH", str(spec_file))

    with patch("cakemail_mcp.server.FastMCP") as mock_fastmcp:
        mock_mcp_instance = MagicMock()
        mock_fastmcp.from_openapi.return_value = mock_mcp_instance

        _ = CakemailMCPServer()

        # Verify that mcp.tool() was called to register custom tools
        # (health check + endpoint discovery + endpoint detail + auth)
        assert mock_mcp_instance.tool.call_count == 4
