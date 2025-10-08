"""
Generic URL builder following industry standards (AWS SDK, OpenAI SDK patterns).
Handles URL construction without service-specific logic.
"""

from typing import Dict, Any, Optional
from urllib.parse import urljoin, urlencode


class URLBuilder:
    """
    Generic URL builder that constructs URLs without service-specific knowledge.
    Follows industry patterns from AWS SDK, OpenAI SDK, and Azure SDK.
    """
    
    def __init__(self, base_url: str):
        """
        Initialize URL builder with base URL.
        
        Args:
            base_url: Base URL for the service (e.g., https://api.service.com)
        """
        self.base_url = base_url.rstrip('/')
    
    def build_url(
        self, 
        endpoint_path: str, 
        query_params: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Build complete URL from base URL, endpoint path, and query parameters.
        
        Args:
            endpoint_path: API endpoint path (e.g., /api/v1/chat/completions)
            query_params: Query parameters to append
            
        Returns:
            Complete URL string
        """
        # Ensure endpoint path starts with /
        if not endpoint_path.startswith('/'):
            endpoint_path = '/' + endpoint_path
        
        # Build base URL + path
        url = f"{self.base_url}{endpoint_path}"
        
        # Add query parameters if provided
        if query_params:
            # Filter out None values
            filtered_params = {k: v for k, v in query_params.items() if v is not None}
            if filtered_params:
                query_string = urlencode(filtered_params)
                separator = "&" if "?" in url else "?"
                url = f"{url}{separator}{query_string}"
        
        return url
    
    def build_url_with_path_params(
        self,
        endpoint_template: str,
        path_params: Dict[str, str],
        query_params: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Build URL with path parameter substitution.
        Handles special cases like Azure OpenAI where base URL may already contain parts of the path.
        
        Args:
            endpoint_template: Template with placeholders (e.g., /api/{version}/users/{user_id})
            path_params: Parameters to substitute in template
            query_params: Query parameters to append
            
        Returns:
            Complete URL string
        """
        # Substitute path parameters
        endpoint_path = endpoint_template.format(**path_params)
        
        # Special handling for Azure OpenAI deployment path duplication
        if '/openai/deployments/' in endpoint_template and '/openai/deployments' in self.base_url.lower():
            # Base URL already contains /openai/deployments/, extract just the deployment and operation part
            # Template: /openai/deployments/{deployment}/{operation}
            # Extract everything after /openai/deployments/
            parts = endpoint_path.split('/openai/deployments/', 1)
            if len(parts) > 1:
                # Use just the deployment/operation part
                endpoint_path = '/' + parts[1]
        
        # Build URL with query parameters
        return self.build_url(endpoint_path, query_params) 