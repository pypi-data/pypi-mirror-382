"""
Placeholder connector classes for services with planned support.
These provide basic structure and helpful error messages for unsupported operations.
"""

from typing import Dict, Any
from .base_connector import BaseConnector
from ..utils.env_manager import ConnectorConfig
from ..auth.base_auth import BaseAuthHandler
from ..utils.logger import get_logger

class PlaceholderConnector(BaseConnector):
    """
    Placeholder connector for services with environment support but no implementation yet.
    Provides basic structure and helpful error messages for unsupported operations.
    """
    
    def __init__(self, config: ConnectorConfig, auth_handler: BaseAuthHandler, service_name: str, **kwargs):
        """Initialize placeholder connector."""
        # Remove 'name' from kwargs to avoid conflicts
        kwargs.pop('name', None)
        super().__init__(config, auth_handler, name=f"{service_name}Placeholder", **kwargs)
        self.service_name = service_name
        

    
    def get_connector_info(self) -> Dict[str, Any]:
        """Get connector information."""
        return {
            "name": self.service_name,
            "version": "placeholder",
            "type": "placeholder",
            "status": "planned",
            "base_url": self.config.base_url,
            "supports": ["configuration", "authentication"],
            "message": f"{self.service_name} connector planned for future implementation"
        }

# Create placeholder connector classes
class AzureConnector(PlaceholderConnector):
    """Placeholder Azure connector."""
    def __init__(self, config: ConnectorConfig, auth_handler: BaseAuthHandler, **kwargs):
        super().__init__(config, auth_handler, "Azure", **kwargs)

class OpenAIConnector(PlaceholderConnector):
    """Placeholder OpenAI connector.""" 
    def __init__(self, config: ConnectorConfig, auth_handler: BaseAuthHandler, **kwargs):
        super().__init__(config, auth_handler, "OpenAI", **kwargs)

class SalesforceConnector(PlaceholderConnector):
    """Placeholder Salesforce connector."""
    def __init__(self, config: ConnectorConfig, auth_handler: BaseAuthHandler, **kwargs):
        super().__init__(config, auth_handler, "Salesforce", **kwargs)

class ModelHubConnector(PlaceholderConnector):
    """Placeholder ModelHub connector."""
    def __init__(self, config: ConnectorConfig, auth_handler: BaseAuthHandler, **kwargs):
        super().__init__(config, auth_handler, "ModelHub", **kwargs)

__all__ = [
    "PlaceholderConnector",
    "AzureConnector", 
    "OpenAIConnector",
    "SalesforceConnector",
    "ModelHubConnector"
] 