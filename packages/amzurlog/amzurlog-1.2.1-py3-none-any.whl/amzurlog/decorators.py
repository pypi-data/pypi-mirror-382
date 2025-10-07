"""
AmzurLog Decorators
===================

This module contains decorators for automatic logging of function calls, performance, and errors:
- log_calls: Log function calls with parameters
- log_performance: Log function performance metrics
- log_errors: Log function errors and exceptions
"""

import time
import functools
import traceback
import threading
from typing import Any, Callable, Optional, Dict
from datetime import datetime

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

from .core import AmzurLogger, LogLevel


def log_calls(
    logger: Optional[AmzurLogger] = None,
    level: LogLevel = LogLevel.DEBUG,
    include_args: bool = True,
    include_kwargs: bool = True,
    include_result: bool = False,
    max_arg_length: int = 100
):
    """
    Decorator to log function calls
    
    Args:
        logger: Logger instance to use (creates default if None)
        level: Log level for call logging
        include_args: Whether to include function arguments
        include_kwargs: Whether to include keyword arguments
        include_result: Whether to include function result
        max_arg_length: Maximum length for argument values in logs
    """
    def decorator(func: Callable) -> Callable:
        if logger is None:
            func_logger = AmzurLogger(f"amzurlog.calls.{func.__module__}.{func.__name__}")
        else:
            func_logger = logger
            
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Prepare call info
            call_info = {
                'function': func.__name__,
                'module': func.__module__,
                'thread_id': threading.get_ident(),
                'thread_name': threading.current_thread().name
            }
            
            # Add arguments if requested
            if include_args and args:
                call_info['args'] = [
                    str(arg)[:max_arg_length] if len(str(arg)) > max_arg_length 
                    else str(arg) for arg in args
                ]
                
            if include_kwargs and kwargs:
                call_info['kwargs'] = {
                    k: str(v)[:max_arg_length] if len(str(v)) > max_arg_length 
                    else str(v) for k, v in kwargs.items()
                }
            
            # Log the call
            func_logger._log(
                level,
                f"Calling function {func.__name__}",
                extra=call_info
            )
            
            try:
                # Execute function
                start_time = time.time()
                result = func(*args, **kwargs)
                end_time = time.time()
                
                # Log successful completion
                success_info = call_info.copy()
                success_info.update({
                    'status': 'success',
                    'execution_time': round(end_time - start_time, 4)
                })
                
                if include_result:
                    result_str = str(result)
                    if len(result_str) > max_arg_length:
                        result_str = result_str[:max_arg_length] + "..."
                    success_info['result'] = result_str
                    
                func_logger._log(
                    level,
                    f"Function {func.__name__} completed successfully",
                    extra=success_info
                )
                
                return result
                
            except Exception as e:
                # Log error
                error_info = call_info.copy()
                error_info.update({
                    'status': 'error',
                    'error_type': type(e).__name__,
                    'error_message': str(e)
                })
                
                func_logger._log(
                    LogLevel.ERROR,
                    f"Function {func.__name__} failed with error",
                    extra=error_info,
                    exc_info=(type(e), e, e.__traceback__)
                )
                
                raise
                
        return wrapper
    return decorator


def log_performance(
    logger: Optional[AmzurLogger] = None,
    level: LogLevel = LogLevel.INFO,
    include_memory: bool = True,
    include_cpu: bool = True,
    threshold_seconds: float = 0.0
):
    """
    Decorator to log function performance metrics
    
    Args:
        logger: Logger instance to use (creates default if None)
        level: Log level for performance logging
        include_memory: Whether to include memory usage
        include_cpu: Whether to include CPU usage
        threshold_seconds: Only log if execution time exceeds this threshold
    """
    def decorator(func: Callable) -> Callable:
        if logger is None:
            func_logger = AmzurLogger(f"amzurlog.performance.{func.__module__}.{func.__name__}")
        else:
            func_logger = logger
            
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get initial metrics
            start_time = time.time()
            start_cpu_time = time.process_time()
            
            if PSUTIL_AVAILABLE and include_memory:
                process = psutil.Process()
                start_memory = process.memory_info().rss
            else:
                start_memory = None
                
            try:
                # Execute function
                result = func(*args, **kwargs)
                
                # Calculate metrics
                end_time = time.time()
                end_cpu_time = time.process_time()
                
                execution_time = end_time - start_time
                cpu_time = end_cpu_time - start_cpu_time
                
                # Check threshold
                if execution_time < threshold_seconds:
                    return result
                
                # Prepare performance info
                perf_info = {
                    'function': func.__name__,
                    'module': func.__module__,
                    'execution_time': round(execution_time, 4),
                    'cpu_time': round(cpu_time, 4),
                    'thread_id': threading.get_ident(),
                    'thread_name': threading.current_thread().name
                }
                
                # Add memory info if available
                if start_memory is not None and PSUTIL_AVAILABLE:
                    try:
                        end_memory = process.memory_info().rss
                        memory_delta = end_memory - start_memory
                        perf_info.update({
                            'memory_start_mb': round(start_memory / 1024 / 1024, 2),
                            'memory_end_mb': round(end_memory / 1024 / 1024, 2),
                            'memory_delta_mb': round(memory_delta / 1024 / 1024, 2)
                        })
                    except Exception:
                        pass
                        
                # Add CPU percentage if available
                if PSUTIL_AVAILABLE and include_cpu:
                    try:
                        cpu_percent = process.cpu_percent()
                        perf_info['cpu_percent'] = cpu_percent
                    except Exception:
                        pass
                
                # Log performance
                func_logger._log(
                    level,
                    f"Performance metrics for {func.__name__}",
                    extra=perf_info
                )
                
                return result
                
            except Exception:
                # Still log performance for failed functions
                end_time = time.time()
                execution_time = end_time - start_time
                
                if execution_time >= threshold_seconds:
                    error_perf_info = {
                        'function': func.__name__,
                        'module': func.__module__,
                        'execution_time': round(execution_time, 4),
                        'status': 'error'
                    }
                    
                    func_logger._log(
                        LogLevel.WARNING,
                        f"Performance metrics for failed function {func.__name__}",
                        extra=error_perf_info
                    )
                
                raise
                
        return wrapper
    return decorator


def log_errors(
    logger: Optional[AmzurLogger] = None,
    level: LogLevel = LogLevel.ERROR,
    reraise: bool = True,
    include_locals: bool = False
):
    """
    Decorator to log function errors and exceptions
    
    Args:
        logger: Logger instance to use (creates default if None)
        level: Log level for error logging
        reraise: Whether to reraise the exception after logging
        include_locals: Whether to include local variables in error log
    """
    def decorator(func: Callable) -> Callable:
        if logger is None:
            func_logger = AmzurLogger(f"amzurlog.errors.{func.__module__}.{func.__name__}")
        else:
            func_logger = logger
            
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Prepare error info
                error_info = {
                    'function': func.__name__,
                    'module': func.__module__,
                    'error_type': type(e).__name__,
                    'error_message': str(e),
                    'thread_id': threading.get_ident(),
                    'thread_name': threading.current_thread().name,
                    'traceback': traceback.format_exc()
                }
                
                # Add function arguments
                if args:
                    error_info['args'] = [str(arg) for arg in args]
                if kwargs:
                    error_info['kwargs'] = {k: str(v) for k, v in kwargs.items()}
                
                # Add local variables if requested
                if include_locals:
                    try:
                        frame = traceback.extract_tb(e.__traceback__)[-1]
                        error_info['locals'] = {
                            k: str(v)[:200] for k, v in frame.locals.items()
                            if not k.startswith('_')
                        }
                    except Exception:
                        pass
                
                # Log the error
                func_logger._log(
                    level,
                    f"Error in function {func.__name__}: {str(e)}",
                    extra=error_info,
                    exc_info=(type(e), e, e.__traceback__)
                )
                
                if reraise:
                    raise
                    
        return wrapper
    return decorator


def log_async_calls(
    logger: Optional[AmzurLogger] = None,
    level: LogLevel = LogLevel.DEBUG,
    include_args: bool = True,
    include_kwargs: bool = True
):
    """
    Decorator to log async function calls
    
    Args:
        logger: Logger instance to use (creates default if None)
        level: Log level for call logging
        include_args: Whether to include function arguments
        include_kwargs: Whether to include keyword arguments
    """
    def decorator(func: Callable) -> Callable:
        if logger is None:
            func_logger = AmzurLogger(f"amzurlog.async.{func.__module__}.{func.__name__}")
        else:
            func_logger = logger
            
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Prepare call info
            call_info = {
                'function': func.__name__,
                'module': func.__module__,
                'is_async': True,
                'thread_id': threading.get_ident(),
                'thread_name': threading.current_thread().name
            }
            
            # Add arguments if requested
            if include_args and args:
                call_info['args'] = [str(arg) for arg in args]
                
            if include_kwargs and kwargs:
                call_info['kwargs'] = {k: str(v) for k, v in kwargs.items()}
            
            # Log the call
            func_logger._log(
                level,
                f"Calling async function {func.__name__}",
                extra=call_info
            )
            
            try:
                # Execute async function
                start_time = time.time()
                result = await func(*args, **kwargs)
                end_time = time.time()
                
                # Log successful completion
                success_info = call_info.copy()
                success_info.update({
                    'status': 'success',
                    'execution_time': round(end_time - start_time, 4)
                })
                
                func_logger._log(
                    level,
                    f"Async function {func.__name__} completed successfully",
                    extra=success_info
                )
                
                return result
                
            except Exception as e:
                # Log error
                error_info = call_info.copy()
                error_info.update({
                    'status': 'error',
                    'error_type': type(e).__name__,
                    'error_message': str(e)
                })
                
                func_logger._log(
                    LogLevel.ERROR,
                    f"Async function {func.__name__} failed with error",
                    extra=error_info,
                    exc_info=(type(e), e, e.__traceback__)
                )
                
                raise
                
        return wrapper
    return decorator