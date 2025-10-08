"""
Core SDK functionality including base connector, factory, and exceptions.
"""

from .factory import ConnectorFactory, connector_factory
from .base_connector import BaseConnector
from .exceptions import (
    ConnectorError,
    AuthenticationError,
    ValidationError,
    APIError,
    ConfigurationError
)

__all__ = [
    "ConnectorFactory",
    "connector_factory", 
    "BaseConnector",
    "ConnectorError",
    "AuthenticationError",
    "ValidationError", 
    "APIError",
    "ConfigurationError"
] 