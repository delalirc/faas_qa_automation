"""
Test Data Generators for FAAS QA Testing

Provides utilities for generating realistic test data.
"""

from decimal import Decimal
from uuid import uuid4
from typing import Dict, Any, Optional
from datetime import datetime


def generate_test_merchant(overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Generate test merchant data

    Args:
        overrides: Optional dict to override default values

    Returns:
        Merchant data dictionary
    """
    merchant = {
        'id': str(uuid4()),
        'name': f'Test Merchant {uuid4().hex[:8]}',
        'email': f'test.merchant.{uuid4().hex[:8]}@qa.faas.local',
        'phone': '+27800000000',
        'trading_name': f'Test Trading {uuid4().hex[:8]}',
        'business_type': 'Sole Proprietor',
        'registration_number': f'TEST{uuid4().hex[:8].upper()}',
    }

    if overrides:
        merchant.update(overrides)

    return merchant


def generate_test_offer(
    partner_id: str,
    merchant_id: str,
    overrides: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generate test offer data

    Args:
        partner_id: Partner ID
        merchant_id: Merchant ID
        overrides: Optional dict to override default values

    Returns:
        Offer data dictionary
    """
    offer = {
        'partner_id': partner_id,
        'merchant_id': merchant_id,
        'amount': Decimal('50000'),
        'term': 12,
        'payback_percentage': Decimal('10'),
        'collection_type': 'SPLIT_PROCESSING',
    }

    if overrides:
        offer.update(overrides)

    return offer


def generate_test_partner(overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Generate test partner data

    Args:
        overrides: Optional dict to override default values

    Returns:
        Partner data dictionary
    """
    partner = {
        'id': str(uuid4()),
        'name': 'Test Partner',
        'configuration': {
            'collection_type': 'SPLIT_PROCESSING',
            'generate_documents': True,
            'integration_enabled': False,
        },
    }

    if overrides:
        partner.update(overrides)

    return partner


def generate_test_session(
    partner_id: str,
    merchant_id: Optional[str] = None,
    session_type: str = 'frontend',
    overrides: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generate test S2O session data

    Args:
        partner_id: Partner ID
        merchant_id: Optional merchant ID (generated if not provided)
        session_type: Session type ('frontend' or 'salesforce')
        overrides: Optional dict to override default values

    Returns:
        Session data dictionary
    """
    if not merchant_id:
        merchant_id = str(uuid4())

    session = {
        'partner_id': partner_id,
        'merchant_id': merchant_id,
        'application_id': f'app-{datetime.now().strftime("%Y%m%d%H%M%S")}-{uuid4().hex[:8]}',
        'session_type': session_type,
    }

    if overrides:
        session.update(overrides)

    return session


def generate_test_contract(
    offer_id: str,
    partner_id: str,
    merchant_id: str,
    overrides: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generate test contract data

    Args:
        offer_id: Offer ID
        partner_id: Partner ID
        merchant_id: Merchant ID
        overrides: Optional dict to override default values

    Returns:
        Contract data dictionary
    """
    contract = {
        'offer_id': offer_id,
        'partner_id': partner_id,
        'merchant_id': merchant_id,
        'external_status': 'SUBMITTED',
        'internal_status': 'SUBMITTED',
        'balance': Decimal('50000'),
    }

    if overrides:
        contract.update(overrides)

    return contract
