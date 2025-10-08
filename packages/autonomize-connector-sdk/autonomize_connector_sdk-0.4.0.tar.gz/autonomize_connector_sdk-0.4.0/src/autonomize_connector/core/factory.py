"""
Connector factory for creating and managing API connectors.
Main entry point for the Autonomize Connector SDK.
Now supports both legacy built-in connectors and dynamic JSON-based registration.
"""

import os
from typing import Dict, Type, Optional, Union, Any, List
from ..auth.factory import AuthFactory
from ..auth.base_auth import BaseAuthHandler
from ..utils.env_manager import env_manager, ConnectorConfig, OAuth2Credentials, APIKeyCredentials
from ..utils.logger import get_logger
from .base_connector import BaseConnector
from .exceptions import ConfigurationError
from .service_defaults import (
    get_service_defaults, 
    get_env_vars, 
    get_base_url_default,
    get_supported_services,
    is_service_supported,
    get_auth_type
)
from .registration import (
    create_connector as create_dynamic_connector,
    list_registered_connectors,
    register_connector as register_dynamic_connector,
    get_connector_info as get_dynamic_connector_info
)

class ConnectorFactory:
    """
    Factory for creating and managing API connectors.
    Handles both legacy class-based and new JSON-based dynamic registration.
    
    Simplified API with only essential methods:
    - register_connector(): Register new connector types (supports both legacy and JSON)
    - quick(): Quick connector creation with auto-detection (90% of users)
    - create(): Full control connector creation (10% of power users)
    """
    
    def __init__(self):
        """Initialize the connector factory."""
        self._legacy_connectors: Dict[str, Type[BaseConnector]] = {}
        self._legacy_configs: Dict[str, Dict[str, Any]] = {}
        self.logger = get_logger('connector.factory')
        
        self.logger.info("Initialized Connector Factory with dynamic registration support")
    
    def register_connector(
        self,
        name: str,
        connector_class: Optional[Type[BaseConnector]] = None,
        default_config: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Register a new connector type - supports both legacy and JSON-based registration.
        
        Args:
            name: Unique name for the connector
            connector_class: Connector class (legacy mode) or None (JSON mode)
            default_config: Configuration (legacy format or JSON connector definition)
        """
        # Check if this is JSON-based registration
        if (connector_class is None and default_config and 
            isinstance(default_config, dict) and 'endpoints' in default_config):
            # JSON-based registration
            json_config = {
                'name': name,
                **default_config
            }
            register_dynamic_connector(json_config)
            self.logger.info(f"Registered JSON-based connector: {name}")
            return
        
        # Legacy class-based registration
        if connector_class and not issubclass(connector_class, BaseConnector):
            raise ConfigurationError(f"Connector class must inherit from BaseConnector")
        
        if connector_class:
            self._legacy_connectors[name.lower()] = connector_class
        if default_config:
            self._legacy_configs[name.lower()] = default_config
        
        self.logger.info(f"Registered legacy connector: {name}")
    
    def quick(self, service_name: str, **overrides) -> BaseConnector:
        """
        Quick connector creation with auto-detection and intelligent defaults.
        This is the recommended method for 90% of users.
        
        Args:
            service_name: Name of the service connector to create
            **overrides: Optional parameter overrides
            
        Returns:
            Initialized connector instance
            
        Raises:
            ConfigurationError: If service not supported or credentials missing
            
        Example:
            # Works for any registered API
            contact_api = factory.quick('jiva_contact')
            azure_api = factory.quick('azure', timeout=60)
        """
        service_name_lower = service_name.lower()
        
        # Try dynamic registration first
        dynamic_connectors = list_registered_connectors()
        if service_name_lower in dynamic_connectors:
            try:
                # Use dynamic connector
                return create_dynamic_connector(service_name_lower)
            except Exception as e:
                self.logger.error(f"Failed to create dynamic connector {service_name}: {str(e)}")
                # Fall through to legacy system
        
        # Check if legacy connector is registered
        if service_name_lower not in self._legacy_connectors:
            available_legacy = list(self._legacy_connectors.keys())
            available_dynamic = dynamic_connectors
            available = available_legacy + available_dynamic
            raise ConfigurationError(
                f"Connector '{service_name}' is not registered. "
                f"Available connectors: {', '.join(available)}"
            )
        
        try:
            # Get service defaults for legacy connectors
            defaults = get_service_defaults(service_name)
            
            # Auto-detect and create credentials
            credentials = self._create_credentials_auto(service_name)
            
            # Create configuration with defaults + overrides
            config = self._create_config_with_defaults(service_name, defaults, overrides)
            
            # Create connector
            return self._instantiate_connector(service_name, credentials, config)
            
        except Exception as e:
            self.logger.error(f"Failed to create {service_name} connector: {str(e)}")
            raise ConfigurationError(
                f"Could not create {service_name} connector. "
                f"Please check your environment variables or use create() for manual setup. "
                f"Error: {str(e)}"
            )
    
    def create(
        self,
        name: str,
        credentials: Optional[Union[OAuth2Credentials, APIKeyCredentials, dict]] = None,
        config: Optional[ConnectorConfig] = None,
        **kwargs
    ) -> BaseConnector:
        """
        Create a connector instance with full control.
        This method is for power users who need manual configuration.
        
        Args:
            name: Name of the connector to create
            credentials: Authentication credentials (auto-loaded from env if not provided)
            config: Connector configuration (auto-loaded from env if not provided)
            **kwargs: Additional arguments passed to connector constructor
            
        Returns:
            Initialized connector instance
            
        Raises:
            ConfigurationError: If connector is not registered or configuration is invalid
        """
        name_lower = name.lower()
        
        # Try dynamic registration first
        dynamic_connectors = list_registered_connectors()
        if name_lower in dynamic_connectors:
            try:
                return create_dynamic_connector(name_lower, config, **kwargs)
            except Exception as e:
                self.logger.error(f"Failed to create dynamic connector {name}: {str(e)}")
                # Fall through to legacy system
        
        # Legacy connector system
        if name_lower not in self._legacy_connectors:
            available_legacy = list(self._legacy_connectors.keys())
            available_dynamic = dynamic_connectors
            available = available_legacy + available_dynamic
            raise ConfigurationError(
                f"Connector '{name}' is not registered. "
                f"Available connectors: {', '.join(available)}"
            )
        
        # Get connector class
        connector_class = self._legacy_connectors[name_lower]
        
        # Load credentials from environment if not provided
        if credentials is None:
            credentials = self._get_credentials_from_env(name_lower)
        
        # Load configuration from environment if not provided
        if config is None:
            config = self._get_config_from_env(name_lower)
        
        # Create authentication handler
        auth_handler = AuthFactory.create(credentials)
        
        # Create and return connector instance
        connector = connector_class(config, auth_handler, name=name, **kwargs)
        
        self.logger.info(f"Created {name} connector")
        return connector
    
    def list_connectors(self) -> Dict[str, Dict[str, Any]]:
        """
        List all registered connectors and their information.
        
        Returns:
            Dictionary with connector information
        """
        result = {}
        
        # List dynamic connectors
        dynamic_connectors = list_registered_connectors()
        for name in dynamic_connectors:
            try:
                info = get_dynamic_connector_info(name)
                result[name] = {
                    'type': 'dynamic',
                    'display_name': info.get('display_name', name),
                    'auth_type': info.get('auth_type', 'unknown'),
                    'operations_count': info.get('operations_count', 0),
                    'endpoints': info.get('endpoints', [])
                }
            except Exception as e:
                result[name] = {
                    'type': 'dynamic',
                    'error': str(e)
                }
        
        # List legacy connectors
        for name, connector_class in self._legacy_connectors.items():
            try:
                defaults = get_service_defaults(name)
                result[name] = {
                    'type': 'legacy',
                    'class': connector_class.__name__,
                    'auth_type': defaults.get('auth_type', 'unknown'),
                    'timeout': defaults.get('timeout', 30),
                    'supported': is_service_supported(name)
                }
            except Exception as e:
                result[name] = {
                    'type': 'legacy',
                    'class': connector_class.__name__,
                    'error': str(e)
                }
        
        return result
    
    # ========================================
    # INTERNAL HELPER METHODS
    # ========================================
    
    def _create_credentials_auto(self, service_name: str) -> Union[OAuth2Credentials, APIKeyCredentials, dict]:
        """
        Auto-detect and create credentials from environment variables using simplified pattern.
        
        Args:
            service_name: Name of the service
            
        Returns:
            Appropriate credentials object
            
        Raises:
            ConfigurationError: If no valid credentials found
        """
        auth_type = get_auth_type(service_name)
        env_vars = get_env_vars(service_name, auth_type)
        
        if not env_vars:
            raise ConfigurationError(f"No environment variable pattern found for {service_name}")
        
        if auth_type == 'oauth2':
            return self._create_oauth2_credentials(env_vars, service_name)
        elif auth_type == 'api_key':
            return self._create_api_key_credentials(env_vars)
        elif auth_type == 'mixed_auth':
            return self._create_mixed_auth_credentials(env_vars)
        elif auth_type == 'azure_custom':
            return self._create_azure_openai_credentials(env_vars)
        else:
            raise ConfigurationError(f"Unsupported auth type: {auth_type}")
    
    def _create_oauth2_credentials(self, env_vars: Dict[str, str], service_name: str) -> OAuth2Credentials:
        """Create OAuth2 credentials from environment variables."""
        client_id = os.getenv(env_vars.get('client_id'))
        client_secret = os.getenv(env_vars.get('client_secret'))
        base_url = os.getenv(env_vars.get('base_url')) or get_base_url_default(service_name)
        
        if not all([client_id, client_secret]):
            missing = []
            if not client_id:
                missing.append(env_vars.get('client_id'))
            if not client_secret:
                missing.append(env_vars.get('client_secret'))
            
            raise ConfigurationError(
                f"Missing required OAuth2 credentials for {service_name}. "
                f"Please set: {', '.join(missing)}"
            )
        
        # Generate token URL from base URL
        if base_url:
            if service_name.lower() == 'azure':
                # Azure requires tenant - try to get from environment
                tenant_id = os.getenv('AZURE_TENANT_ID')
                if tenant_id:
                    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
                else:
                    token_url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
            else:
                # Standard OAuth2 token URL pattern
                token_url = f"{base_url.rstrip('/')}/oauth/token"
        else:
            raise ConfigurationError(f"No base URL found for {service_name}")
        
        # Get scope from service defaults
        defaults = get_service_defaults(service_name)
        scope = defaults.get('scope')
        
        return OAuth2Credentials(
            client_id=client_id,
            client_secret=client_secret,
            token_url=token_url,
            scope=scope
        )
    
    def _create_api_key_credentials(self, env_vars: Dict[str, str]) -> APIKeyCredentials:
        """Create API key credentials from environment variables."""
        api_key = os.getenv(env_vars.get('api_key'))
        
        if not api_key:
            raise ConfigurationError(
                f"Missing required API key. Please set: {env_vars.get('api_key')}"
            )
        
        return APIKeyCredentials(
            api_key=api_key,
            header_name="Authorization",
            header_format="Bearer {api_key}"
        )
    
    def _create_mixed_auth_credentials(self, env_vars: Dict[str, str]) -> dict:
        """Create mixed auth credentials (like Salesforce) from environment variables."""
        credentials = {}
        required = ['client_id', 'client_secret', 'username', 'password']
        
        for field in required:
            env_var = env_vars.get(field)
            if env_var:
                value = os.getenv(env_var)
                if value:
                    credentials[field] = value
        
        missing = [env_vars[field] for field in required if field not in credentials]
        
        if missing:
            raise ConfigurationError(
                f"Missing required Salesforce credentials. Please set: {', '.join(missing)}"
            )
        
        return credentials
    
    def _create_azure_openai_credentials(self, env_vars: Dict[str, str]) -> APIKeyCredentials:
        """Create Azure OpenAI credentials from environment variables."""
        api_key = os.getenv(env_vars.get('api_key'))
        base_url = os.getenv(env_vars.get('base_url'))
        deployment = os.getenv(env_vars.get('deployment'))
        api_version = os.getenv(env_vars.get('api_version'))
        
        if not api_key:
            raise ConfigurationError(f"Missing required Azure OpenAI API key: {env_vars.get('api_key')}")
        if not base_url:
            raise ConfigurationError(f"Missing required Azure OpenAI base URL: {env_vars.get('base_url')}")
        
        # Store additional Azure OpenAI specific info in additional_headers for the connector to access
        additional_headers = {}
        if deployment:
            additional_headers['DEPLOYMENT'] = deployment
        if api_version:
            additional_headers['API_VERSION'] = api_version
        
        return APIKeyCredentials(
            api_key=api_key,
            header_name="api-key",
            header_format="{api_key}",
            additional_headers=additional_headers
        )
    
    def _create_config_with_defaults(
        self, 
        service_name: str, 
        defaults: Dict[str, Any], 
        overrides: Dict[str, Any]
    ) -> ConnectorConfig:
        """Create configuration with service defaults and user overrides."""
        
        # Start with service defaults
        config_params = {
            'timeout': defaults.get('timeout', 30),
            'retry_count': defaults.get('retry_count', 3),
            'rate_limit': defaults.get('rate_limit', 100)
        }
        
        # Get base URL
        base_url = overrides.get('base_url')
        if not base_url:
            # Try environment variable first
            env_vars = get_env_vars(service_name)
            if env_vars.get('base_url'):
                base_url = os.getenv(env_vars['base_url'])
            
            # Use smart default if still not found
            if not base_url:
                base_url = get_base_url_default(service_name)
        
        if not base_url:
            raise ConfigurationError(f"No base URL found for {service_name}")
        
        config_params['base_url'] = base_url
        
        # For Azure OpenAI, add deployment and api_version from environment if not in overrides
        if service_name.lower() == 'azure_openai':
            env_vars = get_env_vars(service_name)
            if 'deployment' not in overrides and env_vars.get('deployment'):
                deployment = os.getenv(env_vars['deployment'])
                if deployment:
                    config_params['deployment'] = deployment
            
            if 'api_version' not in overrides and env_vars.get('api_version'):
                api_version = os.getenv(env_vars['api_version'])
                if api_version:
                    config_params['api_version'] = api_version
        
        # Apply user overrides
        config_params.update(overrides)
        
        return ConnectorConfig(**config_params)
    
    def _instantiate_connector(
        self, 
        service_name: str, 
        credentials: Any, 
        config: ConnectorConfig
    ) -> BaseConnector:
        """Instantiate the connector with credentials and configuration."""
        connector_class = self._legacy_connectors[service_name.lower()]
        auth_handler = AuthFactory.create(credentials)
        
        connector = connector_class(config, auth_handler, name=service_name)
        self.logger.info(f"Successfully created {service_name} connector with auto-detection")
        
        return connector
    
    def _get_credentials_from_env(self, name: str) -> Union[OAuth2Credentials, APIKeyCredentials, dict]:
        """Get credentials from environment variables (backward compatibility)."""
        return self._create_credentials_auto(name)
    
    def _get_config_from_env(self, name: str) -> ConnectorConfig:
        """Get configuration from environment variables (backward compatibility)."""
        defaults = get_service_defaults(name)
        return self._create_config_with_defaults(name, defaults, {})

# Create global factory instance
connector_factory = ConnectorFactory() 