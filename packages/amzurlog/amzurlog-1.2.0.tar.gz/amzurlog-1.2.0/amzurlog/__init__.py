"""
AmzurLog - A Custom Logging Library
===================================

A powerful, flexible, and easy-to-use logging library built from scratch.

Features:
- Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- File and console handlers
- Custom formatters
- Log rotation
- Performance monitoring
- Security logging
- Structured logging with JSON support
- Context managers
- Thread-safe operations
"""

from .core import AmzurLogger, LogLevel
from .handlers import FileHandler, ConsoleHandler, RotatingFileHandler, TimedRotatingFileHandler
from .formatters import SimpleFormatter, JSONFormatter, ColoredFormatter
from .filters import LevelFilter, PatternFilter, RateLimitFilter
from .decorators import log_performance, log_calls, log_errors
from .context import LogContext, RequestContext, log_context
from .config import AmzurLogConfig, quick_setup
from .specialized import SpecializedLoggers, SecurityLogger, AuditLogger, APILogger, LLMLogger, ErrorLogger
from .specialized_decorators import (
    log_security_event, log_audit_action, log_api_endpoint, 
    log_llm_interaction, log_database_operation
)
from .sensitive_data import (
    SensitiveDataProtector, SensitiveDataFilter, 
    create_default_protector, create_strict_protector, create_compliance_protector,
    protect_passwords_and_tokens, mask_email_and_ids, sanitize_log_message
)
from .sensitive_formatters import (
    SensitiveSimpleFormatter, SensitiveJSONFormatter, SensitiveColoredFormatter
)
from .streaming_handlers import (
    StreamingHandler, ELKStreamingHandler, GrafanaStreamingHandler,
    KafkaStreamingHandler, RedisStreamingHandler, MultiStreamingHandler
)
from .streaming import StreamManager, StreamEvent, StreamDestinationType
from .streaming_configs import (
    get_elk_config, get_grafana_loki_config, get_kafka_config, get_redis_config,
    get_example_config, list_example_configs
)
from .exception_handlers import ExceptionHandler, SentryHandler, RollbarHandler
from .exception_tracking import (
    ExceptionTracker, ExceptionSeverity, ExceptionStatus, track_exceptions,
    install_global_exception_handler, get_global_tracker, set_global_tracker
)
from .exception_configs import (
    get_sentry_config, get_rollbar_config, get_webhook_exception_config,
    get_example_exception_config, list_example_exception_configs
)

__version__ = "1.2.0"
__author__ = "AmzurATG"
__email__ = "support@amzur.com"

# Default logger instance
default_logger = AmzurLogger("amzurlog")

# Add console handler to default logger
_default_handler = ConsoleHandler()
_default_handler.set_formatter(SimpleFormatter())
default_logger.add_handler(_default_handler)

# Convenience functions for quick logging
def debug(message, **kwargs):
    """Log a debug message"""
    default_logger.debug(message, **kwargs)

def info(message, **kwargs):
    """Log an info message"""
    default_logger.info(message, **kwargs)

def warning(message, **kwargs):
    """Log a warning message"""
    default_logger.warning(message, **kwargs)

def error(message, **kwargs):
    """Log an error message"""
    default_logger.error(message, **kwargs)

def critical(message, **kwargs):
    """Log a critical message"""
    default_logger.critical(message, **kwargs)

def configure_logger(name=None, level=LogLevel.INFO, handlers=None, formatters=None):
    """Configure and return a logger instance"""
    logger = AmzurLogger(name or "amzurlog")
    logger.set_level(level)
    
    if handlers:
        for handler in handlers:
            logger.add_handler(handler)
    
    return logger

__all__ = [
    'AmzurLogger',
    'LogLevel',
    'FileHandler',
    'ConsoleHandler', 
    'RotatingFileHandler',
    'SimpleFormatter',
    'JSONFormatter',
    'ColoredFormatter',
    'SensitiveSimpleFormatter',
    'SensitiveJSONFormatter', 
    'SensitiveColoredFormatter',
    'LevelFilter',
    'PatternFilter',
    'RateLimitFilter',
    'SensitiveDataFilter',
    'log_performance',
    'log_calls',
    'log_errors',
    'LogContext',
    'RequestContext',
    'log_context',
    'AmzurLogConfig',
    'quick_setup',
    'SpecializedLoggers',
    'SecurityLogger',
    'AuditLogger',
    'APILogger',
    'LLMLogger',
    'ErrorLogger',
    'log_security_event',
    'log_audit_action',
    'log_api_endpoint',
    'log_llm_interaction',
    'log_database_operation',
    'SensitiveDataProtector',
    'create_default_protector',
    'create_strict_protector', 
    'create_compliance_protector',
    'protect_passwords_and_tokens',
    'mask_email_and_ids',
    'sanitize_log_message',
    'StreamingHandler',
    'ELKStreamingHandler',
    'GrafanaStreamingHandler',
    'KafkaStreamingHandler',
    'RedisStreamingHandler',
    'MultiStreamingHandler',
    'StreamManager',
    'StreamEvent',
    'StreamDestinationType',
    'get_elk_config',
    'get_grafana_loki_config',
    'get_kafka_config',
    'get_redis_config',
    'get_example_config',
    'list_example_configs',
    'ExceptionHandler',
    'SentryHandler',
    'RollbarHandler',
    'ExceptionTracker',
    'ExceptionSeverity',
    'ExceptionStatus',
    'track_exceptions',
    'install_global_exception_handler',
    'get_global_tracker',
    'set_global_tracker',
    'get_sentry_config',
    'get_rollbar_config',
    'get_webhook_exception_config',
    'get_example_exception_config',
    'list_example_exception_configs',
    'debug',
    'info',
    'warning',
    'error',
    'critical',
    'configure_logger',
    'default_logger'
]