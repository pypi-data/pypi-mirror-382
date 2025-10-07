"""
Core AmzurLog Components
========================

This module contains the core logging functionality including:
- LogLevel enumeration
- LogRecord class for representing log entries
- AmzurLogger class for the main logging interface
"""

import time
import threading
import traceback
from enum import IntEnum
from typing import Any, Dict, List, Optional, Union
from datetime import datetime


class LogLevel(IntEnum):
    """Log levels enumeration"""
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50

    @classmethod
    def from_string(cls, level_str: str) -> 'LogLevel':
        """Convert string to LogLevel"""
        level_map = {
            'DEBUG': cls.DEBUG,
            'INFO': cls.INFO,
            'WARNING': cls.WARNING,
            'ERROR': cls.ERROR,
            'CRITICAL': cls.CRITICAL
        }
        return level_map.get(level_str.upper(), cls.INFO)

    def __str__(self):
        return self.name


class LogRecord:
    """Represents a single log record"""
    
    def __init__(
        self,
        level: LogLevel,
        message: str,
        logger_name: str,
        timestamp: Optional[datetime] = None,
        extra: Optional[Dict[str, Any]] = None,
        exc_info: Optional[tuple] = None
    ):
        self.level = level
        self.message = message
        self.logger_name = logger_name
        self.timestamp = timestamp or datetime.now()
        self.extra = extra or {}
        self.exc_info = exc_info
        self.thread_id = threading.get_ident()
        self.thread_name = threading.current_thread().name
        
        # Add exception information if available
        if exc_info and len(exc_info) == 3:
            self.exception_text = ''.join(traceback.format_exception(*exc_info))
        else:
            self.exception_text = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert log record to dictionary"""
        record_dict = {
            'timestamp': self.timestamp.isoformat(),
            'level': str(self.level),
            'logger': self.logger_name,
            'message': self.message,
            'thread_id': self.thread_id,
            'thread_name': self.thread_name,
        }
        
        # Add extra fields
        record_dict.update(self.extra)
        
        # Add exception info if present
        if self.exception_text:
            record_dict['exception'] = self.exception_text
            
        return record_dict


class AmzurLogger:
    """Main logger class for AmzurLog"""
    
    def __init__(self, name: str):
        self.name = name
        self.level = LogLevel.INFO
        self.handlers = []
        self.filters = []
        self._lock = threading.RLock()
        self.disabled = False
        self.propagate = True
        
    def set_level(self, level: Union[LogLevel, str, int]):
        """Set the logging level"""
        if isinstance(level, str):
            level = LogLevel.from_string(level)
        elif isinstance(level, int):
            level = LogLevel(level)
        self.level = level
        
    def add_handler(self, handler):
        """Add a handler to the logger"""
        with self._lock:
            if handler not in self.handlers:
                self.handlers.append(handler)
                
    def remove_handler(self, handler):
        """Remove a handler from the logger"""
        with self._lock:
            if handler in self.handlers:
                self.handlers.remove(handler)
                
    def add_filter(self, filter_obj):
        """Add a filter to the logger"""
        with self._lock:
            if filter_obj not in self.filters:
                self.filters.append(filter_obj)
                
    def remove_filter(self, filter_obj):
        """Remove a filter from the logger"""
        with self._lock:
            if filter_obj in self.filters:
                self.filters.remove(filter_obj)
                
    def is_enabled_for(self, level: LogLevel) -> bool:
        """Check if logger is enabled for the given level"""
        return not self.disabled and level >= self.level
        
    def _apply_filters(self, record: LogRecord) -> bool:
        """Apply all filters to the record"""
        for filter_obj in self.filters:
            if not filter_obj.filter(record):
                return False
        return True
        
    def _log(
        self,
        level: LogLevel,
        message: str,
        extra: Optional[Dict[str, Any]] = None,
        exc_info: Optional[tuple] = None,
        **kwargs
    ):
        """Internal logging method"""
        if not self.is_enabled_for(level):
            return
            
        # Merge extra and kwargs
        if extra is None:
            extra = {}
        extra.update(kwargs)
        
        # Create log record
        record = LogRecord(
            level=level,
            message=message,
            logger_name=self.name,
            extra=extra,
            exc_info=exc_info
        )
        
        # Apply filters
        if not self._apply_filters(record):
            return
            
        # Send to handlers
        with self._lock:
            for handler in self.handlers:
                try:
                    handler.handle(record)
                except Exception as e:
                    # Don't let handler errors break logging
                    print(f"Error in handler {handler}: {e}")
                    
    def debug(self, message: str, **kwargs):
        """Log a debug message"""
        self._log(LogLevel.DEBUG, message, **kwargs)
        
    def info(self, message: str, **kwargs):
        """Log an info message"""
        self._log(LogLevel.INFO, message, **kwargs)
        
    def warning(self, message: str, **kwargs):
        """Log a warning message"""
        self._log(LogLevel.WARNING, message, **kwargs)
        
    def error(self, message: str, exc_info: bool = False, **kwargs):
        """Log an error message"""
        exc_info_tuple = None
        if exc_info:
            import sys
            exc_info_tuple = sys.exc_info()
        self._log(LogLevel.ERROR, message, exc_info=exc_info_tuple, **kwargs)
        
    def critical(self, message: str, exc_info: bool = False, **kwargs):
        """Log a critical message"""
        exc_info_tuple = None
        if exc_info:
            import sys
            exc_info_tuple = sys.exc_info()
        self._log(LogLevel.CRITICAL, message, exc_info=exc_info_tuple, **kwargs)
        
    def exception(self, message: str, **kwargs):
        """Log an exception with traceback"""
        import sys
        self._log(LogLevel.ERROR, message, exc_info=sys.exc_info(), **kwargs)
        
    def log(self, level: Union[LogLevel, str, int], message: str, **kwargs):
        """Log a message at the specified level"""
        if isinstance(level, str):
            level = LogLevel.from_string(level)
        elif isinstance(level, int):
            level = LogLevel(level)
        self._log(level, message, **kwargs)