from framework.api.client import ServiceClient
from requests import Response


class ContractClient(ServiceClient):
    """Client for contract service"""

    def __init__(self, base_url: str | None, token: str | None):
        super().__init__("contract", base_url, token)

    def get_contract(self, contract_id: str) -> Response:
        """Get contract by ID"""
        return self.get(f"/v1/contracts/{contract_id}")

    def get_contracts_by_merchant(self, merchant_id: str) -> Response:
        """Get contracts for a merchant"""
        return self.get(f"/v1/contracts?merchant_id={merchant_id}")

    def get_contracts_by_partner(self, partner_id: str) -> Response:
        """Get contracts for a partner"""
        return self.get(f"/v1/contracts?partner_id={partner_id}")

    def get_contracts_by_offer(self, offer_id: str) -> Response:
        """Get contracts for an offer"""
        return self.get(f"/v1/contracts?offer_id={offer_id}")
