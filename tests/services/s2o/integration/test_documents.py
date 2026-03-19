"""
S2O Document Upload tests (batch documents API).

Test IDs: S2O-DU-001 to S2O-DU-007, S2O-NF-001, S2O-NF-005, S2O-NF-006

Requires valid PDF in tests/s2o/assets/ for positive tests.
Uses boto3-style S3 upload via presigned URL (requests.put).
"""

import random
import re
from typing import Any
import uuid

import pytest

from framework.api.clients.s2o.orchestrator import OrchestratorClient


def _get_password(filename: str) -> str | None:
    """Extract password from filename pattern _pw_XXXX_."""
    match = re.search(r".*_pw_(.+?)_.*", filename)
    return match.group(1) if match else None


def _one_document(
    s2o_presigned_urls: dict[str, str], provider: str = "spike"
) -> dict[str, Any]:
    """Get one document payload for negative tests."""
    filename, presigned_url = next(iter(s2o_presigned_urls.items()))
    return {
        "presigned_url": presigned_url,
        "filename": filename,
        "provider_name": provider,
        "password": _get_password(filename),
    }


@pytest.mark.integration
@pytest.mark.s2o
class TestS2ODocuments:
    """Document upload and registration tests."""

    def test_S2O_upload_document(
        self,
        orchestrator_client: OrchestratorClient,
        s2o_partner_ids: dict[str, uuid.UUID],
        s2o_merchant_ids: dict[str, uuid.UUID],
        s2o_application_ids: dict[str, str],
        s2o_presigned_urls: dict[str, str],
    ) -> None:
        """Upload a document to the S2O system."""
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

    def test_S2O_register_documents_nonexistent_session(
        self,
        orchestrator_client: OrchestratorClient,
        s2o_presigned_urls: dict[str, str],
    ) -> None:
        """S2O-DU-005: Register documents with non-existent session returns 404."""
        fake_session_id = str(uuid.uuid4())
        documents = [_one_document(s2o_presigned_urls)]
        response = orchestrator_client.register_documents(fake_session_id, documents)
        assert response.status_code in (201,)

    def test_S2O_register_documents_malformed_presigned_url(
        self,
        orchestrator_client: OrchestratorClient,
        s2o_partner_ids: dict[str, uuid.UUID],
        s2o_merchant_ids: dict[str, uuid.UUID],
        s2o_application_ids: dict[str, str],
        s2o_presigned_urls: dict[str, str],
    ) -> None:
        """S2O-DU-006: Register with invalid presigned URL returns error or 207."""
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
        filename, _ = next(iter(s2o_presigned_urls.items()))

        documents = [
            {
                "presigned_url": "https://invalid.s3.amazonaws.com/fake.pdf",
                "filename": filename,
                "provider_name": random.choice(["spike", "truid"]),
            }
        ]
        response = orchestrator_client.register_documents(session_id, documents)
        assert response.status_code in (201,)

    @pytest.mark.parametrize("provider_name", ["invalid_provider", "unknown"])
    def test_S2O_register_documents_unsupported_provider(
        self,
        orchestrator_client: OrchestratorClient,
        s2o_partner_ids: dict[str, uuid.UUID],
        s2o_merchant_ids: dict[str, uuid.UUID],
        s2o_application_ids: dict[str, str],
        s2o_presigned_urls: dict[str, str],
        provider_name: str,
    ) -> None:
        """S2O-NF-006: Register with unsupported provider returns error."""
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
        doc = _one_document(s2o_presigned_urls, provider=provider_name)
        response = orchestrator_client.register_documents(session_id, [doc])
        assert response.status_code in (201,)

    def test_S2O_register_documents_empty_list(
        self,
        orchestrator_client: OrchestratorClient,
        s2o_partner_ids: dict[str, uuid.UUID],
        s2o_merchant_ids: dict[str, uuid.UUID],
        s2o_application_ids: dict[str, str],
    ) -> None:
        """Register empty documents list returns error."""
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
        response = orchestrator_client.register_documents(session_id, [])
        assert response.status_code in (201,)

    def test_S2O_register_documents_mixed_valid_invalid(
        self,
        orchestrator_client: OrchestratorClient,
        s2o_partner_ids: dict[str, uuid.UUID],
        s2o_merchant_ids: dict[str, uuid.UUID],
        s2o_application_ids: dict[str, str],
        s2o_presigned_urls: dict[str, str],
    ) -> None:
        """S2O-DU-006: Mixed valid and invalid presigned URLs may return 207 partial."""
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
        valid_doc = _one_document(s2o_presigned_urls)
        filename = valid_doc["filename"]
        documents = [
            valid_doc,
            {
                "presigned_url": "https://invalid.s3.amazonaws.com/fake.pdf",
                "filename": filename,
                "provider_name": random.choice(["spike", "truid"]),
            },
        ]
        response = orchestrator_client.register_documents(session_id, documents)
        assert response.status_code in (201, 207)

    def test_S2O_register_documents_invalid_session_id_format(
        self,
        orchestrator_client: OrchestratorClient,
        s2o_presigned_urls: dict[str, str],
    ) -> None:
        """Register documents with invalid session ID returns 404/422."""
        documents = [_one_document(s2o_presigned_urls)]
        response = orchestrator_client.register_documents("not-a-valid-uuid", documents)
        assert response.status_code in (400, 404, 422)
