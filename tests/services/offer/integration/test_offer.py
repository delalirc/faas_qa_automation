"""
Integration tests for Offer
"""

from typing import Any
from framework.api.clients.offer import OfferClient
import pytest
from tests.conftest import get_test_partner_ids


@pytest.mark.integration
@pytest.mark.offer
class TestOffer:
    """Integration tests for offer"""

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
            "readvance",
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
            "readvance",
        }

        # Verify all required fields are present in the offer
        assert all(field in offer for field in fields)
