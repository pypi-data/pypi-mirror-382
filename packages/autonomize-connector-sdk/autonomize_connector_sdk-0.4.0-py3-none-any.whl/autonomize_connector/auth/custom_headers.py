"""
Custom Headers Authentication handler.
"""

import os
from typing import Dict, Optional
from .base_auth import BaseAuthHandler
from ..utils.logger import get_logger


class CustomHeadersCredentials:
    """Credentials for Custom Headers Authentication."""
    
    def __init__(self, headers: Dict[str, str]):
        self.headers = headers


class CustomHeadersHandler(BaseAuthHandler):
    """
    Handle Custom Headers Authentication.
    
    Allows flexible header-based authentication patterns.
    """
    
    def __init__(self, headers: Dict[str, str]):
        """
        Initialize Custom Headers handler.
        
        Args:
            headers: Dictionary of header names to values or env var names
                    Values can be:
                    - Direct strings: "my-api-key-value"
                    - Environment variable references: "{{API_KEY}}"
        """
        credentials = CustomHeadersCredentials(headers)
        super().__init__(credentials)
        self.logger = get_logger(self.__class__.__name__)
        
        if not headers:
            raise ValueError("At least one header is required for Custom Headers auth")
    
    def _resolve_header_value(self, value: str) -> str:
        """
        Resolve header value, expanding environment variables if needed.
        
        Args:
            value: Header value (can contain {{ENV_VAR}} patterns)
            
        Returns:
            Resolved header value
        """
        # Check if value is an environment variable reference
        if value.startswith('{{') and value.endswith('}}'):
            env_var = value[2:-2].strip()
            resolved_value = os.getenv(env_var)
            if resolved_value is None:
                self.logger.warning(f"Environment variable {env_var} not found")
                return value  # Return original if env var not found
            return resolved_value
        
        return value
    
    async def get_auth_headers(self) -> Dict[str, str]:
        """
        Get authentication headers with resolved values.
        
        Returns:
            Dictionary with custom headers
        """
        try:
            resolved_headers = {}
            
            for header_name, header_value in self.credentials.headers.items():
                resolved_value = self._resolve_header_value(header_value)
                resolved_headers[header_name] = resolved_value
            
            return resolved_headers
            
        except Exception as e:
            self.logger.error(f"Failed to create Custom Headers: {str(e)}")
            raise
    
    async def refresh_credentials(self) -> bool:
        """
        Custom headers typically don't support refresh.
        
        Returns:
            False (Custom headers usually cannot be refreshed)
        """
        return False  # Custom headers typically cannot be refreshed
    
    def is_authenticated(self) -> bool:
        """
        Check if handler has valid headers.
        
        Returns:
            True if headers are configured
        """
        return bool(self.credentials.headers)
    
    async def handle_auth_error(self, status_code: int, response_text: str) -> bool:
        """
        Handle authentication errors.
        
        Custom headers typically don't support refresh, so return False.
        
        Args:
            status_code: HTTP status code
            response_text: Response body text
            
        Returns:
            False (Custom headers usually cannot be refreshed)
        """
        self.logger.warning(f"Custom Headers auth failed with status {status_code}: {response_text}")
        return False  # Custom headers typically cannot be refreshed
    
    def get_auth_info(self) -> Dict[str, str]:
        """
        Get authentication information for debugging.
        
        Returns:
            Dictionary with auth type and header info (values masked)
        """
        masked_headers = {}
        for key, value in self.credentials.headers.items():
            if len(value) > 8:
                masked_headers[key] = f"{value[:4]}***{value[-4:]}"
            else:
                masked_headers[key] = "***masked***"
        
        return {
            "auth_type": "custom_headers",
            "headers": masked_headers,
            "header_count": str(len(self.credentials.headers)),
            "authenticated": str(self.is_authenticated())
        } 