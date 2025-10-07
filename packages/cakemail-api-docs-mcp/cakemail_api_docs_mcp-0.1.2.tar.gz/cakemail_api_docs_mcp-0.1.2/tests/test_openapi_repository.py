"""Tests for OpenAPI repository."""

import json
from unittest.mock import MagicMock, patch

import httpx
import pytest

from cakemail_mcp.openapi_repository import OpenAPIRepository


@pytest.fixture
def sample_openapi_spec():
    """Sample OpenAPI specification for testing."""
    return {
        "openapi": "3.0.0",
        "info": {"title": "Test API", "version": "1.0.0"},
        "paths": {
            "/users": {
                "get": {
                    "summary": "List users",
                    "responses": {"200": {"description": "Success"}},
                }
            }
        },
        "servers": [{"url": "https://api.example.com"}],
    }


def test_repository_initialization():
    """Test repository initialization."""
    repo = OpenAPIRepository("/path/to/spec.json")
    assert repo.spec_path == "/path/to/spec.json"
    assert not repo.is_loaded
    assert repo.spec is None


def test_load_from_file(tmp_path, sample_openapi_spec):
    """Test loading OpenAPI spec from a local file."""
    spec_file = tmp_path / "openapi.json"
    spec_file.write_text(json.dumps(sample_openapi_spec))

    repo = OpenAPIRepository(str(spec_file))
    loaded_spec = repo.load()

    assert loaded_spec == sample_openapi_spec
    assert repo.is_loaded
    assert repo.spec == sample_openapi_spec


def test_load_from_file_not_found():
    """Test loading from non-existent file raises FileNotFoundError."""
    repo = OpenAPIRepository("/nonexistent/spec.json")

    with pytest.raises(FileNotFoundError, match="OpenAPI specification not found"):
        repo.load()


def test_load_from_file_invalid_json(tmp_path):
    """Test loading invalid JSON raises ValueError."""
    spec_file = tmp_path / "invalid.json"
    spec_file.write_text("{ invalid json }")

    repo = OpenAPIRepository(str(spec_file))

    with pytest.raises(ValueError, match="Invalid JSON"):
        repo.load()


def test_load_from_url(sample_openapi_spec):
    """Test loading OpenAPI spec from a URL."""
    mock_response = MagicMock()
    mock_response.json.return_value = sample_openapi_spec

    with patch("cakemail_mcp.openapi_repository.httpx.get") as mock_get:
        mock_get.return_value = mock_response

        repo = OpenAPIRepository("https://example.com/openapi.json")
        loaded_spec = repo.load()

        assert loaded_spec == sample_openapi_spec
        assert repo.is_loaded
        mock_get.assert_called_once_with(
            "https://example.com/openapi.json",
            timeout=30.0,
            follow_redirects=True,
        )


def test_load_from_url_http_error():
    """Test loading from URL with HTTP error."""
    with patch("cakemail_mcp.openapi_repository.httpx.get") as mock_get:
        mock_get.side_effect = httpx.HTTPError("Connection failed")

        repo = OpenAPIRepository("https://example.com/openapi.json")

        with pytest.raises(httpx.HTTPError):
            repo.load()


def test_load_from_url_invalid_json():
    """Test loading URL with invalid JSON response."""
    mock_response = MagicMock()
    mock_response.json.side_effect = json.JSONDecodeError("Invalid", "", 0)

    with patch("cakemail_mcp.openapi_repository.httpx.get") as mock_get:
        mock_get.return_value = mock_response

        repo = OpenAPIRepository("https://example.com/openapi.json")

        with pytest.raises(ValueError, match="Invalid JSON"):
            repo.load()


def test_validate_spec_missing_version():
    """Test validation fails when openapi/swagger field is missing."""
    repo = OpenAPIRepository("/path/to/spec.json")

    with pytest.raises(ValueError, match="missing 'openapi' or 'swagger' field"):
        repo._validate_spec({"info": {"title": "Test"}})


def test_validate_spec_not_dict():
    """Test validation fails when spec is not a dictionary."""
    repo = OpenAPIRepository("/path/to/spec.json")

    with pytest.raises(ValueError, match="must be a dictionary"):
        repo._validate_spec([])


def test_validate_spec_swagger_version():
    """Test validation accepts Swagger 2.0 specs."""
    repo = OpenAPIRepository("/path/to/spec.json")
    spec = {"swagger": "2.0", "info": {"title": "Test"}}

    # Should not raise
    repo._validate_spec(spec)


def test_load_caches_result(tmp_path, sample_openapi_spec):
    """Test that load() caches the result and doesn't reload."""
    spec_file = tmp_path / "openapi.json"
    spec_file.write_text(json.dumps(sample_openapi_spec))

    repo = OpenAPIRepository(str(spec_file))

    # First load
    spec1 = repo.load()

    # Modify file
    spec_file.write_text(json.dumps({"openapi": "3.0.0", "info": {}}))

    # Second load should return cached version
    spec2 = repo.load()

    assert spec1 == spec2
    assert spec2 == sample_openapi_spec


def test_relative_path_conversion(tmp_path, sample_openapi_spec, monkeypatch):
    """Test that relative paths are handled correctly."""
    monkeypatch.chdir(tmp_path)

    spec_file = tmp_path / "openapi.json"
    spec_file.write_text(json.dumps(sample_openapi_spec))

    repo = OpenAPIRepository("openapi.json")
    loaded_spec = repo.load()

    assert loaded_spec == sample_openapi_spec
