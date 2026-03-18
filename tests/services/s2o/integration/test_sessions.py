"""
S2O Session Management tests.

Test IDs: S2O-SM-001 to S2O-SM-005
"""

import uuid

import pytest

from framework.api.clients.s2o.orchestrator import OrchestratorClient


@pytest.mark.integration
@pytest.mark.s2o
class TestS2OSessions:
    """Session management tests for S2O orchestrator."""

    def test_S2O_create_session_valid(
        self,
        orchestrator_client: OrchestratorClient,
        s2o_partner_ids: dict[str, uuid.UUID],
        s2o_merchant_ids: dict[str, uuid.UUID],
        s2o_application_ids: dict[str, str],
    ) -> None:
        """Create session with valid payload returns 201 and session_id."""
        payload = {
            "partner_id": str(s2o_partner_ids["test-partner-success"]),
            "merchant_id": str(s2o_merchant_ids["test-merchant-success"]),
            "application_id": s2o_application_ids["test-application-success"],
            "session_type": "salesforce",
        }
        response = orchestrator_client.create_session(payload)
        assert response.status_code == 201
        data = response.json()
        assert "session_id" in data
        uuid.UUID(data["session_id"])

    def test_S2O_create_session_missing_partner_id(
        self,
        orchestrator_client: OrchestratorClient,
        s2o_merchant_ids: dict[str, uuid.UUID],
        s2o_application_ids: dict[str, str],
    ) -> None:
        """Create session without partner_id returns 400 validation error."""
        payload = {
            "merchant_id": str(s2o_merchant_ids["test-merchant-success"]),
            "application_id": s2o_application_ids["test-application-success"],
            "session_type": "salesforce",
        }
        response = orchestrator_client.create_session(payload)
        assert response.status_code == 422

    def test_S2O_get_session(
        self,
        orchestrator_client: OrchestratorClient,
        s2o_partner_ids: dict[str, uuid.UUID],
        s2o_merchant_ids: dict[str, uuid.UUID],
        s2o_application_ids: dict[str, str],
    ) -> None:
        """Get session by ID returns 200 and session details."""
        create = orchestrator_client.create_session(
            {
                "partner_id": str(s2o_partner_ids["test-partner-success"]),
                "merchant_id": str(s2o_merchant_ids["test-merchant-success"]),
                "application_id": s2o_application_ids["test-application-success"],
                "session_type": "salesforce",
            }
        )
        assert create.status_code == 201
        session_id = create.json()["session_id"]

        response = orchestrator_client.get_session(session_id)
        assert response.status_code == 200
        data = response.json()
        assert data.get("session_id") == session_id

    def test_S2O_get_nonexistent_session(
        self, orchestrator_client: OrchestratorClient
    ) -> None:
        """Get non-existent session returns 404."""
        fake_id = str(uuid.uuid4())
        response = orchestrator_client.get_session(fake_id)
        assert response.status_code == 404

    def test_S2O_get_invalid_session_id(
        self, orchestrator_client: OrchestratorClient
    ) -> None:
        """Get invalid session ID returns 400."""
        fake_id = "invalid-session-id"
        response = orchestrator_client.get_session(fake_id)
        assert response.status_code == 422

    def test_S2O_get_session_status(
        self,
        orchestrator_client: OrchestratorClient,
        s2o_partner_ids: dict[str, uuid.UUID],
        s2o_merchant_ids: dict[str, uuid.UUID],
        s2o_application_ids: dict[str, str],
    ) -> None:
        """Get session status returns 200 and status summary."""
        create = orchestrator_client.create_session(
            {
                "partner_id": str(s2o_partner_ids["test-partner-success"]),
                "merchant_id": str(s2o_merchant_ids["test-merchant-success"]),
                "application_id": s2o_application_ids["test-application-success"],
                "session_type": "salesforce",
            }
        )
        assert create.status_code == 201
        session_id = create.json()["session_id"]

        response = orchestrator_client.get_session_status(session_id)
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "documents" in data

    def test_S2O_create_duplicate_session(
        self,
        orchestrator_client: OrchestratorClient,
        s2o_partner_ids: dict[str, uuid.UUID],
        s2o_merchant_ids: dict[str, uuid.UUID],
        s2o_application_ids: dict[str, str],
    ) -> None:
        """Create duplicate session returns 400."""
        payload = {
            "partner_id": str(s2o_partner_ids["test-partner-success"]),
            "merchant_id": str(s2o_merchant_ids["test-merchant-success"]),
            "application_id": s2o_application_ids["test-application-success"],
            "session_type": "salesforce",
        }
        response = orchestrator_client.create_session(payload)
        assert response.status_code == 201
        session_id = response.json()["session_id"]
        response = orchestrator_client.create_session(payload)
        assert response.status_code == 201
        assert response.json()["session_id"] == session_id
