from typing import Any
from framework.api.client import ServiceClient
from requests import Response


class OfferClient(ServiceClient):
    """Client for offer service"""

    def __init__(self, base_url: str | None, token: str | None):
        super().__init__("offer", base_url, token)

    def get_offer(
        self,
        partner_id: str,
        merchant_id: str | None = None,
        offer_id: str | None = None,
        extended: bool | None = None,
    ) -> Response:
        """Get offer(s) by partner_id, merchant_id, or offer_id"""
        params: dict[str, Any] = {}
        if merchant_id:
            params["merchantID"] = merchant_id
        if offer_id:
            params["offerID"] = offer_id
        if extended is not None:
            params["extended"] = extended

        return self.get(f"/{partner_id}/offer", params=params)

    def get_offers(
        self,
        partner_id: str,
        page: int | None = None,
        page_size: int | None = None,
        extended: bool | None = None,
    ) -> Response:
        """Get all offers for a partner"""
        params: dict[str, Any] = {}
        if page:
            params["page"] = page
        if page_size:
            params["pageSize"] = page_size
        if extended is not None:
            params["extended"] = extended

        return self.get(f"/{partner_id}/offers", params=params)

    def validate_offer(
        self, partner_id: str, offer_id: str, data: dict[str, Any]
    ) -> Response:
        """Validate an offer"""
        return self.post(f"/{partner_id}/validate?offerID={offer_id}", data)

    def get_offer_validation(
        self, partner_id: str, offer_validation_id: str
    ) -> Response:
        """Get offer validation"""
        return self.get(
            f"/{partner_id}/validate?offerValidationID={offer_validation_id}"
        )

    def get_health(self) -> Response:
        """Get health check"""
        return self.get("/health")

    def get_version(self) -> Response:
        """Get API version"""
        return self.get("/version")
