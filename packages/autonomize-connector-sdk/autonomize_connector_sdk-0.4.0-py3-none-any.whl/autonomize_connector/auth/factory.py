"""
Authentication factory for creating appropriate auth handlers.
"""

from typing import Union, Any
from .oauth2 import OAuth2Handler
from .api_key import APIKeyHandler
from .base_auth import BaseAuthHandler
from ..utils.env_manager import OAuth2Credentials, APIKeyCredentials
from ..core.exceptions import ConfigurationError

class AuthFactory:
    """Factory for creating authentication handlers."""
    
    @staticmethod
    def create(credentials: Union[OAuth2Credentials, APIKeyCredentials, dict]) -> BaseAuthHandler:
        """
        Create appropriate authentication handler based on credentials type.
        
        Args:
            credentials: Credentials object or dictionary
            
        Returns:
            Appropriate authentication handler instance
            
        Raises:
            ConfigurationError: If credentials type is not supported
        """
        if isinstance(credentials, OAuth2Credentials):
            return OAuth2Handler(credentials)
        
        elif isinstance(credentials, APIKeyCredentials):
            return APIKeyHandler(credentials)
        
        elif isinstance(credentials, dict):
            # Try to determine auth type from dictionary
            return AuthFactory._create_from_dict(credentials)
        
        else:
            raise ConfigurationError(
                f"Unsupported credentials type: {type(credentials)}. "
                f"Supported types: OAuth2Credentials, APIKeyCredentials, or dict"
            )
    
    @staticmethod
    def _create_from_dict(credentials: dict) -> BaseAuthHandler:
        """
        Create auth handler from dictionary credentials.
        
        Args:
            credentials: Dictionary containing credential information
            
        Returns:
            Appropriate authentication handler
            
        Raises:
            ConfigurationError: If dict format is not recognized
        """
        # Check for OAuth2 pattern
        if all(key in credentials for key in ['client_id', 'client_secret', 'token_url']):
            oauth2_creds = OAuth2Credentials(
                client_id=credentials['client_id'],
                client_secret=credentials['client_secret'],
                token_url=credentials['token_url'],
                scope=credentials.get('scope')
            )
            return OAuth2Handler(oauth2_creds)
        
        # Check for API key pattern
        elif 'api_key' in credentials:
            api_key_creds = APIKeyCredentials(
                api_key=credentials['api_key'],
                header_name=credentials.get('header_name', 'X-API-Key')
            )
            return APIKeyHandler(api_key_creds)
        
        # Check for alternative API key patterns
        elif 'key' in credentials:
            api_key_creds = APIKeyCredentials(
                api_key=credentials['key'],
                header_name=credentials.get('header_name', 'X-API-Key')
            )
            return APIKeyHandler(api_key_creds)
        
        else:
            raise ConfigurationError(
                "Could not determine authentication type from credentials dictionary. "
                "Expected OAuth2 format: {client_id, client_secret, token_url, [scope]} "
                "or API Key format: {api_key, [header_name]}"
            )
    
    @staticmethod
    def create_oauth2(client_id: str, client_secret: str, token_url: str, scope: str = None) -> OAuth2Handler:
        """
        Convenience method to create OAuth2 handler.
        
        Args:
            client_id: OAuth2 client ID
            client_secret: OAuth2 client secret
            token_url: OAuth2 token endpoint URL
            scope: Optional OAuth2 scope
            
        Returns:
            OAuth2Handler instance
        """
        credentials = OAuth2Credentials(
            client_id=client_id,
            client_secret=client_secret,
            token_url=token_url,
            scope=scope
        )
        return OAuth2Handler(credentials)
    
    @staticmethod
    def create_api_key(api_key: str, header_name: str = "X-API-Key") -> APIKeyHandler:
        """
        Convenience method to create API Key handler.
        
        Args:
            api_key: API key value
            header_name: Header name for the API key (default: X-API-Key)
            
        Returns:
            APIKeyHandler instance
        """
        credentials = APIKeyCredentials(
            api_key=api_key,
            header_name=header_name
        )
        return APIKeyHandler(credentials) 