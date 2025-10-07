"""
AmzurLog Exception Tracking and Integration
===========================================

This module provides comprehensive exception tracking capabilities with integration
for monitoring platforms like Sentry, Rollbar, and custom exception handlers.

Features:
- Automatic exception capture and enrichment
- Sentry integration with context
- Custom exception handlers
- Exception rate limiting and filtering
- Performance impact monitoring
- Exception correlation and grouping
"""

import sys
import inspect
import traceback
import threading
import time
import uuid
from functools import wraps
from typing import Dict, Any, Optional, List, Callable, Union, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
from enum import Enum

from .core import LogRecord, LogLevel, AmzurLogger


class ExceptionSeverity(Enum):
    """Exception severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ExceptionStatus(Enum):
    """Exception status tracking"""
    NEW = "new"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    IGNORED = "ignored"


@dataclass
class ExceptionFingerprint:
    """Unique identifier for exception types"""
    exception_type: str
    function_name: str
    file_path: str
    line_number: int
    
    def to_string(self) -> str:
        """Convert to string representation"""
        return f"{self.exception_type}:{self.function_name}:{self.file_path}:{self.line_number}"


@dataclass
class ExceptionContext:
    """Rich context information for exceptions"""
    # Basic exception info
    exception_type: str
    exception_message: str
    traceback_text: str
    fingerprint: str
    
    # Location info
    function_name: str
    file_path: str
    line_number: int
    module_name: str
    
    # Runtime context
    timestamp: datetime
    thread_id: int
    thread_name: str
    process_id: int
    
    # Application context
    user_id: Optional[str] = None
    request_id: Optional[str] = None
    session_id: Optional[str] = None
    environment: Optional[str] = None
    
    # Additional context
    local_variables: Optional[Dict[str, Any]] = None
    global_variables: Optional[Dict[str, Any]] = None
    breadcrumbs: Optional[List[Dict[str, Any]]] = None
    tags: Optional[Dict[str, str]] = None
    extra: Optional[Dict[str, Any]] = None
    
    # Severity and status
    severity: ExceptionSeverity = ExceptionSeverity.MEDIUM
    status: ExceptionStatus = ExceptionStatus.NEW
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        result['severity'] = self.severity.value
        result['status'] = self.status.value
        return result


class ExceptionRateLimiter:
    """Rate limiter for exception reporting"""
    
    def __init__(self, max_exceptions: int = 100, time_window: int = 3600):
        """
        Initialize rate limiter
        
        Args:
            max_exceptions: Maximum exceptions per time window
            time_window: Time window in seconds
        """
        self.max_exceptions = max_exceptions
        self.time_window = time_window
        self._exception_times = defaultdict(deque)
        self._lock = threading.Lock()
    
    def should_report(self, fingerprint: str) -> bool:
        """Check if exception should be reported"""
        current_time = time.time()
        
        with self._lock:
            # Clean old entries
            times = self._exception_times[fingerprint]
            while times and current_time - times[0] > self.time_window:
                times.popleft()
            
            # Check if under limit
            if len(times) < self.max_exceptions:
                times.append(current_time)
                return True
            
            return False
    
    def get_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get rate limiting statistics"""
        current_time = time.time()
        stats = {}
        
        with self._lock:
            for fingerprint, times in self._exception_times.items():
                # Clean old entries
                while times and current_time - times[0] > self.time_window:
                    times.popleft()
                
                stats[fingerprint] = {
                    'count': len(times),
                    'limit': self.max_exceptions,
                    'time_window': self.time_window,
                    'rate_limited': len(times) >= self.max_exceptions
                }
        
        return stats


class ExceptionCapture:
    """Captures and enriches exception information"""
    
    def __init__(self, capture_locals: bool = True, capture_globals: bool = False):
        self.capture_locals = capture_locals
        self.capture_globals = capture_globals
        self._breadcrumbs = deque(maxlen=50)
        self._context = {}
        self._lock = threading.Lock()
    
    def add_breadcrumb(self, message: str, category: str = "custom", level: str = "info", **data):
        """Add a breadcrumb for debugging context"""
        breadcrumb = {
            'message': message,
            'category': category,
            'level': level,
            'timestamp': datetime.utcnow().isoformat(),
            'data': data
        }
        
        with self._lock:
            self._breadcrumbs.append(breadcrumb)
    
    def set_context(self, key: str, value: Any):
        """Set context information"""
        with self._lock:
            self._context[key] = value
    
    def get_context(self) -> Dict[str, Any]:
        """Get current context"""
        with self._lock:
            return self._context.copy()
    
    def get_breadcrumbs(self) -> List[Dict[str, Any]]:
        """Get current breadcrumbs"""
        with self._lock:
            return list(self._breadcrumbs)
    
    def capture_exception(
        self,
        exc_type: type,
        exc_value: Exception,
        exc_traceback: Any,
        extra_context: Optional[Dict[str, Any]] = None
    ) -> ExceptionContext:
        """Capture detailed exception information"""
        import os
        
        # Get traceback information
        tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        traceback_text = ''.join(tb_lines)
        
        # Find the last frame that's not in this module
        frame = exc_traceback
        while frame.tb_next:
            frame = frame.tb_next
        
        frame_info = frame.tb_frame
        
        # Extract location information
        file_path = frame_info.f_code.co_filename
        function_name = frame_info.f_code.co_name
        line_number = frame.tb_lineno
        module_name = inspect.getmodule(frame_info).__name__ if inspect.getmodule(frame_info) else "unknown"
        
        # Create fingerprint
        fingerprint_obj = ExceptionFingerprint(
            exception_type=exc_type.__name__,
            function_name=function_name,
            file_path=os.path.basename(file_path),
            line_number=line_number
        )
        
        # Capture variables
        local_vars = {}
        global_vars = {}
        
        if self.capture_locals:
            try:
                local_vars = {k: self._safe_repr(v) for k, v in frame_info.f_locals.items()}
            except Exception:
                local_vars = {"error": "Failed to capture local variables"}
        
        if self.capture_globals:
            try:
                global_vars = {k: self._safe_repr(v) for k, v in frame_info.f_globals.items() 
                              if not k.startswith('__')}
            except Exception:
                global_vars = {"error": "Failed to capture global variables"}
        
        # Create exception context
        context = ExceptionContext(
            exception_type=exc_type.__name__,
            exception_message=str(exc_value),
            traceback_text=traceback_text,
            fingerprint=fingerprint_obj.to_string(),
            function_name=function_name,
            file_path=file_path,
            line_number=line_number,
            module_name=module_name,
            timestamp=datetime.utcnow(),
            thread_id=threading.get_ident(),
            thread_name=threading.current_thread().name,
            process_id=os.getpid(),
            local_variables=local_vars,
            global_variables=global_vars,
            breadcrumbs=self.get_breadcrumbs(),
            extra=extra_context or {}
        )
        
        # Add current context
        current_context = self.get_context()
        if 'user_id' in current_context:
            context.user_id = current_context['user_id']
        if 'request_id' in current_context:
            context.request_id = current_context['request_id']
        if 'session_id' in current_context:
            context.session_id = current_context['session_id']
        if 'environment' in current_context:
            context.environment = current_context['environment']
        if 'tags' in current_context:
            context.tags = current_context['tags']
        
        return context
    
    def _safe_repr(self, obj: Any, max_length: int = 200) -> str:
        """Safely convert object to string representation"""
        try:
            result = repr(obj)
            if len(result) > max_length:
                result = result[:max_length] + "..."
            return result
        except Exception:
            return f"<{type(obj).__name__} object at {hex(id(obj))}>"


class SentryIntegration:
    """Integration with Sentry error tracking"""
    
    def __init__(self, dsn: str, environment: str = "production", **sentry_config):
        """
        Initialize Sentry integration
        
        Args:
            dsn: Sentry DSN
            environment: Environment name
            **sentry_config: Additional Sentry configuration
        """
        self.dsn = dsn
        self.environment = environment
        self.sentry_config = sentry_config
        self._sentry = None
        self._initialized = False
        
        self._initialize_sentry()
    
    def _initialize_sentry(self):
        """Initialize Sentry SDK"""
        try:
            import sentry_sdk
            from sentry_sdk.integrations.logging import LoggingIntegration
            
            # Configure Sentry
            config = {
                'dsn': self.dsn,
                'environment': self.environment,
                'traces_sample_rate': self.sentry_config.get('traces_sample_rate', 0.1),
                'profiles_sample_rate': self.sentry_config.get('profiles_sample_rate', 0.1),
                'attach_stacktrace': True,
                'send_default_pii': self.sentry_config.get('send_default_pii', False),
                'max_breadcrumbs': self.sentry_config.get('max_breadcrumbs', 50),
                'debug': self.sentry_config.get('debug', False)
            }
            
            # Add logging integration
            logging_integration = LoggingIntegration(
                level=self.sentry_config.get('logging_level', 'INFO'),
                event_level=self.sentry_config.get('event_level', 'ERROR')
            )
            config['integrations'] = [logging_integration]
            
            # Add custom integrations
            if 'integrations' in self.sentry_config:
                config['integrations'].extend(self.sentry_config['integrations'])
            
            sentry_sdk.init(**config)
            self._sentry = sentry_sdk
            self._initialized = True
            
        except ImportError:
            print("Sentry SDK not installed. Install with: pip install sentry-sdk")
            self._initialized = False
        except Exception as e:
            print(f"Failed to initialize Sentry: {e}")
            self._initialized = False
    
    def is_available(self) -> bool:
        """Check if Sentry is available"""
        return self._initialized and self._sentry is not None
    
    def capture_exception(self, exception_context: ExceptionContext) -> Optional[str]:
        """Send exception to Sentry"""
        if not self.is_available():
            return None
        
        try:
            with self._sentry.configure_scope() as scope:
                # Set user context
                if exception_context.user_id:
                    scope.set_user({"id": exception_context.user_id})
                
                # Set tags
                if exception_context.tags:
                    for key, value in exception_context.tags.items():
                        scope.set_tag(key, value)
                
                # Set extra context
                scope.set_extra("fingerprint", exception_context.fingerprint)
                scope.set_extra("function_name", exception_context.function_name)
                scope.set_extra("module_name", exception_context.module_name)
                scope.set_extra("thread_id", exception_context.thread_id)
                scope.set_extra("thread_name", exception_context.thread_name)
                scope.set_extra("process_id", exception_context.process_id)
                
                if exception_context.request_id:
                    scope.set_extra("request_id", exception_context.request_id)
                if exception_context.session_id:
                    scope.set_extra("session_id", exception_context.session_id)
                
                # Add local variables if available
                if exception_context.local_variables:
                    scope.set_extra("local_variables", exception_context.local_variables)
                
                # Add breadcrumbs
                if exception_context.breadcrumbs:
                    for breadcrumb in exception_context.breadcrumbs:
                        self._sentry.add_breadcrumb(breadcrumb)
                
                # Set fingerprint for grouping
                scope.fingerprint = [exception_context.fingerprint]
                
                # Set level based on severity
                if exception_context.severity == ExceptionSeverity.CRITICAL:
                    scope.level = "fatal"
                elif exception_context.severity == ExceptionSeverity.HIGH:
                    scope.level = "error"
                elif exception_context.severity == ExceptionSeverity.MEDIUM:
                    scope.level = "warning"
                else:
                    scope.level = "info"
                
                # Capture the exception
                event_id = self._sentry.capture_message(
                    f"{exception_context.exception_type}: {exception_context.exception_message}",
                    level=scope.level
                )
                
                return event_id
                
        except Exception as e:
            print(f"Failed to send exception to Sentry: {e}")
            return None
    
    def capture_message(self, message: str, level: str = "info", **kwargs) -> Optional[str]:
        """Send custom message to Sentry"""
        if not self.is_available():
            return None
        
        try:
            with self._sentry.configure_scope() as scope:
                for key, value in kwargs.items():
                    scope.set_extra(key, value)
                
                return self._sentry.capture_message(message, level=level)
        except Exception as e:
            print(f"Failed to send message to Sentry: {e}")
            return None


class ExceptionTracker:
    """Main exception tracking and management system"""
    
    def __init__(
        self,
        logger: AmzurLogger,
        rate_limiter: Optional[ExceptionRateLimiter] = None,
        capture_locals: bool = True,
        capture_globals: bool = False
    ):
        """
        Initialize exception tracker
        
        Args:
            logger: AmzurLog logger instance
            rate_limiter: Rate limiter for exception reporting
            capture_locals: Whether to capture local variables
            capture_globals: Whether to capture global variables
        """
        self.logger = logger
        self.rate_limiter = rate_limiter or ExceptionRateLimiter()
        self.capture = ExceptionCapture(capture_locals, capture_globals)
        self.integrations = {}
        self.exception_handlers = []
        self._stats = {
            'total_exceptions': 0,
            'reported_exceptions': 0,
            'rate_limited_exceptions': 0,
            'last_exception_time': None
        }
        self._lock = threading.Lock()
    
    def add_integration(self, name: str, integration):
        """Add an exception tracking integration"""
        self.integrations[name] = integration
    
    def add_sentry_integration(self, dsn: str, **config):
        """Add Sentry integration"""
        sentry_integration = SentryIntegration(dsn, **config)
        self.add_integration('sentry', sentry_integration)
        return sentry_integration
    
    def add_exception_handler(self, handler: Callable[[ExceptionContext], None]):
        """Add custom exception handler"""
        self.exception_handlers.append(handler)
    
    def set_user_context(self, user_id: str, **kwargs):
        """Set user context for exception tracking"""
        self.capture.set_context('user_id', user_id)
        for key, value in kwargs.items():
            self.capture.set_context(key, value)
    
    def set_request_context(self, request_id: str, **kwargs):
        """Set request context for exception tracking"""
        self.capture.set_context('request_id', request_id)
        for key, value in kwargs.items():
            self.capture.set_context(key, value)
    
    def add_breadcrumb(self, message: str, category: str = "custom", **data):
        """Add breadcrumb for debugging context"""
        self.capture.add_breadcrumb(message, category, **data)
    
    def handle_exception(
        self,
        exc_type: type = None,
        exc_value: Exception = None,
        exc_traceback: Any = None,
        severity: ExceptionSeverity = ExceptionSeverity.MEDIUM,
        extra_context: Optional[Dict[str, Any]] = None
    ) -> Optional[ExceptionContext]:
        """Handle an exception with full tracking"""
        # Get current exception if not provided
        if exc_type is None:
            exc_type, exc_value, exc_traceback = sys.exc_info()
        
        if exc_type is None:
            return None
        
        with self._lock:
            self._stats['total_exceptions'] += 1
            self._stats['last_exception_time'] = datetime.utcnow()
        
        # Capture exception details
        exception_context = self.capture.capture_exception(
            exc_type, exc_value, exc_traceback, extra_context
        )
        exception_context.severity = severity
        
        # Check rate limiting
        if not self.rate_limiter.should_report(exception_context.fingerprint):
            with self._lock:
                self._stats['rate_limited_exceptions'] += 1
            return exception_context
        
        with self._lock:
            self._stats['reported_exceptions'] += 1
        
        # Log the exception
        self._log_exception(exception_context)
        
        # Send to integrations
        self._send_to_integrations(exception_context)
        
        # Call custom handlers
        for handler in self.exception_handlers:
            try:
                handler(exception_context)
            except Exception as e:
                self.logger.error(f"Exception handler failed: {e}")
        
        return exception_context
    
    def _log_exception(self, context: ExceptionContext):
        """Log exception using AmzurLog"""
        log_data = {
            'exception_type': context.exception_type,
            'exception_message': context.exception_message,
            'fingerprint': context.fingerprint,
            'function_name': context.function_name,
            'file_path': context.file_path,
            'line_number': context.line_number,
            'module_name': context.module_name,
            'severity': context.severity.value,
            'thread_id': context.thread_id,
            'thread_name': context.thread_name
        }
        
        if context.user_id:
            log_data['user_id'] = context.user_id
        if context.request_id:
            log_data['request_id'] = context.request_id
        if context.session_id:
            log_data['session_id'] = context.session_id
        if context.tags:
            log_data['tags'] = context.tags
        if context.extra:
            log_data.update(context.extra)
        
        # Log at appropriate level
        if context.severity == ExceptionSeverity.CRITICAL:
            level = LogLevel.CRITICAL
        elif context.severity == ExceptionSeverity.HIGH:
            level = LogLevel.ERROR
        elif context.severity == ExceptionSeverity.MEDIUM:
            level = LogLevel.WARNING
        else:
            level = LogLevel.INFO
        
        self.logger.log(
            level,
            f"Exception captured: {context.exception_type}: {context.exception_message}",
            **log_data
        )
    
    def _send_to_integrations(self, context: ExceptionContext):
        """Send exception to all configured integrations"""
        for name, integration in self.integrations.items():
            try:
                if hasattr(integration, 'capture_exception'):
                    integration.capture_exception(context)
            except Exception as e:
                self.logger.error(f"Failed to send exception to {name}: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get exception tracking statistics"""
        with self._lock:
            stats = self._stats.copy()
        
        # Add rate limiter stats
        stats['rate_limiter'] = self.rate_limiter.get_stats()
        
        # Add integration status
        stats['integrations'] = {}
        for name, integration in self.integrations.items():
            if hasattr(integration, 'is_available'):
                stats['integrations'][name] = {
                    'available': integration.is_available(),
                    'type': type(integration).__name__
                }
            else:
                stats['integrations'][name] = {
                    'available': True,
                    'type': type(integration).__name__
                }
        
        return stats


def track_exceptions(
    tracker: ExceptionTracker,
    severity: ExceptionSeverity = ExceptionSeverity.MEDIUM,
    reraise: bool = True
):
    """Decorator to automatically track exceptions"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Add function context
                tracker.add_breadcrumb(
                    f"Entering function {func.__name__}",
                    category="function_call",
                    data={'args': len(args), 'kwargs': list(kwargs.keys())}
                )
                
                # Track the exception
                tracker.handle_exception(severity=severity)
                
                if reraise:
                    raise
        return wrapper
    return decorator


# Global exception tracker instance
_global_tracker: Optional[ExceptionTracker] = None


def get_global_tracker() -> Optional[ExceptionTracker]:
    """Get the global exception tracker"""
    return _global_tracker


def set_global_tracker(tracker: ExceptionTracker):
    """Set the global exception tracker"""
    global _global_tracker
    _global_tracker = tracker


def install_global_exception_handler():
    """Install global exception handler for unhandled exceptions"""
    def handle_exception(exc_type, exc_value, exc_traceback):
        if _global_tracker:
            _global_tracker.handle_exception(
                exc_type, exc_value, exc_traceback,
                severity=ExceptionSeverity.CRITICAL
            )
        
        # Call the original handler
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
    
    sys.excepthook = handle_exception