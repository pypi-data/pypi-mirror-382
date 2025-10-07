"""
AmzurLog Exception Handler
==========================

Handler for exception tracking and reporting with external service integration.
"""

import sys
import threading
from typing import Optional, Dict, Any, List
from .handlers import BaseHandler
from .core import LogRecord
from .exception_tracking import ExceptionTracker, ExceptionSeverity, ExceptionCapture


class ExceptionHandler(BaseHandler):
    """Handler that captures and reports exceptions to external services"""
    
    def __init__(
        self,
        exception_tracker: Optional[ExceptionTracker] = None,
        level=None,
        auto_capture: bool = True,
        capture_locals: bool = True,
        capture_globals: bool = False
    ):
        """
        Initialize exception handler
        
        Args:
            exception_tracker: Exception tracker instance
            level: Log level filter
            auto_capture: Whether to automatically capture exceptions
            capture_locals: Whether to capture local variables
            capture_globals: Whether to capture global variables
        """
        super().__init__(level)
        self.exception_tracker = exception_tracker
        self.auto_capture = auto_capture
        self.capture_locals = capture_locals
        self.capture_globals = capture_globals
        
        if not self.exception_tracker:
            # Create a basic logger for the tracker
            from .core import AmzurLogger
            logger = AmzurLogger("exception_handler")
            self.exception_tracker = ExceptionTracker(
                logger=logger,
                capture_locals=capture_locals,
                capture_globals=capture_globals
            )
        
        # Install global exception handler if auto_capture is enabled
        if auto_capture:
            self._install_exception_hook()
    
    def _install_exception_hook(self):
        """Install global exception handler"""
        original_excepthook = sys.excepthook
        
        def exception_hook(exc_type, exc_value, exc_traceback):
            try:
                # Track the exception
                self.exception_tracker.handle_exception(
                    exc_type, exc_value, exc_traceback,
                    severity=ExceptionSeverity.CRITICAL
                )
            except Exception as e:
                print(f"Error in exception handler: {e}")
            
            # Call original handler
            original_excepthook(exc_type, exc_value, exc_traceback)
        
        sys.excepthook = exception_hook
    
    def emit(self, formatted_message: str, record: LogRecord):
        """Handle log record and capture exceptions if present"""
        try:
            # Check if this is an exception log
            if record.exc_info or record.exception_text:
                self._handle_exception_record(record)
            
            # Also capture any current exception context
            exc_type, exc_value, exc_traceback = sys.exc_info()
            if exc_type is not None:
                # Determine severity based on log level
                if record.level.value >= 50:  # CRITICAL
                    severity = ExceptionSeverity.CRITICAL
                elif record.level.value >= 40:  # ERROR
                    severity = ExceptionSeverity.HIGH
                elif record.level.value >= 30:  # WARNING
                    severity = ExceptionSeverity.MEDIUM
                else:
                    severity = ExceptionSeverity.LOW
                
                # Add context from log record
                extra_context = {
                    'log_message': record.message,
                    'logger_name': record.logger_name,
                    'log_level': record.level.name
                }
                extra_context.update(record.extra)
                
                self.exception_tracker.handle_exception(
                    exc_type, exc_value, exc_traceback,
                    severity=severity,
                    extra_context=extra_context
                )
                
        except Exception as e:
            self.handle_error(e, record)
    
    def _handle_exception_record(self, record: LogRecord):
        """Handle a log record that contains exception information"""
        if record.exc_info:
            exc_type, exc_value, exc_traceback = record.exc_info
            
            # Determine severity
            if record.level.value >= 50:
                severity = ExceptionSeverity.CRITICAL
            elif record.level.value >= 40:
                severity = ExceptionSeverity.HIGH
            else:
                severity = ExceptionSeverity.MEDIUM
            
            # Add log context
            extra_context = {
                'log_message': record.message,
                'logger_name': record.logger_name,
                'log_level': record.level.name
            }
            extra_context.update(record.extra)
            
            self.exception_tracker.handle_exception(
                exc_type, exc_value, exc_traceback,
                severity=severity,
                extra_context=extra_context
            )
    
    def add_sentry_integration(self, dsn: str, **config):
        """Add Sentry integration"""
        return self.exception_tracker.add_sentry_integration(dsn, **config)
    
    def add_integration(self, name: str, integration):
        """Add custom integration"""
        self.exception_tracker.add_integration(name, integration)
    
    def set_user_context(self, user_id: str, **kwargs):
        """Set user context"""
        self.exception_tracker.set_user_context(user_id, **kwargs)
    
    def set_request_context(self, request_id: str, **kwargs):
        """Set request context"""
        self.exception_tracker.set_request_context(request_id, **kwargs)
    
    def add_breadcrumb(self, message: str, category: str = "custom", **data):
        """Add breadcrumb"""
        self.exception_tracker.add_breadcrumb(message, category, **data)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get exception tracking statistics"""
        return self.exception_tracker.get_stats()
    
    def close(self):
        """Close the exception handler"""
        # No specific cleanup needed
        pass


class SentryHandler(ExceptionHandler):
    """Specialized handler for Sentry integration"""
    
    def __init__(
        self,
        sentry_dsn: str,
        environment: str = "production",
        level=None,
        **sentry_config
    ):
        """
        Initialize Sentry handler
        
        Args:
            sentry_dsn: Sentry DSN
            environment: Environment name
            level: Log level filter
            **sentry_config: Additional Sentry configuration
        """
        super().__init__(level=level)
        
        # Add Sentry integration
        self.sentry_integration = self.add_sentry_integration(
            sentry_dsn,
            environment=environment,
            **sentry_config
        )
    
    def is_available(self) -> bool:
        """Check if Sentry is available"""
        return self.sentry_integration.is_available()


class RollbarHandler(ExceptionHandler):
    """Handler for Rollbar integration"""
    
    def __init__(
        self,
        rollbar_token: str,
        environment: str = "production",
        level=None,
        **rollbar_config
    ):
        """
        Initialize Rollbar handler
        
        Args:
            rollbar_token: Rollbar access token
            environment: Environment name
            level: Log level filter
            **rollbar_config: Additional Rollbar configuration
        """
        super().__init__(level=level)
        
        # Create and add Rollbar integration
        rollbar_integration = RollbarIntegration(
            rollbar_token,
            environment=environment,
            **rollbar_config
        )
        self.add_integration('rollbar', rollbar_integration)
        self.rollbar_integration = rollbar_integration
    
    def is_available(self) -> bool:
        """Check if Rollbar is available"""
        return self.rollbar_integration.is_available()


class RollbarIntegration:
    """Integration with Rollbar error tracking"""
    
    def __init__(self, access_token: str, environment: str = "production", **config):
        """
        Initialize Rollbar integration
        
        Args:
            access_token: Rollbar access token
            environment: Environment name
            **config: Additional Rollbar configuration
        """
        self.access_token = access_token
        self.environment = environment
        self.config = config
        self._rollbar = None
        self._initialized = False
        
        self._initialize_rollbar()
    
    def _initialize_rollbar(self):
        """Initialize Rollbar SDK"""
        try:
            import rollbar
            
            rollbar.init(
                self.access_token,
                environment=self.environment,
                **self.config
            )
            
            self._rollbar = rollbar
            self._initialized = True
            
        except ImportError:
            print("Rollbar SDK not installed. Install with: pip install rollbar")
            self._initialized = False
        except Exception as e:
            print(f"Failed to initialize Rollbar: {e}")
            self._initialized = False
    
    def is_available(self) -> bool:
        """Check if Rollbar is available"""
        return self._initialized and self._rollbar is not None
    
    def capture_exception(self, exception_context) -> Optional[str]:
        """Send exception to Rollbar"""
        if not self.is_available():
            return None
        
        try:
            # Set extra data
            extra_data = {
                'fingerprint': exception_context.fingerprint,
                'function_name': exception_context.function_name,
                'module_name': exception_context.module_name,
                'thread_id': exception_context.thread_id,
                'thread_name': exception_context.thread_name,
                'process_id': exception_context.process_id
            }
            
            if exception_context.user_id:
                extra_data['user_id'] = exception_context.user_id
            if exception_context.request_id:
                extra_data['request_id'] = exception_context.request_id
            if exception_context.session_id:
                extra_data['session_id'] = exception_context.session_id
            if exception_context.local_variables:
                extra_data['local_variables'] = exception_context.local_variables
            
            # Report to Rollbar
            result = self._rollbar.report_message(
                f"{exception_context.exception_type}: {exception_context.exception_message}",
                level=self._get_rollbar_level(exception_context.severity),
                extra_data=extra_data
            )
            
            return str(result) if result else None
            
        except Exception as e:
            print(f"Failed to send exception to Rollbar: {e}")
            return None
    
    def _get_rollbar_level(self, severity):
        """Convert severity to Rollbar level"""
        from .exception_tracking import ExceptionSeverity
        
        if severity == ExceptionSeverity.CRITICAL:
            return 'critical'
        elif severity == ExceptionSeverity.HIGH:
            return 'error'
        elif severity == ExceptionSeverity.MEDIUM:
            return 'warning'
        else:
            return 'info'


class CustomExceptionIntegration:
    """Base class for custom exception integrations"""
    
    def __init__(self, name: str):
        self.name = name
    
    def is_available(self) -> bool:
        """Check if integration is available"""
        return True
    
    def capture_exception(self, exception_context) -> Optional[str]:
        """Capture exception - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement capture_exception")


class WebhookExceptionIntegration(CustomExceptionIntegration):
    """Integration that sends exceptions to a webhook"""
    
    def __init__(self, webhook_url: str, headers: Optional[Dict[str, str]] = None):
        super().__init__("webhook")
        self.webhook_url = webhook_url
        self.headers = headers or {}
    
    def capture_exception(self, exception_context) -> Optional[str]:
        """Send exception to webhook"""
        try:
            import requests
            
            payload = {
                'exception_type': exception_context.exception_type,
                'exception_message': exception_context.exception_message,
                'fingerprint': exception_context.fingerprint,
                'timestamp': exception_context.timestamp.isoformat(),
                'function_name': exception_context.function_name,
                'file_path': exception_context.file_path,
                'line_number': exception_context.line_number,
                'severity': exception_context.severity.value
            }
            
            if exception_context.user_id:
                payload['user_id'] = exception_context.user_id
            if exception_context.request_id:
                payload['request_id'] = exception_context.request_id
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            
            return response.text
            
        except Exception as e:
            print(f"Failed to send exception to webhook: {e}")
            return None
