"""
AmzurLog Filters
================

This module contains various filters for controlling which log records are processed:
- LevelFilter: Filter based on log level
- PatternFilter: Filter based on message patterns
- RateLimitFilter: Rate limiting for log messages
"""

import re
import time
import threading
from typing import Pattern, Union
from collections import defaultdict

from .core import LogRecord, LogLevel


class BaseFilter:
    """Base class for all filters"""
    
    def filter(self, record: LogRecord) -> bool:
        """Filter a log record - return True to allow, False to block"""
        raise NotImplementedError("Subclasses must implement filter()")


class LevelFilter(BaseFilter):
    """Filter based on log level"""
    
    def __init__(self, min_level: Union[LogLevel, str, int] = None, max_level: Union[LogLevel, str, int] = None):
        self.min_level = self._convert_level(min_level) if min_level else None
        self.max_level = self._convert_level(max_level) if max_level else None
        
    def _convert_level(self, level: Union[LogLevel, str, int]) -> LogLevel:
        """Convert level to LogLevel enum"""
        if isinstance(level, str):
            return LogLevel.from_string(level)
        elif isinstance(level, int):
            return LogLevel(level)
        return level
        
    def filter(self, record: LogRecord) -> bool:
        """Filter based on level range"""
        if self.min_level and record.level < self.min_level:
            return False
        if self.max_level and record.level > self.max_level:
            return False
        return True


class PatternFilter(BaseFilter):
    """Filter based on message patterns"""
    
    def __init__(self, pattern: Union[str, Pattern], include: bool = True, flags: int = 0):
        if isinstance(pattern, str):
            self.pattern = re.compile(pattern, flags)
        else:
            self.pattern = pattern
        self.include = include  # True to include matches, False to exclude
        
    def filter(self, record: LogRecord) -> bool:
        """Filter based on pattern matching"""
        matches = bool(self.pattern.search(record.message))
        return matches if self.include else not matches


class LoggerFilter(BaseFilter):
    """Filter based on logger name"""
    
    def __init__(self, logger_names: Union[str, list], include: bool = True):
        if isinstance(logger_names, str):
            self.logger_names = {logger_names}
        else:
            self.logger_names = set(logger_names)
        self.include = include
        
    def filter(self, record: LogRecord) -> bool:
        """Filter based on logger name"""
        matches = record.logger_name in self.logger_names
        return matches if self.include else not matches


class ThreadFilter(BaseFilter):
    """Filter based on thread ID or name"""
    
    def __init__(self, thread_ids: Union[int, list] = None, thread_names: Union[str, list] = None, include: bool = True):
        self.thread_ids = set()
        self.thread_names = set()
        self.include = include
        
        if thread_ids:
            if isinstance(thread_ids, int):
                self.thread_ids.add(thread_ids)
            else:
                self.thread_ids.update(thread_ids)
                
        if thread_names:
            if isinstance(thread_names, str):
                self.thread_names.add(thread_names)
            else:
                self.thread_names.update(thread_names)
                
    def filter(self, record: LogRecord) -> bool:
        """Filter based on thread ID or name"""
        matches = False
        
        if self.thread_ids and record.thread_id in self.thread_ids:
            matches = True
        if self.thread_names and record.thread_name in self.thread_names:
            matches = True
            
        # If no criteria specified, allow all
        if not self.thread_ids and not self.thread_names:
            matches = True
            
        return matches if self.include else not matches


class RateLimitFilter(BaseFilter):
    """Rate limiting filter to prevent log spam"""
    
    def __init__(self, max_rate: int = 10, time_window: int = 60, per_logger: bool = True):
        self.max_rate = max_rate  # Maximum messages per time window
        self.time_window = time_window  # Time window in seconds
        self.per_logger = per_logger  # Apply rate limit per logger or globally
        self.message_counts = defaultdict(list)
        self._lock = threading.RLock()
        
    def _get_key(self, record: LogRecord) -> str:
        """Get the key for rate limiting"""
        if self.per_logger:
            return f"{record.logger_name}:{record.level.name}"
        else:
            return "global"
            
    def _cleanup_old_entries(self, timestamps: list, current_time: float):
        """Remove timestamps outside the time window"""
        cutoff_time = current_time - self.time_window
        while timestamps and timestamps[0] < cutoff_time:
            timestamps.pop(0)
            
    def filter(self, record: LogRecord) -> bool:
        """Filter based on rate limiting"""
        current_time = time.time()
        key = self._get_key(record)
        
        with self._lock:
            timestamps = self.message_counts[key]
            
            # Clean up old entries
            self._cleanup_old_entries(timestamps, current_time)
            
            # Check if we're over the limit
            if len(timestamps) >= self.max_rate:
                return False
                
            # Add current timestamp
            timestamps.append(current_time)
            return True


class DuplicateFilter(BaseFilter):
    """Filter to prevent duplicate messages"""
    
    def __init__(self, time_window: int = 60, max_duplicates: int = 1):
        self.time_window = time_window
        self.max_duplicates = max_duplicates
        self.message_history = {}
        self._lock = threading.RLock()
        
    def _get_message_key(self, record: LogRecord) -> str:
        """Get a key to identify duplicate messages"""
        return f"{record.logger_name}:{record.level.name}:{record.message}"
        
    def _cleanup_old_entries(self, current_time: float):
        """Remove old entries outside the time window"""
        cutoff_time = current_time - self.time_window
        keys_to_remove = []
        
        for key, timestamps in self.message_history.items():
            # Remove old timestamps
            while timestamps and timestamps[0] < cutoff_time:
                timestamps.pop(0)
            # Remove empty entries
            if not timestamps:
                keys_to_remove.append(key)
                
        for key in keys_to_remove:
            del self.message_history[key]
            
    def filter(self, record: LogRecord) -> bool:
        """Filter duplicate messages"""
        current_time = time.time()
        message_key = self._get_message_key(record)
        
        with self._lock:
            # Clean up old entries
            self._cleanup_old_entries(current_time)
            
            # Check duplicates
            if message_key not in self.message_history:
                self.message_history[message_key] = []
                
            timestamps = self.message_history[message_key]
            
            if len(timestamps) >= self.max_duplicates:
                return False
                
            timestamps.append(current_time)
            return True


class FieldFilter(BaseFilter):
    """Filter based on custom fields in the log record"""
    
    def __init__(self, field_name: str, values: Union[str, list], include: bool = True):
        self.field_name = field_name
        if isinstance(values, str):
            self.values = {values}
        else:
            self.values = set(values)
        self.include = include
        
    def filter(self, record: LogRecord) -> bool:
        """Filter based on field values"""
        field_value = record.extra.get(self.field_name)
        
        if field_value is None:
            return not self.include  # If field not present, exclude if include=True
            
        matches = str(field_value) in self.values
        return matches if self.include else not matches


class CompositeFilter(BaseFilter):
    """Combine multiple filters with AND/OR logic"""
    
    def __init__(self, filters: list, operator: str = 'AND'):
        self.filters = filters
        self.operator = operator.upper()
        
        if self.operator not in ('AND', 'OR'):
            raise ValueError("Operator must be 'AND' or 'OR'")
            
    def filter(self, record: LogRecord) -> bool:
        """Apply composite filtering"""
        if not self.filters:
            return True
            
        if self.operator == 'AND':
            return all(f.filter(record) for f in self.filters)
        else:  # OR
            return any(f.filter(record) for f in self.filters)