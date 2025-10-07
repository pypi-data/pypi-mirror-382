"""
AmzurLog Context Management
===========================

This module provides context management for logging, allowing you to:
- Add contextual information to all logs within a scope
- Manage structured logging contexts
- Handle request/response contexts
"""

import threading
from typing import Dict, Any, Optional
from contextlib import contextmanager
from contextvars import ContextVar

from .core import AmzurLogger


# Context variables for async support
_log_context: ContextVar[Dict[str, Any]] = ContextVar('log_context', default={})


class LogContext:
    """Context manager for adding structured context to logs"""
    
    def __init__(self, logger: AmzurLogger, **context_data):
        self.logger = logger
        self.context_data = context_data
        self.original_log_method = None
        
    def __enter__(self):
        """Enter the context"""
        # Store original _log method
        self.original_log_method = self.logger._log
        
        # Create new _log method that adds context
        def _log_with_context(level, message, extra=None, exc_info=None, **kwargs):
            if extra is None:
                extra = {}
            
            # Merge context data
            merged_extra = self.context_data.copy()
            merged_extra.update(extra)
            merged_extra.update(kwargs)
            
            return self.original_log_method(level, message, extra=merged_extra, exc_info=exc_info)
        
        # Replace the logger's _log method
        self.logger._log = _log_with_context
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context"""
        # Restore original _log method
        if self.original_log_method:
            self.logger._log = self.original_log_method


class ThreadLocalContext:
    """Thread-local context storage for logging"""
    
    def __init__(self):
        self._local = threading.local()
        
    def set_context(self, **context_data):
        """Set context data for the current thread"""
        if not hasattr(self._local, 'context'):
            self._local.context = {}
        self._local.context.update(context_data)
        
    def get_context(self) -> Dict[str, Any]:
        """Get context data for the current thread"""
        if not hasattr(self._local, 'context'):
            self._local.context = {}
        return self._local.context.copy()
        
    def clear_context(self):
        """Clear context data for the current thread"""
        if hasattr(self._local, 'context'):
            self._local.context.clear()
            
    def remove_key(self, key: str):
        """Remove a specific key from context"""
        if hasattr(self._local, 'context') and key in self._local.context:
            del self._local.context[key]


# Global thread-local context instance
thread_context = ThreadLocalContext()


class ContextAwareLogger(AmzurLogger):
    """Logger that automatically includes thread-local context"""
    
    def __init__(self, name: str, use_thread_context: bool = True, use_context_vars: bool = True):
        super().__init__(name)
        self.use_thread_context = use_thread_context
        self.use_context_vars = use_context_vars
        
    def _log(self, level, message, extra=None, exc_info=None, **kwargs):
        """Override _log to include context data"""
        if extra is None:
            extra = {}
            
        # Add thread-local context
        if self.use_thread_context:
            thread_ctx = thread_context.get_context()
            for key, value in thread_ctx.items():
                if key not in extra:
                    extra[key] = value
                    
        # Add context variables (for async support)
        if self.use_context_vars:
            try:
                ctx_vars = _log_context.get()
                for key, value in ctx_vars.items():
                    if key not in extra:
                        extra[key] = value
            except LookupError:
                pass
                
        # Merge kwargs
        extra.update(kwargs)
        
        return super()._log(level, message, extra=extra, exc_info=exc_info)


@contextmanager
def log_context(**context_data):
    """Context manager for adding temporary context data"""
    # Store current context
    old_context = {}
    if thread_context.get_context():
        old_context = thread_context.get_context()
        
    try:
        # Set new context
        thread_context.set_context(**context_data)
        yield
    finally:
        # Restore old context
        thread_context.clear_context()
        if old_context:
            thread_context.set_context(**old_context)


class AsyncLogContext:
    """Async context manager for logging context using context variables"""
    
    def __init__(self, **context_data):
        self.context_data = context_data
        self.token = None
        
    async def __aenter__(self):
        # Get current context
        current_context = _log_context.get({})
        
        # Merge with new context
        new_context = current_context.copy()
        new_context.update(self.context_data)
        
        # Set new context
        self.token = _log_context.set(new_context)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Reset context
        if self.token:
            _log_context.reset(self.token)


def async_log_context(**context_data):
    """Factory function for async logging context"""
    return AsyncLogContext(**context_data)


class RequestContext:
    """Specialized context for HTTP request logging"""
    
    def __init__(
        self,
        request_id: str,
        method: str = None,
        path: str = None,
        user_id: str = None,
        ip_address: str = None,
        user_agent: str = None,
        **extra_context
    ):
        self.context_data = {
            'request_id': request_id,
            'request_method': method,
            'request_path': path,
            'user_id': user_id,
            'client_ip': ip_address,
            'user_agent': user_agent,
            **extra_context
        }
        
        # Remove None values
        self.context_data = {k: v for k, v in self.context_data.items() if v is not None}
        
    def __enter__(self):
        """Enter the request context"""
        thread_context.set_context(**self.context_data)
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the request context"""
        # Remove request-specific keys
        for key in self.context_data:
            thread_context.remove_key(key)
            
    def update(self, **context_data):
        """Update the context with additional data"""
        self.context_data.update(context_data)
        thread_context.set_context(**context_data)


class TransactionContext:
    """Context for database transaction logging"""
    
    def __init__(self, transaction_id: str, operation: str = None, **extra_context):
        self.context_data = {
            'transaction_id': transaction_id,
            'db_operation': operation,
            **extra_context
        }
        
        # Remove None values
        self.context_data = {k: v for k, v in self.context_data.items() if v is not None}
        
    def __enter__(self):
        """Enter the transaction context"""
        thread_context.set_context(**self.context_data)
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the transaction context"""
        # Remove transaction-specific keys
        for key in self.context_data:
            thread_context.remove_key(key)
            
    def update(self, **context_data):
        """Update the context with additional data"""
        self.context_data.update(context_data)
        thread_context.set_context(**context_data)


def set_global_context(**context_data):
    """Set global context that persists across the thread"""
    thread_context.set_context(**context_data)


def clear_global_context():
    """Clear all global context"""
    thread_context.clear_context()


def get_current_context() -> Dict[str, Any]:
    """Get the current logging context"""
    context = thread_context.get_context()
    
    # Add context variables if available
    try:
        ctx_vars = _log_context.get()
        for key, value in ctx_vars.items():
            if key not in context:
                context[key] = value
    except LookupError:
        pass
        
    return context