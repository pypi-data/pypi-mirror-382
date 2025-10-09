"""
Offers API module for Recruitee.
"""
from typing import Dict, Optional, List, Union
import requests


class Offers:
    """
    Class for interacting with Recruitee offers API.
    
    This class provides methods for managing offers in Recruitee.
    """
    def __init__(self, recruitee_client):
        """
        Initialize the Offers API client.
        
        Args:
            recruitee_client: An instance of the Recruitee client
        """
        self.client = recruitee_client

    def get_offers(self, filters: Optional[Dict] = None) -> requests.Response:
        """
        Get all offers from Recruitee.
        
        Args:
            filters: Optional filters to apply
            
        Returns:
            Response from the API
        """
        return self.client.get(
            endpoint="offers",
            params=filters
        )
    
    def get_offer(self, offer_id: str, filters: Optional[Dict] = None) -> requests.Response:
        """
        Get a specific offer from Recruitee.
        
        Args:
            offer_id: The ID of the offer
            filters: Optional filters to apply
            
        Returns:
            Response from the API
        """
        return self.client.get(
            endpoint=f"offers/{offer_id}",
            params=filters
        )
    
    def create_offer(self, title: str, description: str, **kwargs) -> requests.Response:
        """
        Create a new offer in Recruitee.
        
        Args:
            title: The title of the offer
            description: The description of the offer
            **kwargs: Additional offer attributes (recruiter_id, hiring_manager_id, etc.)
            
        Returns:
            Response from the API
        """
        data = {
            'offer': {
                'title': title,
                'description': description,
                **kwargs
            }
        }
        return self.post_offer(data)
    
    def update_offer(self, offer_id: str, data: Dict) -> requests.Response:
        """
        Update an existing offer in Recruitee.
        
        Args:
            offer_id: The ID of the offer
            data: The data to update
            
        Returns:
            Response from the API
        """
        return self.patch_offer(offer_id, data)
    
    def post_offer(self, data: Dict) -> requests.Response:
        """
        Create a new offer in Recruitee.
        
        Args:
            data: The offer data
            
        Returns:
            Response from the API
        """
        return self.client.post(
            endpoint="offers",
            json=data
        )
    
    def patch_offer(self, offer_id: str, data: Dict) -> requests.Response:
        """
        Update an existing offer in Recruitee.
        
        Args:
            offer_id: The ID of the offer
            data: The data to update
            
        Returns:
            Response from the API
        """
        return self.client.patch(
            endpoint=f"offers/{offer_id}",
            json=data
        )
    
    def delete_offer(self, offer_id: str) -> requests.Response:
        """
        Delete an offer from Recruitee.
        
        Args:
            offer_id: The ID of the offer
            
        Returns:
            Response from the API
        """
        return self.client.delete(
            endpoint=f"offers/{offer_id}"
        )
    
    def patch_offer_slug(self, offer_id: str, data: Dict) -> requests.Response:
        """
        Update an offer's slug in Recruitee.
        
        Args:
            offer_id: The ID of the offer
            data: The data to update
            
        Returns:
            Response from the API
        """
        return self.client.patch(
            endpoint=f"offers/{offer_id}/change_slug",
            json=data
        )
    
    def post_add_offer_tag(self, offer_id: str, data: Dict) -> requests.Response:
        """
        Add a tag to an offer.
        
        Args:
            offer_id: The ID of the offer
            data: The tag data
            
        Returns:
            Response from the API
        """
        return self.client.post(
            endpoint=f"offers/{offer_id}/offer_tags",
            json=data
        )
    
    def patch_publish_offer(self, offer_id: str) -> requests.Response:
        """
        Publish an offer.
        
        Args:
            offer_id: The ID of the offer
            
        Returns:
            Response from the API
        """
        return self.client.patch(
            endpoint=f"offers/{offer_id}/publish"
        )
    
    def patch_unpublish_offer(self, offer_id: str) -> requests.Response:
        """
        Unpublish an offer.
        
        Args:
            offer_id: The ID of the offer
            
        Returns:
            Response from the API
        """
        return self.client.patch(
            endpoint=f"offers/{offer_id}/unpublish"
        ) 