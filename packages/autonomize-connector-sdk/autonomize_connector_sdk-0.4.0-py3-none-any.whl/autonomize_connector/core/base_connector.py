"""
Base connector class that provides common functionality for all API connectors.
Handles HTTP requests, authentication, error handling, retries, and more.
"""

import aiohttp
import asyncio
import json
from typing import Dict, Any, Optional, Union, List
from abc import ABC, abstractmethod
from urllib.parse import urljoin

from ..auth.base_auth import BaseAuthHandler
from ..utils.logger import get_logger
from ..utils.env_manager import ConnectorConfig
from .exceptions import APIError, AuthenticationError, create_jiva_exception
from .url_system import EndpointResolver

class BaseConnector(ABC):
    """
    Abstract base class for all API connectors.
    Provides common functionality like HTTP requests, authentication, and error handling.
    """
    
    def __init__(self, config: ConnectorConfig, auth_handler: BaseAuthHandler, name: str = None):
        """
        Initialize base connector.
        
        Args:
            config: Connector configuration
            auth_handler: Authentication handler
            name: Connector name for logging
        """
        self.config = config
        self.auth_handler = auth_handler
        self.name = name or self.__class__.__name__
        self.logger = get_logger(f'connector.{self.name.lower()}')
        
        # HTTP session configuration
        self.timeout = aiohttp.ClientTimeout(total=config.timeout)
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Central URL system
        self.endpoint_resolver = EndpointResolver()
        
        self.logger.info(f"Initialized {self.name} connector with base URL: {config.base_url}")
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self._ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def _ensure_session(self):
        """Ensure HTTP session is created."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=self.timeout,
                connector=aiohttp.TCPConnector(limit=100)
            )
    
    async def close(self):
        """Close HTTP session and cleanup resources."""
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None
    
    def _resolve_endpoint_url(
        self,
        operation: str,
        service_params: Optional[Dict[str, Any]] = None,
        query_params: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Resolve endpoint URL using the central URL system.
        
        Args:
            operation: Operation name (e.g., 'chat_completion', 'create_contact')
            service_params: Service-specific parameters (e.g., deployment for Azure OpenAI)
            query_params: Query parameters to append
            
        Returns:
            Complete URL for the operation
        """
        service_name = self._get_service_name()
        
        return self.endpoint_resolver.resolve_endpoint_simple(
            service_name=service_name,
            operation=operation,
            base_url=self.config.base_url,
            service_params=service_params or {},
            query_params=query_params
        )
    
    def _get_service_name(self) -> str:
        """
        Get the service name for URL resolution.
        Subclasses can override this to specify their service name.
        
        Returns:
            Service name for URL resolution
        """
        # Default: use the connector name in lowercase
        # Subclasses should override this for specific service names
        return self.name.lower().replace('connector', '').replace('jiva', 'jiva')
    
    async def execute_request(
        self,
        method: str,
        endpoint: str = None,
        url: str = None,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        retry_count: Optional[int] = None,
        retryable_status_codes: Optional[List[int]] = None,
        ssl_verify: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Execute HTTP request with authentication, error handling, and retries.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint: API endpoint (relative to base URL) - use this OR url
            url: Complete URL - use this OR endpoint  
            data: Request body data
            params: Query parameters
            headers: Additional headers
            retry_count: Number of retries (defaults to config)
            retryable_status_codes: HTTP status codes that should trigger retries
            ssl_verify: SSL certificate verification (True/False, defaults to True)
            
        Returns:
            Response data as dictionary
            
        Raises:
            APIError: If request fails
            AuthenticationError: If authentication fails
        """
        await self._ensure_session()
        
        # Build full URL - support both endpoint and url patterns
        if url:
            # Use the provided complete URL
            request_url = url
        elif endpoint:
            # Build URL from base_url + endpoint
            request_url = urljoin(self.config.base_url.rstrip('/') + '/', endpoint.lstrip('/'))
        else:
            raise ValueError("Either 'endpoint' or 'url' parameter must be provided")
        
        # Prepare headers
        request_headers = await self.auth_handler.prepare_request_headers(headers)
        
        # Set retry count
        max_retries = retry_count if retry_count is not None else self.config.retry_count
        
        # Set retryable status codes (allow connectors to customize)
        default_retryable_codes = [408, 429, 502, 503, 504]
        retry_codes = retryable_status_codes if retryable_status_codes is not None else default_retryable_codes
        
        self.logger.debug(f"Making {method} request to {request_url}")
        
        for attempt in range(max_retries + 1):
            try:
                async with self.session.request(
                    method=method,
                    url=request_url,
                    json=data,
                    params=params,
                    headers=request_headers,
                    ssl=ssl_verify
                ) as response:
                    
                    response_text = await response.text()
                    
                    # Handle successful responses
                    if 200 <= response.status < 300:
                        return await self._process_successful_response(response, response_text)
                    
                    # Handle authentication errors
                    if response.status in [401, 403]:
                        if await self._handle_auth_error(response.status, response_text, attempt, max_retries):
                            # Update headers with refreshed token
                            request_headers = await self.auth_handler.prepare_request_headers(headers)
                            continue
                    
                    # Handle retryable errors
                    if response.status in retry_codes and attempt < max_retries:
                        wait_time = 2 ** attempt  # Exponential backoff
                        self.logger.warning(f"Retryable error {response.status}, retrying in {wait_time}s...")
                        await asyncio.sleep(wait_time)
                        continue
                    
                    # Handle other errors
                    await self._handle_api_error(response.status, response_text, request_url, method)
                    
            except aiohttp.ClientError as e:
                if attempt < max_retries:
                    wait_time = 2 ** attempt  # Exponential backoff
                    self.logger.warning(f"Request failed, retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    raise APIError(f"HTTP request failed after {max_retries + 1} attempts: {str(e)}")
            
            except Exception as e:
                self.logger.error(f"Unexpected error during request: {str(e)}")
                raise APIError(f"Unexpected error: {str(e)}")
        
        # Should not reach here
        raise APIError("Request failed after all retry attempts")
    
    async def _process_successful_response(self, response: aiohttp.ClientResponse, response_text: str) -> Dict[str, Any]:
        """Process successful HTTP response."""
        if response.content_type and 'application/json' in response.content_type:
            try:
                return json.loads(response_text) if response_text else {}
            except json.JSONDecodeError as e:
                self.logger.warning(f"Failed to parse JSON response: {str(e)}")
                return {'raw_response': response_text}
        else:
            # Non-JSON response
            return {'raw_response': response_text, 'content_type': response.content_type}
    
    async def _handle_auth_error(self, status_code: int, response_text: str, attempt: int, max_retries: int) -> bool:
        """
        Handle authentication errors and attempt recovery.
        
        Returns:
            True if recovery was attempted and should retry, False otherwise
        """
        if attempt < max_retries:
            self.logger.warning(f"Authentication error (status {status_code}), attempting to refresh credentials...")
            
            if await self.auth_handler.handle_auth_error(status_code, response_text):
                self.logger.info("Successfully refreshed authentication credentials")
                return True
            else:
                self.logger.error("Failed to refresh authentication credentials")
        
        raise AuthenticationError(f"Authentication failed: {response_text}")
    
    async def _handle_api_error(self, status_code: int, response_text: str, url: str, method: str):
        """Handle API errors and create appropriate exceptions."""
        self.logger.error(f"API error: {method} {url} returned {status_code}: {response_text}")
        
        # Try to create specific exception based on connector type
        try:
            if 'jiva' in self.name.lower():
                raise create_jiva_exception(status_code, response_text)
        except Exception:
            pass
        
        # Fallback to generic API error
        raise APIError(f"API request failed with status {status_code}: {response_text}", status_code=status_code)
    
    # Convenience methods for common HTTP operations
    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Execute GET request."""
        return await self.execute_request('GET', endpoint, params=params, **kwargs)
    
    async def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Execute POST request."""
        return await self.execute_request('POST', endpoint, data=data, **kwargs)
    
    async def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Execute PUT request."""
        return await self.execute_request('PUT', endpoint, data=data, **kwargs)
    
    async def delete(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Execute DELETE request."""
        return await self.execute_request('DELETE', endpoint, **kwargs)
    
    async def patch(self, endpoint: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Execute PATCH request."""
        return await self.execute_request('PATCH', endpoint, data=data, **kwargs)
    

    
    def get_connector_info(self) -> Dict[str, Any]:
        """
        Get connector information for debugging.
        
        Returns:
            Dictionary with connector status and configuration
        """
        return {
            'name': self.name,
            'base_url': self.config.base_url,
            'timeout': self.config.timeout,
            'retry_count': self.config.retry_count,
            'rate_limit': self.config.rate_limit,
            'authenticated': self.auth_handler.is_authenticated() if self.auth_handler else False,
            'session_active': self.session is not None and not self.session.closed
        } 