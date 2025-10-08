"""
Dynamic Connector Registration System
Handles JSON-based connector definitions and generates connector classes at runtime.
"""

import json
import re
import os
from typing import Dict, Any, List, Optional, Type
from pathlib import Path

from ..auth import OAuth2Handler, APIKeyHandler, BasicAuthHandler, BearerTokenHandler, CustomHeadersHandler
from ..core.base_connector import BaseConnector
from ..utils.env_manager import ConnectorConfig, APIKeyCredentials, OAuth2Credentials
from ..utils.logger import get_logger


class DynamicConnector(BaseConnector):
    """
    Dynamically generated connector from JSON configuration.
    Provides all operations defined in the connector JSON config.
    """
    
    def __init__(self, config: ConnectorConfig, auth_handler, connector_def: Dict[str, Any], **kwargs):
        """Initialize dynamic connector with JSON definition."""
        self.connector_def = connector_def
        self.connector_name = connector_def['name']
        self.endpoints = connector_def.get('endpoints', {})
        
        # Extract name from kwargs or use connector name
        connector_name = kwargs.pop('name', self.connector_name)
        super().__init__(config, auth_handler, name=connector_name, **kwargs)
        
        # Generate methods for each endpoint
        self._generate_endpoint_methods()
        
        self.logger.info(f"Dynamic connector '{self.connector_name}' initialized with {len(self.endpoints)} endpoints")
    
    def _get_service_name(self) -> str:
        """Return the service name for URL building."""
        return self.connector_def.get('service_name', self.connector_name)
    
    def _get_service_params(self) -> Dict[str, Any]:
        """Get service-specific parameters for URL building."""
        return self.connector_def.get('service_params', {})
    
    def _get_query_params(self) -> Dict[str, Any]:
        """Get default query parameters."""
        return self.connector_def.get('default_query_params', {})
    
    def _generate_endpoint_methods(self):
        """Dynamically generate methods for each endpoint."""
        for operation_name, endpoint_config in self.endpoints.items():
            # Create method dynamically
            method = self._create_endpoint_method(operation_name, endpoint_config)
            setattr(self, operation_name, method)
    
    def _create_endpoint_method(self, operation_name: str, endpoint_config: Dict[str, Any]):
        """Create a method for a specific endpoint."""
        async def endpoint_method(self, **kwargs):
            """
            Execute {operation_name} operation.
            
            Endpoint: {method} {path}
            
            Args:
                **kwargs: Request parameters (data, params, path_params)
                
            Returns:
                API response
            """.format(
                operation_name=operation_name,
                method=endpoint_config.get('method', 'GET'),
                path=endpoint_config.get('path', '/')
            )
            return await self._execute_endpoint(operation_name, endpoint_config, **kwargs)
        
        # Set method name and docstring
        endpoint_method.__name__ = operation_name
        endpoint_method.__doc__ = f"""
        Execute {operation_name} operation.
        
        Endpoint: {endpoint_config.get('method', 'GET')} {endpoint_config.get('path', '')}
        
        Args:
            **kwargs: Request parameters (data, params, path_params)
            
        Returns:
            API response
        """
        
        # Bind method to instance
        return endpoint_method.__get__(self, type(self))
    
    async def _execute_endpoint(self, operation_name: str, endpoint_config: Dict[str, Any], **kwargs):
        """Execute a specific endpoint operation."""
        try:
            # Extract parameters
            data = kwargs.get('data')
            params = kwargs.get('params')
            path_params = kwargs.get('path_params', {})
            
            # Merge with service params for path substitution
            all_path_params = {**self._get_service_params(), **path_params}
            
            # Build endpoint path with parameter substitution
            endpoint_path = endpoint_config['path']
            if all_path_params:
                endpoint_path = self._replace_path_params(endpoint_path, all_path_params)
            
            # Get method and other config
            method = endpoint_config.get('method', 'GET').upper()
            timeout = endpoint_config.get('timeout')
            retry_config = endpoint_config.get('retry', {})
            ssl_verify = endpoint_config.get('ssl_verify')
            headers = endpoint_config.get('headers')

            # Merge query parameters (handle None values)
            query_params = self._get_query_params() or {}
            params = params or {}
            final_params = {**query_params, **params}
            
            # Build complete URL directly from config (bypass central system for dynamic connectors)
            from urllib.parse import urlencode

            # Build base URL + endpoint path
            base_url = self.config.base_url.rstrip('/')
            endpoint_path = endpoint_path.lstrip('/')
            url = f"{base_url}/{endpoint_path}"
            
            # Add query parameters if any
            if final_params:
                # Filter out None values
                clean_params = {k: v for k, v in final_params.items() if v is not None}
                if clean_params:
                    url += '?' + urlencode(clean_params)
            
            # Execute request using the complete URL
            response = await self.execute_request(
                method=method,
                url=url,
                data=data,
                headers=headers,
                retry_count=retry_config.get('max_attempts', 3),
                ssl_verify=ssl_verify
            )
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error executing {operation_name}: {str(e)}")
            raise
    
    def _replace_path_params(self, path: str, path_params: Dict[str, Any]) -> str:
        """Replace path parameters in URL path."""
        for key, value in path_params.items():
            path = path.replace(f'{{{key}}}', str(value))
        return path
    

    
    def get_connector_info(self) -> Dict[str, Any]:
        """Get information about this connector."""
        return {
            "name": self.connector_name,
            "display_name": self.connector_def.get('display_name', self.connector_name),
            "base_url": self.connector_def.get('base_url'),
            "auth_type": self.connector_def.get('auth', {}).get('type'),
            "endpoints": list(self.endpoints.keys()),
            "operations_count": len(self.endpoints)
        }


class ConnectorRegistry:
    """
    Registry for managing dynamically registered connectors.
    Handles JSON config parsing, validation, and connector instantiation.
    """
    
    def __init__(self):
        """Initialize the connector registry."""
        self.registered_connectors: Dict[str, Dict[str, Any]] = {}
        self.logger = get_logger(self.__class__.__name__)
    
    def register_connector(self, connector_config: Dict[str, Any]) -> None:
        """
        Register a connector from JSON configuration.
        
        Args:
            connector_config: Complete connector configuration
            
        Raises:
            ValueError: If configuration is invalid
        """
        # Validate required fields
        self._validate_connector_config(connector_config)
        
        # Process environment variables
        processed_config = self._process_env_variables(connector_config)
        
        connector_name = processed_config['name']
        self.registered_connectors[connector_name] = processed_config
        
        self.logger.info(f"Registered connector: {connector_name}")
    
    def register_from_file(self, config_path: str) -> None:
        """
        Register connector from JSON file.
        
        Args:
            config_path: Path to JSON configuration file
        """
        config_path = Path(config_path)
        if not config_path.exists():
            raise FileNotFoundError(f"Connector config file not found: {config_path}")
        
        with open(config_path, 'r') as f:
            connector_config = json.load(f)
        
        self.register_connector(connector_config)
    
    def create_connector(self, connector_name: str, config: ConnectorConfig = None, **kwargs) -> DynamicConnector:
        """
        Create a connector instance from registry.
        
        Args:
            connector_name: Name of registered connector
            config: Optional connector configuration
            **kwargs: Additional arguments
            
        Returns:
            DynamicConnector instance
            
        Raises:
            ValueError: If connector not registered
        """
        if connector_name not in self.registered_connectors:
            available = list(self.registered_connectors.keys())
            raise ValueError(f"Connector '{connector_name}' not registered. Available: {available}")
        
        connector_def = self.registered_connectors[connector_name]
        
        # Create configuration if not provided
        if config is None:
            config = self._create_config_from_definition(connector_def)
        
        # Create auth handler
        auth_handler = self._create_auth_handler(connector_def)
        
        # Create and return dynamic connector
        return DynamicConnector(config, auth_handler, connector_def, **kwargs)
    
    def list_registered_connectors(self) -> List[str]:
        """Get list of registered connector names."""
        return list(self.registered_connectors.keys())
    
    def get_connector_info(self, connector_name: str) -> Dict[str, Any]:
        """Get information about a registered connector."""
        if connector_name not in self.registered_connectors:
            raise ValueError(f"Connector '{connector_name}' not registered")
        
        connector_def = self.registered_connectors[connector_name]
        return {
            "name": connector_name,
            "display_name": connector_def.get('display_name', connector_name),
            "base_url": connector_def.get('base_url'),
            "auth_type": connector_def.get('auth', {}).get('type'),
            "endpoints": connector_def.get('endpoints', {}),  # ✅ Return full dict, not list
            "validation": connector_def.get('validation', {}),  # ✅ Include validation schemas
            "service_params": connector_def.get('service_params', {}),  # ✅ Include service params
            "default_query_params": connector_def.get('default_query_params', {}),  # ✅ Include query params
            "operations_count": len(connector_def.get('endpoints', {}))
        }
    
    def _validate_connector_config(self, config: Dict[str, Any]) -> None:
        """Validate connector configuration."""
        required_fields = ['name', 'base_url', 'auth', 'endpoints']
        
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Required field '{field}' missing in connector config")
        
        # Validate auth config
        auth_config = config['auth']
        if 'type' not in auth_config:
            raise ValueError("Auth type is required")
        
        # Validate endpoints
        endpoints = config['endpoints']
        if not isinstance(endpoints, dict) or len(endpoints) == 0:
            raise ValueError("At least one endpoint must be defined")
        
        for endpoint_name, endpoint_config in endpoints.items():
            if 'path' not in endpoint_config:
                raise ValueError(f"Endpoint '{endpoint_name}' missing required 'path' field")
    
    def _process_env_variables(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Process environment variables in configuration."""
        config_str = json.dumps(config)
        
        # Replace {{VAR_NAME}} with environment variables
        pattern = re.compile(r'\{\{(.*?)\}\}')
        
        def replacer(match):
            var_name = match.group(1).strip()
            return os.getenv(var_name, f'{{{{{var_name}}}}}')
        
        processed_str = pattern.sub(replacer, config_str)
        return json.loads(processed_str)
    
    def _create_config_from_definition(self, connector_def: Dict[str, Any]) -> ConnectorConfig:
        """Create ConnectorConfig from connector definition."""
        return ConnectorConfig(
            base_url=connector_def.get('base_url'),
            timeout=connector_def.get('timeout', 30),
            rate_limit=connector_def.get('rate_limit', 100)
        )
    
    def _create_auth_handler(self, connector_def: Dict[str, Any]):
        """Create appropriate auth handler based on configuration."""
        auth_config = connector_def['auth']
        auth_type = auth_config['type'].lower()
        
        if auth_type == 'oauth2':
            return self._create_oauth2_handler(auth_config)
        elif auth_type == 'api_key':
            return self._create_api_key_handler(auth_config, connector_def)
        elif auth_type == 'basic':
            return self._create_basic_auth_handler(auth_config)
        elif auth_type == 'bearer':
            return self._create_bearer_handler(auth_config)
        elif auth_type == 'custom':
            return self._create_custom_headers_handler(auth_config)
        else:
            available_types = ['oauth2', 'api_key', 'basic', 'bearer', 'custom']
            raise ValueError(f"Unsupported auth type: {auth_type}. Available: {available_types}")
    
    def _create_oauth2_handler(self, auth_config: Dict[str, Any]) -> OAuth2Handler:
        """Create OAuth2 handler from configuration."""
        credentials = OAuth2Credentials(
            client_id=os.getenv(auth_config.get('client_id_env', 'CLIENT_ID')),
            client_secret=os.getenv(auth_config.get('client_secret_env', 'CLIENT_SECRET')),
            token_url=auth_config.get('token_url'),
            scope=auth_config.get('scope', 'openid')
        )
        return OAuth2Handler(credentials)
    
    def _create_api_key_handler(self, auth_config: Dict[str, Any], connector_def: Dict[str, Any]) -> APIKeyHandler:
        """Create API Key handler from configuration."""
        api_key = os.getenv(auth_config.get('api_key_env', 'API_KEY'))
        additional_headers = {}
        
        # Handle additional headers from auth config
        if 'additional_headers' in auth_config:
            for key, env_var in auth_config['additional_headers'].items():
                additional_headers[key] = os.getenv(env_var)
        
        # For Azure OpenAI, use the correct header name and format
        if 'azure_openai' in connector_def['name'].lower():
            header_name = "api-key"
            header_format = "{api_key}"
        else:
            header_name = "Authorization"
            header_format = "Bearer {api_key}"
        
        credentials = APIKeyCredentials(
            api_key=api_key,
            header_name=header_name,
            header_format=header_format,
            additional_headers=additional_headers
        )
        
        return APIKeyHandler(credentials)
    
    def _create_basic_auth_handler(self, auth_config: Dict[str, Any]) -> BasicAuthHandler:
        """Create Basic Auth handler from configuration."""
        username = os.getenv(auth_config.get('username_env', 'USERNAME'))
        password = os.getenv(auth_config.get('password_env', 'PASSWORD'))
        
        return BasicAuthHandler(username=username, password=password)
    
    def _create_bearer_handler(self, auth_config: Dict[str, Any]) -> BearerTokenHandler:
        """Create Bearer Token handler from configuration."""
        token = os.getenv(auth_config.get('token_env', 'BEARER_TOKEN'))
        token_prefix = auth_config.get('token_prefix', 'Bearer')
        
        return BearerTokenHandler(token=token, token_prefix=token_prefix)
    
    def _create_custom_headers_handler(self, auth_config: Dict[str, Any]) -> CustomHeadersHandler:
        """Create Custom Headers handler from configuration."""
        headers = auth_config.get('headers', {})
        
        # Process environment variables in header values
        processed_headers = {}
        for header_name, header_value in headers.items():
            if isinstance(header_value, str) and header_value.startswith('{{') and header_value.endswith('}}'):
                env_var = header_value[2:-2].strip()
                processed_headers[header_name] = f"{{{{{env_var}}}}}"
            else:
                processed_headers[header_name] = header_value
        
        return CustomHeadersHandler(headers=processed_headers)


# Global registry instance
_registry = ConnectorRegistry()

# Public API functions
def register_connector(connector_config: Dict[str, Any]) -> None:
    """Register a connector from JSON configuration."""
    _registry.register_connector(connector_config)

def register_from_file(config_path: str) -> None:
    """Register connector from JSON file."""
    _registry.register_from_file(config_path)

def create_connector(connector_name: str, config: ConnectorConfig = None, **kwargs) -> DynamicConnector:
    """Create a registered connector instance."""
    return _registry.create_connector(connector_name, config, **kwargs)

def list_registered_connectors() -> List[str]:
    """Get list of registered connector names."""
    return _registry.list_registered_connectors()

def get_connector_info(connector_name: str) -> Dict[str, Any]:
    """Get information about a registered connector."""
    return _registry.get_connector_info(connector_name) 