"""
Environment helpers for FAAS QA Testing
"""

import os
from typing import Optional


def get_base_url(environment: Optional[str] = None) -> str:
    """
    Get base URL for the specified environment
    
    Args:
        environment: Environment name ('dev', 'uat', 'prod'). 
                    If None, uses BASE_URL env var or defaults to dev.
    
    Returns:
        Base URL string
    """
    if environment:
        return f'https://{environment}.api.rcdevops.co.za'
    
    return os.getenv('BASE_URL', 'https://uat.api.rcdevops.co.za')


def get_environment() -> str:
    """
    Get current environment name from BASE_URL
    
    Returns:
        Environment name ('dev', 'uat', 'prod', or 'unknown')
    """
    base_url = os.getenv('BASE_URL', 'https://uat.api.rcdevops.co.za')
    
    if 'dev.api' in base_url:
        return 'dev'
    elif 'uat.api' in base_url:
        return 'uat'
    elif 'prod.api' in base_url or 'api.rcdevops.co.za' in base_url:
        return 'prod'
    else:
        return 'unknown'


def is_ci() -> bool:
    """
    Check if running in CI environment
    
    Returns:
        True if in CI, False otherwise
    """
    return os.getenv('CI', '').lower() in ('true', '1', 'yes')


def is_local() -> bool:
    """
    Check if running locally (not in CI)
    
    Returns:
        True if running locally, False otherwise
    """
    return not is_ci()
