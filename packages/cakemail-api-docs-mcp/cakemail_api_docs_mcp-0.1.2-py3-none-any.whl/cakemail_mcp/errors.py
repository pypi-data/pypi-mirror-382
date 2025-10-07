"""Error handling utilities for MCP tools."""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class MCPError:
    """Standard error codes for MCP tools."""

    MISSING_PARAMETER = "MISSING_PARAMETER"
    INVALID_PARAMETER = "INVALID_PARAMETER"
    ENDPOINT_NOT_FOUND = "ENDPOINT_NOT_FOUND"
    SPEC_LOAD_ERROR = "SPEC_LOAD_ERROR"


def create_error_response(
    error: str,
    code: str,
    details: dict[str, Any] | None = None,
    log_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a structured error response.

    Args:
        error: Human-readable error message
        code: Error code from MCPError
        details: Optional additional error details
        log_context: Optional context for logging

    Returns:
        Structured error response dictionary
    """
    # Log the error with full context
    log_msg = f"MCP Error [{code}]: {error}"
    if log_context:
        log_msg += f" | Context: {log_context}"
    logger.error(log_msg)

    response: dict[str, Any] = {
        "error": error,
        "code": code,
    }

    if details:
        response["details"] = details

    return response


def find_similar_paths(target: str, available_paths: list[str], limit: int = 3) -> list[str]:
    """Find similar paths using simple string matching.

    Args:
        target: The path that wasn't found
        available_paths: List of available paths
        limit: Maximum number of suggestions

    Returns:
        List of similar paths
    """
    # Simple similarity: paths that contain parts of the target or vice versa
    suggestions = []

    # Normalize paths for comparison
    target_parts = set(target.lower().strip("/").split("/"))

    for path in available_paths:
        path_parts = set(path.lower().strip("/").split("/"))

        # Calculate overlap
        overlap = len(target_parts & path_parts)

        if overlap > 0:
            suggestions.append((overlap, path))

    # Sort by overlap (descending) and take top matches
    suggestions.sort(reverse=True, key=lambda x: x[0])
    return [path for _, path in suggestions[:limit]]
