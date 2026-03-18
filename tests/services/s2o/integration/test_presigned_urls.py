"""
S2O Document Upload tests.

Test IDs: S2O-DU-001 to S2O-DU-007

Requires valid PDF in tests/s2o/assets/ for positive tests.
Uses boto3-style S3 upload via presigned URL (requests.put).
"""

from pathlib import Path
import random
import uuid

import pytest
import requests

from framework.api.clients.s2o.orchestrator import OrchestratorClient
from tests.services.s2o.conftest import list_asset_filenames


@pytest.mark.integration
@pytest.mark.s2o
class TestS2OPresignedUrls:
    """Presigned URL tests."""

    @pytest.mark.parametrize(
        "provider_name",
        ["spike", "truid"],
    )
    def test_S2O_get_presigned_url(
        self,
        orchestrator_client: OrchestratorClient,
        provider_name: str,
        s2o_partner_ids: dict[str, uuid.UUID],
        s2o_merchant_ids: dict[str, uuid.UUID],
        s2o_application_ids: dict[str, str],
    ) -> None:
        """Get presigned URL for bank statement returns 200 and presigned_url."""
        filename = "test_statement.pdf"
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

        response = orchestrator_client.get_document_presigned_url(
            session_id,
            data={
                "filename": filename,
                "provider_name": provider_name,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["presigned_url"] is not None
        assert provider_name in data["presigned_url"]
        assert data["document_id"] is not None
        assert data["password"] is None
        assert data["metadata"] is None
        assert data["filename"] == filename
        assert data["provider_name"] == provider_name

    @pytest.mark.parametrize(
        "provider_name",
        ["spike", "truid"],
    )
    def test_S2O_get_presigned_url_with_password(
        self,
        orchestrator_client: OrchestratorClient,
        provider_name: str,
        s2o_partner_ids: dict[str, uuid.UUID],
        s2o_merchant_ids: dict[str, uuid.UUID],
        s2o_application_ids: dict[str, str],
    ) -> None:
        """Get presigned URL for bank statement returns 200 and presigned_url."""
        filename = "test_statement_with_password.pdf"
        password = "test123"
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

        response = orchestrator_client.get_document_presigned_url(
            session_id,
            data={
                "filename": filename,
                "provider_name": provider_name,
                "password": password,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["presigned_url"] is not None
        assert provider_name in data["presigned_url"]
        assert data["document_id"] is not None
        assert data["password"] != password
        assert all(char == "*" for char in data["password"])
        assert data["metadata"] is None
        assert data["filename"] == filename
        assert data["provider_name"] == provider_name

    @pytest.mark.parametrize(
        "provider_name",
        ["spike", "truid"],
    )
    def test_S2O_get_presigned_url_with_metadata(
        self,
        orchestrator_client: OrchestratorClient,
        provider_name: str,
        s2o_partner_ids: dict[str, uuid.UUID],
        s2o_merchant_ids: dict[str, uuid.UUID],
        s2o_application_ids: dict[str, str],
    ) -> None:
        """Get presigned URL for bank statement returns 200 and presigned_url."""
        filename = "test_statement_with_metadata.pdf"
        metadata = {
            "key": "value",
        }
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

        response = orchestrator_client.get_document_presigned_url(
            session_id,
            data={
                "filename": filename,
                "provider_name": provider_name,
                "metadata": metadata,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["presigned_url"] is not None
        assert provider_name in data["presigned_url"]
        assert data["document_id"] is not None
        assert data["password"] is None
        assert data["metadata"] == metadata
        assert data["filename"] == filename
        assert data["provider_name"] == provider_name

    @pytest.mark.parametrize(
        "provider_name",
        ["spike", "truid"],
    )
    def test_S2O_get_presigned_url_missing_filename(
        self,
        orchestrator_client: OrchestratorClient,
        provider_name: str,
        s2o_partner_ids: dict[str, uuid.UUID],
        s2o_merchant_ids: dict[str, uuid.UUID],
        s2o_application_ids: dict[str, str],
    ) -> None:
        """Get presigned URL for bank statement returns 200 and presigned_url."""
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

        response = orchestrator_client.get_document_presigned_url(
            session_id,
            data={
                "provider_name": provider_name,
            },
        )
        assert response.status_code == 422
        assert response.json()

    @pytest.mark.parametrize(
        "provider_name",
        ["spike", "truid"],
    )
    def test_S2O_get_presigned_url_missing_provider_name(
        self,
        orchestrator_client: OrchestratorClient,
        provider_name: str,
        s2o_partner_ids: dict[str, uuid.UUID],
        s2o_merchant_ids: dict[str, uuid.UUID],
        s2o_application_ids: dict[str, str],
    ) -> None:
        """Get presigned URL for bank statement with missing provider_name returns 200 and presigned_url."""
        filename = "test_statement.pdf"
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

        response = orchestrator_client.get_document_presigned_url(
            session_id,
            data={
                "filename": filename,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["presigned_url"] is not None
        assert data["document_id"] is not None
        assert data["password"] is None
        assert data["metadata"] is None
        assert data["filename"] == filename
        assert data["provider_name"] is not None

    def test_S2O_presigned_url_nonexistent_session(
        self,
        orchestrator_client: OrchestratorClient,
    ) -> None:
        """Presigned URL for non-existent session returns 404."""
        fake_id = str(uuid.uuid4())
        response = orchestrator_client.get_document_presigned_url(
            fake_id,
            data={
                "filename": "test.pdf",
                "provider_name": "spike",
            },
        )
        assert response.status_code == 400
        assert response.json()

    def test_S2O_presigned_url_invalid_session_id(
        self,
        orchestrator_client: OrchestratorClient,
    ) -> None:
        """Presigned URL for invalid session_id returns 404."""
        response = orchestrator_client.get_document_presigned_url(
            "invalid_session_id",
            data={
                "filename": "test.pdf",
                "provider_name": "spike",
            },
        )
        assert response.status_code == 422
        assert response.json()

    @pytest.mark.parametrize(
        "provider_name, filename",
        [
            (random.choice(["spike", "truid"]), filename)
            for filename in list_asset_filenames()
        ],
    )
    def test_S2O_upload_pdf_via_presigned_url(
        self,
        orchestrator_client: OrchestratorClient,
        s2o_partner_ids: dict[str, uuid.UUID],
        s2o_merchant_ids: dict[str, uuid.UUID],
        s2o_application_ids: dict[str, str],
        provider_name: str,
        filename: str,
    ) -> None:
        """
        Upload PDF to S3 via presigned URL.
        """
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

        presigned_resp = orchestrator_client.get_document_presigned_url(
            session_id,
            data={
                "filename": filename,
                "provider_name": provider_name,
            },
        )
        assert presigned_resp.status_code == 201
        data = presigned_resp.json()
        assert data["presigned_url"] is not None

        path = Path(__file__).parent.parent / "assets" / filename
        assert path.exists()

        with open(path, "rb") as f:
            upload_resp = requests.put(
                data["presigned_url"],
                data=f,
                headers={"Content-Type": "application/pdf"},
            )
        assert upload_resp.status_code in (200, 204)
