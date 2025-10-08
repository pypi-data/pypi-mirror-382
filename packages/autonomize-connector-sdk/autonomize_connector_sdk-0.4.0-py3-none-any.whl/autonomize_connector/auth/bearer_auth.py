"""
Bearer Token Authentication handler.
"""

from typing import Dict, Optional
from .base_auth import BaseAuthHandler
from ..utils.logger import get_logger


class BearerTokenCredentials:
    """Credentials for Bearer Token Authentication."""
    
    def __init__(self, token: str, token_prefix: str = "Bearer"):
        self.token = token
        self.token_prefix = token_prefix


class BearerTokenHandler(BaseAuthHandler):
    """
    Handle Bearer Token Authentication.
    
    Sends token as Authorization: Bearer <token> header.
    """
    
    def __init__(self, token: str, token_prefix: str = "Bearer"):
        """
        Initialize Bearer Token handler.
        
        Args:
            token: Bearer token for authentication
            token_prefix: Prefix for the token (default: "Bearer")
        """
        credentials = BearerTokenCredentials(token, token_prefix)
        super().__init__(credentials)
        self.logger = get_logger(self.__class__.__name__)
        
        if not token:
            raise ValueError("Token is required for Bearer Token auth")
    
    async def get_auth_headers(self) -> Dict[str, str]:
        """
        Get authentication headers for Bearer Token.
        
        Returns:
            Dictionary with Authorization header containing bearer token
        """
        try:
            return {
                "Authorization": f"{self.credentials.token_prefix} {self.credentials.token}"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create Bearer Token headers: {str(e)}")
            raise
    
    async def refresh_credentials(self) -> bool:
        """
        Bearer tokens typically don't support refresh.
        
        Returns:
            False (Bearer tokens usually cannot be refreshed)
        """
        return False  # Bearer tokens typically cannot be refreshed
    
    def is_authenticated(self) -> bool:
        """
        Check if handler has valid token.
        
        Returns:
            True if token is available
        """
        return bool(self.credentials.token)
    
    async def handle_auth_error(self, status_code: int, response_text: str) -> bool:
        """
        Handle authentication errors.
        
        Bearer tokens typically don't support refresh, so return False.
        
        Args:
            status_code: HTTP status code
            response_text: Response body text
            
        Returns:
            False (Bearer tokens usually cannot be refreshed)
        """
        self.logger.warning(f"Bearer Token auth failed with status {status_code}: {response_text}")
        return False  # Bearer tokens typically cannot be refreshed
    
    def get_auth_info(self) -> Dict[str, str]:
        """
        Get authentication information for debugging.
        
        Returns:
            Dictionary with auth type and token info (token masked)
        """
        token = self.credentials.token
        return {
            "auth_type": "bearer",
            "token_prefix": self.credentials.token_prefix,
            "token": f"***{token[-4:] if len(token) > 4 else '***'}",
            "authenticated": str(self.is_authenticated())
        } 