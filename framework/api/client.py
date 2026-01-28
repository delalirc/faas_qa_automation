"""
Shared API Client for FAAS QA Testing

Provides a consistent interface for making API calls in tests.
"""

import requests
from typing import Dict, Optional, Any
import os


class APIClient:
    """Generic API client for testing FAAS services"""

    def __init__(self, base_url: str, token: Optional[str] = None):
        """
        Initialize API client

        Args:
            base_url: Base URL for the service (e.g., 'https://dev.api.rcdevops.co.za/offer')
            token: Optional authentication token
        """
        self.base_url = base_url.rstrip('/')
        self.token = token or os.getenv('AUTH_TOKEN')
        self.session = requests.Session()

        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        })

        if self.token:
            self.session.headers.update({
                'Authorization': f'Bearer {self.token}',
            })

    def get(self, path: str, **kwargs) -> requests.Response:
        """Make GET request"""
        url = f'{self.base_url}{path}' if not path.startswith('http') else path
        return self.session.get(url, **kwargs)

    def post(self, path: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> requests.Response:
        """Make POST request"""
        url = f'{self.base_url}{path}' if not path.startswith('http') else path
        return self.session.post(url, json=data, **kwargs)

    def put(self, path: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> requests.Response:
        """Make PUT request"""
        url = f'{self.base_url}{path}' if not path.startswith('http') else path
        return self.session.put(url, json=data, **kwargs)

    def patch(self, path: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> requests.Response:
        """Make PATCH request"""
        url = f'{self.base_url}{path}' if not path.startswith('http') else path
        return self.session.patch(url, json=data, **kwargs)

    def delete(self, path: str, **kwargs) -> requests.Response:
        """Make DELETE request"""
        url = f'{self.base_url}{path}' if not path.startswith('http') else path
        return self.session.delete(url, **kwargs)

    def set_token(self, token: str):
        """Update authentication token"""
        self.token = token
        self.session.headers.update({
            'Authorization': f'Bearer {token}',
        })


class ServiceClient(APIClient):
    """Base class for service-specific API clients"""

    def __init__(self, service_name: str, base_url: Optional[str] = None, token: Optional[str] = None):
        """
        Initialize service-specific client

        Args:
            service_name: Name of the service (e.g., 'offer', 'contract')
            base_url: Optional base URL, defaults to environment variable
            token: Optional authentication token
        """
        if not base_url:
            base_url = os.getenv('BASE_URL', 'https://dev.api.rcdevops.co.za')

        super().__init__(f'{base_url}/{service_name}', token)
        self.service_name = service_name


# Service-specific clients
class OfferClient(ServiceClient):
    """Client for offer service"""

    def __init__(self, base_url: Optional[str] = None, token: Optional[str] = None):
        super().__init__('offer', base_url, token)

    def get_offer(self, partner_id: str, merchant_id: Optional[str] = None, offer_id: Optional[str] = None, extended: Optional[bool] = None) -> requests.Response:
        """Get offer(s) by partner_id, merchant_id, or offer_id"""
        params = {}
        if merchant_id:
            params['merchantID'] = merchant_id
        if offer_id:
            params['offerID'] = offer_id
        if extended is not None:
            params['extended'] = extended
        
        return self.get(f'/{partner_id}/offer', params=params)

    def get_offers(self, partner_id: str, page: Optional[int] = None, page_size: Optional[int] = None, extended: Optional[bool] = None) -> requests.Response:
        """Get all offers for a partner"""
        params = {}
        if page:
            params['page'] = page
        if page_size:
            params['pageSize'] = page_size
        if extended is not None:
            params['extended'] = extended
        
        return self.get(f'/{partner_id}/offers', params=params)

    def validate_offer(self, partner_id: str, offer_id: str, data: Dict[str, Any]) -> requests.Response:
        """Validate an offer"""
        return self.post(f'/{partner_id}/validate?offerID={offer_id}', data)
    
    def get_offer_validation(self, partner_id: str, offer_validation_id: str) -> requests.Response:
        """Get offer validation"""
        return self.get(f'/{partner_id}/validate?offerValidationID={offer_validation_id}')

    def get_health(self) -> requests.Response:
        """Get health check"""
        return self.get('/health')

    def get_version(self) -> requests.Response:
        """Get API version"""
        return self.get('/version')


class ContractClient(ServiceClient):
    """Client for contract service"""

    def __init__(self, base_url: Optional[str] = None, token: Optional[str] = None):
        super().__init__('contract', base_url, token)

    def get_contract(self, contract_id: str) -> requests.Response:
        """Get contract by ID"""
        return self.get(f'/v1/contracts/{contract_id}')

    def get_contracts_by_merchant(self, merchant_id: str) -> requests.Response:
        """Get contracts for a merchant"""
        return self.get(f'/v1/contracts?merchant_id={merchant_id}')

    def get_contracts_by_partner(self, partner_id: str) -> requests.Response:
        """Get contracts for a partner"""
        return self.get(f'/v1/contracts?partner_id={partner_id}')

    def get_contracts_by_offer(self, offer_id: str) -> requests.Response:
        """Get contracts for an offer"""
        return self.get(f'/v1/contracts?offer_id={offer_id}')


class CollectionsClient(ServiceClient):
    """Client for collections service"""

    def __init__(self, base_url: Optional[str] = None, token: Optional[str] = None):
        super().__init__('collections', base_url, token)

    def get_collections(self, contract_id: str) -> requests.Response:
        """Get collections for a contract"""
        return self.get(f'/v1/contracts/{contract_id}/collections')


class OrchestratorClient(ServiceClient):
    """Client for S2O orchestrator"""

    def __init__(self, base_url: Optional[str] = None, token: Optional[str] = None):
        super().__init__('orchestrator', base_url, token)

    def create_session(self, data: Dict[str, Any]) -> requests.Response:
        """Create a new S2O session"""
        return self.post('/api/v1/sessions', data)

    def get_session(self, session_id: str) -> requests.Response:
        """Get session by ID"""
        return self.get(f'/api/v1/sessions/{session_id}')

    def get_session_status(self, session_id: str) -> requests.Response:
        """Get session status"""
        return self.get(f'/api/v1/sessions/{session_id}/status')

    def get_session_offer(self, session_id: str) -> requests.Response:
        """Get session offer"""
        return self.get(f'/api/v1/sessions/{session_id}/offer')

    def get_document_presigned_url(self, session_id: str, filename: str) -> requests.Response:
        """Get presigned URL for document upload"""
        return self.post(
            f'/api/v1/documents/{session_id}/presigned-url',
            {'filename': filename}
        )


class IntegrationClient(ServiceClient):
    """Client for integration service"""

    def __init__(self, base_url: Optional[str] = None, token: Optional[str] = None):
        super().__init__('integration', base_url, token)

    def get_health(self) -> requests.Response:
        """Get health check"""
        return self.get('/health')

    def get_info(self) -> requests.Response:
        """Get service info"""
        return self.get('/info')

    def get_version(self) -> requests.Response:
        """Get API version"""
        return self.get('/version')

    def get_openapi(self) -> requests.Response:
        """Get OpenAPI specification"""
        return self.get('/openapi')

    def get_integrations(self, partner_id: str) -> requests.Response:
        """Get integrations for a partner"""
        return self.get(f'/{partner_id}/integrations')

    def post_integration_contract(self, partner_id: str, data: Dict[str, Any]) -> requests.Response:
        """Post integration contract"""
        return self.post(f'/{partner_id}/contract', data)

    def get_merchant_contract(
        self, 
        partner_id: str, 
        contract_id: str, 
        merchant_id: str
    ) -> requests.Response:
        """Get merchant contract"""
        return self.get(
            f'/{partner_id}/contract',
            params={'contract_id': contract_id, 'merchant_id': merchant_id}
        )
