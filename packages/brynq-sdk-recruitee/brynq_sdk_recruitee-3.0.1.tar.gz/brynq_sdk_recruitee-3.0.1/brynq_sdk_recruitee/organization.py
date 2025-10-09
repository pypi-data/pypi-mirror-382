"""
Organization API module for Recruitee.
"""
from typing import Dict, Optional, List, Union
import requests


class Organization:
    """
    Class for interacting with Recruitee organization API.
    
    This class provides methods for managing organization entities in Recruitee,
    including locations, departments, and companies.
    """
    def __init__(self, recruitee_client):
        """
        Initialize the Organization API client.
        
        Args:
            recruitee_client: An instance of the Recruitee client
        """
        self.client = recruitee_client

    # Locations methods
    def get_locations(self, filters: Optional[Dict] = None) -> requests.Response:
        """
        Get locations data from Recruitee.
        
        Args:
            filters: Optional filters to apply
            
        Returns:
            Response from the API
        """
        return self.client.get(
            endpoint="locations",
            params=filters
        )
    
    # Departments methods
    def get_departments(self, filters: Optional[Dict] = None) -> requests.Response:
        """
        Get departments data from Recruitee.
        
        Args:
            filters: Optional filters to apply
            
        Returns:
            Response from the API
        """
        return self.client.get(
            endpoint="departments",
            params=filters
        )
    
    # Companies methods
    def get_companies(self, filters: Optional[Dict] = None) -> requests.Response:
        """
        Get companies data from Recruitee.
        
        Args:
            filters: Optional filters to apply
            
        Returns:
            Response from the API
        """
        return self.client.get(
            endpoint="",
            params=filters
        )
    
    # Memberships methods
    def get_memberships(self, filters: Optional[Dict] = None) -> requests.Response:
        """
        Get memberships data from Recruitee.
        
        Args:
            filters: Optional filters to apply
            
        Returns:
            Response from the API
        """
        return self.client.get(
            endpoint="memberships",
            params=filters
        ) 