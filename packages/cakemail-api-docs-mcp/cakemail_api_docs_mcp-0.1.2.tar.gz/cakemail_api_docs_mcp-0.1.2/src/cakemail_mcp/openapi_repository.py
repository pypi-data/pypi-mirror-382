"""OpenAPI specification loading and management."""

import json
import logging
from pathlib import Path
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class OpenAPIRepository:
    """Repository for loading and managing OpenAPI specifications.

    Supports loading from local files and remote URLs.
    """

    def __init__(self, spec_path: str) -> None:
        """Initialize the repository.

        Args:
            spec_path: Path to local file or URL to OpenAPI specification
        """
        self.spec_path = spec_path
        self._spec: dict[str, Any] | None = None

    def load(self) -> dict[str, Any]:
        """Load the OpenAPI specification.

        Returns:
            Parsed OpenAPI specification as a dictionary

        Raises:
            FileNotFoundError: If local file doesn't exist
            ValueError: If spec cannot be parsed or is invalid
            httpx.HTTPError: If URL cannot be fetched
        """
        if self._spec is not None:
            return self._spec

        if self.spec_path.startswith(("http://", "https://")):
            self._spec = self._load_from_url(self.spec_path)
        else:
            self._spec = self._load_from_file(self.spec_path)

        self._validate_spec(self._spec)
        return self._spec

    def _load_from_file(self, file_path: str) -> dict[str, Any]:
        """Load OpenAPI spec from a local file.

        Args:
            file_path: Path to the local file

        Returns:
            Parsed OpenAPI specification

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file cannot be parsed as JSON
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"OpenAPI specification not found at: {file_path}")

        logger.info(f"Loading OpenAPI spec from file: {file_path}")

        try:
            with path.open("r", encoding="utf-8") as f:
                spec: dict[str, Any] = json.load(f)
            logger.info(
                f"Successfully loaded OpenAPI spec from {file_path} "
                f"(version: {spec.get('openapi', 'unknown')})"
            )
            return spec
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in OpenAPI spec file: {e}") from e

    def _load_from_url(self, url: str) -> dict[str, Any]:
        """Load OpenAPI spec from a URL.

        Args:
            url: URL to fetch the spec from

        Returns:
            Parsed OpenAPI specification

        Raises:
            httpx.HTTPError: If URL cannot be fetched
            ValueError: If response cannot be parsed as JSON
        """
        logger.info(f"Fetching OpenAPI spec from URL: {url}")

        try:
            response = httpx.get(url, timeout=30.0, follow_redirects=True)
            response.raise_for_status()
            spec: dict[str, Any] = response.json()
            logger.info(
                f"Successfully fetched OpenAPI spec from {url} "
                f"(version: {spec.get('openapi', 'unknown')})"
            )
            return spec
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch OpenAPI spec from {url}: {e}")
            raise
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in OpenAPI spec response: {e}") from e

    def _validate_spec(self, spec: dict[str, Any]) -> None:
        """Validate the loaded OpenAPI specification.

        Args:
            spec: The OpenAPI specification to validate

        Raises:
            ValueError: If spec is invalid
        """
        # Basic validation - check for required fields
        if not isinstance(spec, dict):
            raise ValueError("OpenAPI spec must be a dictionary")

        if "openapi" not in spec and "swagger" not in spec:
            raise ValueError(
                "Invalid OpenAPI spec: missing 'openapi' or 'swagger' field"
            )

        version = spec.get("openapi") or spec.get("swagger")
        logger.debug(f"Validated OpenAPI spec version: {version}")

    @property
    def spec(self) -> dict[str, Any] | None:
        """Get the loaded specification without triggering a load.

        Returns:
            The loaded spec or None if not yet loaded
        """
        return self._spec

    @property
    def is_loaded(self) -> bool:
        """Check if the spec has been loaded.

        Returns:
            True if spec is loaded, False otherwise
        """
        return self._spec is not None
