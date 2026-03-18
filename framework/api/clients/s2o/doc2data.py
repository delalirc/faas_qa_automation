from typing import Any
from framework.api.client import ServiceClient
from requests import Response


class Doc2DataClient(ServiceClient):
    """Client for Doc2Data OCR service"""

    def __init__(self, base_url: str | None, token: str | None):
        super().__init__("doc2data", base_url, token)

    def get_health(self) -> Response:
        """Health check"""
        return self.get("/health")

    def get_info(self) -> Response:
        """Service info"""
        return self.get("/info")

    def get_version(self) -> Response:
        """Service version"""
        return self.get("/version")

    def create_document(self, data: dict[str, Any]) -> Response:
        """Create document"""
        return self.post("/api/v1/documents", data)

    def create_document_presigned(
        self,
        data: dict[str, Any],
    ) -> Response:
        """Create document and get presigned URL for upload"""
        return self.post("/api/v1/documents/pre-signed", data)

    def get_document(self, document_id: str) -> Response:
        """Get document status"""
        return self.get(f"/api/v1/documents/{document_id}")

    def get_document_results(self, document_id: str) -> Response:
        """List OCR result files"""
        return self.get(f"/api/v1/documents/{document_id}/results")
