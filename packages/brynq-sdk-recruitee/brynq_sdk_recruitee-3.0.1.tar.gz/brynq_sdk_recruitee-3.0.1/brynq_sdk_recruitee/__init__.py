"""
Recruitee SDK for Python
~~~~~~~~~~~~~~~~~~~~~~~

A Python SDK for interacting with the Recruitee API.

This SDK provides a clean, modular interface to the Recruitee API with specialized
modules for different aspects of the API (candidates, offers, organization, etc.).
"""

from typing import Dict, Any
import requests
from .recruitee import Recruitee
from .candidates import Candidates
from .offers import Offers
from .organization import Organization
from .vacancies import Vacancies
from .applicants import Applicants

__version__ = '1.0.0'
__author__ = 'BrynQ'
__license__ = 'BrynQ License'

class RecruiteeError(Exception):
    """Base exception for Recruitee SDK errors."""
    pass

class RecruiteeAuthError(RecruiteeError):
    """Raised when there are authentication issues."""
    pass

class RecruiteeConfigError(RecruiteeError):
    """Raised when there are configuration issues."""
    pass

def validate_credentials(credentials: Dict[str, Any]) -> None:
    """
    Validate the credentials dictionary has required fields.
    
    Args:
        credentials: Dictionary containing credentials
        
    Raises:
        RecruiteeConfigError: If required credentials are missing
    """
    required_fields = ['company_id', 'token']
    missing_fields = [field for field in required_fields if field not in credentials]
    
    if missing_fields:
        raise RecruiteeConfigError(
            f"Missing required credentials: {', '.join(missing_fields)}"
        )

# Export all classes
__all__ = [
    'Recruitee',
    'Candidates',
    'Offers',
    'Organization',
    'Vacancies',
    'Applicants',
    'RecruiteeError',
    'RecruiteeAuthError',
    'RecruiteeConfigError',
    'validate_credentials'
]