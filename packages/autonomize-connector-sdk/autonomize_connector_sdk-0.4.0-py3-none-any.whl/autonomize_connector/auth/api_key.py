"""
API Key authentication handler for APIs using simple API key authentication.
"""

from typing import Dict
from .base_auth import BaseAuthHandler
from ..utils.env_manager import APIKeyCredentials

class APIKeyHandler(BaseAuthHandler):
    """API Key authentication handler."""
    
    def __init__(self, credentials: APIKeyCredentials):
        """
        Initialize API Key handler.
        
        Args:
            credentials: API key credentials containing api_key and header_name
        """
        super().__init__(credentials)
    
    async def get_auth_headers(self) -> Dict[str, str]:
        """
        Get authentication headers with API key and any additional headers.
        
        Returns:
            Dictionary with API key header and additional headers
        """
        # Format the API key value using the template
        formatted_value = self.credentials.header_format.format(api_key=self.credentials.api_key)
        
        # Start with the main API key header
        headers = {
            self.credentials.header_name: formatted_value
        }
        
        # Add any additional headers
        if self.credentials.additional_headers:
            headers.update(self.credentials.additional_headers)
        
        return headers
    
    async def refresh_credentials(self) -> bool:
        """
        API keys don't typically need refreshing.
        
        Returns:
            Always True for API keys
        """
        return True
    
    def is_authenticated(self) -> bool:
        """
        Check if we have a valid API key.
        
        Returns:
            True if we have an API key, False otherwise
        """
        return bool(self.credentials.api_key)
    
    async def handle_auth_error(self, status_code: int, response_text: str) -> bool:
        """
        Handle authentication errors for API key auth.
        
        API keys can't be refreshed, so we just return False for auth errors.
        
        Args:
            status_code: HTTP status code of the failed request
            response_text: Response text from the failed request
            
        Returns:
            Always False since API keys can't be refreshed
        """
        return False
    
    def get_auth_info(self) -> Dict[str, str]:
        """
        Get authentication information for debugging.
        
        Returns:
            Dictionary with auth type and API key info (sensitive data masked)
        """
        # Mask API key - show first 8 chars and last 4 chars
        api_key = self.credentials.api_key or "None"
        if len(api_key) > 12:
            masked_key = api_key[:8] + "***" + api_key[-4:]
        elif len(api_key) > 8:
            masked_key = api_key[:4] + "***" + api_key[-2:]
        else:
            masked_key = "***masked***"
        
        return {
            "auth_type": "api_key",
            "api_key": masked_key,
            "header_name": self.credentials.header_name,
            "header_format": self.credentials.header_format,
            "additional_headers_count": len(self.credentials.additional_headers) if self.credentials.additional_headers else 0,
            "authenticated": str(self.is_authenticated())
        } 