import uuid
from framework.api.clients.s2o.orchestrator import OrchestratorClient

class TestS2OJourney:
    def test_S2O_journey(
        self,
        orchestrator_client: OrchestratorClient,
        s2o_partner_ids: dict[str, uuid.UUID],
        s2o_merchant_ids: dict[str, uuid.UUID],
        s2o_application_ids: dict[str, str],
    ) -> None:
        """Test S2O journey."""
        payload = {
            "partner_id": str(s2o_partner_ids["test-partner-journey"]),
            "merchant_id": str(s2o_merchant_ids["test-merchant-journey"]),
            "application_id": s2o_application_ids["test-application-journey"],
            "session_type": "salesforce",
        }
        response = orchestrator_client.create_session(payload)
        assert response.status_code == 201
        data = response.json()
        assert "session_id" in data
        uuid.UUID(data["session_id"])

        
        
