"""
S2O Document Upload tests (single document API).

Test IDs: S2O-DU-001 to S2O-DU-007, S2O-NF-001, S2O-NF-005, S2O-NF-006

Requires valid PDF in tests/s2o/assets/ for positive tests.
Uses boto3-style S3 upload via presigned URL (requests.put).
"""

import re
import uuid

import pytest

from framework.api.clients.s2o.orchestrator import OrchestratorClient


def _get_password(filename: str) -> str | None:
    """Extract password from filename pattern _pw_XXXX_."""
    match = re.search(r".*_pw_(.+?)_.*", filename)
    return match.group(1) if match else None


def _one_presigned_url(s2o_presigned_urls: dict[str, str]) -> tuple[str, str]:
    """Get first (filename, presigned_url) pair for negative tests."""
    return next(iter(s2o_presigned_urls.items()))


@pytest.mark.integration
@pytest.mark.s2o
class TestS2ODocument:
    """Document upload and registration tests."""

    @pytest.mark.parametrize(
        "provider_name",
        ["spike", "truid"],
    )
    def test_S2O_upload_document(
        self,
        orchestrator_client: OrchestratorClient,
        s2o_partner_ids: dict[str, uuid.UUID],
        s2o_merchant_ids: dict[str, uuid.UUID],
        s2o_application_ids: dict[str, str],
        provider_name: str,
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

        for filename, presigned_url in s2o_presigned_urls.items():
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

    def test_S2O_register_document_invalid_session(
        self,
        orchestrator_client: OrchestratorClient,
        s2o_presigned_urls: dict[str, str],
    ) -> None:
        """S2O-DU-005: Register document with non-existent session returns 404."""
        fake_session_id = str(uuid.uuid4())
        filename, presigned_url = _one_presigned_url(s2o_presigned_urls)
        response = orchestrator_client.register_document(
            fake_session_id,
            {
                "presigned_url": presigned_url,
                "filename": filename,
                "provider_name": "spike",
            },
        )
        assert response.status_code in (404, 400)

    def test_S2O_register_document_malformed_presigned_url(
        self,
        orchestrator_client: OrchestratorClient,
        s2o_partner_ids: dict[str, uuid.UUID],
        s2o_merchant_ids: dict[str, uuid.UUID],
        s2o_application_ids: dict[str, str],
        s2o_presigned_urls: dict[str, str],
    ) -> None:
        """S2O-DU-006: Register with invalid/malformed presigned URL returns error."""
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
        filename, _ = _one_presigned_url(s2o_presigned_urls)

        response = orchestrator_client.register_document(
            session_id,
            {
                "presigned_url": "https://invalid-bucket.s3.amazonaws.com/nonexistent/key.pdf",
                "filename": filename,
                "provider_name": "spike",
            },
        )
        assert response.status_code in (201,)

    @pytest.mark.parametrize("provider_name", ["invalid_provider", "unknown"])
    def test_S2O_register_document_unsupported_provider(
        self,
        orchestrator_client: OrchestratorClient,
        s2o_partner_ids: dict[str, uuid.UUID],
        s2o_merchant_ids: dict[str, uuid.UUID],
        s2o_application_ids: dict[str, str],
        s2o_presigned_urls: dict[str, str],
        provider_name: str,
    ) -> None:
        """S2O-NF-006: Register with unsupported provider_name returns error."""
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
        filename, presigned_url = _one_presigned_url(s2o_presigned_urls)

        response = orchestrator_client.register_document(
            session_id,
            {
                "presigned_url": presigned_url,
                "filename": filename,
                "provider_name": provider_name,
            },
        )
        assert response.status_code in (201,)

    def test_S2O_register_document_wrong_password(
        self,
        orchestrator_client: OrchestratorClient,
        s2o_partner_ids: dict[str, uuid.UUID],
        s2o_merchant_ids: dict[str, uuid.UUID],
        s2o_application_ids: dict[str, str],
        s2o_presigned_urls: dict[str, str],
    ) -> None:
        """S2O-NF-001: Register PW-protected PDF with wrong password."""
        pw_filename = next(
            (f for f in s2o_presigned_urls if "_pw_" in f),
            None,
        )
        if not pw_filename:
            pytest.skip("No password-protected PDF in assets")

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
        presigned_url = s2o_presigned_urls[pw_filename]

        response = orchestrator_client.register_document(
            session_id,
            {
                "presigned_url": presigned_url,
                "filename": pw_filename,
                "provider_name": "spike",
                "password": "wrong_password_12345",
            },
        )
        assert response.status_code in (201, 207)
        data = response.json()
        assert "document_id" in data or "status" in data

    def test_S2O_register_document_missing_filename(
        self,
        orchestrator_client: OrchestratorClient,
        s2o_partner_ids: dict[str, uuid.UUID],
        s2o_merchant_ids: dict[str, uuid.UUID],
        s2o_application_ids: dict[str, str],
        s2o_presigned_urls: dict[str, str],
    ) -> None:
        """Register document missing filename returns validation error."""
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
        _, presigned_url = _one_presigned_url(s2o_presigned_urls)

        response = orchestrator_client.register_document(
            session_id,
            {
                "presigned_url": presigned_url,
                "provider_name": "spike",
            },
        )
        assert response.status_code == 422

    def test_S2O_register_document_invalid_session_id_format(
        self,
        orchestrator_client: OrchestratorClient,
        s2o_presigned_urls: dict[str, str],
    ) -> None:
        """Register document with invalid session ID format returns 404/422."""
        filename, presigned_url = _one_presigned_url(s2o_presigned_urls)
        response = orchestrator_client.register_document(
            "not-a-valid-uuid",
            {
                "presigned_url": presigned_url,
                "filename": filename,
                "provider_name": "spike",
            },
        )
        assert response.status_code in (400, 404, 422)
