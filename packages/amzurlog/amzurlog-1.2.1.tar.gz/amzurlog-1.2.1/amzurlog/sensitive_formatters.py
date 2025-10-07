"""
Sensitive Data Aware Formatters
==============================

Formatters that automatically protect sensitive information in log output.
"""

import json
from datetime import datetime
from typing import Dict, Any
from .formatters import SimpleFormatter, JSONFormatter, ColoredFormatter
from .sensitive_data import SensitiveDataProtector, SensitiveDataFilter


class SensitiveSimpleFormatter(SimpleFormatter):
    """Simple formatter with automatic sensitive data protection"""
    
    def __init__(self, 
                 format_string: str = None,
                 protector: SensitiveDataProtector = None):
        """
        Initialize formatter with sensitive data protection
        
        Args:
            format_string: Log format string
            protector: SensitiveDataProtector instance
        """
        super().__init__(format_string)
        self.protector = protector or SensitiveDataProtector()
    
    def format(self, record) -> str:
        """Format log record with sensitive data protection"""
        # Protect the record's extra data
        if hasattr(record, 'extra') and record.extra:
            record.extra = self.protector.protect_dict(record.extra)
        
        # Protect the message
        if hasattr(record, 'message') and record.message:
            record.message = self.protector.protect_text_patterns(record.message)
        
        # Get the formatted output
        formatted_output = super().format(record)
        
        # Apply pattern protection to the final formatted string as well
        return self.protector.protect_text_patterns(formatted_output)


class SensitiveJSONFormatter(JSONFormatter):
    """JSON formatter with automatic sensitive data protection"""
    
    def __init__(self, 
                 include_timestamp: bool = True,
                 protector: SensitiveDataProtector = None):
        """
        Initialize JSON formatter with sensitive data protection
        
        Args:
            include_timestamp: Whether to include timestamp in output
            protector: SensitiveDataProtector instance
        """
        super().__init__(include_timestamp)
        self.protector = protector or SensitiveDataProtector()
    
    def format(self, record) -> str:
        """Format log record as protected JSON"""
        # Protect the record's extra data first
        if hasattr(record, 'extra') and record.extra:
            record.extra = self.protector.protect_dict(record.extra)
        
        # Protect the message
        if hasattr(record, 'message') and record.message:
            record.message = self.protector.protect_text_patterns(record.message)
        
        # Use the parent JSONFormatter to format the protected record
        return super().format(record)


class SensitiveColoredFormatter(ColoredFormatter):
    """Colored formatter with automatic sensitive data protection"""
    
    def __init__(self, 
                 format_string: str = None,
                 protector: SensitiveDataProtector = None):
        """
        Initialize colored formatter with sensitive data protection
        
        Args:
            format_string: Log format string
            protector: SensitiveDataProtector instance
        """
        super().__init__(format_string)
        self.protector = protector or SensitiveDataProtector()
    
    def format(self, record) -> str:
        """Format log record with colors and sensitive data protection"""
        # Protect the record's extra data
        if hasattr(record, 'extra') and record.extra:
            record.extra = self.protector.protect_dict(record.extra)
        
        # Protect the message
        if hasattr(record, 'message') and record.message:
            record.message = self.protector.protect_text_patterns(record.message)
        
        # Get the formatted output
        formatted_output = super().format(record)
        
        # Apply pattern protection to the final formatted string as well
        return self.protector.protect_text_patterns(formatted_output)