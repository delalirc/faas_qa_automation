"""
Shared pytest configuration and fixtures for FAAS QA tests
"""

from datetime import datetime
import os, boto3
from pathlib import Path
from uuid import UUID, uuid5, NAMESPACE_URL
import pytest
from framework.api.clients.s2o.orchestrator import OrchestratorClient
from framework.api.clients.s2o.doc2data import Doc2DataClient


@pytest.fixture
def orchestrator_client(base_url: str, auth_token: str | None) -> OrchestratorClient:
    """Orchestrator (S2O) service client fixture"""
    return OrchestratorClient(base_url=base_url, token=auth_token)


@pytest.fixture
def doc2data_client(base_url: str, auth_token: str | None) -> Doc2DataClient:
    """Doc2Data service client fixture"""
    return Doc2DataClient(base_url=base_url, token=auth_token)


@pytest.fixture
def s2o_partner_ids() -> dict[str, UUID]:
    """Test partners and their IDs (fixture version for use in tests)"""
    prefix = "test-partner"
    return {
        f"{prefix}-success": build_id(f"{prefix}-success"),
        f"{prefix}-failure": build_id(f"{prefix}-failure"),
        f"{prefix}-not-found": build_id(f"{prefix}-not-found"),
        f"{prefix}-journey": build_id(f"{prefix}-journey"),
    }


@pytest.fixture
def s2o_merchant_ids() -> dict[str, UUID]:
    """Test merchant IDs for S2O"""
    prefix = "test-merchant"
    return {
        f"{prefix}-success": build_id(f"{prefix}-success"),
        f"{prefix}-failure": build_id(f"{prefix}-failure"),
        f"{prefix}-not-found": build_id(f"{prefix}-not-found"),
        f"{prefix}-journey": build_id(f"{prefix}-journey"),
    }


@pytest.fixture
def s2o_application_ids() -> dict[str, str]:
    """Test application IDs for S2O"""
    prefix = "test-application"
    return {
        f"{prefix}-success": f"Appl-{build_id(f'{prefix}-success')}",
        f"{prefix}-failure": f"Appl-{build_id(f'{prefix}-failure')}",
        f"{prefix}-not-found": f"Appl-{build_id(f'{prefix}-not-found')}",
        f"{prefix}-journey": f"Appl-{build_id(f'{prefix}-journey')}",
    }


def build_id(prefix: str) -> UUID:
    return uuid5(NAMESPACE_URL, f"{prefix}-{datetime.today()}")


def list_asset_filenames() -> list[str]:
    """List all filenames in the assets directory"""
    return [f.name for f in (Path(__file__).parent / "assets").iterdir()]


def get_filenames() -> list[str]:
    """Map identifiers to bank statement filenames."""
    return [
        "30_Aug_2025_-_(Free)..A1IjTVRWBldUSRkkFwBQSAsBdBZSAQRTU0wQIxQDA0xXUiV_v1.pdf",
        "Aug_2025_Fnb_v1.pdf",
        "BS_Kevana_Group_19_Aug_2025_Absa_pw_4108795464_v1.pdf",
        "BS_Kevana_Group_19_Dec_2025_Absa_pw_4108795464_v1.pdf",
        "BS_Kevana_Group_19_Jan_2026_Absa_pw_4108795464_v1.pdf",
        "BS_Kevana_Group_19_Nov_2025_Absa_pw_4108795464_v1.pdf",
        "BS_Kevana_Group_19_Oct_2025_Absa_pw_4108795464_v1.pdf",
        "BS_Kevana_Group_19_Sept_2025_Absa_pw_4108795464_v1.pdf",
        "BS_Tiger_Wheel_and_Tyre_Aug_2025_v1.pdf",
        "Capitec_01_August_2025_to_31_August_2025_v1.pdf",
        "Statement_1088395317_01Aug2025-17Jan2026_v1.pdf",
    ]


@pytest.fixture(scope="session")
def s2o_presigned_urls() -> dict[str, str]:
    """Get presigned URL for bank statement"""
    result: dict[str, str] = {}
    for filename in get_filenames():
        bucket_name = (
            os.getenv("S3_BUCKET_ORCHESTRATOR") or "rc-faas-s2o-orchestrator-uat"
        )
        s3_client = boto3.client("s3")
        presigned_url = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket_name, "Key": f"tests/{filename}"},
            ExpiresIn=3600,
        )
        result[filename] = presigned_url
    return result
