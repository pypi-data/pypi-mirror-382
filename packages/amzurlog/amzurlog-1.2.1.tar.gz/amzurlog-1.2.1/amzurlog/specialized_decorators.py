"""
AmzurLog Specialized Decorators
===============================

This module provides decorators for automatic specialized logging:
- Security event decorators
- Audit trail decorators
- API endpoint decorators
- LLM interaction decorators
"""

import time
import functools
import traceback
from typing import Callable, Optional, Any
from datetime import datetime

from .core import AmzurLogger
from .specialized import SpecializedLoggers


def log_security_event(
    event_type: str,
    logger: Optional[AmzurLogger] = None,
    include_args: bool = False
):
    """
    Decorator to automatically log security events
    
    Args:
        event_type: Type of security event
        logger: Logger instance (creates default if None)
        include_args: Whether to include function arguments
    """
    def decorator(func: Callable) -> Callable:
        if logger is None:
            specialized = SpecializedLoggers.create(f"security.{func.__module__}.{func.__name__}")
        else:
            specialized = SpecializedLoggers(logger)
            
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            user_id = kwargs.get('user_id') or kwargs.get('current_user', {}).get('id', 'anonymous')
            request_id = kwargs.get('request_id', 'unknown')
            
            # Build security context
            security_context = {
                'user_id': str(user_id),
                'request_id': str(request_id),
                'function_name': func.__name__,
                'module': func.__module__,
                'ip': kwargs.get('client_ip', 'unknown'),
                'user_agent': kwargs.get('user_agent', 'unknown')
            }
            
            if include_args and args:
                security_context['args'] = [str(arg)[:100] for arg in args]
                
            try:
                result = func(*args, **kwargs)
                
                specialized.security.security_event(
                    f"Security operation completed: {func.__name__}",
                    event_type=event_type,
                    status='success',
                    **security_context
                )
                
                return result
                
            except Exception as e:
                specialized.security.security_event(
                    f"Security operation failed: {func.__name__}",
                    event_type=event_type,
                    status='failed',
                    error_type=type(e).__name__,
                    error_message=str(e),
                    **security_context
                )
                raise
                
        return wrapper
    return decorator


def log_audit_action(
    action: str,
    resource: str,
    logger: Optional[AmzurLogger] = None
):
    """
    Decorator to automatically log audit events
    
    Args:
        action: Audit action being performed
        resource: Resource being acted upon
        logger: Logger instance (creates default if None)
    """
    def decorator(func: Callable) -> Callable:
        if logger is None:
            specialized = SpecializedLoggers.create(f"audit.{func.__module__}.{func.__name__}")
        else:
            specialized = SpecializedLoggers(logger)
            
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            user_id = kwargs.get('user_id') or kwargs.get('current_user', {}).get('id', 'anonymous')
            resource_id = kwargs.get('resource_id') or kwargs.get('id')
            
            try:
                result = func(*args, **kwargs)
                
                specialized.audit.audit_event(
                    f"Audit: {action} completed successfully on {resource}",
                    action=action,
                    user_id=str(user_id),
                    resource=resource,
                    resource_id=str(resource_id) if resource_id else None,
                    status='success',
                    function_name=func.__name__
                )
                
                return result
                
            except Exception as e:
                specialized.audit.audit_event(
                    f"Audit: {action} failed on {resource}",
                    action=action,
                    user_id=str(user_id),
                    resource=resource,
                    resource_id=str(resource_id) if resource_id else None,
                    status='failed',
                    error_type=type(e).__name__,
                    error_message=str(e),
                    function_name=func.__name__
                )
                raise
                
        return wrapper
    return decorator


def log_api_endpoint(
    logger: Optional[AmzurLogger] = None,
    log_request_body: bool = False,
    log_response_body: bool = False
):
    """
    Decorator to automatically log API endpoint calls
    
    Args:
        logger: Logger instance (creates default if None)
        log_request_body: Whether to log request body
        log_response_body: Whether to log response body
    """
    def decorator(func: Callable) -> Callable:
        if logger is None:
            specialized = SpecializedLoggers.create(f"api.{func.__module__}.{func.__name__}")
        else:
            specialized = SpecializedLoggers(logger)
            
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            request_id = kwargs.get('request_id', f"req-{int(time.time())}")
            
            # Extract request info (assuming FastAPI-style)
            request = kwargs.get('request')
            method = getattr(request, 'method', 'UNKNOWN') if request else 'UNKNOWN'
            path = getattr(request, 'url', {}).path if request else func.__name__
            user_id = kwargs.get('user_id', 'anonymous')
            
            api_context = {
                'request_id': request_id,
                'method': method,
                'path': path,
                'user_id': str(user_id),
                'function_name': func.__name__
            }
            
            if log_request_body and request:
                try:
                    body = await request.body()
                    api_context['request_body'] = body.decode()[:500]
                except:
                    api_context['request_body'] = 'Unable to read'
            
            try:
                result = await func(*args, **kwargs)
                duration = int((time.time() - start_time) * 1000)
                
                # Extract status code from result if possible
                status_code = getattr(result, 'status_code', 200)
                
                if log_response_body:
                    api_context['response_body'] = str(result)[:500]
                
                specialized.api.api_request(
                    f"API call completed: {method} {path}",
                    status_code=status_code,
                    duration=duration,
                    **api_context
                )
                
                return result
                
            except Exception as e:
                duration = int((time.time() - start_time) * 1000)
                
                specialized.api.api_error(
                    f"API call failed: {method} {path}",
                    error_type=type(e).__name__,
                    error_message=str(e),
                    duration=duration,
                    **api_context
                )
                raise
                
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            request_id = kwargs.get('request_id', f"req-{int(time.time())}")
            
            api_context = {
                'request_id': request_id,
                'method': 'SYNC',
                'path': func.__name__,
                'user_id': str(kwargs.get('user_id', 'anonymous')),
                'function_name': func.__name__
            }
            
            try:
                result = func(*args, **kwargs)
                duration = int((time.time() - start_time) * 1000)
                
                specialized.api.api_request(
                    f"API call completed: {func.__name__}",
                    status_code=200,
                    duration=duration,
                    **api_context
                )
                
                return result
                
            except Exception as e:
                duration = int((time.time() - start_time) * 1000)
                
                specialized.api.api_error(
                    f"API call failed: {func.__name__}",
                    error_type=type(e).__name__,
                    error_message=str(e),
                    duration=duration,
                    **api_context
                )
                raise
        
        # Return appropriate wrapper based on function type
        if hasattr(func, '__code__') and func.__code__.co_flags & 0x80:  # Check if coroutine
            return async_wrapper
        else:
            return sync_wrapper
            
    return decorator


def log_llm_interaction(
    model: str,
    logger: Optional[AmzurLogger] = None,
    track_tokens: bool = True,
    track_cost: bool = False
):
    """
    Decorator to automatically log LLM interactions
    
    Args:
        model: LLM model being used
        logger: Logger instance (creates default if None)
        track_tokens: Whether to track token usage
        track_cost: Whether to track cost
    """
    def decorator(func: Callable) -> Callable:
        if logger is None:
            specialized = SpecializedLoggers.create(f"llm.{func.__module__}.{func.__name__}")
        else:
            specialized = SpecializedLoggers(logger)
            
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            user_id = kwargs.get('user_id', 'anonymous')
            
            try:
                result = await func(*args, **kwargs)
                duration = int((time.time() - start_time) * 1000)
                
                # Extract token count from result
                tokens = 0
                cost = None
                
                if track_tokens and hasattr(result, 'usage'):
                    tokens = getattr(result.usage, 'total_tokens', 0)
                elif isinstance(result, str):
                    tokens = len(result.split())  # Rough estimate
                
                if track_cost:
                    # Basic cost estimation (would need actual pricing)
                    cost = tokens * 0.00002  # Example rate
                
                specialized.llm.llm_interaction(
                    f"LLM interaction completed with {model}",
                    user_id=str(user_id),
                    model=model,
                    tokens=tokens,
                    duration=duration,
                    cost=cost,
                    function_name=func.__name__
                )
                
                return result
                
            except Exception as e:
                duration = int((time.time() - start_time) * 1000)
                
                specialized.llm.llm_error(
                    f"LLM interaction failed with {model}",
                    user_id=str(user_id),
                    model=model,
                    error_type=type(e).__name__,
                    error_message=str(e),
                    duration=duration,
                    function_name=func.__name__
                )
                raise
                
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            user_id = kwargs.get('user_id', 'anonymous')
            
            try:
                result = func(*args, **kwargs)
                duration = int((time.time() - start_time) * 1000)
                
                tokens = 0
                if track_tokens:
                    if hasattr(result, 'usage'):
                        tokens = getattr(result.usage, 'total_tokens', 0)
                    elif isinstance(result, str):
                        tokens = len(result.split())
                
                cost = None
                if track_cost:
                    cost = tokens * 0.00002
                
                specialized.llm.llm_interaction(
                    f"LLM interaction completed with {model}",
                    user_id=str(user_id),
                    model=model,
                    tokens=tokens,
                    duration=duration,
                    cost=cost,
                    function_name=func.__name__
                )
                
                return result
                
            except Exception as e:
                duration = int((time.time() - start_time) * 1000)
                
                specialized.llm.llm_error(
                    f"LLM interaction failed with {model}",
                    user_id=str(user_id),
                    model=model,
                    error_type=type(e).__name__,
                    error_message=str(e),
                    duration=duration,
                    function_name=func.__name__
                )
                raise
        
        # Return appropriate wrapper
        if hasattr(func, '__code__') and func.__code__.co_flags & 0x80:
            return async_wrapper
        else:
            return sync_wrapper
            
    return decorator


def log_database_operation(
    operation: str,
    table: str = None,
    logger: Optional[AmzurLogger] = None
):
    """
    Decorator to log database operations
    
    Args:
        operation: Database operation (SELECT, INSERT, UPDATE, DELETE)
        table: Database table name
        logger: Logger instance (creates default if None)
    """
    def decorator(func: Callable) -> Callable:
        if logger is None:
            specialized = SpecializedLoggers.create(f"db.{func.__module__}.{func.__name__}")
        else:
            specialized = SpecializedLoggers(logger)
            
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration = int((time.time() - start_time) * 1000)
                
                # Try to extract record count from result
                record_count = None
                if hasattr(result, '__len__'):
                    record_count = len(result)
                elif hasattr(result, 'rowcount'):
                    record_count = result.rowcount
                
                specialized.audit.audit_event(
                    f"Database operation completed: {operation} on {table or 'unknown'}",
                    action=f"db_{operation.lower()}",
                    user_id=str(kwargs.get('user_id', 'system')),
                    resource=table or 'database',
                    duration=duration,
                    record_count=record_count,
                    function_name=func.__name__
                )
                
                return result
                
            except Exception as e:
                duration = int((time.time() - start_time) * 1000)
                
                specialized.error.database_error(
                    f"Database operation failed: {operation} on {table or 'unknown'}",
                    operation=operation,
                    table=table or 'unknown',
                    error_message=str(e),
                    duration=duration,
                    function_name=func.__name__
                )
                raise
                
        return wrapper
    return decorator