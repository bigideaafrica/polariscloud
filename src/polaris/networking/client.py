"""
Networking client for Polaris.

This module provides client functionality for network operations.
"""

import requests
from requests.exceptions import RequestException

from polaris.utils.logging import get_logger

# Initialize logger
logger = get_logger('network')


class NetworkClient:
    """
    Network client for Polaris
    
    This class handles network operations for the Polaris project.
    """
    
    def __init__(self, base_url=None, timeout=30):
        """
        Initialize network client
        
        Args:
            base_url (str, optional): Base URL for API requests
            timeout (int): Request timeout in seconds
        """
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
    
    def get(self, endpoint, params=None, headers=None):
        """
        Perform a GET request
        
        Args:
            endpoint (str): API endpoint
            params (dict, optional): Query parameters
            headers (dict, optional): Request headers
            
        Returns:
            dict: Response data or None if request failed
        """
        url = self._build_url(endpoint)
        try:
            response = self.session.get(
                url,
                params=params,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            logger.error(f"GET request failed: {str(e)}")
            return None
    
    def post(self, endpoint, data=None, json=None, headers=None):
        """
        Perform a POST request
        
        Args:
            endpoint (str): API endpoint
            data (dict, optional): Form data
            json (dict, optional): JSON data
            headers (dict, optional): Request headers
            
        Returns:
            dict: Response data or None if request failed
        """
        url = self._build_url(endpoint)
        try:
            response = self.session.post(
                url,
                data=data,
                json=json,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            logger.error(f"POST request failed: {str(e)}")
            return None
    
    def _build_url(self, endpoint):
        """
        Build a full URL from the endpoint
        
        Args:
            endpoint (str): API endpoint
            
        Returns:
            str: Full URL
        """
        if self.base_url:
            return f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        return endpoint 