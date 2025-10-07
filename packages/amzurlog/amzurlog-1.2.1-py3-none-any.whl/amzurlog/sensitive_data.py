"""
Sensitive Data Protection for AmzurLog
=====================================

This module provides comprehensive sensitive data protection including:
- Password and token masking with placeholders (*****)
- Email and API key masking (partial visibility)
- PII protection
- Custom field redaction
- Pattern-based detection
"""

import re
import json
from typing import Any, Dict, List, Set, Pattern, Union
from .core import LogLevel


class SensitiveDataProtector:
    """Comprehensive sensitive data protection for logging"""
    
    # Fields that should be completely replaced with placeholders
    PLACEHOLDER_FIELDS = {
        'password', 'passwd', 'pwd', 'secret', 'token', 'auth_token', 
        'access_token', 'refresh_token', 'jwt', 'bearer_token', 'oauth_token',
        'private_key', 'secret_key', 'encryption_key', 'session_key',
        'credit_card', 'card_number', 'cvv', 'ssn', 'social_security',
        'pin', 'otp', 'verification_code', 'auth_code'
    }
    
    # Fields that should be partially masked (show some characters)
    MASKING_FIELDS = {
        'email', 'email_address', 'username', 'user_name', 'phone', 'phone_number',
        'api_key', 'client_id', 'user_id', 'account_id', 'customer_id',
        'ip_address', 'ip', 'address', 'street_address'
    }
    
    # Regex patterns for automatic detection
    SENSITIVE_PATTERNS = {
        'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
        'credit_card': re.compile(r'\b(?:\d{4}[-\s]?){3}\d{4}\b'),
        'ssn': re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
        'phone': re.compile(r'\b\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b'),
        'api_key': re.compile(r'\b[A-Za-z0-9]{32,}\b'),
        'jwt': re.compile(r'\bey[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*\b'),
        'ip_address': re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'),
        'password_context': re.compile(r'\b(?:password|passwd|pwd)\s*(?:is|=|:)\s*([A-Za-z0-9@#$%^&*!]{4,})', re.IGNORECASE),
        'token_context': re.compile(r'\b(?:token|key)\s*(?:is|=|:)\s*([A-Za-z0-9_-]{8,})', re.IGNORECASE)
    }
    
    def __init__(self, 
                 placeholder: str = "******",
                 mask_char: str = "*",
                 show_chars: int = 3,
                 custom_placeholder_fields: Set[str] = None,
                 custom_masking_fields: Set[str] = None,
                 enabled: bool = True):
        """
        Initialize sensitive data protector
        
        Args:
            placeholder: String to replace sensitive values (default: "******")
            mask_char: Character used for masking (default: "*")
            show_chars: Number of characters to show when masking (default: 3)
            custom_placeholder_fields: Additional fields to replace with placeholders
            custom_masking_fields: Additional fields to mask partially
            enabled: Whether protection is enabled (default: True)
        """
        self.placeholder = placeholder
        self.mask_char = mask_char
        self.show_chars = show_chars
        self.enabled = enabled
        
        # Combine default and custom fields
        self.placeholder_fields = self.PLACEHOLDER_FIELDS.copy()
        if custom_placeholder_fields:
            self.placeholder_fields.update(custom_placeholder_fields)
            
        self.masking_fields = self.MASKING_FIELDS.copy()
        if custom_masking_fields:
            self.masking_fields.update(custom_masking_fields)
    
    def mask_value(self, value: str, show_chars: int = None) -> str:
        """
        Mask a value showing only the first few characters
        
        Args:
            value: Value to mask
            show_chars: Number of characters to show (uses instance default if None)
        
        Returns:
            Masked value
        """
        if not value or not isinstance(value, str):
            return str(value)
            
        show = show_chars if show_chars is not None else self.show_chars
        
        if len(value) <= show:
            return self.mask_char * len(value)
        
        return value[:show] + self.mask_char * (len(value) - show)
    
    def mask_email(self, email: str) -> str:
        """
        Mask email address showing first few chars of username and domain
        
        Args:
            email: Email address to mask
        
        Returns:
            Masked email (e.g., "joh***@exa***.com")
        """
        if '@' not in email:
            return self.mask_value(email)
        
        username, domain = email.split('@', 1)
        
        # Mask username
        if len(username) <= 3:
            masked_username = self.mask_char * len(username)
        else:
            masked_username = username[:3] + self.mask_char * (len(username) - 3)
        
        # Mask domain but keep TLD visible
        if '.' in domain:
            domain_parts = domain.rsplit('.', 1)
            domain_name = domain_parts[0]
            tld = domain_parts[1]
            
            if len(domain_name) <= 3:
                masked_domain = self.mask_char * len(domain_name)
            else:
                masked_domain = domain_name[:3] + self.mask_char * (len(domain_name) - 3)
            
            return f"{masked_username}@{masked_domain}.{tld}"
        else:
            return f"{masked_username}@{self.mask_value(domain)}"
    
    def mask_api_key(self, api_key: str) -> str:
        """
        Mask API key showing first and last few characters
        
        Args:
            api_key: API key to mask
        
        Returns:
            Masked API key (e.g., "abc***xyz")
        """
        if len(api_key) <= 6:
            return self.mask_char * len(api_key)
        
        return api_key[:3] + self.mask_char * (len(api_key) - 6) + api_key[-3:]
    
    def protect_field_value(self, field_name: str, value: Any) -> Any:
        """
        Protect a field value based on its name and content
        
        Args:
            field_name: Name of the field
            value: Value to protect
        
        Returns:
            Protected value
        """
        if not self.enabled or value is None:
            return value
        
        field_lower = field_name.lower()
        str_value = str(value)
        
        # Check for placeholder fields (complete replacement)
        for sensitive_field in self.placeholder_fields:
            if sensitive_field in field_lower:
                return self.placeholder
        
        # Check for masking fields (partial masking)
        for masking_field in self.masking_fields:
            if masking_field in field_lower:
                if 'email' in field_lower and '@' in str_value:
                    return self.mask_email(str_value)
                elif 'api_key' in field_lower or 'key' in field_lower:
                    return self.mask_api_key(str_value)
                else:
                    return self.mask_value(str_value)
        
        return value
    
    def protect_text_patterns(self, text: str) -> str:
        """
        Protect sensitive patterns found in text using regex
        
        Args:
            text: Text to scan and protect
        
        Returns:
            Text with sensitive patterns protected
        """
        if not self.enabled or not text:
            return text
        
        protected_text = text
        
        # Apply pattern-based protection
        for pattern_name, pattern in self.SENSITIVE_PATTERNS.items():
            if pattern_name == 'email':
                protected_text = pattern.sub(
                    lambda m: self.mask_email(m.group(0)), 
                    protected_text
                )
            elif pattern_name in ['credit_card', 'ssn', 'jwt']:
                protected_text = pattern.sub(self.placeholder, protected_text)
            elif pattern_name in ['password_context', 'token_context']:
                # For context patterns, replace the captured value with placeholder
                protected_text = pattern.sub(
                    lambda m: m.group(0).replace(m.group(1), self.placeholder),
                    protected_text
                )
            elif pattern_name in ['api_key']:
                protected_text = pattern.sub(
                    lambda m: self.mask_api_key(m.group(0)), 
                    protected_text
                )
            else:
                protected_text = pattern.sub(
                    lambda m: self.mask_value(m.group(0)), 
                    protected_text
                )
        
        return protected_text
    
    def protect_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively protect sensitive data in a dictionary
        
        Args:
            data: Dictionary to protect
        
        Returns:
            Protected dictionary
        """
        if not self.enabled or not isinstance(data, dict):
            return data
        
        protected = {}
        
        for key, value in data.items():
            if isinstance(value, dict):
                protected[key] = self.protect_dict(value)
            elif isinstance(value, list):
                protected[key] = self.protect_list(value)
            elif isinstance(value, str):
                # First check field name, then patterns
                field_protected = self.protect_field_value(key, value)
                if field_protected != value:
                    protected[key] = field_protected
                else:
                    protected[key] = self.protect_text_patterns(value)
            else:
                protected[key] = self.protect_field_value(key, value)
        
        return protected
    
    def protect_list(self, data: List[Any]) -> List[Any]:
        """
        Recursively protect sensitive data in a list
        
        Args:
            data: List to protect
        
        Returns:
            Protected list
        """
        if not self.enabled or not isinstance(data, list):
            return data
        
        protected = []
        
        for item in data:
            if isinstance(item, dict):
                protected.append(self.protect_dict(item))
            elif isinstance(item, list):
                protected.append(self.protect_list(item))
            elif isinstance(item, str):
                protected.append(self.protect_text_patterns(item))
            else:
                protected.append(item)
        
        return protected
    
    def protect_log_data(self, log_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Protect sensitive data in log record
        
        Args:
            log_data: Log data dictionary
        
        Returns:
            Protected log data
        """
        if not self.enabled:
            return log_data
        
        # Protect the main log data
        protected_data = self.protect_dict(log_data.copy())
        
        # Special handling for message field
        if 'message' in protected_data and isinstance(protected_data['message'], str):
            protected_data['message'] = self.protect_text_patterns(protected_data['message'])
        
        return protected_data


class SensitiveDataFilter:
    """Log filter that removes or masks sensitive information"""
    
    def __init__(self, protector: SensitiveDataProtector = None):
        """
        Initialize filter with a data protector
        
        Args:
            protector: SensitiveDataProtector instance (creates default if None)
        """
        self.protector = protector or SensitiveDataProtector()
    
    def filter(self, record) -> bool:
        """
        Filter log record to protect sensitive data
        
        Args:
            record: Log record to filter
        
        Returns:
            True to allow the record (always returns True after protection)
        """
        # Protect the record's extra data
        if hasattr(record, 'extra') and record.extra:
            record.extra = self.protector.protect_dict(record.extra)
        
        # Protect the message
        if hasattr(record, 'message') and record.message:
            record.message = self.protector.protect_text_patterns(record.message)
        
        return True


# Convenience functions for common protection scenarios
def create_default_protector() -> SensitiveDataProtector:
    """Create a default sensitive data protector with standard settings"""
    return SensitiveDataProtector()


def create_strict_protector() -> SensitiveDataProtector:
    """Create a strict protector that masks more aggressively"""
    return SensitiveDataProtector(
        show_chars=2,  # Show fewer characters
        custom_placeholder_fields={'client_secret', 'private_token', 'session_id'},
        custom_masking_fields={'first_name', 'last_name', 'full_name', 'address'}
    )


def create_compliance_protector() -> SensitiveDataProtector:
    """Create a protector configured for compliance (GDPR, HIPAA, etc.)"""
    return SensitiveDataProtector(
        show_chars=1,  # Minimal visibility
        custom_placeholder_fields={
            'patient_id', 'medical_record', 'diagnosis', 'treatment',
            'social_security', 'tax_id', 'passport', 'driver_license'
        },
        custom_masking_fields={
            'patient_name', 'doctor_name', 'insurance_id', 'member_id'
        }
    )


# Quick setup functions
def protect_passwords_and_tokens(data: Dict[str, Any]) -> Dict[str, Any]:
    """Quick function to protect common sensitive fields in data"""
    protector = SensitiveDataProtector()
    return protector.protect_dict(data)


def mask_email_and_ids(data: Dict[str, Any]) -> Dict[str, Any]:
    """Quick function to mask emails and IDs in data"""
    protector = SensitiveDataProtector()
    return protector.protect_dict(data)


def sanitize_log_message(message: str) -> str:
    """Quick function to sanitize sensitive patterns in log messages"""
    protector = SensitiveDataProtector()
    return protector.protect_text_patterns(message)