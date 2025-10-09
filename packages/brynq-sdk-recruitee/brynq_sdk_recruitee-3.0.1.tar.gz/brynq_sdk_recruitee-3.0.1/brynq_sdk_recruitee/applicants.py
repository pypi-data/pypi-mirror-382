"""
Applicants API module for Recruitee.
"""
from typing import Dict, Optional, List, Union
import requests


class Applicants:
    """
    Class for interacting with Recruitee applicants API.
    
    This class provides methods for creating, updating, and managing applicants in Recruitee.
    """
    def __init__(self, recruitee_client):
        """
        Initialize the Applicants API client.
        
        Args:
            recruitee_client: An instance of the Recruitee client
        """
        self.client = recruitee_client

    def get_applicants(self, filters: Optional[Dict] = None) -> requests.Response:
        """
        Get all applicants from Recruitee.
        
        Args:
            filters: Optional filters to apply
            
        Returns:
            Response from the API
        """
        return self.client.get_candidates(filters=filters)
    
    def get_applicant(self, candidate_id: str) -> requests.Response:
        """
        Get a specific applicant from Recruitee.
        
        Args:
            candidate_id: The ID of the candidate
            
        Returns:
            Response from the API
        """
        return self.client.get_candidate(candidate_id=candidate_id)
    
    def update_applicant_tags(self, candidate_ids: List[str], tags: List[str]) -> requests.Response:
        """
        Update tags for multiple applicants.
        
        Args:
            candidate_ids: List of candidate IDs
            tags: List of tags to add
            
        Returns:
            Response from the API
        """
        data = {
            "candidates": candidate_ids,
            "tags": tags
        }
        return self.client.patch_bulk_candidates_tags(data=data)
    
    def get_applicant_mailbox(self, candidate_id: str) -> requests.Response:
        """
        Get the mailbox for a specific applicant.
        
        Args:
            candidate_id: The ID of the candidate
            
        Returns:
            Response from the API
        """
        return self.client.get_mailbox(candidate_id=candidate_id)
