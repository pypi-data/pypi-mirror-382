"""
Basic Authentication handler for HTTP Basic Auth.
"""

import base64
from typing import Dict, Optional
from .base_auth import BaseAuthHandler
from ..utils.logger import get_logger


class BasicAuthCredentials:
    """Credentials for Basic Authentication."""
    
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password


class BasicAuthHandler(BaseAuthHandler):
    """
    Handle HTTP Basic Authentication.
    
    Encodes username:password in base64 and sends as Authorization header.
    """
    
    def __init__(self, username: str, password: str):
        """
        Initialize Basic Auth handler.
        
        Args:
            username: Username for authentication
            password: Password for authentication
        """
        credentials = BasicAuthCredentials(username, password)
        super().__init__(credentials)
        self.logger = get_logger(self.__class__.__name__)
        
        if not username or not password:
            raise ValueError("Both username and password are required for Basic Auth")
    
    async def get_auth_headers(self) -> Dict[str, str]:
        """
        Get authentication headers for Basic Auth.
        
        Returns:
            Dictionary with Authorization header containing base64 encoded credentials
        """
        try:
            # Encode username:password in base64
            credentials = f"{self.credentials.username}:{self.credentials.password}"
            encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('ascii')
            
            return {
                "Authorization": f"Basic {encoded_credentials}"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create Basic Auth headers: {str(e)}")
            raise
    
    async def refresh_credentials(self) -> bool:
        """
        Basic Auth doesn't support credential refresh.
        
        Returns:
            False (Basic Auth credentials cannot be refreshed)
        """
        return False  # Basic Auth doesn't support refresh
    
    def is_authenticated(self) -> bool:
        """
        Check if handler has valid credentials.
        
        Returns:
            True if username and password are available
        """
        return bool(self.credentials.username and self.credentials.password)
    
    async def handle_auth_error(self, status_code: int, response_text: str) -> bool:
        """
        Handle authentication errors.
        
        Basic Auth typically doesn't support token refresh, so return False.
        
        Args:
            status_code: HTTP status code
            response_text: Response body text
            
        Returns:
            False (Basic Auth doesn't support refresh)
        """
        self.logger.warning(f"Basic Auth failed with status {status_code}: {response_text}")
        return False  # Basic Auth cannot be refreshed
    
    def get_auth_info(self) -> Dict[str, str]:
        """
        Get authentication information for debugging.
        
        Returns:
            Dictionary with auth type and username (password masked)
        """
        return {
            "auth_type": "basic",
            "username": self.credentials.username,
            "password": "***masked***",
            "authenticated": str(self.is_authenticated())
        } 