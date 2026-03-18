"""
Shared API Client for FAAS QA Testing

Provides a consistent interface for making API calls in tests.
"""

import requests
from typing import Any
import os


class APIClient:
    """Generic API client for testing FAAS services"""

    def __init__(self, base_url: str, token: str | None = None):
        """
        Initialize API client

        Args:
            base_url: Base URL for the service (e.g., 'https://dev.api.rcdevops.co.za/offer')
            token: Optional authentication token
        """
        self.base_url = base_url.rstrip('/')
        self.token = token or os.getenv('AUTH_TOKEN')
        self.session = requests.Session()

        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        })

        if self.token:
            self.session.headers.update({
                'Authorization': f'Bearer {self.token}',
            })

    def get(self, path: str, **kwargs: Any) -> requests.Response:
        """Make GET request"""
        url = f'{self.base_url}{path}' if not path.startswith('http') else path
        return self.session.get(url, **kwargs)

    def post(self, path: str, data: Any = None, **kwargs: Any) -> requests.Response:
        """Make POST request"""
        url = f'{self.base_url}{path}' if not path.startswith('http') else path
        return self.session.post(url, json=data, **kwargs)

    def put(self, path: str, data: Any = None, **kwargs: Any) -> requests.Response:
        """Make PUT request"""
        url = f'{self.base_url}{path}' if not path.startswith('http') else path
        return self.session.put(url, json=data, **kwargs)

    def patch(self, path: str, data: Any = None, **kwargs: Any) -> requests.Response:
        """Make PATCH request"""
        url = f'{self.base_url}{path}' if not path.startswith('http') else path
        return self.session.patch(url, json=data, **kwargs)

    def delete(self, path: str, **kwargs: Any) -> requests.Response:
        """Make DELETE request"""
        url = f'{self.base_url}{path}' if not path.startswith('http') else path
        return self.session.delete(url, **kwargs)

    def set_token(self, token: str) -> None:
        """Update authentication token"""
        self.token = token
        self.session.headers.update({
            'Authorization': f'Bearer {token}',
        })


class ServiceClient(APIClient):
    """Base class for service-specific API clients"""

    def __init__(self, service_name: str, base_url: str | None = None, token: str | None = None):
        """
        Initialize service-specific client

        Args:
            service_name: Name of the service (e.g., 'offer', 'contract')
            base_url: Optional base URL, defaults to environment variable
            token: Optional authentication token
        """
        if not base_url:
            base_url = os.getenv('BASE_URL', 'https://dev.api.rcdevops.co.za')

        super().__init__(f'{base_url}/{service_name}', token)
        self.service_name = service_name






