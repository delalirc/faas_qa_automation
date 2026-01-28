"""
Partner API Client for FAAS QA Testing

Handles partner configuration retrieval and partner-specific API interactions.
"""

import requests
from typing import Dict, Optional, Any
import os
from .client import ServiceClient


class PartnerClient(ServiceClient):
    """Client for partner service"""

    def __init__(self, base_url: Optional[str] = None, token: Optional[str] = None):
        super().__init__('partner', base_url, token)

    def get_partner_config(self, partner_id: str) -> requests.Response:
        """Get partner configuration including offer URL/cloudfront domain"""
        return self.get(f'/{partner_id}/config')

    def get_partner_info(self, partner_id: str) -> requests.Response:
        """Get partner information"""
        return self.get(f'/{partner_id}')

    def get_partner_integrations(self, partner_id: str) -> requests.Response:
        """Get partner integrations"""
        return self.get(f'/{partner_id}/integrations')


class CRMClient(ServiceClient):
    """Client for CRM service (Salesforce integration)"""

    def __init__(self, base_url: Optional[str] = None, token: Optional[str] = None):
        super().__init__('crm', base_url, token)

    def get_contract(self, contract_id: str) -> requests.Response:
        """Get contract from CRM"""
        return self.get(f'/contracts/{contract_id}')

    def query_salesforce(self, query: str) -> requests.Response:
        """Query Salesforce directly"""
        return self.get(f'/salesforce/query', params={'q': query})

    def verify_contract_submission(self, contract_id: str) -> requests.Response:
        """Verify contract was submitted to CRM"""
        return self.get(f'/contracts/{contract_id}/verify')


class FinanceClient(ServiceClient):
    """Client for finance service (Sage integration)"""

    def __init__(self, base_url: Optional[str] = None, token: Optional[str] = None):
        super().__init__('finance', base_url, token)

    def get_contract_sage(self, contract_id: str) -> requests.Response:
        """Get contract Sage integration data"""
        return self.get(f'/contracts/{contract_id}/sage')

    def sync_contract_to_sage(self, contract_id: str) -> requests.Response:
        """Sync contract to Sage"""
        return self.post(f'/contracts/{contract_id}/sync-sage')
