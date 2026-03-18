"""
S2O Health & Connectivity tests.

Test IDs: S2O-HC-001 to S2O-HC-004
"""

import pytest

from framework.api.clients.s2o.orchestrator import OrchestratorClient


@pytest.mark.integration
@pytest.mark.health
@pytest.mark.s2o
class TestS2OHealth:
    """Health checks for S2O services."""

    def test_S2O_orchestrator_health(
        self, orchestrator_client: OrchestratorClient
    ) -> None:
        """Orchestrator health check returns 200 and ACTIVE."""
        response = orchestrator_client.get("/health")
        assert response.status_code == 200
        assert response.json()

    def test_S2O_orchestrator_info(
        self, orchestrator_client: OrchestratorClient
    ) -> None:
        """Orchestrator info and version endpoints return 200."""
        info_resp = orchestrator_client.get("/info")
        assert info_resp.status_code == 200
        assert info_resp.json()
    
    def test_S2O_orchestrator_version(
        self, orchestrator_client: OrchestratorClient
    ) -> None:
        """Orchestrator version endpoint returns 200."""
        version_resp = orchestrator_client.get("/version")
        assert version_resp.status_code == 200
        assert version_resp.json()

    
