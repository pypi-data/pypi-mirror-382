"""
Environment manager for handling credentials and configuration.
Loads configuration from environment variables with validation.
"""

import os
from dataclasses import dataclass
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

@dataclass
class OAuth2Credentials:
    """OAuth2 credentials for API authentication."""
    client_id: str
    client_secret: str
    token_url: str
    scope: Optional[str] = None

@dataclass
class APIKeyCredentials:
    """API Key credentials for API authentication with support for custom headers."""
    api_key: str
    header_name: str = "X-API-Key"
    header_format: str = "{api_key}"  # Format template for the header value
    additional_headers: Optional[Dict[str, str]] = None  # Additional static headers

@dataclass
class ConnectorConfig:
    """Base configuration for any connector."""
    base_url: str
    timeout: int = 30
    retry_count: int = 3
    rate_limit: int = 100
    # Additional fields for specialized connectors
    deployment: Optional[str] = None
    api_version: Optional[str] = None
    model: Optional[str] = None

class EnvironmentManager:
    """Manages environment variables and creates credential objects."""
    
    def __init__(self):
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.default_timeout = int(os.getenv('CONNECTOR_TIMEOUT', 30))
        self.default_retry_count = int(os.getenv('CONNECTOR_RETRY_COUNT', 3))
        self.default_rate_limit = int(os.getenv('CONNECTOR_DEFAULT_RATE_LIMIT', 100))
    
    def get_jiva_credentials(self) -> OAuth2Credentials:
        """Get Jiva OAuth2 credentials from environment."""
        client_id = os.getenv('JIVA_CLIENT_ID')
        client_secret = os.getenv('JIVA_CLIENT_SECRET')
        token_url = os.getenv('JIVA_TOKEN_URL')
        scope = os.getenv('JIVA_SCOPE')
        
        if not all([client_id, client_secret, token_url]):
            raise ValueError(
                "Missing required Jiva credentials. Please set JIVA_CLIENT_ID, "
                "JIVA_CLIENT_SECRET, and JIVA_TOKEN_URL environment variables."
            )
        
        return OAuth2Credentials(
            client_id=client_id,
            client_secret=client_secret,
            token_url=token_url,
            scope=scope
        )
    
    def get_jiva_config(self) -> ConnectorConfig:
        """Get Jiva connector configuration."""
        base_url = os.getenv('JIVA_BASE_URL')
        if not base_url:
            raise ValueError("Missing JIVA_BASE_URL environment variable.")
        
        return ConnectorConfig(
            base_url=base_url,
            timeout=self.default_timeout,
            retry_count=self.default_retry_count,
            rate_limit=self.default_rate_limit
        )
    
    def get_azure_credentials(self) -> OAuth2Credentials:
        """Get Azure OAuth2 credentials from environment."""
        client_id = os.getenv('AZURE_CLIENT_ID')
        client_secret = os.getenv('AZURE_CLIENT_SECRET')
        tenant_id = os.getenv('AZURE_TENANT_ID')
        
        if not all([client_id, client_secret, tenant_id]):
            raise ValueError(
                "Missing required Azure credentials. Please set AZURE_CLIENT_ID, "
                "AZURE_CLIENT_SECRET, and AZURE_TENANT_ID environment variables."
            )
        
        token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
        
        return OAuth2Credentials(
            client_id=client_id,
            client_secret=client_secret,
            token_url=token_url,
            scope="https://management.azure.com/.default"
        )
    
    def get_azure_config(self) -> ConnectorConfig:
        """Get Azure connector configuration."""
        base_url = os.getenv('AZURE_BASE_URL', 'https://management.azure.com')
        
        return ConnectorConfig(
            base_url=base_url,
            timeout=self.default_timeout,
            retry_count=self.default_retry_count,
            rate_limit=self.default_rate_limit
        )
    
    def get_salesforce_credentials(self) -> Dict[str, str]:
        """Get Salesforce credentials from environment."""
        client_id = os.getenv('SALESFORCE_CLIENT_ID')
        client_secret = os.getenv('SALESFORCE_CLIENT_SECRET')
        username = os.getenv('SALESFORCE_USERNAME')
        password = os.getenv('SALESFORCE_PASSWORD')
        security_token = os.getenv('SALESFORCE_SECURITY_TOKEN')
        
        if not all([client_id, client_secret, username, password, security_token]):
            raise ValueError(
                "Missing required Salesforce credentials. Please set SALESFORCE_CLIENT_ID, "
                "SALESFORCE_CLIENT_SECRET, SALESFORCE_USERNAME, SALESFORCE_PASSWORD, "
                "and SALESFORCE_SECURITY_TOKEN environment variables."
            )
        
        return {
            'client_id': client_id,
            'client_secret': client_secret,
            'username': username,
            'password': password,
            'security_token': security_token
        }
    
    def get_salesforce_config(self) -> ConnectorConfig:
        """Get Salesforce connector configuration."""
        base_url = os.getenv('SALESFORCE_BASE_URL')
        if not base_url:
            raise ValueError("Missing SALESFORCE_BASE_URL environment variable.")
        
        return ConnectorConfig(
            base_url=base_url,
            timeout=self.default_timeout,
            retry_count=self.default_retry_count,
            rate_limit=self.default_rate_limit
        )
    
    def get_modelhub_credentials(self) -> OAuth2Credentials:
        """Get ModelHub OAuth2 credentials from environment."""
        client_id = os.getenv('MODELHUB_CLIENT_ID')
        client_secret = os.getenv('MODELHUB_CLIENT_SECRET')
        token_url = os.getenv('MODELHUB_TOKEN_URL')
        
        if not all([client_id, client_secret, token_url]):
            raise ValueError(
                "Missing required ModelHub credentials. Please set MODELHUB_CLIENT_ID, "
                "MODELHUB_CLIENT_SECRET, and MODELHUB_TOKEN_URL environment variables."
            )
        
        return OAuth2Credentials(
            client_id=client_id,
            client_secret=client_secret,
            token_url=token_url
        )
    
    def get_modelhub_config(self) -> ConnectorConfig:
        """Get ModelHub connector configuration."""
        base_url = os.getenv('MODELHUB_BASE_URL')
        if not base_url:
            raise ValueError("Missing MODELHUB_BASE_URL environment variable.")
        
        return ConnectorConfig(
            base_url=base_url,
            timeout=self.default_timeout,
            retry_count=self.default_retry_count,
            rate_limit=self.default_rate_limit
        )
    
    def get_openai_credentials(self) -> APIKeyCredentials:
        """Get OpenAI API credentials from environment."""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("Missing OPENAI_API_KEY environment variable.")
        
        return APIKeyCredentials(
            api_key=api_key,
            header_name="Authorization",  # OpenAI uses "Authorization: Bearer {token}"
            header_format="Bearer {api_key}"  # Bearer token format
        )
    
    def get_openai_config(self) -> ConnectorConfig:
        """Get OpenAI connector configuration."""
        base_url = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
        
        return ConnectorConfig(
            base_url=base_url,
            timeout=self.default_timeout,
            retry_count=self.default_retry_count,
            rate_limit=self.default_rate_limit
        )
    
    def get_azure_openai_credentials(self) -> APIKeyCredentials:
        """Get Azure OpenAI credentials from environment using enhanced API key pattern."""
        api_key = os.getenv('OPENAI_API_KEY')
        endpoint = os.getenv('OPENAI_API_BASE_ENDPOINT')
        
        if not api_key:
            raise ValueError("Missing OPENAI_API_KEY environment variable.")
        if not endpoint:
            raise ValueError("Missing OPENAI_API_BASE_ENDPOINT environment variable.")
        
        return APIKeyCredentials(
            api_key=api_key,
            header_name="API-KEY",  # Azure OpenAI uses custom header name
            header_format="{api_key}",  # Direct API key, no Bearer prefix
            additional_headers={"ENDPOINT": endpoint}  # Additional required header
        )
    
    def get_azure_openai_config(self) -> ConnectorConfig:
        """Get Azure OpenAI connector configuration."""
        base_url = os.getenv('OPENAI_API_BASE')
        endpoint = os.getenv('OPENAI_API_BASE_ENDPOINT')
        deployment = os.getenv('AZURE_OPENAI_CHATGPT_DEPLOYMENT')
        api_version = os.getenv('OPENAI_API_VERSION', '2024-02-01')
        model = os.getenv('MODEL_OPENAI')
        
        if not base_url:
            raise ValueError("Missing OPENAI_API_BASE environment variable.")
        
        # Determine the correct base URL to use
        # If OPENAI_API_BASE already includes /openai/deployments/, use the endpoint instead
        if '/openai/deployments/' in base_url:
            # Use the clean endpoint URL and let the connector build the full URL
            final_base_url = endpoint.rstrip('/') if endpoint else base_url.split('/openai/deployments/')[0]
        else:
            # Use the base URL as-is
            final_base_url = base_url.rstrip('/')
        
        return ConnectorConfig(
            base_url=final_base_url,
            timeout=60,  # AI operations may take longer
            retry_count=3,
            rate_limit=60,  # Azure OpenAI rate limits
            deployment=deployment,
            api_version=api_version,
            model=model
        )
    
    def get_api_key_credentials(self, prefix: str) -> APIKeyCredentials:
        """Get API key credentials for a given prefix (e.g., 'APIKEY_API')."""
        api_key = os.getenv(f'{prefix}_KEY')
        header_name = os.getenv(f'{prefix}_HEADER_NAME', 'X-API-Key')
        
        if not api_key:
            raise ValueError(f"Missing required API key. Please set {prefix}_KEY environment variable.")
        
        return APIKeyCredentials(
            api_key=api_key,
            header_name=header_name
        )
    
    def get_generic_config(self, prefix: str) -> ConnectorConfig:
        """Get generic connector configuration for a given prefix."""
        base_url = os.getenv(f'{prefix}_BASE_URL')
        if not base_url:
            raise ValueError(f"Missing {prefix}_BASE_URL environment variable.")
        
        return ConnectorConfig(
            base_url=base_url,
            timeout=self.default_timeout,
            retry_count=self.default_retry_count,
            rate_limit=self.default_rate_limit
        )
    
    def validate_environment(self, connector_name: str) -> bool:
        """Validate that required environment variables are set for a connector."""
        try:
            if connector_name.lower() == 'jiva':
                self.get_jiva_credentials()
                self.get_jiva_config()
            elif connector_name.lower() == 'azure':
                self.get_azure_credentials()
                self.get_azure_config()
            elif connector_name.lower() == 'salesforce':
                self.get_salesforce_credentials()
                self.get_salesforce_config()
            elif connector_name.lower() == 'modelhub':
                self.get_modelhub_credentials()
                self.get_modelhub_config()
            elif connector_name.lower() == 'openai':
                self.get_openai_credentials()
                self.get_openai_config()
            elif connector_name.lower() == 'azure_openai':
                self.get_azure_openai_credentials()
                self.get_azure_openai_config()
            else:
                # For generic connectors, try both OAuth2 and API key patterns
                prefix = connector_name.upper()
                try:
                    OAuth2Credentials(
                        client_id=os.getenv(f'{prefix}_CLIENT_ID'),
                        client_secret=os.getenv(f'{prefix}_CLIENT_SECRET'),
                        token_url=os.getenv(f'{prefix}_TOKEN_URL')
                    )
                except:
                    self.get_api_key_credentials(prefix)
                
                self.get_generic_config(prefix)
            
            return True
        except ValueError:
            return False

# Global instance
env_manager = EnvironmentManager() 