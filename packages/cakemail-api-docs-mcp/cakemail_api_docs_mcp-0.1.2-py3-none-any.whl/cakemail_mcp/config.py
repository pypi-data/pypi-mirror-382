"""Configuration management for Cakemail MCP Server."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class Config:
    """Configuration settings for the MCP server.

    Attributes:
        openapi_spec_path: Path to the OpenAPI specification file or URL
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """

    openapi_spec_path: str
    log_level: str

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        # Validate log level
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if self.log_level.upper() not in valid_levels:
            raise ValueError(
                f"Invalid LOG_LEVEL: {self.log_level}. "
                f"Must be one of {', '.join(valid_levels)}"
            )

        # Convert relative paths to absolute
        if not self.openapi_spec_path.startswith(("http://", "https://")):
            path = Path(self.openapi_spec_path)
            if not path.is_absolute():
                path = Path.cwd() / path
            self.openapi_spec_path = str(path)


def get_config() -> Config:
    """Load and return the application configuration.

    Returns:
        Config object with loaded settings

    Raises:
        ValueError: If required configuration is missing or invalid
    """
    # If user provided custom path, use it; otherwise use package-bundled file
    openapi_spec_path = os.getenv("OPENAPI_SPEC_PATH")
    if openapi_spec_path is None:
        # Default to package-bundled openapi.json
        package_dir = Path(__file__).parent
        openapi_spec_path = str(package_dir / "openapi.json")

    log_level = os.getenv("LOG_LEVEL", "INFO")

    return Config(
        openapi_spec_path=openapi_spec_path,
        log_level=log_level,
    )
