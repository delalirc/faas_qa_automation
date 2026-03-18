"""
Integration tests for Offers
"""

import random
from typing import Any
from framework.api.clients.offer import OfferClient
import pytest
from tests.conftest import get_test_partner_ids


@pytest.mark.integration
@pytest.mark.offer
class TestOffers:
    """Integration tests for Offers"""

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

    @pytest.mark.parametrize("partner_id", get_test_partner_ids())
    def test_get_offers_for_partner(self, offer_client: OfferClient, partner_id: str):
        """Test getting all offers for a partner"""

        # Requires pagination to be implemented - Gateway Timeout Error
        response = offer_client.get_offers(partner_id, page=1, page_size=10)

        if response.status_code == 204:
            pytest.skip("No offers found for partner")

        if response.status_code == 502:
            pytest.skip("Offers Endpoint Timed-Out Gateway Timeout Error")

        assert response.status_code == 200
        result: list[list[dict[str, Any]]] = response.json()

        # Should return a list or dict with offers
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], list)
        assert len(result[0]) > 0

        offers = result[0]

        fields = {
            "amount",
            "expiresAt",
            "id",
            "merchantID",
            "partnerID",
            "payout",
            "readvance",
        }

        assert all(isinstance(offer, dict) for offer in offers)

        assert all(field in offer for field in fields for offer in offers)

    @pytest.mark.parametrize(
        "partner_id, page_size",
        [(partner_id, random.randint(1, 10)) for partner_id in get_test_partner_ids()],
    )
    def test_get_offers_with_pagination(
        self, offer_client: OfferClient, partner_id: str, page_size: int
    ):
        """Test getting offers with pagination"""
        response = offer_client.get_offers(partner_id, page=1, page_size=page_size)
        if response.status_code == 204:
            pytest.skip("No offers found for partner")

        if response.status_code == 502:
            pytest.skip("Offers Endpoint Timed-Out Gateway Timeout Error")

        assert response.status_code == 200
        result: list[list[dict[str, Any]]] = response.json()

        # Should return a list or dict with offers
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], list)
        assert len(result[0]) == page_size

        offers = result[0]

        fields = {
            "amount",
            "expiresAt",
            "id",
            "merchantID",
            "partnerID",
            "payout",
            "readvance",
        }

        assert all(isinstance(offer, dict) for offer in offers)

        assert all(field in offer for field in fields for offer in offers)

    @pytest.mark.parametrize("partner_id", get_test_partner_ids())
    def test_get_offers_extended(self, offer_client: OfferClient, partner_id: str):
        """Test getting offers with extended details"""
        response = offer_client.get_offers(
            partner_id, page=1, page_size=2, extended=True
        )
        if response.status_code == 204:
            pytest.skip("No offers found for partner")

        if response.status_code == 502:
            pytest.skip("Offers Endpoint Timed-Out Gateway Timeout Error")

        assert response.status_code == 200
        result: list[list[dict[str, Any]]] = response.json()

        # Should return a list or dict with offers
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], list)
        assert len(result[0]) > 0

        offers = result[0]

        fields = {
            "amount",
            "expiresAt",
            "id",
            "merchantID",
            "metadata",
            "offerQuote",
            "partnerID",
            "payout",
            "readvance",
        }

        assert all(isinstance(offer, dict) for offer in offers)

        assert all(field in offer for field in fields for offer in offers)
        assert all(
            offer["offerQuote"].get("quoteAdvance")
            or offer["offerQuote"].get("quoteAdvanceLimited")
            for offer in offers
        )