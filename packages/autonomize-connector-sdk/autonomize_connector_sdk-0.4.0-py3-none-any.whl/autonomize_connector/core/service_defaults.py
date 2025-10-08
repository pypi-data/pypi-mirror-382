"""
Service defaults registry for all supported APIs.
This module contains default configurations, authentication patterns, and endpoints
for various API services, making it easy to add new APIs with minimal configuration.
"""

from typing import Dict, Any, List

# Authentication pattern definitions
AUTH_PATTERNS = {
    'oauth2': ['CLIENT_ID', 'CLIENT_SECRET', 'TOKEN_URL'],
    'api_key': ['API_KEY', 'KEY'],
    'bearer_token': ['ACCESS_TOKEN', 'BEARER_TOKEN'],
    'basic_auth': ['USERNAME', 'PASSWORD'],
    'mixed_auth': ['CLIENT_ID', 'CLIENT_SECRET', 'USERNAME', 'PASSWORD']  # Like Salesforce
}

# Smart base URL defaults for services
BASE_URL_DEFAULTS = {
    'jiva': 'https://api.jiva.com',
    'jiva_contact': 'https://api.jiva.com',
    'jiva_document': 'https://api.jiva.com',
    'jiva_member': 'https://api.jiva.com',
    'jiva_care_plan': 'https://api.jiva.com',
    'azure': 'https://management.azure.com',
    'openai': 'https://api.openai.com/v1',
    'azure_openai': None,  # Requires custom endpoint
    'salesforce': 'https://login.salesforce.com',
    'modelhub': 'https://api.modelhub.com'
}

# Service-specific defaults and configurations
SERVICE_DEFAULTS = {
    # Jiva Healthcare API family
    'jiva': {
        'auth_type': 'oauth2',
        'timeout': 30,
        'rate_limit': 100,
        'retry_count': 3,
        'scope': 'read write'
    },
    
    'jiva_contact': {
        'auth_type': 'oauth2', 
        'timeout': 30,
        'rate_limit': 100,
        'retry_count': 3,
        'scope': 'read write'
    },
    
    'jiva_document': {
        'auth_type': 'oauth2',
        'timeout': 30, 
        'rate_limit': 100,
        'retry_count': 3,
        'scope': 'read write'
    },
    
    # Microsoft Azure
    'azure': {
        'auth_type': 'oauth2',
        'timeout': 45,
        'rate_limit': 200,
        'retry_count': 3,
        'scope': 'https://management.azure.com/.default',
        'requires_tenant': True
    },
    
    # OpenAI 
    'openai': {
        'auth_type': 'api_key',
        'timeout': 30,
        'rate_limit': 60,
        'retry_count': 3,
        'header_name': 'Authorization',
        'header_format': 'Bearer {api_key}'
    },
    
    # Azure OpenAI (separate from regular OpenAI)
    'azure_openai': {
        'auth_type': 'azure_custom',
        'timeout': 60,
        'rate_limit': 60,
        'retry_count': 3,
        'api_version': '2024-02-01',
        'requires_deployment': True,
        'supported_models': ['gpt-4o', 'gpt-4', 'gpt-35-turbo', 'text-embedding-ada-002']
    },
    
    # Salesforce CRM
    'salesforce': {
        'auth_type': 'mixed_auth',
        'timeout': 35,
        'rate_limit': 150,
        'retry_count': 3
    },
    
    # ModelHub (Internal AI/ML)
    'modelhub': {
        'auth_type': 'oauth2',
        'timeout': 60,
        'rate_limit': 50,
        'retry_count': 3
    }
}

def get_service_defaults(service_name: str) -> Dict[str, Any]:
    """
    Get default configuration for a service.
    
    Args:
        service_name: Name of the service
        
    Returns:
        Dictionary of default configuration values
    """
    return SERVICE_DEFAULTS.get(service_name.lower(), {})

def get_env_vars(service_name: str, auth_type: str = None) -> Dict[str, str]:
    """
    Get environment variable names for a service using universal pattern.
    
    Universal Pattern:
    - Service families use family prefix: jiva_contact -> JIVA_*
    - Individual services use full name: salesforce -> SALESFORCE_*
    - Special cases for backward compatibility
    
    Args:
        service_name: Name of the service (e.g., 'jiva_contact', 'azure_openai', 'openai')
        auth_type: Authentication type (oauth2, api_key, etc.)
        
    Returns:
        Dictionary mapping credential fields to environment variable names
    """
    service_lower = service_name.lower()
    
    # Universal pattern with special cases for backward compatibility
    if service_lower.startswith('jiva_'):
        # Jiva family: jiva_contact, jiva_document -> JIVA_*
        prefix = 'JIVA'
    elif service_lower == 'azure_openai':
        # Azure OpenAI: Use proper AZURE_OPENAI_* prefix for consistency
        # This prevents namespace collision with regular OpenAI
        prefix = 'AZURE_OPENAI'
    else:
        # All other services: Use full service name as prefix
        prefix = service_name.upper()
    
    # Auto-detect auth type if not provided
    if not auth_type:
        defaults = get_service_defaults(service_name)
        auth_type = defaults.get('auth_type', 'oauth2')
    
    if auth_type == 'oauth2':
        return {
            'client_id': f'{prefix}_CLIENT_ID',
            'client_secret': f'{prefix}_CLIENT_SECRET',
            'base_url': f'{prefix}_BASE_URL'
        }
    elif auth_type == 'api_key':
        return {
            'api_key': f'{prefix}_API_KEY',
            'base_url': f'{prefix}_BASE_URL'
        }
    elif auth_type == 'mixed_auth':  # Salesforce
        return {
            'client_id': f'{prefix}_CLIENT_ID',
            'client_secret': f'{prefix}_CLIENT_SECRET',
            'username': f'{prefix}_USERNAME',
            'password': f'{prefix}_PASSWORD',
            'base_url': f'{prefix}_BASE_URL'
        }
    elif auth_type == 'azure_custom':  # Azure OpenAI - consistent pattern
        return {
            'api_key': f'{prefix}_API_KEY',
            'base_url': f'{prefix}_API_BASE',
            'deployment': f'{prefix}_CHATGPT_DEPLOYMENT',
            'api_version': f'{prefix}_API_VERSION'
        }
    else:
        # Fallback to OAuth2 pattern
        return {
            'client_id': f'{prefix}_CLIENT_ID',
            'client_secret': f'{prefix}_CLIENT_SECRET',
            'base_url': f'{prefix}_BASE_URL'
        }

def get_base_url_default(service_name: str) -> str:
    """
    Get default base URL for a service.
    
    Args:
        service_name: Name of the service
        
    Returns:
        Default base URL or None if no default available
    """
    return BASE_URL_DEFAULTS.get(service_name.lower())

def get_supported_services() -> List[str]:
    """Get list of all supported service names."""
    return list(SERVICE_DEFAULTS.keys())

def is_service_supported(service_name: str) -> bool:
    """Check if a service is supported."""
    return service_name.lower() in SERVICE_DEFAULTS

def get_auth_type(service_name: str) -> str:
    """Get the authentication type for a service."""
    defaults = get_service_defaults(service_name)
    return defaults.get('auth_type', 'oauth2')

# Backward compatibility - keep get_env_pattern as alias
def get_env_pattern(service_name: str, auth_type: str = None) -> Dict[str, str]:
    """Backward compatibility alias for get_env_vars."""
    return get_env_vars(service_name, auth_type) 