"""
AmzurLog Configuration and Setup
=================================

This module provides configuration classes and setup utilities for AmzurLog.
"""

import os
import json
from typing import Dict, Any, List, Optional, Union
from pathlib import Path

from .core import AmzurLogger, LogLevel
from .handlers import FileHandler, ConsoleHandler, RotatingFileHandler, TimedRotatingFileHandler, MultiHandler
from .formatters import SimpleFormatter, JSONFormatter, ColoredFormatter, CSVFormatter
from .filters import LevelFilter, PatternFilter, RateLimitFilter
from .context import ContextAwareLogger
from .streaming_handlers import (
    StreamingHandler, ELKStreamingHandler, GrafanaStreamingHandler,
    KafkaStreamingHandler, RedisStreamingHandler, MultiStreamingHandler
)
from .exception_handlers import ExceptionHandler, SentryHandler, RollbarHandler


class AmzurLogConfig:
    """Configuration class for AmzurLog"""
    
    def __init__(self, config_dict: Optional[Dict[str, Any]] = None):
        """
        Initialize configuration
        
        Args:
            config_dict: Configuration dictionary
        """
        self.config = config_dict or {}
        self._loggers = {}
        
    @classmethod
    def from_file(cls, config_path: str) -> 'AmzurLogConfig':
        """Load configuration from JSON file"""
        with open(config_path, 'r', encoding='utf-8') as f:
            config_dict = json.load(f)
        return cls(config_dict)
        
    @classmethod
    def from_env(cls, prefix: str = 'AMZURLOG_') -> 'AmzurLogConfig':
        """Load configuration from environment variables"""
        config = {}
        
        # Basic configuration from env vars
        log_level = os.getenv(f'{prefix}LEVEL', 'INFO')
        log_format = os.getenv(f'{prefix}FORMAT', 'simple')
        log_file = os.getenv(f'{prefix}FILE')
        log_dir = os.getenv(f'{prefix}DIR', 'logs')
        
        config['level'] = log_level
        config['format'] = log_format
        
        if log_file:
            config['file'] = log_file
        else:
            config['directory'] = log_dir
            
        # Console logging
        console_enabled = os.getenv(f'{prefix}CONSOLE', 'true').lower() == 'true'
        config['console'] = {'enabled': console_enabled}
        
        # Rotation settings
        max_size = os.getenv(f'{prefix}MAX_SIZE', '10MB')
        backup_count = int(os.getenv(f'{prefix}BACKUP_COUNT', '5'))
        
        config['rotation'] = {
            'max_size': max_size,
            'backup_count': backup_count
        }
        
        return cls(config)
        
    def _parse_size(self, size_str: str) -> int:
        """Parse size string (e.g., '10MB') to bytes"""
        if isinstance(size_str, int):
            return size_str
            
        size_str = size_str.upper()
        multipliers = {
            'B': 1,
            'KB': 1024,
            'MB': 1024 * 1024,
            'GB': 1024 * 1024 * 1024
        }
        
        for suffix, multiplier in multipliers.items():
            if size_str.endswith(suffix):
                number = size_str[:-len(suffix)]
                return int(number) * multiplier
                
        # Default to bytes if no suffix
        return int(size_str)
        
    def _create_formatter(self, formatter_config: Union[str, Dict[str, Any]]):
        """Create formatter from configuration"""
        if isinstance(formatter_config, str):
            formatter_type = formatter_config
            formatter_options = {}
        else:
            formatter_type = formatter_config.get('type', 'simple')
            formatter_options = formatter_config.get('options', {})
            
        if formatter_type == 'simple':
            format_string = formatter_options.get('format')
            return SimpleFormatter(format_string)
        elif formatter_type == 'json':
            indent = formatter_options.get('indent')
            ensure_ascii = formatter_options.get('ensure_ascii', False)
            return JSONFormatter(indent=indent, ensure_ascii=ensure_ascii)
        elif formatter_type == 'colored':
            format_string = formatter_options.get('format')
            use_colors = formatter_options.get('use_colors')
            return ColoredFormatter(format_string, use_colors)
        elif formatter_type == 'csv':
            fields = formatter_options.get('fields')
            delimiter = formatter_options.get('delimiter', ',')
            return CSVFormatter(fields=fields, delimiter=delimiter)
        else:
            return SimpleFormatter()
            
    def _create_handler(self, handler_config: Dict[str, Any]):
        """Create handler from configuration"""
        handler_type = handler_config.get('type', 'console')
        level = handler_config.get('level')
        if level:
            level = LogLevel.from_string(level)
            
        if handler_type == 'console':
            handler = ConsoleHandler(level=level)
        elif handler_type == 'file':
            filename = handler_config.get('filename', 'app.log')
            mode = handler_config.get('mode', 'a')
            encoding = handler_config.get('encoding', 'utf-8')
            handler = FileHandler(filename, mode, encoding, level)
        elif handler_type == 'rotating':
            filename = handler_config.get('filename', 'app.log')
            max_bytes = self._parse_size(handler_config.get('max_bytes', '10MB'))
            backup_count = handler_config.get('backup_count', 5)
            encoding = handler_config.get('encoding', 'utf-8')
            handler = RotatingFileHandler(filename, max_bytes, backup_count, encoding, level)
        elif handler_type == 'timed_rotating':
            filename = handler_config.get('filename', 'app.log')
            when = handler_config.get('when', 'midnight')
            interval = handler_config.get('interval', 1)
            backup_count = handler_config.get('backup_count', 0)
            encoding = handler_config.get('encoding', 'utf-8')
            delay = handler_config.get('delay', False)
            utc = handler_config.get('utc', False)
            at_time = handler_config.get('at_time')
            if at_time:
                # Parse time string like "02:30" into datetime.time
                from datetime import datetime
                try:
                    at_time = datetime.strptime(at_time, "%H:%M").time()
                except ValueError:
                    at_time = None
            handler = TimedRotatingFileHandler(filename, when, interval, backup_count, 
                                             encoding, delay, utc, at_time, level)
        elif handler_type == 'streaming':
            # Create streaming handler based on class specification
            handler_class = handler_config.get('class', 'StreamingHandler')
            
            if handler_class == 'ELKStreamingHandler':
                handler = ELKStreamingHandler(
                    elasticsearch_hosts=handler_config.get('elasticsearch_hosts', ['localhost:9200']),
                    index_pattern=handler_config.get('index_pattern', 'amzurlog-{date}'),
                    level=level,
                    **{k: v for k, v in handler_config.items() 
                       if k not in ['type', 'class', 'level', 'formatter', 'filters']}
                )
            elif handler_class == 'GrafanaStreamingHandler':
                handler = GrafanaStreamingHandler(
                    backend=handler_config.get('backend', 'loki'),
                    backend_config=handler_config.get('backend_config', {}),
                    level=level,
                    **{k: v for k, v in handler_config.items() 
                       if k not in ['type', 'class', 'level', 'formatter', 'filters', 'backend', 'backend_config']}
                )
            elif handler_class == 'KafkaStreamingHandler':
                handler = KafkaStreamingHandler(
                    bootstrap_servers=handler_config.get('bootstrap_servers', ['localhost:9092']),
                    topic=handler_config.get('topic', 'amzurlog-events'),
                    level=level,
                    **{k: v for k, v in handler_config.items() 
                       if k not in ['type', 'class', 'level', 'formatter', 'filters', 'bootstrap_servers', 'topic']}
                )
            elif handler_class == 'RedisStreamingHandler':
                handler = RedisStreamingHandler(
                    redis_host=handler_config.get('redis_host', 'localhost'),
                    redis_port=handler_config.get('redis_port', 6379),
                    redis_db=handler_config.get('redis_db', 0),
                    stream_name=handler_config.get('stream_name', 'amzurlog:events'),
                    level=level,
                    **{k: v for k, v in handler_config.items() 
                       if k not in ['type', 'class', 'level', 'formatter', 'filters', 'redis_host', 'redis_port', 'redis_db', 'stream_name']}
                )
            elif handler_class == 'MultiStreamingHandler':
                handler = MultiStreamingHandler(
                    streamers_config=handler_config.get('streamers_config', {}),
                    level=level,
                    **{k: v for k, v in handler_config.items() 
                       if k not in ['type', 'class', 'level', 'formatter', 'filters', 'streamers_config']}
                )
            else:
                # Generic streaming handler
                stream_config = handler_config.get('stream_config', {})
                handler = StreamingHandler(
                    stream_config=stream_config,
                    level=level,
                    **{k: v for k, v in handler_config.items() 
                       if k not in ['type', 'class', 'level', 'formatter', 'filters', 'stream_config']}
                )
        elif handler_type == 'exception':
            # Create exception handler based on class specification
            handler_class = handler_config.get('class', 'ExceptionHandler')
            
            if handler_class == 'SentryHandler':
                handler = SentryHandler(
                    sentry_dsn=handler_config.get('sentry_dsn'),
                    environment=handler_config.get('environment', 'production'),
                    level=level,
                    **{k: v for k, v in handler_config.items() 
                       if k not in ['type', 'class', 'level', 'formatter', 'filters', 'sentry_dsn', 'environment']}
                )
            elif handler_class == 'RollbarHandler':
                handler = RollbarHandler(
                    rollbar_token=handler_config.get('rollbar_token'),
                    environment=handler_config.get('environment', 'production'),
                    level=level,
                    **{k: v for k, v in handler_config.items() 
                       if k not in ['type', 'class', 'level', 'formatter', 'filters', 'rollbar_token', 'environment']}
                )
            else:
                # Generic exception handler
                handler = ExceptionHandler(
                    level=level,
                    auto_capture=handler_config.get('auto_capture', True),
                    capture_locals=handler_config.get('capture_locals', True),
                    capture_globals=handler_config.get('capture_globals', False)
                )
                
                # Add integrations if specified
                integrations_config = handler_config.get('integrations', {})
                for integration_name, integration_config in integrations_config.items():
                    if integration_config.get('type') == 'sentry':
                        handler.add_sentry_integration(
                            integration_config.get('dsn'),
                            environment=integration_config.get('environment', 'production'),
                            **{k: v for k, v in integration_config.items() 
                               if k not in ['type', 'dsn', 'environment']}
                        )
                    elif integration_config.get('type') == 'webhook':
                        from .exception_handlers import WebhookExceptionIntegration
                        webhook_integration = WebhookExceptionIntegration(
                            webhook_url=integration_config.get('url'),
                            headers=integration_config.get('headers', {})
                        )
                        handler.add_integration(integration_name, webhook_integration)
        else:
            handler = ConsoleHandler(level=level)
            
        # Set formatter
        formatter_config = handler_config.get('formatter')
        if formatter_config:
            formatter = self._create_formatter(formatter_config)
            handler.set_formatter(formatter)
            
        # Add filters
        filters_config = handler_config.get('filters', [])
        for filter_config in filters_config:
            filter_obj = self._create_filter(filter_config)
            if filter_obj:
                handler.add_filter(filter_obj)
                
        return handler
        
    def _create_filter(self, filter_config: Dict[str, Any]):
        """Create filter from configuration"""
        filter_type = filter_config.get('type')
        
        if filter_type == 'level':
            min_level = filter_config.get('min_level')
            max_level = filter_config.get('max_level')
            return LevelFilter(min_level, max_level)
        elif filter_type == 'pattern':
            pattern = filter_config.get('pattern')
            include = filter_config.get('include', True)
            return PatternFilter(pattern, include)
        elif filter_type == 'rate_limit':
            max_rate = filter_config.get('max_rate', 10)
            time_window = filter_config.get('time_window', 60)
            per_logger = filter_config.get('per_logger', True)
            return RateLimitFilter(max_rate, time_window, per_logger)
            
        return None
        
    def setup_logger(
        self,
        name: str,
        logger_config: Optional[Dict[str, Any]] = None
    ) -> AmzurLogger:
        """Set up a logger with the given configuration"""
        if name in self._loggers:
            return self._loggers[name]
            
        # Use logger-specific config or fall back to global config
        config = logger_config or self.config
        
        # Create logger
        use_context = config.get('use_context', True)
        if use_context:
            logger = ContextAwareLogger(name)
        else:
            logger = AmzurLogger(name)
            
        # Set level
        level = config.get('level', 'INFO')
        logger.set_level(LogLevel.from_string(level))
        
        # Add handlers
        handlers_config = config.get('handlers', [])
        if not handlers_config:
            # Default configuration
            handlers_config = self._get_default_handlers_config(config)
            
        for handler_config in handlers_config:
            handler = self._create_handler(handler_config)
            logger.add_handler(handler)
            
        # Add logger-level filters
        filters_config = config.get('filters', [])
        for filter_config in filters_config:
            filter_obj = self._create_filter(filter_config)
            if filter_obj:
                logger.add_filter(filter_obj)
                
        self._loggers[name] = logger
        return logger
        
    def _get_default_handlers_config(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get default handlers configuration"""
        handlers = []
        
        # Console handler
        console_config = config.get('console', {'enabled': True})
        if console_config.get('enabled', True):
            handler_config = {
                'type': 'console',
                'formatter': {
                    'type': config.get('format', 'colored'),
                    'options': {}
                }
            }
            handlers.append(handler_config)
            
        # File handler
        log_file = config.get('file')
        log_dir = config.get('directory', 'logs')
        
        if log_file or log_dir:
            if log_file:
                filename = log_file
            else:
                os.makedirs(log_dir, exist_ok=True)
                filename = os.path.join(log_dir, 'app.log')
                
            # Check if rotation is configured
            rotation_config = config.get('rotation')
            if rotation_config:
                handler_config = {
                    'type': 'rotating',
                    'filename': filename,
                    'max_bytes': rotation_config.get('max_size', '10MB'),
                    'backup_count': rotation_config.get('backup_count', 5),
                    'formatter': {
                        'type': 'json',
                        'options': {'indent': 2}
                    }
                }
            else:
                handler_config = {
                    'type': 'file',
                    'filename': filename,
                    'formatter': {
                        'type': 'json',
                        'options': {'indent': 2}
                    }
                }
            handlers.append(handler_config)
            
        return handlers
        
    def get_logger(self, name: str) -> Optional[AmzurLogger]:
        """Get an existing logger"""
        return self._loggers.get(name)
        
    def list_loggers(self) -> List[str]:
        """List all configured loggers"""
        return list(self._loggers.keys())
        
    def shutdown(self):
        """Shutdown all loggers and handlers"""
        for logger in self._loggers.values():
            for handler in logger.handlers:
                try:
                    handler.close()
                except Exception:
                    pass
        self._loggers.clear()


def configure_from_dict(config_dict: Dict[str, Any]) -> AmzurLogConfig:
    """Configure AmzurLog from a dictionary"""
    return AmzurLogConfig(config_dict)


def configure_from_file(config_path: str) -> AmzurLogConfig:
    """Configure AmzurLog from a JSON file"""
    return AmzurLogConfig.from_file(config_path)


def configure_from_env(prefix: str = 'AMZURLOG_') -> AmzurLogConfig:
    """Configure AmzurLog from environment variables"""
    return AmzurLogConfig.from_env(prefix)


def quick_setup(
    level: str = 'INFO',
    log_file: Optional[str] = None,
    format_type: str = 'colored',
    console: bool = True
) -> AmzurLogger:
    """Quick setup for a default logger"""
    config_dict = {
        'level': level,
        'format': format_type,
        'console': {'enabled': console}
    }
    
    if log_file:
        config_dict['file'] = log_file
        
    config = AmzurLogConfig(config_dict)
    return config.setup_logger('amzurlog')