"""
Autonomize Connector SDK - Simplified API Integration
Simple, powerful API connectors with industry-standard patterns.

# Simple API (90% of users) - requires registration first
import autonomize_connector as ac

# Register connectors (once per application/pod)
ac.register_connector({
    "name": "jiva_contact",
    "base_url": "https://api.jiva.com",
    "auth": {"type": "oauth2", "client_id_env": "JIVA_CLIENT_ID"},
    "endpoints": {"create_contact": {"path": "/contacts", "method": "POST"}}
})

# Use connectors
contact = ac.jiva_contact()
azure = ac.azure_openai()

# Advanced API (10% of users)
from autonomize_connector import connector_factory
contact = connector_factory.create('jiva_contact')

## Environment Setup

Simple pattern that works for all services:

```bash
# OAuth2 Services (Jiva, Azure)
export JIVA_CLIENT_ID="your_client_id"
export JIVA_CLIENT_SECRET="your_client_secret"

# API Key Services (OpenAI)
export OPENAI_API_KEY="sk_..."
```
"""

from .core.factory import connector_factory
from .core.registration import (
    register_connector,
    register_from_file,
    list_registered_connectors,
    get_connector_info
)
from .utils.env_manager import ConnectorConfig
from .utils.logger import get_logger

# Version info
__version__ = "0.4.0"
__author__ = "Autonomize AI"

# Initialize logger
logger = get_logger("autonomize_connector")

def __getattr__(name: str):
    """
    Dynamic attribute access for simple API.
    Enables: ac.jiva_contact(), ac.azure_openai(), etc.
    
    Args:
        name: Connector name
        
    Returns:
        Function that creates the connector instance
        
    Raises:
        AttributeError: If connector not registered
    """
    # Check if this looks like a connector name
    if not name.startswith('_'):
        try:
            # Return a function that creates the connector
            def create_connector_instance():
                return connector_factory.quick(name)
            
            # Set helpful attributes on the function
            create_connector_instance.__name__ = name
            create_connector_instance.__doc__ = f"""
            Create {name} connector instance.
            
            Returns:
                Configured {name} connector instance
                
            Raises:
                ConfigurationError: If connector not registered or credentials missing
                
            Example:
                connector = ac.{name}()
                # Use the connector...
            """
            
            return create_connector_instance
            
        except Exception:
            # If we can't create the connector, fall through to normal AttributeError
            pass
    
    # For non-connector attributes, raise normal AttributeError
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


# Public API exports
__all__ = [
    # Core functionality
    'connector_factory',
    
    # Dynamic registration
    'register_connector',
    'register_from_file', 
    'list_registered_connectors',
    'get_connector_info',
    
    # Configuration
    'ConnectorConfig',
    
    # Version
    '__version__',
    '__author__'
]

# Simple startup message
logger.info(f"Autonomize Connector SDK v{__version__} initialized")
logger.info("Use ac.register_connector() to register JSON-based connectors, then ac.{connector_name}() to use them") 