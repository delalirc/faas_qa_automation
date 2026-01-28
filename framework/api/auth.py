"""
Authentication helpers for FAAS QA Testing
"""

import os
import requests
from typing import Optional


def get_test_token() -> str:
    """
    Get authentication token for testing

    Returns:
        Authentication token string

    Raises:
        ValueError: If token cannot be obtained
    """
    # First, try environment variable
    token = os.getenv("AUTH_TOKEN")
    if token:
        return token

    # Try to get from Cognito (if credentials available)
    cognito_token = _get_cognito_token()
    if cognito_token:
        return cognito_token

    raise ValueError(
        "No authentication token available. "
        "Set AUTH_TOKEN environment variable or configure Cognito credentials."
    )


def _get_cognito_token() -> Optional[str]:
    """
    Get token from Cognito (if configured)

    Returns:
        Token if successful, None otherwise
    """
    cognito_url = os.getenv("COGNITO_URL")
    client_id = os.getenv("COGNITO_CLIENT_ID")
    client_secret = os.getenv("COGNITO_CLIENT_SECRET")
    scope = os.getenv("COGNITO_SCOPE")
    grant_type = "Client Credentials"
    print(cognito_url, client_id, client_secret, scope, grant_type)

    if not all([cognito_url, client_id, client_secret, scope, grant_type]):
        raise ValueError("Missing required Cognito configuration")

    try:
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        data = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": scope,
        }
        response = requests.post(str(cognito_url), headers=headers, data=data)
        return response.json()["access_token"]
    except Exception as e:
        print(f"Error getting Cognito token: {e}")
        return None


def validate_token(token: str) -> bool:
    """
    Validate that a token is properly formatted

    Args:
        token: Token to validate

    Returns:
        True if token appears valid
    """
    if not token:
        return False

    # Basic JWT format check (3 parts separated by dots)
    parts = token.split(".")
    return len(parts) == 3
