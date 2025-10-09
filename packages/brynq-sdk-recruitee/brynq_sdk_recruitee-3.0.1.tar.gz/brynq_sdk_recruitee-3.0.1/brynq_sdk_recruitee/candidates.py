"""
Candidates API module for Recruitee.
"""
from typing import Dict, Optional, List, Union
import requests


class Candidates:
    """
    Class for interacting with Recruitee candidates API.
    
    This class provides methods for managing candidates in Recruitee.
    """
    def __init__(self, recruitee_client):
        """
        Initialize the Candidates API client.
        
        Args:
            recruitee_client: An instance of the Recruitee client
        """
        self.client = recruitee_client

    def get_candidates(self, filters: Optional[Dict] = None) -> requests.Response:
        """
        Get all candidates from Recruitee.
        
        Args:
            filters: Optional filters to apply
            
        Returns:
            Response from the API
        """
        return self.client.get(
            endpoint="candidates",
            params=filters
        )
    
    def get_candidate(self, candidate_id: str) -> requests.Response:
        """
        Get a specific candidate from Recruitee.
        
        Args:
            candidate_id: The ID of the candidate
            
        Returns:
            Response from the API
        """
        return self.client.get(
            endpoint=f"candidates/{candidate_id}"
        )
    
    def get_candidate_details(self, candidate_id: str) -> requests.Response:
        """
        Get detailed information about a specific candidate from Recruitee.
        This is an alias for get_candidate for backward compatibility.
        
        Args:
            candidate_id: The ID of the candidate
            
        Returns:
            Response from the API
        """
        return self.get_candidate(candidate_id)
    
    def patch_bulk_candidates_tags(self, data: Dict) -> requests.Response:
        """
        Update tags for multiple candidates.
        
        Args:
            data: Dictionary containing candidates and tags
            
        Returns:
            Response from the API
        """
        return self.client.patch(
            endpoint="bulk/candidates/tags",
            json=data
        )
    
    def update_candidate_tags(self, candidate_ids: List[str], tags: List[str]) -> requests.Response:
        """
        Update tags for multiple candidates.
        
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
        return self.patch_bulk_candidates_tags(data)
    
    def update_rehire_tags(self, candidate_ids: List[str], tags: List[str]) -> requests.Response:
        """
        Update rehire-related tags for multiple candidates.
        This is an alias for update_candidate_tags for backward compatibility.
        
        Args:
            candidate_ids: List of candidate IDs
            tags: List of tags to add
            
        Returns:
            Response from the API
        """
        return self.update_candidate_tags(candidate_ids, tags)
    
    def get_mailbox(self, candidate_id: str) -> requests.Response:
        """
        Get the mailbox for a specific candidate.
        
        Args:
            candidate_id: The ID of the candidate
            
        Returns:
            Response from the API
        """
        return self.client.get(
            endpoint=f"mailbox/candidate/{candidate_id}"
        ) 