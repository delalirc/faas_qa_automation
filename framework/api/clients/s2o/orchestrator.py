from typing import Any
from framework.api.client import ServiceClient
from requests import Response


class OrchestratorClient(ServiceClient):
    """Client for S2O orchestrator"""

    def __init__(self, base_url: str | None, token: str | None):
        super().__init__("orchestrator", base_url, token)

    def create_session(self, data: dict[str, Any]) -> Response:
        """Create a new S2O session"""
        return self.post("/api/v1/sessions", data)

    def get_session(self, session_id: str) -> Response:
        """Get session by ID"""
        return self.get(f"/api/v1/sessions/{session_id}")

    def get_session_status(self, session_id: str) -> Response:
        """Get session status"""
        return self.get(f"/api/v1/sessions/{session_id}/status")

    def get_session_documents(self, session_id: str) -> Response:
        """Get document status for session"""
        return self.get(f"/api/v1/sessions/{session_id}/documents")

    def get_session_offer(self, session_id: str) -> Response:
        """Get session offer"""
        return self.get(f"/api/v1/sessions/{session_id}/offer")

    def get_document_presigned_url(
        self,
        session_id: str,
        data: dict[str, Any],
    ) -> Response:
        """Get presigned URL for document upload"""
        return self.post(
            f"/api/v1/documents/{session_id}/presigned-url",
            data,
        )

    def register_documents(
        self,
        session_id: str,
        documents: list[dict[str, Any]],
    ) -> Response:
        """Register uploaded documents. Each document: presigned_url, filename, provider_name, optional password."""
        url = f"{self.base_url}/api/v1/documents/{session_id}"
        return self.post(url, data=documents)

    def register_document(
        self,
        session_id: str,
        data: dict[str, Any],
    ) -> Response:
        """Register uploaded document. Document: presigned_url, filename, provider_name, optional password."""
        url = f"{self.base_url}/api/v1/documents/{session_id}/document"
        return self.post(url, data=data)
