"""
Smoke tests for Offer service
Quick health checks to verify service is operational
"""

import pytest


@pytest.mark.smoke
class TestOfferSmoke:
    """Smoke tests for offer service"""

    def test_service_is_accessible(self, offer_client):
        """Verify offer service is accessible"""
        response = offer_client.get_health()
        assert response.status_code == 200

    def test_service_returns_version(self, offer_client):
        """Verify service returns version information"""
        response = offer_client.get_version()
        assert response.status_code == 200
        assert 'version' in response.json() or 'environment' in response.json()
