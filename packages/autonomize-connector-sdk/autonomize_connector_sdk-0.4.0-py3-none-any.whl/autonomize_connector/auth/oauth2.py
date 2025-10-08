"""
OAuth2 authentication handler for APIs using OAuth 2.0.
Handles token acquisition, refresh, and automatic retry on auth failures.
"""

import aiohttp
import time
import asyncio
from typing import Dict, Optional
from .base_auth import BaseAuthHandler
from ..utils.env_manager import OAuth2Credentials
from ..core.exceptions import AuthenticationError

class OAuth2Handler(BaseAuthHandler):
    """OAuth2 authentication handler for client credentials flow."""
    
    def __init__(self, credentials: OAuth2Credentials):
        """
        Initialize OAuth2 handler.
        
        Args:
            credentials: OAuth2 credentials containing client_id, client_secret, token_url
        """
        super().__init__(credentials)
        self.access_token: Optional[str] = None
        self.token_expiry: Optional[float] = None
        self.token_type: str = "Bearer"
        self._refresh_lock = asyncio.Lock()
    
    async def get_auth_headers(self) -> Dict[str, str]:
        """
        Get authentication headers with valid access token.
        
        Returns:
            Dictionary with Authorization header
        """
        if self.is_token_expired():
            await self.refresh_credentials()
        
        if not self.access_token:
            raise AuthenticationError("No valid access token available")
        
        return {
            'Authorization': f'{self.token_type} {self.access_token}'
        }
    
    async def refresh_credentials(self) -> bool:
        """
        Refresh OAuth2 access token using client credentials flow.
        
        Returns:
            True if token refresh was successful, False otherwise
        """
        async with self._refresh_lock:
            # Check if another coroutine already refreshed the token
            if not self.is_token_expired():
                return True
            
            try:
                await self._request_new_token()
                return True
            except Exception as e:
                raise AuthenticationError(f"Failed to refresh OAuth2 token: {str(e)}")
    
    def is_authenticated(self) -> bool:
        """
        Check if we have a valid access token.
        
        Returns:
            True if we have a valid token, False otherwise
        """
        return self.access_token is not None and not self.is_token_expired()
    
    def is_token_expired(self) -> bool:
        """
        Check if the current token is expired or will expire soon.
        
        Returns:
            True if token is expired or will expire within 5 minutes
        """
        if not self.token_expiry:
            return True
        
        # Consider token expired 5 minutes before actual expiry for safety
        safety_margin = 300  # 5 minutes
        return time.time() >= (self.token_expiry - safety_margin)
    
    async def _request_new_token(self) -> None:
        """
        Request a new access token from the OAuth2 provider.
        
        Raises:
            AuthenticationError: If token request fails
        """
        # Prepare token request data
        token_data = {
            'grant_type': 'client_credentials',
            'client_id': self.credentials.client_id,
            'client_secret': self.credentials.client_secret
        }
        
        # Add scope if provided
        if self.credentials.scope:
            token_data['scope'] = self.credentials.scope
        
        # Request headers
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json'
        }
        
        # Make token request
        timeout = aiohttp.ClientTimeout(total=30)
        
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    self.credentials.token_url,
                    data=token_data,
                    headers=headers
                ) as response:
                    
                    response_text = await response.text()
                    
                    if response.status == 200:
                        await self._process_token_response(response_text)
                    else:
                        raise AuthenticationError(
                            f"OAuth2 token request failed with status {response.status}: {response_text}"
                        )
                        
        except aiohttp.ClientError as e:
            raise AuthenticationError(f"OAuth2 token request failed: {str(e)}")
    
    async def _process_token_response(self, response_text: str) -> None:
        """
        Process successful token response and store token details.
        
        Args:
            response_text: JSON response from token endpoint
        """
        try:
            import json
            token_response = json.loads(response_text)
            
            # Extract token information
            self.access_token = token_response.get('access_token')
            if not self.access_token:
                raise AuthenticationError("No access_token in OAuth2 response")
            
            # Extract token type (default to Bearer)
            self.token_type = token_response.get('token_type', 'Bearer')
            
            # Calculate token expiry
            expires_in = token_response.get('expires_in', 3600)  # Default 1 hour
            self.token_expiry = time.time() + expires_in
            
        except json.JSONDecodeError as e:
            raise AuthenticationError(f"Invalid JSON in OAuth2 token response: {str(e)}")
    
    async def handle_auth_error(self, status_code: int, response_text: str) -> bool:
        """
        Handle authentication errors by attempting token refresh.
        
        Args:
            status_code: HTTP status code of the failed request
            response_text: Response text from the failed request
            
        Returns:
            True if token refresh was attempted, False otherwise
        """
        if status_code in [401, 403]:
            try:
                # Force token refresh
                self.access_token = None
                self.token_expiry = None
                await self.refresh_credentials()
                return True
            except AuthenticationError:
                return False
        
        return False
    
    def get_auth_info(self) -> Dict[str, str]:
        """
        Get authentication information for debugging.
        
        Returns:
            Dictionary with auth type and OAuth2 info (sensitive data masked)
        """
        return {
            "auth_type": "oauth2",
            "client_id": self.credentials.client_id[:8] + "..." if self.credentials.client_id else "None",
            "scope": self.credentials.scope or "None",
            "token_url": self.credentials.token_url or "None",
            "has_token": str(bool(self.access_token)),
            "token_expired": str(self.is_token_expired()),
            "authenticated": str(self.is_authenticated())
        }
    
    def get_token_info(self) -> Dict[str, any]:
        """
        Get current token information for debugging.
        
        Returns:
            Dictionary with token status information
        """
        return {
            'has_token': self.access_token is not None,
            'token_type': self.token_type,
            'expires_at': self.token_expiry,
            'is_expired': self.is_token_expired(),
            'time_to_expiry': (self.token_expiry - time.time()) if self.token_expiry else None
        } 