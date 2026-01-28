"""
Smoke tests for all FAAS services
Quick health checks to verify services are operational
"""

import pytest
from framework.api.client import APIClient
from framework.api.auth import get_test_token


@pytest.mark.smoke
class TestAllServicesHealth:
    """Smoke tests for all services"""
    
    SERVICES = [
        'offer', 'integration', 'contract', 'collections', 'finance',
        'settlement', 'partner', 'merchant', 'crm',
        'delivery', 'sendmail', 'document', 'orchestrator',
    ]
    
    @pytest.fixture
    def base_url(self):
        import os
        return os.getenv('BASE_URL', 'https://dev.api.rcdevops.co.za')
    
    @pytest.fixture
    def token(self):
        try:
            return get_test_token()
        except ValueError:
            pytest.skip("No authentication token available")
    
    @pytest.mark.parametrize('service', SERVICES)
    def test_service_health(self, service, base_url, token):
        """Test that each service is healthy"""
        client = APIClient(f'{base_url}/{service}', token)
        
        # Try health endpoint
        response = client.get('/health')
        
        assert response.status_code == 200, f"Service {service} health check failed"
        result = response.json()
        assert result.get('status') in ['healthy', 'ok', 'active'] or 'status' in result
