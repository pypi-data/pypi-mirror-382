"""
Central service registry containing URL patterns and metadata for all services.
This replaces scattered service-specific URL building logic with centralized patterns.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class ServicePattern:
    """Service-specific URL and parameter patterns."""
    url_pattern: str  # URL template with placeholders
    required_params: List[str]  # Required parameters for this service
    optional_params: List[str]  # Optional parameters
    auth_pattern: str  # Authentication pattern type
    default_query_params: Dict[str, Any]  # Default query parameters


class ServiceRegistry:
    """
    Central registry of service patterns and metadata.
    Replaces service-specific URL building logic with declarative patterns.
    """
    
    # Service patterns following industry standards
    SERVICE_PATTERNS = {
        # Azure OpenAI - Complex deployment-based URLs
        'azure_openai': ServicePattern(
            url_pattern='/openai/deployments/{deployment}/{operation}',
            required_params=['deployment'],
            optional_params=['api_version'],
            auth_pattern='api_key_header',
            default_query_params={'api-version': '2024-02-01'}
        ),
        
        # Jiva Healthcare APIs - Standard REST patterns
        'jiva': ServicePattern(
            url_pattern='/api/v1/{operation}',
            required_params=[],
            optional_params=['version'],
            auth_pattern='oauth2_bearer',
            default_query_params={}
        ),
        
        'jiva_contact': ServicePattern(
            url_pattern='/api/v1/contact/{operation}',
            required_params=[],
            optional_params=['version'],
            auth_pattern='oauth2_bearer',
            default_query_params={}
        ),
        
        'jiva_document': ServicePattern(
            url_pattern='/api/v1/document/{operation}',
            required_params=[],
            optional_params=['version'],
            auth_pattern='oauth2_bearer',
            default_query_params={}
        ),
        
        'jiva_member': ServicePattern(
            url_pattern='/api/v1/member/{operation}',
            required_params=[],
            optional_params=['version'],
            auth_pattern='oauth2_bearer',
            default_query_params={}
        ),
        
        'jiva_care_plan': ServicePattern(
            url_pattern='/api/v1/care-plan/{operation}',
            required_params=[],
            optional_params=['version'],
            auth_pattern='oauth2_bearer',
            default_query_params={}
        ),
        
        # OpenAI - Simple pattern
        'openai': ServicePattern(
            url_pattern='/v1/{operation}',
            required_params=[],
            optional_params=[],
            auth_pattern='bearer_token',
            default_query_params={}
        ),
        
        # Salesforce - Standard REST with versioning
        'salesforce': ServicePattern(
            url_pattern='/services/data/v{version}/{operation}',
            required_params=['version'],
            optional_params=[],
            auth_pattern='oauth2_bearer',
            default_query_params={}
        ),
        
        # Azure Management - Resource-based URLs
        'azure': ServicePattern(
            url_pattern='/subscriptions/{subscription_id}/resourceGroups/{resource_group}/{operation}',
            required_params=['subscription_id', 'resource_group'],
            optional_params=['api_version'],
            auth_pattern='oauth2_bearer',
            default_query_params={'api-version': '2021-04-01'}
        ),
    }
    
    # Operation mappings for services that have different endpoint names
    OPERATION_MAPPINGS = {
        'azure_openai': {
            'chat_completion': 'chat/completions',
            'embeddings': 'embeddings',
            'completions': 'completions',
            'models': 'models'
        },
        'jiva_contact': {
            'create_contact': 'contacts',
            'get_contact': 'contacts',
            'update_contact': 'contacts',
            'delete_contact': 'contacts',
            'search_contacts': 'contacts/search'
        },
        'jiva_document': {
            'upload_document': 'documents',
            'get_document': 'documents',
            'delete_document': 'documents',
            'search_documents': 'documents/search'
        },
        'openai': {
            'chat_completion': 'chat/completions',
            'completions': 'completions',
            'embeddings': 'embeddings',
            'models': 'models'
        }
    }
    
    @classmethod
    def get_service_pattern(cls, service_name: str) -> Optional[ServicePattern]:
        """Get service pattern for a given service."""
        return cls.SERVICE_PATTERNS.get(service_name.lower())
    
    @classmethod
    def get_operation_endpoint(cls, service_name: str, operation: str) -> str:
        """
        Get the actual endpoint path for an operation.
        
        Args:
            service_name: Name of the service
            operation: Operation name
            
        Returns:
            Endpoint path for the operation
        """
        service_mappings = cls.OPERATION_MAPPINGS.get(service_name.lower(), {})
        return service_mappings.get(operation, operation)
    
    @classmethod
    def is_service_supported(cls, service_name: str) -> bool:
        """Check if a service is supported."""
        return service_name.lower() in cls.SERVICE_PATTERNS
    
    @classmethod
    def get_supported_services(cls) -> List[str]:
        """Get list of all supported services."""
        return list(cls.SERVICE_PATTERNS.keys())
    
    @classmethod
    def validate_service_params(cls, service_name: str, params: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Validate parameters for a service.
        
        Args:
            service_name: Name of the service
            params: Parameters to validate
            
        Returns:
            Dictionary with 'missing' and 'extra' parameter lists
        """
        pattern = cls.get_service_pattern(service_name)
        if not pattern:
            return {'missing': [], 'extra': list(params.keys())}
        
        provided_params = set(params.keys())
        required_params = set(pattern.required_params)
        all_valid_params = set(pattern.required_params + pattern.optional_params)
        
        missing = list(required_params - provided_params)
        extra = list(provided_params - all_valid_params)
        
        return {'missing': missing, 'extra': extra} 