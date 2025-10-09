"""
Core Recruitee API client.
"""

import requests
from typing import Union, List, Dict, Any, Optional, Literal
from brynq_sdk_brynq import BrynQ


class Recruitee(BrynQ):
    """
    Core client for interacting with the Recruitee API.

    This is the base client that provides low-level access to the Recruitee API.
    For specific API endpoints, use the specialized classes like Candidates, Offers, and Organization.

    Args:
        label: Label or list of labels for credentials
        api_type: Type of API to use (default: "API")
    """
    def __init__(self, system_type: Optional[Literal['source', 'target']] = None):
        super().__init__()
        self.timeout = 3600
        credentials = self.interfaces.credentials.get(system="recruitee", system_type=system_type)
        credentials = credentials.get('data')
        self.base_url = f'https://api.recruitee.com/c/{credentials["company_id"]}/'
        self.headers = {
            "Authorization": f"Bearer {credentials['token']}",
            "Content-Type": "application/json",
            "x-recruitee-partner-name": "brynq",
            "x-recruitee-partner-id": "86bza977z"
        }

    def get(self, endpoint: str, params: Optional[Dict] = None) -> requests.Response:
        """
        Make a GET request to the Recruitee API.

        Args:
            endpoint: API endpoint to call
            params: Optional parameters to include in the request

        Returns:
            Response from the API
        """
        url = f"{self.base_url}{endpoint}"
        response = requests.get(url=url,
                                headers=self.headers,
                                params=params,
                                timeout=self.timeout)
        response.raise_for_status()
        return response

    def post(self, endpoint: str, json: Optional[Dict] = None) -> requests.Response:
        """
        Make a POST request to the Recruitee API.

        Args:
            endpoint: API endpoint to call
            json: Optional JSON data to include in the request

        Returns:
            Response from the API
        """
        url = f"{self.base_url}{endpoint}"
        return requests.post(url=url,
                             headers=self.headers,
                             json=json,
                             timeout=self.timeout)

    def patch(self, endpoint: str, json: Optional[Dict] = None) -> requests.Response:
        """
        Make a PATCH request to the Recruitee API.

        Args:
            endpoint: API endpoint to call
            json: Optional JSON data to include in the request

        Returns:
            Response from the API
        """
        url = f"{self.base_url}{endpoint}"
        return requests.patch(url=url,
                              headers=self.headers,
                              json=json,
                              timeout=self.timeout)

    def delete(self, endpoint: str) -> requests.Response:
        """
        Make a DELETE request to the Recruitee API.

        Args:
            endpoint: API endpoint to call

        Returns:
            Response from the API
        """
        url = f"{self.base_url}{endpoint}"
        return requests.delete(url=url,
                               headers=self.headers,
                               timeout=self.timeout)
