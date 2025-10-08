"""
Custom exceptions for the Autonomize Connector SDK.
Based on API documentation and common integration patterns.
"""

class ConnectorError(Exception):
    """Base exception for all connector-related errors."""
    
    def __init__(self, message: str, details: dict = None, status_code: int = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}
        self.status_code = status_code

class AuthenticationError(ConnectorError):
    """Raised when authentication fails."""
    pass

class ValidationError(ConnectorError):
    """Raised when data validation fails."""
    
    def __init__(self, message: str, field: str = None, **kwargs):
        super().__init__(message, **kwargs)
        self.field = field

class APIError(ConnectorError):
    """Raised when API calls fail."""
    pass

class ConfigurationError(ConnectorError):
    """Raised when configuration is invalid."""
    pass

# Jiva-specific exceptions based on API documentation
class JivaError(ConnectorError):
    """Base exception for Jiva API errors."""
    pass

class ContactNotFoundError(JivaError):
    """HTTP 404: Contact information not found in Jiva for a given CONTACT_ID."""
    
    def __init__(self, contact_id: str):
        message = f"Contact information not found in Jiva for a Given CONTACT_ID-{contact_id}"
        super().__init__(message, status_code=404)
        self.contact_id = contact_id

class ContactInactiveError(JivaError):
    """HTTP 410: Entity CONTACT_ID is inactive in Jiva."""
    
    def __init__(self, contact_id: str):
        message = f"Entity CONTACT_ID-{contact_id} is inactive in Jiva"
        super().__init__(message, status_code=410)
        self.contact_id = contact_id

class MultiplePreferredFlagsError(JivaError):
    """HTTP 400: Multiple preferred records provided."""
    
    def __init__(self, field_type: str):
        message = f"Multiple preferred records provided in {field_type}"
        super().__init__(message, status_code=400)
        self.field_type = field_type

class PreferredFlagNotFoundError(JivaError):
    """HTTP 400: At least one preferred record should be provided."""
    
    def __init__(self, collection_type: str):
        message = f"At least one preferred record should be provided in {collection_type}"
        super().__init__(message, status_code=400)
        self.collection_type = collection_type

class InactiveAddressFlagError(JivaError):
    """HTTP 400: Inactive address provided in payload."""
    
    def __init__(self):
        message = "Inactive address provided in payload"
        super().__init__(message, status_code=400)

class InactivePhoneFlagError(JivaError):
    """HTTP 400: Inactive phone provided in payload."""
    
    def __init__(self):
        message = "Inactive phone provided in payload"
        super().__init__(message, status_code=400)

class InactiveEmailFlagError(JivaError):
    """HTTP 400: Inactive email provided in payload."""
    
    def __init__(self):
        message = "Inactive email provided in payload"
        super().__init__(message, status_code=400)

class InvalidParameterValueError(JivaError):
    """HTTP 400: Parameter value received in URL/payload is invalid."""
    
    def __init__(self, parameter: str, value: str):
        message = f"Parameter value received is invalid: {parameter}={value}"
        super().__init__(message, status_code=400)
        self.parameter = parameter
        self.value = value

class InvalidMemberAndEpisodeCombinationError(JivaError):
    """HTTP 400: Combination of member and episode identifiers is invalid."""
    
    def __init__(self, member_info: str, episode_info: str):
        message = f"Combination of member and episode identifiers is invalid: {member_info}, {episode_info}"
        super().__init__(message, status_code=400)
        self.member_info = member_info
        self.episode_info = episode_info

class JsonValidatorError(JivaError):
    """HTTP 400: Payload validation error. Cannot process request."""
    
    def __init__(self, validation_details: str):
        message = f"Payload validation error. Cannot process request: {validation_details}"
        super().__init__(message, status_code=400)
        self.validation_details = validation_details

class InsufficientParametersError(JivaError):
    """HTTP 400: At least one query parameter is required."""
    
    def __init__(self, operation: str):
        message = f"At least one query parameter is required for {operation}"
        super().__init__(message, status_code=400)
        self.operation = operation

class MemberNotFoundError(JivaError):
    """HTTP 404: Member not found in Jiva for given identifiers."""
    
    def __init__(self, member_identifiers: str):
        message = f"Member not found in Jiva for given identifiers: {member_identifiers}"
        super().__init__(message, status_code=404)
        self.member_identifiers = member_identifiers

class EpisodeNotFoundError(JivaError):
    """HTTP 404: No episode found for a given search criteria."""
    
    def __init__(self, episode_identifiers: str):
        message = f"No episode found for given search criteria: {episode_identifiers}"
        super().__init__(message, status_code=404)
        self.episode_identifiers = episode_identifiers

class ContactEntityNotFoundError(JivaError):
    """HTTP 404: No Contact Entity found for a given search criteria."""
    
    def __init__(self, search_criteria: str):
        message = f"No Contact Entity found for given search criteria: {search_criteria}"
        super().__init__(message, status_code=404)
        self.search_criteria = search_criteria

class MemberInactiveError(JivaError):
    """HTTP 410: Member exists but inactive in Jiva."""
    
    def __init__(self, member_id: str):
        message = f"Member {member_id} exists but inactive in Jiva"
        super().__init__(message, status_code=410)
        self.member_id = member_id

class EpisodeInactiveError(JivaError):
    """HTTP 410: Episode exists but inactive in Jiva."""
    
    def __init__(self, episode_id: str):
        message = f"Episode {episode_id} exists but inactive in Jiva"
        super().__init__(message, status_code=410)
        self.episode_id = episode_id

class MultipleMembersFoundError(JivaError):
    """HTTP 501: Multiple members found in Jiva for given identifiers."""
    
    def __init__(self, member_identifiers: str):
        message = f"Multiple members found in Jiva for given identifiers: {member_identifiers}"
        super().__init__(message, status_code=501)
        self.member_identifiers = member_identifiers

class MultipleEpisodesFoundError(JivaError):
    """HTTP 501: Multiple episodes found for a given search criteria."""
    
    def __init__(self, episode_criteria: str):
        message = f"Multiple episodes found for given search criteria: {episode_criteria}"
        super().__init__(message, status_code=501)
        self.episode_criteria = episode_criteria

class ExtContactIdFoundError(JivaError):
    """HTTP 404: Ext contact ID already attached to another contact."""
    
    def __init__(self, ext_contact_id: str):
        message = f"Ext contact Id {ext_contact_id} attached to another contact in Jiva"
        super().__init__(message, status_code=404)
        self.ext_contact_id = ext_contact_id

class CodeValueNotFoundError(JivaError):
    """HTTP 404: Code value not found in Jiva."""
    
    def __init__(self, field_name: str, value: str):
        message = f"{field_name} {value} not found in Jiva"
        super().__init__(message, status_code=404)
        self.field_name = field_name
        self.value = value

class InvalidStateCombinationError(JivaError):
    """HTTP 404: Invalid combination of stateCd and countryCd."""
    
    def __init__(self, state_cd: str, country_cd: str):
        message = f"stateCd {state_cd} and countryCd {country_cd} combination not found in Jiva"
        super().__init__(message, status_code=404)
        self.state_cd = state_cd
        self.country_cd = country_cd

# Factory function to create appropriate exceptions from API responses
def create_jiva_exception(status_code: int, error_message: str, **kwargs) -> JivaError:
    """Create appropriate Jiva exception based on status code and message."""
    
    if status_code == 404:
        if "Contact information not found" in error_message:
            contact_id = kwargs.get('contact_id', 'unknown')
            return ContactNotFoundError(contact_id)
        elif "attached to another contact" in error_message:
            ext_contact_id = kwargs.get('ext_contact_id', 'unknown')
            return ExtContactIdFoundError(ext_contact_id)
        elif "not found in Jiva" in error_message:
            field_name = kwargs.get('field_name', 'Field')
            value = kwargs.get('value', 'unknown')
            return CodeValueNotFoundError(field_name, value)
        elif "combination not found" in error_message:
            state_cd = kwargs.get('state_cd', 'unknown')
            country_cd = kwargs.get('country_cd', 'unknown')
            return InvalidStateCombinationError(state_cd, country_cd)
    
    elif status_code == 410:
        if "is inactive in Jiva" in error_message:
            contact_id = kwargs.get('contact_id', 'unknown')
            return ContactInactiveError(contact_id)
    
    elif status_code == 400:
        if "Multiple preferred records" in error_message:
            field_type = kwargs.get('field_type', 'records')
            return MultiplePreferredFlagsError(field_type)
        elif "Inactive address" in error_message:
            return InactiveAddressFlagError()
        elif "Inactive phone" in error_message:
            return InactivePhoneFlagError()
        elif "Inactive email" in error_message:
            return InactiveEmailFlagError()
    
    # Fallback to generic Jiva error
    return JivaError(error_message, status_code=status_code) 