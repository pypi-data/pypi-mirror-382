"""
AmzurLog Formatters
===================

This module contains various formatters for converting log records to strings:
- SimpleFormatter: Basic text formatting
- JSONFormatter: JSON format output
- ColoredFormatter: Colored console output
"""

import json
import sys
from datetime import datetime
from typing import Dict, Any

from .core import LogRecord, LogLevel


class BaseFormatter:
    """Base class for all formatters"""
    
    def format(self, record: LogRecord) -> str:
        """Format a log record - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement format()")


class SimpleFormatter(BaseFormatter):
    """Simple text formatter"""
    
    def __init__(self, format_string: str = None):
        self.format_string = format_string or "[{timestamp}] {level}: {message}"
        
    def format(self, record: LogRecord) -> str:
        """Format the log record as simple text"""
        try:
            # Prepare format variables
            format_vars = {
                'timestamp': record.timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
                'level': record.level.name,
                'logger': record.logger_name,
                'message': record.message,
                'thread_id': record.thread_id,
                'thread_name': record.thread_name,
            }
            
            # Add extra fields
            format_vars.update(record.extra)
            
            # Format the message
            formatted = self.format_string.format(**format_vars)
            
            # Add exception info if present
            if record.exception_text:
                formatted += f"\n{record.exception_text}"
                
            return formatted
            
        except Exception as e:
            # Fallback formatting
            return f"[{record.timestamp}] {record.level.name}: {record.message} (Format Error: {e})"


class JSONFormatter(BaseFormatter):
    """JSON formatter"""
    
    def __init__(self, indent: int = None, ensure_ascii: bool = False):
        self.indent = indent
        self.ensure_ascii = ensure_ascii
        
    def format(self, record: LogRecord) -> str:
        """Format the log record as JSON"""
        try:
            record_dict = record.to_dict()
            return json.dumps(
                record_dict,
                indent=self.indent,
                ensure_ascii=self.ensure_ascii,
                default=str
            )
        except Exception as e:
            # Fallback to simple dict
            fallback = {
                'timestamp': str(record.timestamp),
                'level': str(record.level),
                'logger': record.logger_name,
                'message': record.message,
                'format_error': str(e)
            }
            return json.dumps(fallback)


class ColoredFormatter(BaseFormatter):
    """Colored console formatter with ANSI color codes"""
    
    # ANSI color codes
    COLORS = {
        LogLevel.DEBUG: '\033[36m',      # Cyan
        LogLevel.INFO: '\033[32m',       # Green
        LogLevel.WARNING: '\033[33m',    # Yellow
        LogLevel.ERROR: '\033[31m',      # Red
        LogLevel.CRITICAL: '\033[35m',   # Magenta
    }
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    def __init__(self, format_string: str = None, use_colors: bool = None):
        self.format_string = format_string or "[{timestamp}] {colored_level}: {message}"
        
        # Auto-detect color support
        if use_colors is None:
            self.use_colors = self._supports_color()
        else:
            self.use_colors = use_colors
            
    def _supports_color(self) -> bool:
        """Check if the terminal supports colors"""
        # Check if output is being redirected
        if not hasattr(sys.stdout, 'isatty') or not sys.stdout.isatty():
            return False
            
        # Check for common color-supporting terminals
        import os
        term = os.environ.get('TERM', '').lower()
        colorterm = os.environ.get('COLORTERM', '').lower()
        
        if 'color' in term or 'color' in colorterm:
            return True
            
        if term in ('xterm', 'xterm-256color', 'screen', 'linux'):
            return True
            
        # Windows command prompt
        if sys.platform == 'win32':
            try:
                import colorama
                return True
            except ImportError:
                return False
                
        return False
        
    def _colorize(self, text: str, level: LogLevel) -> str:
        """Add color codes to text based on log level"""
        if not self.use_colors:
            return text
            
        color = self.COLORS.get(level, '')
        return f"{color}{text}{self.RESET}"
        
    def format(self, record: LogRecord) -> str:
        """Format the log record with colors"""
        try:
            # Prepare format variables
            format_vars = {
                'timestamp': record.timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
                'level': record.level.name,
                'colored_level': self._colorize(record.level.name, record.level),
                'logger': record.logger_name,
                'message': record.message,
                'thread_id': record.thread_id,
                'thread_name': record.thread_name,
            }
            
            # Add extra fields
            format_vars.update(record.extra)
            
            # Format the message
            formatted = self.format_string.format(**format_vars)
            
            # Add exception info if present
            if record.exception_text:
                colored_exception = self._colorize(record.exception_text, LogLevel.ERROR)
                formatted += f"\n{colored_exception}"
                
            return formatted
            
        except Exception as e:
            # Fallback formatting
            fallback_msg = f"[{record.timestamp}] {record.level.name}: {record.message} (Format Error: {e})"
            return self._colorize(fallback_msg, record.level)


class TemplateFormatter(BaseFormatter):
    """Template-based formatter with custom field handling"""
    
    def __init__(self, template: str, field_formatters: Dict[str, callable] = None):
        self.template = template
        self.field_formatters = field_formatters or {}
        
    def format(self, record: LogRecord) -> str:
        """Format using template with custom field formatters"""
        try:
            # Prepare format variables
            format_vars = {
                'timestamp': record.timestamp,
                'level': record.level,
                'logger': record.logger_name,
                'message': record.message,
                'thread_id': record.thread_id,
                'thread_name': record.thread_name,
            }
            
            # Add extra fields
            format_vars.update(record.extra)
            
            # Apply custom formatters
            for field, formatter in self.field_formatters.items():
                if field in format_vars:
                    try:
                        format_vars[field] = formatter(format_vars[field])
                    except Exception:
                        pass  # Keep original value on error
                        
            # Format the message
            formatted = self.template.format(**format_vars)
            
            # Add exception info if present
            if record.exception_text:
                formatted += f"\n{record.exception_text}"
                
            return formatted
            
        except Exception as e:
            # Fallback formatting
            return f"[{record.timestamp}] {record.level.name}: {record.message} (Template Error: {e})"


class CSVFormatter(BaseFormatter):
    """CSV formatter for structured logging"""
    
    def __init__(self, fields: list = None, delimiter: str = ',', quote_char: str = '"'):
        self.fields = fields or ['timestamp', 'level', 'logger', 'message']
        self.delimiter = delimiter
        self.quote_char = quote_char
        
    def _quote_field(self, value: str) -> str:
        """Quote a field if necessary"""
        value_str = str(value)
        if self.delimiter in value_str or self.quote_char in value_str or '\n' in value_str:
            # Escape quote characters by doubling them
            escaped = value_str.replace(self.quote_char, self.quote_char + self.quote_char)
            return f"{self.quote_char}{escaped}{self.quote_char}"
        return value_str
        
    def format(self, record: LogRecord) -> str:
        """Format the log record as CSV"""
        try:
            # Prepare all available fields
            all_fields = {
                'timestamp': record.timestamp.isoformat(),
                'level': record.level.name,
                'logger': record.logger_name,
                'message': record.message,
                'thread_id': record.thread_id,
                'thread_name': record.thread_name,
            }
            
            # Add extra fields
            all_fields.update(record.extra)
            
            # Extract values for specified fields
            values = []
            for field in self.fields:
                value = all_fields.get(field, '')
                values.append(self._quote_field(value))
                
            return self.delimiter.join(values)
            
        except Exception as e:
            # Fallback formatting
            return f"CSV Format Error: {e}"
            
    def get_header(self) -> str:
        """Get the CSV header row"""
        return self.delimiter.join(self.fields)