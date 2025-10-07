"""
AmzurLog Exception Tracking Configuration
==========================================

Configuration templates and helpers for exception tracking integrations.
"""

from typing import Dict, Any, Optional, List


def get_sentry_config(
    dsn: str,
    environment: str = "production",
    traces_sample_rate: float = 0.1,
    profiles_sample_rate: float = 0.1,
    send_default_pii: bool = False,
    **kwargs
) -> Dict[str, Any]:
    """
    Get configuration for Sentry integration
    
    Args:
        dsn: Sentry DSN
        environment: Environment name
        traces_sample_rate: Performance monitoring sample rate
        profiles_sample_rate: Profiling sample rate
        send_default_pii: Whether to send personally identifiable information
        **kwargs: Additional Sentry configuration
    
    Returns:
        Configuration dictionary for Sentry
    """
    config = {
        'type': 'exception',
        'class': 'SentryHandler',
        'sentry_dsn': dsn,
        'environment': environment,
        'traces_sample_rate': traces_sample_rate,
        'profiles_sample_rate': profiles_sample_rate,
        'send_default_pii': send_default_pii,
        'max_breadcrumbs': kwargs.get('max_breadcrumbs', 50),
        'debug': kwargs.get('debug', False),
        'attach_stacktrace': kwargs.get('attach_stacktrace', True),
        'auto_capture': kwargs.get('auto_capture', True),
        'capture_locals': kwargs.get('capture_locals', True),
        'capture_globals': kwargs.get('capture_globals', False)
    }
    
    # Add additional Sentry-specific config
    if 'release' in kwargs:
        config['release'] = kwargs['release']
    if 'server_name' in kwargs:
        config['server_name'] = kwargs['server_name']
    if 'before_send' in kwargs:
        config['before_send'] = kwargs['before_send']
    
    return config


def get_rollbar_config(
    access_token: str,
    environment: str = "production",
    **kwargs
) -> Dict[str, Any]:
    """
    Get configuration for Rollbar integration
    
    Args:
        access_token: Rollbar access token
        environment: Environment name
        **kwargs: Additional Rollbar configuration
    
    Returns:
        Configuration dictionary for Rollbar
    """
    config = {
        'type': 'exception',
        'class': 'RollbarHandler',
        'rollbar_token': access_token,
        'environment': environment,
        'auto_capture': kwargs.get('auto_capture', True),
        'capture_locals': kwargs.get('capture_locals', True),
        'capture_globals': kwargs.get('capture_globals', False)
    }
    
    # Add Rollbar-specific config
    if 'code_version' in kwargs:
        config['code_version'] = kwargs['code_version']
    if 'root' in kwargs:
        config['root'] = kwargs['root']
    if 'branch' in kwargs:
        config['branch'] = kwargs['branch']
    
    return config


def get_webhook_exception_config(
    webhook_url: str,
    headers: Optional[Dict[str, str]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Get configuration for webhook exception integration
    
    Args:
        webhook_url: Webhook URL
        headers: HTTP headers
        **kwargs: Additional configuration
    
    Returns:
        Configuration dictionary for webhook integration
    """
    config = {
        'type': 'exception',
        'class': 'ExceptionHandler',
        'integrations': {
            'webhook': {
                'type': 'webhook',
                'url': webhook_url,
                'headers': headers or {}
            }
        },
        'auto_capture': kwargs.get('auto_capture', True),
        'capture_locals': kwargs.get('capture_locals', True),
        'capture_globals': kwargs.get('capture_globals', False)
    }
    
    return config


def get_multi_exception_config(
    integrations: Dict[str, Dict[str, Any]],
    **kwargs
) -> Dict[str, Any]:
    """
    Get configuration for multiple exception tracking services
    
    Args:
        integrations: Dictionary of integration configurations
        **kwargs: Additional configuration
    
    Returns:
        Configuration dictionary for multi-service exception tracking
    """
    config = {
        'type': 'exception',
        'class': 'ExceptionHandler',
        'integrations': integrations,
        'auto_capture': kwargs.get('auto_capture', True),
        'capture_locals': kwargs.get('capture_locals', True),
        'capture_globals': kwargs.get('capture_globals', False),
        'rate_limit': {
            'max_exceptions': kwargs.get('max_exceptions', 100),
            'time_window': kwargs.get('time_window', 3600)
        }
    }
    
    return config


# Example configurations
EXAMPLE_EXCEPTION_CONFIGS = {
    'sentry_basic': {
        'description': 'Basic Sentry error tracking',
        'config': {
            'handlers': [
                {
                    'type': 'console',
                    'level': 'INFO',
                    'formatter': {'type': 'colored'}
                },
                get_sentry_config(
                    dsn='https://your-dsn@sentry.io/project-id',
                    environment='production'
                )
            ]
        }
    },
    
    'sentry_advanced': {
        'description': 'Advanced Sentry with performance monitoring',
        'config': {
            'handlers': [
                {
                    'type': 'console',
                    'level': 'WARNING',
                    'formatter': {'type': 'colored'}
                },
                {
                    'type': 'file',
                    'filename': 'logs/app.log',
                    'formatter': {'type': 'json'}
                },
                get_sentry_config(
                    dsn='https://your-dsn@sentry.io/project-id',
                    environment='production',
                    traces_sample_rate=1.0,
                    profiles_sample_rate=1.0,
                    release='1.0.0',
                    capture_locals=True,
                    max_breadcrumbs=100
                )
            ]
        }
    },
    
    'rollbar_basic': {
        'description': 'Basic Rollbar error tracking',
        'config': {
            'handlers': [
                {
                    'type': 'console',
                    'level': 'INFO',
                    'formatter': {'type': 'colored'}
                },
                get_rollbar_config(
                    access_token='your-rollbar-token',
                    environment='production'
                )
            ]
        }
    },
    
    'webhook_integration': {
        'description': 'Custom webhook exception reporting',
        'config': {
            'handlers': [
                {
                    'type': 'console',
                    'level': 'INFO',
                    'formatter': {'type': 'colored'}
                },
                get_webhook_exception_config(
                    webhook_url='https://your-webhook.example.com/exceptions',
                    headers={'Authorization': 'Bearer your-token'}
                )
            ]
        }
    },
    
    'multi_service': {
        'description': 'Multiple exception tracking services',
        'config': {
            'handlers': [
                {
                    'type': 'console',
                    'level': 'WARNING',
                    'formatter': {'type': 'colored'}
                },
                {
                    'type': 'rotating',
                    'filename': 'logs/app.log',
                    'max_bytes': '50MB',
                    'backup_count': 5,
                    'formatter': {'type': 'json'}
                },
                get_multi_exception_config(
                    integrations={
                        'sentry': {
                            'type': 'sentry',
                            'dsn': 'https://your-dsn@sentry.io/project-id',
                            'environment': 'production'
                        },
                        'webhook': {
                            'type': 'webhook',
                            'url': 'https://your-webhook.example.com/exceptions'
                        }
                    },
                    max_exceptions=50,
                    time_window=1800
                )
            ]
        }
    },
    
    'development': {
        'description': 'Development environment with detailed tracking',
        'config': {
            'handlers': [
                {
                    'type': 'console',
                    'level': 'DEBUG',
                    'formatter': {'type': 'colored'}
                },
                get_sentry_config(
                    dsn='https://your-dsn@sentry.io/project-id',
                    environment='development',
                    debug=True,
                    traces_sample_rate=1.0,
                    capture_locals=True,
                    capture_globals=True,
                    send_default_pii=True
                )
            ]
        }
    },
    
    'production_secure': {
        'description': 'Production environment with security focus',
        'config': {
            'handlers': [
                {
                    'type': 'console',
                    'level': 'ERROR',
                    'formatter': {'type': 'json'}
                },
                {
                    'type': 'rotating',
                    'filename': 'logs/errors.log',
                    'max_bytes': '100MB',
                    'backup_count': 10,
                    'level': 'ERROR',
                    'formatter': {'type': 'json'}
                },
                get_sentry_config(
                    dsn='https://your-dsn@sentry.io/project-id',
                    environment='production',
                    traces_sample_rate=0.01,
                    profiles_sample_rate=0.01,
                    send_default_pii=False,
                    capture_locals=False,
                    capture_globals=False,
                    max_breadcrumbs=25
                )
            ]
        }
    }
}


def get_example_exception_config(config_name: str) -> Dict[str, Any]:
    """
    Get an example exception configuration by name
    
    Args:
        config_name: Name of the example configuration
    
    Returns:
        Example configuration dictionary
    
    Raises:
        KeyError: If config_name is not found
    """
    if config_name not in EXAMPLE_EXCEPTION_CONFIGS:
        available = ', '.join(EXAMPLE_EXCEPTION_CONFIGS.keys())
        raise KeyError(f"Unknown config '{config_name}'. Available: {available}")
    
    return EXAMPLE_EXCEPTION_CONFIGS[config_name]['config']


def list_example_exception_configs() -> Dict[str, str]:
    """
    List all available example exception configurations
    
    Returns:
        Dictionary mapping config names to descriptions
    """
    return {name: config['description'] for name, config in EXAMPLE_EXCEPTION_CONFIGS.items()}


def create_exception_config_template() -> str:
    """
    Create a template configuration file for exception tracking
    
    Returns:
        JSON configuration template as string
    """
    import json
    
    template = {
        "level": "INFO",
        "handlers": [
            {
                "type": "console",
                "level": "INFO",
                "formatter": {
                    "type": "colored"
                }
            },
            {
                "type": "exception",
                "class": "SentryHandler",
                "sentry_dsn": "https://your-dsn@sentry.io/project-id",
                "environment": "production",
                "traces_sample_rate": 0.1,
                "auto_capture": True,
                "capture_locals": True,
                "level": "ERROR"
            }
        ]
    }
    
    return json.dumps(template, indent=2)


def validate_sentry_dsn(dsn: str) -> bool:
    """
    Validate Sentry DSN format
    
    Args:
        dsn: Sentry DSN to validate
    
    Returns:
        True if DSN format is valid
    """
    if not dsn or not isinstance(dsn, str):
        return False
    
    # Basic DSN format validation
    if not dsn.startswith(('https://', 'http://')):
        return False
    
    if '@sentry.io/' not in dsn and '@sentry.' not in dsn:
        return False
    
    return True


def get_environment_specific_config(
    environment: str,
    service_configs: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Get environment-specific exception tracking configuration
    
    Args:
        environment: Environment name (development, staging, production)
        service_configs: Service-specific configurations
    
    Returns:
        Environment-optimized configuration
    """
    base_config = {
        'auto_capture': True,
        'capture_locals': environment != 'production',
        'capture_globals': environment == 'development'
    }
    
    if environment == 'development':
        base_config.update({
            'debug': True,
            'traces_sample_rate': 1.0,
            'profiles_sample_rate': 1.0,
            'send_default_pii': True,
            'max_breadcrumbs': 100
        })
    elif environment == 'staging':
        base_config.update({
            'debug': False,
            'traces_sample_rate': 0.5,
            'profiles_sample_rate': 0.1,
            'send_default_pii': False,
            'max_breadcrumbs': 50
        })
    else:  # production
        base_config.update({
            'debug': False,
            'traces_sample_rate': 0.01,
            'profiles_sample_rate': 0.001,
            'send_default_pii': False,
            'max_breadcrumbs': 25,
            'rate_limit': {
                'max_exceptions': 100,
                'time_window': 3600
            }
        })
    
    # Merge with service-specific configs
    for service, config in service_configs.items():
        base_config[service] = {**base_config.get(service, {}), **config}
    
    return base_config
