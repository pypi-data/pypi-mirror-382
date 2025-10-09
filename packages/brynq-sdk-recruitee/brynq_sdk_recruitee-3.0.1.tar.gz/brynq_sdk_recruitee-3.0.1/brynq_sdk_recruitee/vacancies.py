"""
Vacancies API module for Recruitee.
"""
from typing import Dict, Optional, List, Union
import requests

from .offers import Offers


class Vacancies:
    """
    Class for interacting with Recruitee vacancies API.
    
    This class provides methods for creating, updating, and managing vacancies in Recruitee.
    Operations are delegated to the Offers class for actual API interactions.
    """
    def __init__(self, recruitee_client):
        """
        Initialize the Vacancies API client.
        
        Args:
            recruitee_client: An instance of the Recruitee client
        """
        self.client = recruitee_client
        self.offers = Offers(recruitee_client)

    def create_vacancy(self, title: str, description: str, **kwargs) -> requests.Response:
        """
        Create a new vacancy in Recruitee.
        
        Args:
            title: The title of the vacancy
            description: The description of the vacancy
            **kwargs: Additional vacancy attributes (recruiter_id, hiring_manager_id, etc.)
            
        Returns:
            Response from the API
        """
        return self.offers.create_offer(title=title, description=description, **kwargs)
    
    def update_vacancy(self, offer_id: str, data: Dict) -> requests.Response:
        """
        Update an existing vacancy in Recruitee.
        
        Args:
            offer_id: The ID of the offer
            data: The data to update
            
        Returns:
            Response from the API
        """
        return self.offers.update_offer(offer_id=offer_id, data=data)
    
    def delete_vacancy(self, offer_id: str) -> requests.Response:
        """
        Delete a vacancy from Recruitee.
        
        Args:
            offer_id: The ID of the offer
            
        Returns:
            Response from the API
        """
        return self.offers.delete_offer(offer_id=offer_id)
    
    def get_vacancies(self, filters: Optional[Dict] = None) -> requests.Response:
        """
        Get all vacancies from Recruitee.
        
        Args:
            filters: Optional filters to apply
            
        Returns:
            Response from the API
        """
        return self.offers.get_offers(filters=filters)
    
    def get_vacancy(self, offer_id: str, filters: Optional[Dict] = None) -> requests.Response:
        """
        Get a specific vacancy from Recruitee.
        
        Args:
            offer_id: The ID of the offer
            filters: Optional filters to apply
            
        Returns:
            Response from the API
        """
        return self.offers.get_offer(offer_id=offer_id, filters=filters)