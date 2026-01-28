"""
Smoke tests for Integration service
Quick health checks to verify service is operational
"""

import pytest


@pytest.mark.smoke
class TestIntegrationSmoke:
    """Smoke tests for integration service"""

    def test_service_is_accessible(self, integration_client):
        """Verify integration service is accessible"""
        response = integration_client.get('/health')
        assert response.status_code == 200

    def test_service_returns_info(self, integration_client):
        """Verify service returns info"""
        response = integration_client.get('/info')
        assert response.status_code == 200
        result = response.json()
        assert 'service' in result or 'version' in result

    def test_service_returns_version(self, integration_client):
        """Verify service returns version information"""
        response = integration_client.get('/version')
        assert response.status_code == 200
        assert 'version' in response.json() or 'environment' in response.json()
