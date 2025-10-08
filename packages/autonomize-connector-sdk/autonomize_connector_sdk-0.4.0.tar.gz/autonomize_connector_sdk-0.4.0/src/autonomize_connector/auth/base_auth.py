"""
Base authentication handler interface.
All authentication methods inherit from this class.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseAuthHandler(ABC):
    """Abstract base class for all authentication handlers."""
    
    def __init__(self, credentials: Any):
        """Initialize with credentials."""
        self.credentials = credentials
    
    @abstractmethod
    async def get_auth_headers(self) -> Dict[str, str]:
        """
        Get authentication headers for HTTP requests.
        
        Returns:
            Dict containing authentication headers
        """
        pass
    
    @abstractmethod
    async def refresh_credentials(self) -> bool:
        """
        Refresh authentication credentials if needed.
        
        Returns:
            True if refresh was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def is_authenticated(self) -> bool:
        """
        Check if current credentials are valid.
        
        Returns:
            True if authenticated, False otherwise
        """
        pass
    
    async def prepare_request_headers(self, additional_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """
        Prepare complete headers for a request including authentication.
        
        Args:
            additional_headers: Optional additional headers to include
            
        Returns:
            Complete headers dictionary
        """
        # Start with auth headers
        headers = await self.get_auth_headers()
        
        # Add standard headers
        headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'Autonomize-Connector-SDK/1.0.0'
        })
        
        # Add any additional headers
        if additional_headers:
            headers.update(additional_headers)
        
        return headers
    
    async def handle_auth_error(self, status_code: int, response_text: str) -> bool:
        """
        Handle authentication errors and attempt recovery.
        
        Args:
            status_code: HTTP status code of the failed request
            response_text: Response text from the failed request
            
        Returns:
            True if recovery was attempted, False if no recovery possible
        """
        if status_code in [401, 403]:
            # Try to refresh credentials
            return await self.refresh_credentials()
        
        return False 