"""
Shared pytest configuration and fixtures for FAAS QA tests
"""

import pytest
import os
from framework.api.auth import get_test_token


@pytest.fixture(scope="session")
def base_url() -> str:
    """Base URL for API testing"""
    return os.getenv("BASE_URL", "https://uat.api.rcdevops.co.za")


@pytest.fixture(scope="session")
def auth_token() -> str:
    """Authentication token for API testing"""
    try:
        return str(get_test_token())
    except ValueError as e:
        print(f"No authentication token available: {e}")
        pytest.skip("No authentication token available")


def get_test_partner_ids() -> list[str]:
    """Get list of test partner IDs for parameterization"""
    return list(get_test_partners().values())


def get_test_partners() -> dict[str, str]:
    """Get test partners and their IDs as a regular function"""
    return {
        "atm": "5e9d531c-791b-463a-aeea-233eb7d04a9b",
        "tabbs": "960f7a46-180d-4615-a87a-31e0dbeb1b64",
        "netcash": "30f50c8b-7b88-49c1-8b61-ca93b8f6ea7e",
        "fnb": "82c1c0a8-a203-4a73-8750-cf2dfe21835d",
        "kazang": "1d51ef18-0d07-403b-a499-3fd2296532ef",
        "korridor": "449703d7-913d-4798-aa28-05adfe7e1ef5",
        "takealot": "e01c1138-d4c3-4b5d-8ca2-ea1034b91f9e",
        "ikhokha": "675911fa-95ad-4fdd-adea-802240c79887",
        "payfast": "c7b09cd3-a52f-468b-93a7-3c438036a50c",
    }


@pytest.fixture
def test_partners() -> dict[str, str]:
    """Test partners and their IDs (fixture version for use in tests)"""
    return get_test_partners()
