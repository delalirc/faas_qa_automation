import random
import re
import time
import uuid
import pytest
from framework.api.clients.s2o.orchestrator import OrchestratorClient

def _get_password(filename: str) -> str | None:
    """Extract password from filename pattern _pw_XXXX_."""
    match = re.search(r".*_pw_(.+?)_.*", filename)
    return match.group(1) if match else None

class TestS2OJourney:
    def test_S2O_journey(
        self,
        orchestrator_client: OrchestratorClient,
        s2o_partner_ids: dict[str, uuid.UUID],
        s2o_merchant_ids: dict[str, uuid.UUID],
        s2o_application_ids: dict[str, str],
        s2o_presigned_urls: dict[str, str],
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
        session_id = data["session_id"]

        
        for filename, presigned_url in s2o_presigned_urls.items():
            provider_name = random.choice(["spike", "truid"])
            response = orchestrator_client.register_document(
                session_id,
                {
                    "presigned_url": presigned_url,
                    "filename": filename,
                    "provider_name": provider_name,
                    "password": _get_password(filename),
                },
            )

            assert response.status_code == 201
            data = response.json()
            assert data["document_id"] is not None
            assert data["filename"] == filename
            assert data["provider_name"] == provider_name
            if data["password"] is not None:
                assert all(char == "*" for char in data["password"])
            else:
                assert data["password"] is None
            assert data["metadata"] is None
            assert data["status"] == "submitted"

        response = orchestrator_client.register_documents(
            session_id,
            [
                {
                    "presigned_url": presigned_url,
                    "filename": filename,
                    "provider_name": random.choice(["spike", "truid"]),
                    "password": _get_password(filename),
                }
                for filename, presigned_url in s2o_presigned_urls.items()
            ],
        )

        assert response.status_code == 201
        data = response.json()

        for item in data:
            assert item["document_id"] is None
            assert item["filename"] is not None
            assert item["provider_name"] is not None
            if item["password"] is not None:
                assert all(char == "*" for char in item["password"])
            else:
                assert item["password"] is None
            assert item["metadata"] is None
            assert item["status"] == "received"
        
        time.sleep(60)
        response = orchestrator_client.get_session(session_id)
        assert response.status_code == 200
        data = response.json()
        assert data.get("session_id") == session_id
        assert len(data["data"]["responses"]) == len(s2o_presigned_urls) * 2
        print(data)
        for item in data["data"]["responses"]:
            assert item["document_id"] is not None





        
        
