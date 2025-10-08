"""
Validation utilities for configuration and data validation.
Includes specific validators for complex API schemas like Jiva.
"""

import re
from typing import Dict, List, Any, Optional, Union
from ..core.exceptions import ValidationError, ConfigurationError

def validate_config(config: Dict[str, Any], required_fields: List[str]) -> bool:
    """
    Validate that a configuration dictionary has required fields.
    
    Args:
        config: Configuration dictionary to validate
        required_fields: List of required field names
        
    Returns:
        True if valid
        
    Raises:
        ConfigurationError: If required fields are missing
    """
    missing_fields = [field for field in required_fields if field not in config]
    
    if missing_fields:
        raise ConfigurationError(
            f"Missing required configuration fields: {', '.join(missing_fields)}"
        )
    
    return True

def validate_credentials(credentials: Any, auth_type: str) -> bool:
    """
    Validate credentials based on authentication type.
    
    Args:
        credentials: Credentials object to validate
        auth_type: Type of authentication (oauth2, api_key)
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If credentials are invalid
    """
    if auth_type.lower() == 'oauth2':
        required_attrs = ['client_id', 'client_secret', 'token_url']
        for attr in required_attrs:
            if not hasattr(credentials, attr) or not getattr(credentials, attr):
                raise ValidationError(f"Missing or empty OAuth2 credential: {attr}")
    
    elif auth_type.lower() == 'api_key':
        if not hasattr(credentials, 'api_key') or not credentials.api_key:
            raise ValidationError("Missing or empty API key")
    
    else:
        raise ValidationError(f"Unsupported authentication type: {auth_type}")
    
    return True

def validate_url(url: str, field_name: str = "URL") -> bool:
    """
    Validate URL format.
    
    Args:
        url: URL to validate
        field_name: Name of the field for error messages
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If URL is invalid
    """
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    if not url_pattern.match(url):
        raise ValidationError(f"Invalid {field_name} format: {url}")
    
    return True

def validate_email(email: str) -> bool:
    """
    Validate email format.
    
    Args:
        email: Email to validate
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If email is invalid
    """
    email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    if not email_pattern.match(email):
        raise ValidationError(f"Invalid email format: {email}")
    
    return True

def validate_phone(phone: str) -> bool:
    """
    Validate phone number format (basic validation).
    
    Args:
        phone: Phone number to validate
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If phone is invalid
    """
    # Remove common separators and spaces
    cleaned_phone = re.sub(r'[^\d+]', '', phone)
    
    # Check for reasonable length (7-15 digits, possibly with country code)
    if not re.match(r'^\+?[\d]{7,15}$', cleaned_phone):
        raise ValidationError(f"Invalid phone number format: {phone}")
    
    return True

# Jiva-specific validators based on API documentation
class JivaValidator:
    """Validator for Jiva API data structures."""
    
    @staticmethod
    def validate_contact(contact_data: Dict[str, Any]) -> bool:
        """
        Validate Jiva contact data structure according to API guide.
        
        Args:
            contact_data: Contact data dictionary
            
        Returns:
            True if valid
            
        Raises:
            ValidationError: If contact data is invalid
        """
        if 'contact' not in contact_data:
            raise ValidationError("Missing 'contact' wrapper in contact data")
        
        contact = contact_data['contact']
        
        # Required fields validation
        if not contact.get('contactName'):
            raise ValidationError("contactName is required", field="contactName")
        
        if len(contact['contactName']) > 100:
            raise ValidationError("contactName cannot exceed 100 characters", field="contactName")
        
        if not contact.get('contactTypes'):
            raise ValidationError("contactTypes is required", field="contactTypes")
        
        if not contact.get('memberLookup'):
            raise ValidationError("memberLookup is required", field="memberLookup")
        
        if not contact.get('phones'):
            raise ValidationError("phones is required", field="phones")
        
        # Validate nested structures
        JivaValidator.validate_contact_types(contact['contactTypes'])
        JivaValidator.validate_member_lookup(contact['memberLookup'])
        JivaValidator.validate_phones(contact['phones'])
        
        if 'episodeLookup' in contact:
            JivaValidator.validate_episode_lookup(contact['episodeLookup'])
        
        if 'addresses' in contact:
            JivaValidator.validate_addresses(contact['addresses'])
        
        if 'emails' in contact:
            JivaValidator.validate_emails(contact['emails'])
        
        if 'note' in contact:
            JivaValidator.validate_note(contact['note'])
        
        if 'daysOfWeek' in contact:
            JivaValidator.validate_days_of_week(contact['daysOfWeek'])
        
        # Validate optional fields with constraints
        JivaValidator.validate_optional_fields(contact)
        
        # Validate business rules
        JivaValidator.validate_business_rules(contact)
        
        return True
    
    @staticmethod
    def validate_contact_types(contact_types: Dict[str, Any]) -> bool:
        """Validate contactTypes structure."""
        if 'contactType' not in contact_types:
            raise ValidationError("contactType array is required in contactTypes", field="contactTypes")
        
        contact_type_list = contact_types['contactType']
        if not isinstance(contact_type_list, list):
            raise ValidationError("contactType must be an array", field="contactTypes")
        
        for i, ct in enumerate(contact_type_list):
            if not ct.get('contactTypeCd'):
                raise ValidationError(f"contactTypeCd is required in contactType[{i}]", field="contactTypes")
        
        return True
    
    @staticmethod
    def validate_addresses(addresses: Dict[str, Any]) -> bool:
        """Validate addresses structure with business rules."""
        if 'address' not in addresses:
            raise ValidationError("address array is required in addresses", field="addresses")
        
        address_list = addresses['address']
        if not isinstance(address_list, list):
            raise ValidationError("address must be an array", field="addresses")
        
        preferred_count = 0
        
        for i, addr in enumerate(address_list):
            # Required fields
            required_fields = ['addressTypeCd', 'addressLine1', 'city', 'zip', 'stateCd', 'countryCd', 'isPreferredAddress', 'recordActive']
            for field in required_fields:
                if field not in addr:
                    raise ValidationError(f"{field} is required in address[{i}]", field="addresses")
            
            # Field length validations
            if len(addr['addressLine1']) > 100:
                raise ValidationError(f"addressLine1 cannot exceed 100 characters in address[{i}]", field="addresses")
            
            if len(addr['city']) > 40:
                raise ValidationError(f"city cannot exceed 40 characters in address[{i}]", field="addresses")
            
            # Count preferred addresses
            if addr.get('isPreferredAddress'):
                preferred_count += 1
        
        # Business rule: Only one preferred address allowed
        if preferred_count > 1:
            raise ValidationError("Multiple preferred addresses provided. Only one address can be marked as preferred.", field="addresses")
        
        return True
    
    @staticmethod
    def validate_phones(phones: Dict[str, Any]) -> bool:
        """Validate phones structure with business rules."""
        if 'phone' not in phones:
            raise ValidationError("phone array is required in phones", field="phones")
        
        phone_list = phones['phone']
        if not isinstance(phone_list, list):
            raise ValidationError("phone must be an array", field="phones")
        
        preferred_count = 0
        
        for i, phone in enumerate(phone_list):
            # Required fields
            required_fields = ['phoneTypeCd', 'phoneNumber', 'isPreferredPhone', 'recordActive']
            for field in required_fields:
                if field not in phone:
                    raise ValidationError(f"{field} is required in phone[{i}]", field="phones")
            
            # Validate phone number
            try:
                validate_phone(phone['phoneNumber'])
            except ValidationError as e:
                raise ValidationError(f"Invalid phone number in phone[{i}]: {e.message}", field="phones")
            
            # Count preferred phones
            if phone.get('isPreferredPhone'):
                preferred_count += 1
        
        # Business rule: Only one preferred phone allowed
        if preferred_count > 1:
            raise ValidationError("Multiple preferred phones provided. Only one phone can be marked as preferred.", field="phones")
        
        return True
    
    @staticmethod
    def validate_emails(emails: Dict[str, Any]) -> bool:
        """Validate emails structure with business rules."""
        if 'email' not in emails:
            raise ValidationError("email array is required in emails", field="emails")
        
        email_list = emails['email']
        if not isinstance(email_list, list):
            raise ValidationError("email must be an array", field="emails")
        
        preferred_count = 0
        
        for i, email in enumerate(email_list):
            # Required fields - Note: Jiva uses 'emailId' not 'emailAddress'
            required_fields = ['emailTypeCd', 'emailId', 'isPreferredEmail', 'recordActive']
            for field in required_fields:
                if field not in email:
                    raise ValidationError(f"{field} is required in email[{i}]", field="emails")
            
            # Validate email format
            try:
                validate_email(email['emailId'])
            except ValidationError as e:
                raise ValidationError(f"Invalid email address in email[{i}]: {e.message}", field="emails")
            
            # Count preferred emails
            if email.get('isPreferredEmail'):
                preferred_count += 1
        
        # Business rule: Only one preferred email allowed
        if preferred_count > 1:
            raise ValidationError("Multiple preferred emails provided. Only one email can be marked as preferred.", field="emails")
        
        return True
    
    @staticmethod
    def validate_member_lookup(member_lookup: Dict[str, Any]) -> bool:
        """Validate memberLookup structure according to API guide."""
        if not isinstance(member_lookup, dict):
            raise ValidationError("memberLookup must be an object", field="memberLookup")
        
        # Check for mutually exclusive options
        has_jiva_id = 'jivaMemberId' in member_lookup
        has_external_id = 'memberId' in member_lookup
        has_member_id_type = 'memberIdTypeCd' in member_lookup
        
        if has_jiva_id and (has_external_id or has_member_id_type):
            raise ValidationError("memberLookup cannot have both jivaMemberId and external ID fields", field="memberLookup")
        
        if has_jiva_id:
            # Validate internal ID option
            if not isinstance(member_lookup['jivaMemberId'], int):
                raise ValidationError("jivaMemberId must be an integer", field="memberLookup")
        elif has_external_id:
            # Validate external ID option
            if not has_member_id_type:
                raise ValidationError("memberIdTypeCd is required when using memberId", field="memberLookup")
            
            if len(member_lookup['memberId']) > 50:
                raise ValidationError("memberId cannot exceed 50 characters", field="memberLookup")
            
            if len(member_lookup['memberIdTypeCd']) > 5:
                raise ValidationError("memberIdTypeCd cannot exceed 5 characters", field="memberLookup")
        else:
            raise ValidationError("memberLookup must have either jivaMemberId OR both memberId and memberIdTypeCd", field="memberLookup")
        
        return True
    
    @staticmethod
    def validate_episode_lookup(episode_lookup: Dict[str, Any]) -> bool:
        """Validate episodeLookup structure according to API guide."""
        if not isinstance(episode_lookup, dict):
            raise ValidationError("episodeLookup must be an object", field="episodeLookup")
        
        # Check for mutually exclusive options
        has_jiva_id = 'jivaEpisodeId' in episode_lookup
        has_external_id = 'extEpisodeId' in episode_lookup
        
        if has_jiva_id and has_external_id:
            raise ValidationError("episodeLookup cannot have both jivaEpisodeId and extEpisodeId", field="episodeLookup")
        
        if has_jiva_id:
            # Validate internal ID option
            if not isinstance(episode_lookup['jivaEpisodeId'], int):
                raise ValidationError("jivaEpisodeId must be an integer", field="episodeLookup")
        elif has_external_id:
            # Validate external ID option
            if len(episode_lookup['extEpisodeId']) > 40:
                raise ValidationError("extEpisodeId cannot exceed 40 characters", field="episodeLookup")
        else:
            raise ValidationError("episodeLookup must have either jivaEpisodeId OR extEpisodeId", field="episodeLookup")
        
        return True
    
    @staticmethod
    def validate_note(note: Dict[str, Any]) -> bool:
        """Validate note structure according to API guide."""
        if not isinstance(note, dict):
            raise ValidationError("note must be an object", field="note")
        
        # Required fields
        required_fields = ['noteTypeCd', 'noteDt', 'noteText']
        for field in required_fields:
            if field not in note:
                raise ValidationError(f"{field} is required in note", field="note")
        
        # Field length validation
        if len(note['noteTypeCd']) > 15:
            raise ValidationError("noteTypeCd cannot exceed 15 characters", field="note")
        
        if len(note['noteText']) > 1000:
            raise ValidationError("noteText cannot exceed 1000 characters", field="note")
        
        # Date format validation
        JivaValidator._validate_date_format(note['noteDt'], "noteDt")
        
        return True
    
    @staticmethod
    def validate_days_of_week(days_of_week: Dict[str, Any]) -> bool:
        """Validate daysOfWeek structure according to API guide."""
        if not isinstance(days_of_week, dict):
            raise ValidationError("daysOfWeek must be an object", field="daysOfWeek")
        
        if 'dayOfWeek' not in days_of_week:
            raise ValidationError("dayOfWeek array is required in daysOfWeek", field="daysOfWeek")
        
        day_list = days_of_week['dayOfWeek']
        if not isinstance(day_list, list):
            raise ValidationError("dayOfWeek must be an array", field="daysOfWeek")
        
        for i, day in enumerate(day_list):
            if not isinstance(day, dict):
                raise ValidationError(f"dayOfWeek[{i}] must be an object", field="daysOfWeek")
            
            if 'weekdayCd' not in day:
                raise ValidationError(f"weekdayCd is required in dayOfWeek[{i}]", field="daysOfWeek")
            
            if len(day['weekdayCd']) > 10:
                raise ValidationError(f"weekdayCd cannot exceed 10 characters in dayOfWeek[{i}]", field="daysOfWeek")
        
        return True
    
    @staticmethod
    def validate_optional_fields(contact: Dict[str, Any]) -> bool:
        """Validate optional fields with specific constraints."""
        # String length validation
        string_fields = {
            'extContactId': 50,
            'organization': 100,
            'importantBecause': 100,
            'preferredMethodOfContactCd': 15,
            'preferredTimeCd': 30
        }
        
        for field, max_length in string_fields.items():
            if contact.get(field) and len(contact[field]) > max_length:
                raise ValidationError(f"{field} cannot exceed {max_length} characters", field=field)
        
        # Date format validation
        date_fields = ['aorStartDate', 'aorEndDate']
        for field in date_fields:
            if contact.get(field):
                JivaValidator._validate_date_format(contact[field], field)
        
        # Boolean validation
        boolean_fields = ['isAuthorizedRepresentative']
        for field in boolean_fields:
            if field in contact and not isinstance(contact[field], bool):
                raise ValidationError(f"{field} must be a boolean value", field=field)
        
        return True
    
    @staticmethod
    def validate_business_rules(contact: Dict[str, Any]) -> bool:
        """Validate comprehensive Jiva business rules."""
        # AOR date validation
        aor_start = contact.get('aorStartDate')
        aor_end = contact.get('aorEndDate')
        if aor_start and aor_end:
            try:
                from datetime import datetime
                start_date = datetime.strptime(aor_start, '%Y-%m-%d')
                end_date = datetime.strptime(aor_end, '%Y-%m-%d')
                if start_date >= end_date:
                    raise ValidationError("aorStartDate must be before aorEndDate", field="aorStartDate")
            except ValueError as e:
                if "time data" in str(e):
                    pass  # Date format errors already caught in field validation
                else:
                    raise
        
        # Collection-specific business rules
        if 'addresses' in contact and contact['addresses']:
            JivaValidator._validate_collection_business_rules(
                contact['addresses'].get('address', []),
                'addresses', 
                'addressTypeCd', 
                'isPreferredAddress'
            )
        
        if 'phones' in contact and contact['phones']:
            JivaValidator._validate_collection_business_rules(
                contact['phones'].get('phone', []),
                'phones',
                'phoneTypeCd',
                'isPreferredPhone'
            )
        
        if 'emails' in contact and contact['emails']:
            JivaValidator._validate_collection_business_rules(
                contact['emails'].get('email', []),
                'emails',
                'emailTypeCd', 
                'isPreferredEmail'
            )
        
        if 'contactTypes' in contact and contact['contactTypes']:
            JivaValidator._validate_contact_types_business_rules(
                contact['contactTypes'].get('contactType', [])
            )
        
        return True
    
    @staticmethod
    def _validate_collection_business_rules(
        collection: List[Dict[str, Any]], 
        collection_name: str, 
        type_field: str, 
        preferred_field: str
    ) -> bool:
        """Validate collection-specific business rules."""
        if not collection:
            return True
        
        # 1. No inactive records validation
        inactive_items = [item for item in collection if item.get('recordActive') is False]
        if inactive_items:
            raise ValidationError(f"API does not allow adding inactive {collection_name} for a contact", field=collection_name)
        
        # 2. No duplicate types validation
        type_values = [item.get(type_field) for item in collection if item.get(type_field)]
        if len(type_values) != len(set(type_values)):
            duplicate_types = [t for t in type_values if type_values.count(t) > 1]
            raise ValidationError(f"Duplicate {type_field} found in {collection_name}: {duplicate_types[0]}", field=collection_name)
        
        # 3. Preferred flag validation
        preferred_items = [item for item in collection if item.get(preferred_field) is True]
        
        if len(collection) == 1:
            # Single item must be preferred
            if len(preferred_items) != 1:
                raise ValidationError(f"If contact has only one {collection_name[:-1]}, it should be marked as preferred", field=collection_name)
        elif len(collection) > 1:
            # Multiple items: exactly one must be preferred
            if len(preferred_items) == 0:
                raise ValidationError(f"At least one preferred record should be provided in {collection_name}", field=collection_name)
            elif len(preferred_items) > 1:
                raise ValidationError(f"Multiple preferred records provided in {collection_name}. Only one can be preferred.", field=collection_name)
        
        return True
    
    @staticmethod
    def _validate_contact_types_business_rules(contact_types: List[Dict[str, Any]]) -> bool:
        """Validate contact types business rules."""
        if not contact_types:
            raise ValidationError("At least one contact type is required", field="contactTypes")
        
        # No duplicate contact types
        type_codes = [ct.get('contactTypeCd') for ct in contact_types if ct.get('contactTypeCd')]
        if len(type_codes) != len(set(type_codes)):
            duplicate_types = [t for t in type_codes if type_codes.count(t) > 1]
            raise ValidationError(f"Duplicate contactTypeCd found: {duplicate_types[0]}", field="contactTypes")
        
        return True
    
    @staticmethod
    def validate_search_parameters(search_params: Dict[str, Any]) -> bool:
        """Validate search parameters according to Jiva API requirements."""
        # At least one search parameter is required
        valid_search_params = [
            'jiva_member_id', 'ext_member_id', 'jiva_episode_id', 
            'ext_episode_id', 'contact_name', 'organization'
        ]
        
        has_search_criteria = any(search_params.get(param) for param in valid_search_params)
        if not has_search_criteria:
            raise ValidationError("At least one search parameter is required")
        
        # Validate pagination parameters
        limit = search_params.get('limit', 50)
        if not isinstance(limit, int) or limit < 1 or limit > 200:
            raise ValidationError("limit must be between 1 and 200", field="limit")
        
        start_index = search_params.get('start_index', 1)
        if not isinstance(start_index, int) or start_index < 1:
            raise ValidationError("start_index must be >= 1", field="start_index")
        
        # Validate external member ID format if provided
        ext_member_id = search_params.get('ext_member_id')
        if ext_member_id and ',' not in ext_member_id:
            raise ValidationError("ext_member_id format must be: memberIdTypeCd,memberId", field="ext_member_id")
        
        return True
    
    @staticmethod
    def validate_code_table_values(contact_data: Dict[str, Any], code_tables: Dict[str, List[str]]) -> bool:
        """Validate all code table values in contact data."""
        # Validate top-level code fields
        for field, value in contact_data.items():
            if field.endswith('Cd') and value:
                table_name = JivaValidator._get_code_table_name(field)
                if table_name and table_name in code_tables:
                    if value not in code_tables[table_name]:
                        raise ValidationError(f"Invalid {field} value '{value}'. Valid values: {code_tables[table_name]}", field=field)
        
        # Validate collection code fields
        collections = ['contactTypes', 'addresses', 'phones', 'emails', 'daysOfWeek']
        for collection_name in collections:
            if collection_name in contact_data:
                JivaValidator._validate_collection_codes(contact_data[collection_name], code_tables, collection_name)
        
        return True
    
    @staticmethod
    def _get_code_table_name(field_name: str) -> Optional[str]:
        """Map field names to code table names."""
        mapping = {
            'contactTypeCd': 'Encounter Contact Type',
            'preferredMethodOfContactCd': 'Contact Preference',
            'preferredTimeCd': 'Preferred Time',
            'addressTypeCd': 'Address Type',
            'stateCd': 'State',
            'countryCd': 'Country',
            'phoneTypeCd': 'Phone Type',
            'emailTypeCd': 'Email Type',
            'noteTypeCd': 'Note Type',
            'weekdayCd': 'Week Days',
            'memberIdTypeCd': 'Member ID Type'
        }
        return mapping.get(field_name)
    
    @staticmethod
    def _validate_collection_codes(collection: Dict[str, Any], code_tables: Dict[str, List[str]], collection_name: str) -> bool:
        """Validate code fields within collections."""
        if collection_name == 'contactTypes' and 'contactType' in collection:
            for ct in collection['contactType']:
                if 'contactTypeCd' in ct:
                    table_name = 'Encounter Contact Type'
                    if ct['contactTypeCd'] not in code_tables.get(table_name, []):
                        raise ValidationError(f"Invalid contactTypeCd '{ct['contactTypeCd']}'", field="contactTypes")
        
        elif collection_name == 'addresses' and 'address' in collection:
            for addr in collection['address']:
                for field in ['addressTypeCd', 'stateCd', 'countryCd']:
                    if field in addr:
                        table_name = JivaValidator._get_code_table_name(field)
                        if table_name and addr[field] not in code_tables.get(table_name, []):
                            raise ValidationError(f"Invalid {field} '{addr[field]}' in address", field="addresses")
        
        elif collection_name == 'phones' and 'phone' in collection:
            for phone in collection['phone']:
                if 'phoneTypeCd' in phone:
                    table_name = 'Phone Type'
                    if phone['phoneTypeCd'] not in code_tables.get(table_name, []):
                        raise ValidationError(f"Invalid phoneTypeCd '{phone['phoneTypeCd']}'", field="phones")
        
        elif collection_name == 'emails' and 'email' in collection:
            for email in collection['email']:
                if 'emailTypeCd' in email:
                    table_name = 'Email Type'
                    if email['emailTypeCd'] not in code_tables.get(table_name, []):
                        raise ValidationError(f"Invalid emailTypeCd '{email['emailTypeCd']}'", field="emails")
        
        elif collection_name == 'daysOfWeek' and 'dayOfWeek' in collection:
            for day in collection['dayOfWeek']:
                if 'weekdayCd' in day:
                    table_name = 'Week Days'
                    if day['weekdayCd'] not in code_tables.get(table_name, []):
                        raise ValidationError(f"Invalid weekdayCd '{day['weekdayCd']}'", field="daysOfWeek")
        
        return True
    
    @staticmethod
    def validate_state_country_combination(state_cd: str, country_cd: str) -> bool:
        """Validate state and country code combination."""
        # US state codes
        us_states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]
        # Canadian provinces 
        ca_provinces = ["AB", "BC", "MB", "NB", "NL", "NS", "NT", "NU", "ON", "PE", "QC", "SK", "YT"]
        
        if country_cd == "US" and state_cd not in us_states:
            raise ValidationError(f"Invalid state code '{state_cd}' for country US", field="stateCd")
        elif country_cd == "CA" and state_cd not in ca_provinces:
            raise ValidationError(f"Invalid province code '{state_cd}' for country CA", field="stateCd")
        
        return True
    
    @staticmethod
    def _validate_date_format(date_string: str, field_name: str = "date") -> bool:
        """Validate date format (YYYY-MM-DD)."""
        try:
            from datetime import datetime
            datetime.strptime(date_string, '%Y-%m-%d')
            return True
        except ValueError:
            raise ValidationError(f"{field_name} must be in YYYY-MM-DD format", field=field_name)