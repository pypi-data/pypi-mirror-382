"""
Endpoint resolver following AWS SDK EndpointResolverV2 pattern.
Handles service-specific URL resolution logic centrally.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass

from .service_registry import ServiceRegistry
from .url_builder import URLBuilder


@dataclass
class EndpointParameters:
    """
    Parameters for endpoint resolution, following AWS SDK pattern.
    Contains both common parameters and service-specific parameters.
    """
    # Common parameters (all services)
    service_name: str
    operation: str
    base_url: str
    
    # Service-specific parameters (dynamic)
    service_params: Dict[str, Any]
    
    # Query parameters
    query_params: Optional[Dict[str, Any]] = None


@dataclass
class ResolvedEndpoint:
    """Resolved endpoint information."""
    url: str
    service_name: str
    operation: str
    resolved_params: Dict[str, Any]


class EndpointResolver:
    """
    Central endpoint resolver following AWS SDK EndpointResolverV2 pattern.
    Handles all service-specific URL building logic in one place.
    """
    
    def __init__(self):
        """Initialize endpoint resolver."""
        self.service_registry = ServiceRegistry()
    
    def resolve_endpoint(self, params: EndpointParameters) -> ResolvedEndpoint:
        """
        Resolve endpoint URL for a service operation.
        
        Args:
            params: Endpoint parameters containing service info and parameters
            
        Returns:
            ResolvedEndpoint with complete URL and metadata
            
        Raises:
            ValueError: If service is not supported or required parameters are missing
        """
        # Get service pattern
        service_pattern = self.service_registry.get_service_pattern(params.service_name)
        if not service_pattern:
            raise ValueError(f"Service '{params.service_name}' is not supported")
        
        # Special handling for Azure OpenAI models endpoint (doesn't need deployment)
        if params.service_name == 'azure_openai' and params.operation == 'models':
            # Use a special pattern for models endpoint
            url_builder = URLBuilder(params.base_url)
            query_params = {}
            query_params.update(service_pattern.default_query_params)
            if params.query_params:
                query_params.update(params.query_params)
            
            final_url = url_builder.build_url('/openai/models', query_params)
            return ResolvedEndpoint(
                url=final_url,
                service_name=params.service_name,
                operation=params.operation,
                resolved_params={'operation': 'models'}
            )
        
        # Validate required parameters
        validation_result = self.service_registry.validate_service_params(
            params.service_name, 
            params.service_params
        )
        
        if validation_result['missing']:
            raise ValueError(
                f"Missing required parameters for {params.service_name}: {validation_result['missing']}"
            )
        
        # Get actual operation endpoint
        operation_endpoint = self.service_registry.get_operation_endpoint(
            params.service_name, 
            params.operation
        )
        
        # Build path parameters for URL template
        path_params = {
            'operation': operation_endpoint,
            **params.service_params
        }
        
        # Merge query parameters
        query_params = {}
        query_params.update(service_pattern.default_query_params)
        if params.query_params:
            query_params.update(params.query_params)
        
        # Create URL builder and build final URL
        url_builder = URLBuilder(params.base_url)
        
        try:
            final_url = url_builder.build_url_with_path_params(
                service_pattern.url_pattern,
                path_params,
                query_params
            )
        except KeyError as e:
            raise ValueError(
                f"Missing required parameter for URL template in {params.service_name}: {e}"
            )
        
        return ResolvedEndpoint(
            url=final_url,
            service_name=params.service_name,
            operation=params.operation,
            resolved_params=path_params
        )
    
    def resolve_endpoint_simple(
        self,
        service_name: str,
        operation: str,
        base_url: str,
        service_params: Optional[Dict[str, Any]] = None,
        query_params: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Simplified endpoint resolution that returns just the URL.
        
        Args:
            service_name: Name of the service
            operation: Operation to perform
            base_url: Base URL for the service
            service_params: Service-specific parameters
            query_params: Query parameters
            
        Returns:
            Complete URL string
        """
        params = EndpointParameters(
            service_name=service_name,
            operation=operation,
            base_url=base_url,
            service_params=service_params or {},
            query_params=query_params
        )
        
        resolved = self.resolve_endpoint(params)
        return resolved.url
    
    def get_service_info(self, service_name: str) -> Dict[str, Any]:
        """
        Get information about a service's URL patterns and requirements.
        
        Args:
            service_name: Name of the service
            
        Returns:
            Dictionary with service information
        """
        service_pattern = self.service_registry.get_service_pattern(service_name)
        if not service_pattern:
            return {'supported': False}
        
        return {
            'supported': True,
            'url_pattern': service_pattern.url_pattern,
            'required_params': service_pattern.required_params,
            'optional_params': service_pattern.optional_params,
            'auth_pattern': service_pattern.auth_pattern,
            'default_query_params': service_pattern.default_query_params,
            'available_operations': list(
                self.service_registry.OPERATION_MAPPINGS.get(service_name, {}).keys()
            )
        } 