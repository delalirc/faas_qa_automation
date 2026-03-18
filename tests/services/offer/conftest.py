"""
Shared pytest configuration and fixtures for FAAS QA tests
"""

import pytest
from framework.api.clients.offer import OfferClient
from framework.api.clients.integration import IntegrationClient


@pytest.fixture
def offer_client(base_url: str, auth_token: str | None) -> OfferClient:
    """Offer service client fixture"""
    return OfferClient(base_url=base_url, token=auth_token)


@pytest.fixture
def integration_client(base_url: str, auth_token: str | None) -> IntegrationClient:
    """Integration service client fixture"""
    return IntegrationClient(base_url=base_url, token=auth_token)
