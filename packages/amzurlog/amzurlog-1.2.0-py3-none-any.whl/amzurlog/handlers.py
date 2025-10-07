"""
AmzurLog Handlers
=================

This module contains various handlers for outputting log records to different destinations:
- FileHandler: Write logs to a file
- ConsoleHandler: Write logs to console/stdout
- RotatingFileHandler: Write logs to files with size-based rotation
- TimedRotatingFileHandler: Write logs to files with time-based rotation
"""

import os
import sys
import threading
import time
import re
from datetime import datetime, timedelta
from typing import TextIO, Optional
from pathlib import Path

from .core import LogRecord


class BaseHandler:
    """Base class for all handlers"""
    
    def __init__(self, level=None):
        self.level = level
        self.formatter = None
        self.filters = []
        self._lock = threading.RLock()
        
    def set_level(self, level):
        """Set the handler's level"""
        self.level = level
        
    def set_formatter(self, formatter):
        """Set the handler's formatter"""
        self.formatter = formatter
        
    def add_filter(self, filter_obj):
        """Add a filter to the handler"""
        with self._lock:
            if filter_obj not in self.filters:
                self.filters.append(filter_obj)
                
    def remove_filter(self, filter_obj):
        """Remove a filter from the handler"""
        with self._lock:
            if filter_obj in self.filters:
                self.filters.remove(filter_obj)
                
    def filter(self, record: LogRecord) -> bool:
        """Apply filters to the record"""
        # Check level
        if self.level and record.level < self.level:
            return False
            
        # Apply custom filters
        for filter_obj in self.filters:
            if not filter_obj.filter(record):
                return False
        return True
        
    def format(self, record: LogRecord) -> str:
        """Format the log record"""
        if self.formatter:
            return self.formatter.format(record)
        else:
            # Default formatting
            timestamp = record.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            return f"[{timestamp}] {record.level.name}: {record.message}"
            
    def handle(self, record: LogRecord):
        """Handle a log record"""
        if not self.filter(record):
            return
            
        try:
            formatted_message = self.format(record)
            self.emit(formatted_message, record)
        except Exception as e:
            self.handle_error(e, record)
            
    def emit(self, formatted_message: str, record: LogRecord):
        """Emit the formatted message - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement emit()")
        
    def handle_error(self, error: Exception, record: LogRecord):
        """Handle errors that occur during logging"""
        print(f"Logging error in {self.__class__.__name__}: {error}", file=sys.stderr)
        
    def close(self):
        """Close the handler - to be implemented by subclasses if needed"""
        pass


class ConsoleHandler(BaseHandler):
    """Handler that writes to console/stdout"""
    
    def __init__(self, stream: Optional[TextIO] = None, level=None):
        super().__init__(level)
        self.stream = stream or sys.stdout
        
    def emit(self, formatted_message: str, record: LogRecord):
        """Write the message to the console"""
        try:
            with self._lock:
                self.stream.write(formatted_message + '\n')
                self.stream.flush()
        except Exception as e:
            self.handle_error(e, record)


class FileHandler(BaseHandler):
    """Handler that writes to a file"""
    
    def __init__(self, filename: str, mode: str = 'a', encoding: str = 'utf-8', level=None):
        super().__init__(level)
        self.filename = filename
        self.mode = mode
        self.encoding = encoding
        self.stream = None
        
        # Create directory if it doesn't exist
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        
        # Open the file
        self._open()
        
    def _open(self):
        """Open the log file"""
        try:
            self.stream = open(self.filename, self.mode, encoding=self.encoding)
        except Exception as e:
            print(f"Failed to open log file {self.filename}: {e}", file=sys.stderr)
            
    def emit(self, formatted_message: str, record: LogRecord):
        """Write the message to the file"""
        if not self.stream:
            return
            
        try:
            with self._lock:
                self.stream.write(formatted_message + '\n')
                self.stream.flush()
        except Exception as e:
            self.handle_error(e, record)
            
    def close(self):
        """Close the file"""
        if self.stream:
            self.stream.close()
            self.stream = None


class RotatingFileHandler(BaseHandler):
    """Handler that writes to files with size-based rotation"""
    
    def __init__(
        self,
        filename: str,
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
        encoding: str = 'utf-8',
        level=None
    ):
        super().__init__(level)
        self.base_filename = filename
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        self.encoding = encoding
        self.stream = None
        
        # Create directory if it doesn't exist
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        
        # Open the file
        self._open()
        
    def _open(self):
        """Open the log file"""
        try:
            self.stream = open(self.base_filename, 'a', encoding=self.encoding)
        except Exception as e:
            print(f"Failed to open log file {self.base_filename}: {e}", file=sys.stderr)
            
    def should_rollover(self) -> bool:
        """Check if the file should be rotated"""
        if not self.stream:
            return False
            
        try:
            # Get current file size
            self.stream.flush()
            return os.path.getsize(self.base_filename) >= self.max_bytes
        except Exception:
            return False
            
    def do_rollover(self):
        """Perform file rotation"""
        if self.stream:
            self.stream.close()
            
        # Rotate existing backup files
        for i in range(self.backup_count - 1, 0, -1):
            src = f"{self.base_filename}.{i}"
            dst = f"{self.base_filename}.{i + 1}"
            
            if os.path.exists(src):
                if os.path.exists(dst):
                    os.remove(dst)
                os.rename(src, dst)
                
        # Move current file to .1
        dst = f"{self.base_filename}.1"
        if os.path.exists(dst):
            os.remove(dst)
        if os.path.exists(self.base_filename):
            os.rename(self.base_filename, dst)
            
        # Open new file
        self._open()
        
    def emit(self, formatted_message: str, record: LogRecord):
        """Write the message to the file with rotation"""
        if not self.stream:
            return
            
        try:
            with self._lock:
                # Check if we need to rotate
                if self.should_rollover():
                    self.do_rollover()
                    
                if self.stream:
                    self.stream.write(formatted_message + '\n')
                    self.stream.flush()
        except Exception as e:
            self.handle_error(e, record)
            
    def close(self):
        """Close the file"""
        if self.stream:
            self.stream.close()
            self.stream = None


class TimedRotatingFileHandler(BaseHandler):
    """Handler that writes to files with time-based rotation"""
    
    def __init__(
        self,
        filename: str,
        when: str = 'h',
        interval: int = 1,
        backup_count: int = 0,
        encoding: str = 'utf-8',
        delay: bool = False,
        utc: bool = False,
        at_time: Optional[datetime] = None,
        level=None
    ):
        """
        Initialize timed rotating file handler
        
        Args:
            filename: Base filename for log files
            when: Type of interval ('S', 'M', 'H', 'D', 'W0'-'W6', 'midnight')
            interval: Interval between rotations
            backup_count: Number of backup files to keep (0 = keep all)
            encoding: File encoding
            delay: If True, defer file opening until first log
            utc: Use UTC time instead of local time
            at_time: Time of day for daily rotation (only for 'midnight')
            level: Log level filter
        """
        super().__init__(level)
        self.base_filename = filename
        self.when = when.upper()
        self.backup_count = backup_count
        self.encoding = encoding
        self.delay = delay
        self.utc = utc
        self.at_time = at_time
        self.interval = interval
        self.stream = None
        
        # Create directory if it doesn't exist
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        
        # Set up rotation timing
        self._setup_rotation_timing()
        
        if not delay:
            self._open()
    
    def _setup_rotation_timing(self):
        """Set up the rotation timing calculations"""
        # Mapping of when values to time calculations
        if self.when == 'S':
            self.interval = 1  # seconds
            self.suffix = "%Y-%m-%d_%H-%M-%S"
            self.extMatch = r"^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}(\.\w+)?$"
        elif self.when == 'M':
            self.interval = 60  # minutes
            self.suffix = "%Y-%m-%d_%H-%M"
            self.extMatch = r"^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}(\.\w+)?$"
        elif self.when == 'H':
            self.interval = 60 * 60  # hours
            self.suffix = "%Y-%m-%d_%H"
            self.extMatch = r"^\d{4}-\d{2}-\d{2}_\d{2}(\.\w+)?$"
        elif self.when == 'D' or self.when == 'MIDNIGHT':
            self.interval = 60 * 60 * 24  # days
            self.suffix = "%Y-%m-%d"
            self.extMatch = r"^\d{4}-\d{2}-\d{2}(\.\w+)?$"
        elif self.when.startswith('W'):
            self.interval = 60 * 60 * 24 * 7  # weeks
            if len(self.when) != 2:
                raise ValueError("You must specify a day for weekly rollover from 0 to 6 (0 is Monday): %s" % self.when)
            if self.when[1] < '0' or self.when[1] > '6':
                raise ValueError("Invalid day specified for weekly rollover: %s" % self.when)
            self.dayOfWeek = int(self.when[1])
            self.suffix = "%Y-%m-%d"
            self.extMatch = r"^\d{4}-\d{2}-\d{2}(\.\w+)?$"
        else:
            raise ValueError("Invalid rollover interval specified: %s" % self.when)
        
        # Calculate the next rollover time
        current_time = int(time.time())
        self.rollover_at = self._compute_rollover(current_time)
    
    def _compute_rollover(self, current_time: int) -> int:
        """Compute when the next rollover should occur"""
        # Convert to datetime for easier calculation
        if self.utc:
            t = datetime.utcfromtimestamp(current_time)
        else:
            t = datetime.fromtimestamp(current_time)
        
        # Calculate next rollover based on when
        if self.when == 'MIDNIGHT' or self.when == 'D':
            # Roll over at midnight
            if self.at_time:
                # Use specific time of day
                next_time = t.replace(hour=self.at_time.hour, minute=self.at_time.minute, 
                                    second=self.at_time.second, microsecond=0)
                if next_time <= t:
                    next_time += timedelta(days=1)
            else:
                # Use midnight
                next_time = (t + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        elif self.when == 'H':
            # Roll over at the top of the next hour
            next_time = (t + timedelta(hours=self.interval)).replace(minute=0, second=0, microsecond=0)
        elif self.when == 'M':
            # Roll over at the next minute boundary
            next_time = (t + timedelta(minutes=self.interval)).replace(second=0, microsecond=0)
        elif self.when == 'S':
            # Roll over at the next second
            next_time = t + timedelta(seconds=self.interval)
        elif self.when.startswith('W'):
            # Roll over on a specific day of the week
            days_to_wait = self.dayOfWeek - t.weekday()
            if days_to_wait <= 0:  # Target day already passed this week
                days_to_wait += 7
            next_time = (t + timedelta(days=days_to_wait)).replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            # Fallback - should not reach here
            next_time = t + timedelta(seconds=self.interval)
        
        return int(next_time.timestamp())
    
    def _get_files_to_delete(self):
        """Get list of old log files that should be deleted"""
        if self.backup_count <= 0:
            return []
        
        dir_name, base_name = os.path.split(self.base_filename)
        file_names = os.listdir(dir_name)
        result = []
        
        # Look for files matching our pattern
        n, e = os.path.splitext(base_name)
        prefix = n + "."
        plen = len(prefix)
        
        for fileName in file_names:
            if fileName[:plen] == prefix:
                suffix = fileName[plen:]
                # Remove any file extension from suffix
                if suffix.endswith(e):
                    suffix = suffix[:-len(e)]
                if re.match(self.extMatch, suffix):
                    result.append(os.path.join(dir_name, fileName))
        
        if len(result) < self.backup_count:
            result = []
        else:
            result.sort()
            result = result[:len(result) - self.backup_count]
        
        return result
    
    def _open(self):
        """Open the log file"""
        try:
            self.stream = open(self.base_filename, 'a', encoding=self.encoding)
        except Exception as e:
            print(f"Failed to open log file {self.base_filename}: {e}", file=sys.stderr)
    
    def should_rollover(self, record: 'LogRecord') -> bool:
        """Check if the file should be rotated based on time"""
        current_time = int(time.time())
        return current_time >= self.rollover_at
    
    def do_rollover(self):
        """Perform the file rotation"""
        if self.stream:
            self.stream.close()
            self.stream = None
        
        # Get the current time for the filename
        current_time = int(time.time())
        if self.utc:
            time_tuple = time.gmtime(current_time)
        else:
            time_tuple = time.localtime(current_time)
        
        # Create the rotated filename
        dfn = self.rotation_filename(self.base_filename + "." + time.strftime(self.suffix, time_tuple))
        
        # Move current file to rotated name
        if os.path.exists(self.base_filename):
            os.rename(self.base_filename, dfn)
        
        # Delete old files if backup_count is set
        if self.backup_count > 0:
            for s in self._get_files_to_delete():
                try:
                    os.remove(s)
                except OSError:
                    pass
        
        # Calculate next rollover time
        self.rollover_at = self._compute_rollover(current_time)
        
        # Open new file
        if not self.delay:
            self._open()
    
    def rotation_filename(self, default_name: str) -> str:
        """
        Modify the filename to add rotation suffix.
        This method can be overridden to customize the rotation filename.
        """
        return default_name
    
    def emit(self, formatted_message: str, record: 'LogRecord'):
        """Write the message to the file with time-based rotation"""
        try:
            with self._lock:
                # Check if we need to rotate
                if self.should_rollover(record):
                    self.do_rollover()
                
                # Open file if delayed
                if self.stream is None:
                    self._open()
                
                if self.stream:
                    self.stream.write(formatted_message + '\n')
                    self.stream.flush()
        except Exception as e:
            self.handle_error(e, record)
    
    def close(self):
        """Close the file"""
        if self.stream:
            self.stream.close()
            self.stream = None


class MultiHandler(BaseHandler):
    """Handler that forwards records to multiple handlers"""
    
    def __init__(self, handlers=None, level=None):
        super().__init__(level)
        self.handlers = handlers or []
        
    def add_handler(self, handler):
        """Add a handler"""
        if handler not in self.handlers:
            self.handlers.append(handler)
            
    def remove_handler(self, handler):
        """Remove a handler"""
        if handler in self.handlers:
            self.handlers.remove(handler)
            
    def emit(self, formatted_message: str, record: LogRecord):
        """Forward the record to all handlers"""
        for handler in self.handlers:
            try:
                handler.handle(record)
            except Exception as e:
                self.handle_error(e, record)
                
    def close(self):
        """Close all handlers"""
        for handler in self.handlers:
            try:
                handler.close()
            except Exception:
                pass