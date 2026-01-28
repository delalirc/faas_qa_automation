"""
Integration tests for Offer service API endpoints
"""

from typing import Any
from uuid import UUID
from framework.api.client import OfferClient
import pytest
from tests.conftest import get_test_partner_ids


@pytest.mark.integration
class TestOfferAPI:
    """Integration tests for offer API endpoints"""

    @pytest.mark.parametrize("partner_id", get_test_partner_ids())
    def test_offer_journey(self, offer_client: OfferClient, partner_id: str):
        """Test getting offer by partner and merchant ID"""
        # This test may need a known merchant_id or skip if none available
        merchant_id, offer_id = self.get_offer_identifiers(offer_client, partner_id)

        if not merchant_id:
            pytest.skip("No test merchant ID available")

        # Get an Offer for a partner and merchant
        offer_details = self.get_offer_details(
            offer_client, partner_id, merchant_id, offer_id
        )

        response = offer_client.validate_offer(
            partner_id,
            offer_id,
            {
                "advance": offer_details["advance"],
                "paybackPercentage": offer_details["paybackPercentage"],
                "term": offer_details["term"],
                "merchantID": offer_details["merchantID"],
            },
        )

        assert response.status_code == 200
        validation_results: dict[str, Any] = response.json()

        assert "isValidated" in validation_results
        assert "offerValidationID" in validation_results
        assert "result" in validation_results
        assert validation_results["isValidated"] == True
        assert isinstance(UUID(validation_results["offerValidationID"]), UUID)
        assert validation_results["result"] == "VALID"

        validation = offer_client.get_offer_validation(
            partner_id,
            validation_results["offerValidationID"],
        )

        assert validation.status_code == 200
        validation_result = validation.json()

        assert validation_result["advance"] == offer_details["advance"]
        assert validation_result["merchantID"] == offer_details["merchantID"]
        assert validation_result["offerID"] == offer_details["offerID"]
        assert (
            validation_result["offerValidationID"]
            == validation_results["offerValidationID"]
        )
        assert (
            validation_result["paybackPercentage"] == offer_details["paybackPercentage"]
        )
        assert validation_result["term"] == offer_details["term"]

    def get_offer_identifiers(
        self, offer_client: OfferClient, partner_id: str
    ) -> tuple[str, str]:
        offers = offer_client.get_offers(partner_id, page=1, page_size=1)
        if offers.status_code == 204:
            pytest.skip("No offers found for partner")

        if offers.status_code == 502:
            pytest.skip("Offers Endpoint Timed-Out Gateway Timeout Error")

        assert offers.status_code == 200
        offers_result: list[list[dict[str, Any]]] = offers.json()
        return offers_result[0][0]["merchantID"], offers_result[0][0]["id"]

    def get_offer_details(
        self,
        offer_client: OfferClient,
        partner_id: str,
        merchant_id: str,
        offer_id: str,
    ) -> dict[str, Any]:
        offer = offer_client.get_offer(
            partner_id, merchant_id=merchant_id, offer_id=offer_id, extended=True
        )
        # May return 200 with offer or 404 if no offer exists
        assert offer.status_code == 200
        offer_result = offer.json()

        quotesAdvanceSummary = offer_result[0]["offerQuote"].get(
            "quoteAdvance"
        ) or offer_result[0]["offerQuote"].get("quoteAdvanceLimited")

        if not quotesAdvanceSummary:
            pytest.fail("No quotes found for offer")

        quotes = quotesAdvanceSummary[0].get("quotes")

        if not quotes:
            pytest.fail("No quotes found for offer")

        advance = quotesAdvanceSummary[0].get("advance")
        paybackPercentage = quotes[0].get("paybackPercentage")
        term = quotes[0].get("term")

        return {
            "advance": advance,
            "paybackPercentage": paybackPercentage,
            "term": term,
            "merchantID": merchant_id,
            "offerID": offer_id,
        }
