"""
Pytest fixtures for API testing
"""

import pytest
from .client import OfferClient, ContractClient, APIClient
from .auth import get_test_token
import os


@pytest.fixture(scope='session')
def base_url():
    """Base URL for API testing"""
    return os.getenv('BASE_URL', 'https://dev.api.rcdevops.co.za')


@pytest.fixture(scope='session')
def auth_token():
    """Authentication token for API testing"""
    return get_test_token()


@pytest.fixture
def api_client(base_url, auth_token):
    """Generic API client fixture"""
    return APIClient(base_url, auth_token)


@pytest.fixture
def offer_client(base_url, auth_token):
    """Offer service client fixture"""
    return OfferClient(base_url, auth_token)


@pytest.fixture
def contract_client(base_url, auth_token):
    """Contract service client fixture"""
    return ContractClient(base_url, auth_token)
