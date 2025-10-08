"""Common API client utilities for Venice API."""

from typing import Dict

from llm_venice.utils import get_venice_key


def get_auth_headers() -> Dict[str, str]:
    """
    Get authentication headers for Venice API requests.

    Returns:
        Dictionary with Authorization header.
    """
    key = get_venice_key()
    return {
        "Authorization": f"Bearer {key}",
        "Accept-Encoding": "gzip",
    }


def get_auth_headers_with_content_type() -> Dict[str, str]:
    """
    Get authentication headers with Content-Type for JSON requests.

    Returns:
        Dictionary with Authorization and Content-Type headers.
    """
    headers = get_auth_headers()
    headers["Content-Type"] = "application/json"
    return headers
