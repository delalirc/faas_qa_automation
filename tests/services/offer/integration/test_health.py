"""
Integration tests for Offer service API endpoints
"""

from framework.api.clients.offer import OfferClient
import pytest


@pytest.mark.integration
@pytest.mark.health
@pytest.mark.offer
class TestOfferHealth:
    """Integration tests for offer API endpoints"""

    def test_health_check(self, offer_client: OfferClient):
        """Test offer service health endpoint"""
        response = offer_client.get_health()
        assert response.status_code == 200
        assert response.json()

    def test_version_endpoint(self, offer_client: OfferClient):
        """Test offer service version endpoint"""
        response = offer_client.get_version()
        assert response.status_code == 200
        assert response.json()