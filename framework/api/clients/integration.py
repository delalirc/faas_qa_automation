from typing import Any
from framework.api.client import ServiceClient
from requests import Response


class IntegrationClient(ServiceClient):
    """Client for integration service"""

    def __init__(self, base_url: str | None, token: str | None):
        super().__init__("integration", base_url, token)

    def get_health(self) -> Response:
        """Get health check"""
        return self.get("/health")

    def get_info(self) -> Response:
        """Get service info"""
        return self.get("/info")

    def get_version(self) -> Response:
        """Get API version"""
        return self.get("/version")

    def get_openapi(self) -> Response:
        """Get OpenAPI specification"""
        return self.get("/openapi")

    def get_integrations(self, partner_id: str) -> Response:
        """Get integrations for a partner"""
        return self.get(f"/{partner_id}/integrations")

    def post_integration_contract(
        self, partner_id: str, data: dict[str, Any]
    ) -> Response:
        """Post integration contract"""
        return self.post(f"/{partner_id}/contract", data)

    def get_merchant_contract(
        self, partner_id: str, contract_id: str, merchant_id: str
    ) -> Response:
        """Get merchant contract"""
        return self.get(
            f"/{partner_id}/contract",
            params={"contract_id": contract_id, "merchant_id": merchant_id},
        )
