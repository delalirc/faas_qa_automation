"""
Integration tests for Offer service API endpoints
"""

from typing import Any
from framework.api.client import OfferClient
import pytest
from tests.conftest import get_test_partner_ids


@pytest.mark.integration
class TestOfferAPI:
    """Integration tests for offer API endpoints"""

    def test_health_check(self, offer_client: OfferClient):
        """Test offer service health endpoint"""
        response = offer_client.get_health()
        assert response.status_code == 200
        response.json()

    def test_version_endpoint(self, offer_client: OfferClient):
        """Test offer service version endpoint"""
        response = offer_client.get_version()
        assert response.status_code == 200
        response.json()

    @pytest.mark.parametrize("partner_id", get_test_partner_ids())
    def test_get_offers_for_partner(self, offer_client: OfferClient, partner_id: str):
        """Test getting all offers for a partner"""
        response = offer_client.get_offers(partner_id)

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

    @pytest.mark.parametrize("partner_id", get_test_partner_ids())
    def test_get_offers_with_pagination(
        self, offer_client: OfferClient, partner_id: str
    ):
        """Test getting offers with pagination"""
        response = offer_client.get_offers(partner_id, page=1, page_size=2)
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
            "readvance"
        }

        assert all(isinstance(offer, dict) for offer in offers)

        assert all(field in offer for field in fields for offer in offers)
        assert all(
            offer["offerQuote"].get("quoteAdvance")
            or offer["offerQuote"].get("quoteAdvanceLimited")
            for offer in offers
        )

    @pytest.mark.parametrize("partner_id", get_test_partner_ids())
    def test_get_offer_by_partner_and_merchant(
        self, offer_client: OfferClient, partner_id: str
    ):
        """Test getting offer by partner and merchant ID"""
        # This test may need a known merchant_id or skip if none available
        merchant_id = None  # Replace with actual test merchant ID if available

        response = offer_client.get_offers(partner_id, page=1, page_size=1)
        if response.status_code == 204:
            pytest.skip("No offers found for partner")

        if response.status_code == 502:
            pytest.skip("Offers Endpoint Timed-Out Gateway Timeout Error")

        result: list[list[dict[str, Any]]] = response.json()

        merchant_id = result[0][0]["merchantID"]

        if not merchant_id:
            pytest.skip("No test merchant ID available")

        response = offer_client.get_offer(partner_id, merchant_id=merchant_id)
        # May return 200 with offer or 404 if no offer exists
        assert response.status_code in [200, 404]
        
        if response.status_code == 404:
            pytest.skip("Offer not found for merchant")
        
        result = response.json()

        # Should return a list with a single offer dict
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], dict)
        
        offer = result[0]

        fields = {
            "amount",
            "expiresAt",
            "id",
            "merchantID",
            "partnerID",
            "payout",
            "readvance"
        }

        # Verify all required fields are present in the offer
        assert all(field in offer for field in fields)

    @pytest.mark.parametrize("partner_id", get_test_partner_ids())
    def test_get_offer_by_partner_and_offer_id(
        self, offer_client: OfferClient, partner_id: str
    ):
        """Test getting offer by partner and merchant ID"""
        # This test may need a known offer_id or skip if none available
        offer_id = None  # Replace with actual test offer ID if available

        response = offer_client.get_offers(partner_id, page=1, page_size=1)
        if response.status_code == 204:
            pytest.skip("No offers found for partner")

        if response.status_code == 502:
            pytest.skip("Offers Endpoint Timed-Out Gateway Timeout Error")

        result: list[list[dict[str, Any]]] = response.json()

        offer_id = result[0][0]["id"]

        if not offer_id:
            pytest.skip("No test offer ID available")

        response = offer_client.get_offer(partner_id, offer_id=offer_id)
        # May return 200 with offer or 404 if no offer exists
        assert response.status_code in [200, 404]
        
        if response.status_code == 404:
            pytest.skip("Offer not found")
        
        result = response.json()

        # Should return a list with a single offer dict
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], dict)
        
        offer = result[0]

        fields = {
            "amount",
            "expiresAt",
            "id",
            "merchantID",
            "partnerID",
            "payout",
            "readvance"
        }

        # Verify all required fields are present in the offer
        assert all(field in offer for field in fields)
