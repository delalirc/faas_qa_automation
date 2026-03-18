"""
Pytest fixtures for API testing
"""

import pytest
from .clients.offer import OfferClient
from .clients.contract import ContractClient
from .clients.s2o.orchestrator import OrchestratorClient
from .clients.s2o.doc2data import Doc2DataClient
from .client import APIClient
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
def api_client(base_url: str, auth_token: str) -> APIClient:
    """Generic API client fixture"""
    return APIClient(base_url, auth_token)


@pytest.fixture
def offer_client(base_url: str, auth_token: str) -> OfferClient:
    """Offer service client fixture"""
    return OfferClient(base_url, auth_token)


@pytest.fixture
def contract_client(base_url: str, auth_token: str) -> ContractClient:
    """Contract service client fixture"""
    return ContractClient(base_url, auth_token)


@pytest.fixture
def orchestrator_client(base_url: str, auth_token: str) -> OrchestratorClient:
    """S2O Orchestrator service client fixture"""
    return OrchestratorClient(base_url, auth_token)

@pytest.fixture
def doc2data_client(base_url: str, auth_token: str) -> Doc2DataClient:
    """S2O Doc2Data service client fixture"""
    return Doc2DataClient(base_url, auth_token)