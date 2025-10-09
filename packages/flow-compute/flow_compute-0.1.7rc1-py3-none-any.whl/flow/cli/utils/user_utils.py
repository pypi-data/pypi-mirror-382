"""User-related utility functions for CLI operations.

Provides helpers for fetching and sanitizing user information from the platform.
"""

from __future__ import annotations

import logging
import re
from typing import Any

from flow.errors import FlowError

logger = logging.getLogger(__name__)


class UserInfoError(FlowError):
    """Raised when unable to fetch or process user information."""

    pass


def get_sanitized_username_from_api(api_client: Any) -> str:
    """Get current user's name from API client, sanitized for use in identifiers.

    Args:
        api_client: API client with get_me() method (e.g., MithrilApiClient)

    Returns:
        Sanitized username (lowercase, alphanumeric and hyphens only).

    Raises:
        UserInfoError: If unable to fetch username from API or API client is invalid
    """
    if not hasattr(api_client, "get_me"):
        raise UserInfoError("API client does not have get_me() method")

    try:
        me_response = api_client.get_me()
    except Exception as e:
        raise UserInfoError(f"Failed to call get_me() on API client: {e}") from e

    me_data = me_response.get("data", me_response) if isinstance(me_response, dict) else me_response

    if not isinstance(me_data, dict):
        raise UserInfoError(f"Expected dict from get_me(), got {type(me_data).__name__}")

    username = me_data.get("user_name") or me_data.get("username")
    if not username:
        raise UserInfoError("API response did not contain user_name or username field")

    # Sanitize username for identifier use (alphanumeric and hyphens only)
    sanitized = re.sub(r"[^a-zA-Z0-9-]", "-", str(username).lower())
    # Remove multiple consecutive hyphens and trim
    sanitized = re.sub(r"-+", "-", sanitized).strip("-")

    if not sanitized:
        raise UserInfoError(f"Username '{username}' became empty after sanitization")

    return sanitized


def get_sanitized_username(flow_client: Any) -> str:
    """Get current user's name from Flow client, sanitized for use in identifiers.

    Args:
        flow_client: Flow SDK client instance with access to provider/API

    Returns:
        Sanitized username (lowercase, alphanumeric and hyphens only).

    Raises:
        UserInfoError: If unable to fetch username from Flow client
    """
    provider = getattr(flow_client, "provider", None)
    if provider is None:
        raise UserInfoError("Flow client does not have a provider")

    api_client = getattr(provider, "_api_client", None)
    if api_client is None:
        raise UserInfoError("Provider does not have an _api_client")

    return get_sanitized_username_from_api(api_client)
