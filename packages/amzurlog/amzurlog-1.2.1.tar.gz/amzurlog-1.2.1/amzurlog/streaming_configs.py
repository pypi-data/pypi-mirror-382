"""
AmzurLog Streaming Configuration Templates
==========================================

This module provides configuration templates and examples for setting up
event streaming with various monitoring platforms.
"""

from typing import Dict, Any, List


def get_elk_config(
    elasticsearch_hosts: List[str] = None,
    index_pattern: str = "amzurlog-{date}",
    username: str = None,
    password: str = None,
    use_ssl: bool = False,
    **kwargs
) -> Dict[str, Any]:
    """
    Get configuration for ELK Stack integration
    
    Args:
        elasticsearch_hosts: List of Elasticsearch hosts
        index_pattern: Index pattern for logs
        username: Elasticsearch username
        password: Elasticsearch password
        use_ssl: Whether to use SSL/TLS
        **kwargs: Additional configuration options
    
    Returns:
        Configuration dictionary for ELK integration
    """
    elasticsearch_hosts = elasticsearch_hosts or ['localhost:9200']
    
    config = {
        'type': 'streaming',
        'class': 'ELKStreamingHandler',
        'elasticsearch_hosts': elasticsearch_hosts,
        'index_pattern': index_pattern,
        'batch_size': kwargs.get('batch_size', 100),
        'batch_timeout': kwargs.get('batch_timeout', 5.0),
        'timeout': kwargs.get('timeout', 30),
        'max_retries': kwargs.get('max_retries', 3),
        'formatter': {
            'type': 'json',
            'options': {
                'indent': None,
                'ensure_ascii': False
            }
        }
    }
    
    if username and password:
        config['username'] = username
        config['password'] = password
    
    if use_ssl:
        config['use_ssl'] = True
        config['verify_certs'] = kwargs.get('verify_certs', True)
        if 'ca_certs' in kwargs:
            config['ca_certs'] = kwargs['ca_certs']
    
    return config


def get_grafana_loki_config(
    loki_url: str = "http://localhost:3100/loki/api/v1/push",
    username: str = None,
    password: str = None,
    bearer_token: str = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Get configuration for Grafana Loki integration
    
    Args:
        loki_url: Grafana Loki push endpoint URL
        username: Basic auth username
        password: Basic auth password
        bearer_token: Bearer token for authentication
        **kwargs: Additional configuration options
    
    Returns:
        Configuration dictionary for Grafana Loki
    """
    config = {
        'type': 'streaming',
        'class': 'GrafanaStreamingHandler',
        'backend': 'loki',
        'backend_config': {
            'url': loki_url
        },
        'batch_size': kwargs.get('batch_size', 100),
        'batch_timeout': kwargs.get('batch_timeout', 5.0),
        'timeout': kwargs.get('timeout', 30),
        'formatter': {
            'type': 'json',
            'options': {
                'indent': None,
                'ensure_ascii': False
            }
        }
    }
    
    if username and password:
        config['backend_config']['username'] = username
        config['backend_config']['password'] = password
    elif bearer_token:
        config['backend_config']['bearer_token'] = bearer_token
    
    return config


def get_kafka_config(
    bootstrap_servers: List[str] = None,
    topic: str = 'amzurlog-events',
    security_config: Dict[str, Any] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Get configuration for Kafka streaming
    
    Args:
        bootstrap_servers: List of Kafka bootstrap servers
        topic: Kafka topic name
        security_config: Security configuration for Kafka
        **kwargs: Additional configuration options
    
    Returns:
        Configuration dictionary for Kafka streaming
    """
    bootstrap_servers = bootstrap_servers or ['localhost:9092']
    
    config = {
        'type': 'streaming',
        'class': 'KafkaStreamingHandler',
        'bootstrap_servers': bootstrap_servers,
        'topic': topic,
        'batch_size': kwargs.get('batch_size', 100),
        'batch_timeout': kwargs.get('batch_timeout', 5.0),
        'retries': kwargs.get('retries', 3),
        'compression_type': kwargs.get('compression_type', 'gzip'),
        'formatter': {
            'type': 'json',
            'options': {
                'indent': None,
                'ensure_ascii': False
            }
        }
    }
    
    if security_config:
        config['kafka_config'] = security_config
    
    return config


def get_redis_config(
    redis_host: str = 'localhost',
    redis_port: int = 6379,
    redis_db: int = 0,
    stream_name: str = 'amzurlog:events',
    password: str = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Get configuration for Redis Streams
    
    Args:
        redis_host: Redis server host
        redis_port: Redis server port
        redis_db: Redis database number
        stream_name: Redis stream name
        password: Redis password
        **kwargs: Additional configuration options
    
    Returns:
        Configuration dictionary for Redis streaming
    """
    config = {
        'type': 'streaming',
        'class': 'RedisStreamingHandler',
        'redis_host': redis_host,
        'redis_port': redis_port,
        'redis_db': redis_db,
        'stream_name': stream_name,
        'batch_size': kwargs.get('batch_size', 100),
        'batch_timeout': kwargs.get('batch_timeout', 5.0),
        'formatter': {
            'type': 'json',
            'options': {
                'indent': None,
                'ensure_ascii': False
            }
        }
    }
    
    if password:
        config['password'] = password
    
    return config


def get_multi_streaming_config(
    destinations: List[str],
    configs: Dict[str, Dict[str, Any]],
    **kwargs
) -> Dict[str, Any]:
    """
    Get configuration for multi-destination streaming
    
    Args:
        destinations: List of destination types
        configs: Configuration for each destination
        **kwargs: Additional configuration options
    
    Returns:
        Configuration dictionary for multi-streaming
    """
    streamers_config = {}
    
    for dest in destinations:
        if dest in configs:
            streamers_config[dest] = configs[dest]
            streamers_config[dest]['enabled'] = True
    
    config = {
        'type': 'streaming',
        'class': 'MultiStreamingHandler',
        'streamers_config': streamers_config,
        'batch_size': kwargs.get('batch_size', 100),
        'batch_timeout': kwargs.get('batch_timeout', 5.0),
        'formatter': {
            'type': 'json',
            'options': {
                'indent': None,
                'ensure_ascii': False
            }
        }
    }
    
    return config


# Example configurations
EXAMPLE_CONFIGS = {
    'elk_stack': {
        'description': 'Complete ELK Stack configuration',
        'config': {
            'handlers': [
                {
                    'type': 'console',
                    'level': 'INFO',
                    'formatter': {
                        'type': 'colored',
                        'options': {}
                    }
                },
                get_elk_config(
                    elasticsearch_hosts=['localhost:9200'],
                    index_pattern='amzurlog-{date}',
                    batch_size=50,
                    batch_timeout=10.0
                )
            ]
        }
    },
    
    'grafana_loki': {
        'description': 'Grafana Loki integration',
        'config': {
            'handlers': [
                {
                    'type': 'console',
                    'level': 'INFO',
                    'formatter': {
                        'type': 'colored',
                        'options': {}
                    }
                },
                get_grafana_loki_config(
                    loki_url='http://localhost:3100/loki/api/v1/push',
                    batch_size=100,
                    batch_timeout=5.0
                )
            ]
        }
    },
    
    'kafka_streaming': {
        'description': 'Kafka event streaming',
        'config': {
            'handlers': [
                {
                    'type': 'console',
                    'level': 'INFO',
                    'formatter': {
                        'type': 'colored',
                        'options': {}
                    }
                },
                get_kafka_config(
                    bootstrap_servers=['localhost:9092'],
                    topic='application-logs',
                    compression_type='gzip'
                )
            ]
        }
    },
    
    'redis_streaming': {
        'description': 'Redis Streams integration',
        'config': {
            'handlers': [
                {
                    'type': 'console',
                    'level': 'INFO',
                    'formatter': {
                        'type': 'colored',
                        'options': {}
                    }
                },
                get_redis_config(
                    redis_host='localhost',
                    redis_port=6379,
                    stream_name='app:logs'
                )
            ]
        }
    },
    
    'multi_destination': {
        'description': 'Multiple streaming destinations',
        'config': {
            'handlers': [
                {
                    'type': 'console',
                    'level': 'INFO',
                    'formatter': {
                        'type': 'colored',
                        'options': {}
                    }
                },
                get_multi_streaming_config(
                    destinations=['elasticsearch', 'kafka', 'redis'],
                    configs={
                        'elasticsearch': {
                            'type': 'elasticsearch',
                            'hosts': ['localhost:9200'],
                            'index_pattern': 'logs-{date}'
                        },
                        'kafka': {
                            'type': 'kafka',
                            'bootstrap_servers': ['localhost:9092'],
                            'topic': 'application-logs'
                        },
                        'redis': {
                            'type': 'redis',
                            'host': 'localhost',
                            'port': 6379,
                            'stream_name': 'app:logs'
                        }
                    }
                )
            ]
        }
    },
    
    'production_elk': {
        'description': 'Production ELK Stack with security',
        'config': {
            'handlers': [
                {
                    'type': 'console',
                    'level': 'WARNING',
                    'formatter': {
                        'type': 'colored',
                        'options': {}
                    }
                },
                {
                    'type': 'rotating',
                    'filename': 'logs/app.log',
                    'max_bytes': '50MB',
                    'backup_count': 10,
                    'formatter': {
                        'type': 'json',
                        'options': {'indent': 2}
                    }
                },
                get_elk_config(
                    elasticsearch_hosts=[
                        'elasticsearch-1.example.com:9200',
                        'elasticsearch-2.example.com:9200',
                        'elasticsearch-3.example.com:9200'
                    ],
                    index_pattern='production-logs-{date}',
                    username='elastic',
                    password='changeme',
                    use_ssl=True,
                    verify_certs=True,
                    batch_size=200,
                    batch_timeout=30.0,
                    timeout=60
                )
            ]
        }
    }
}


def get_example_config(config_name: str) -> Dict[str, Any]:
    """
    Get an example configuration by name
    
    Args:
        config_name: Name of the example configuration
    
    Returns:
        Example configuration dictionary
    
    Raises:
        KeyError: If config_name is not found
    """
    if config_name not in EXAMPLE_CONFIGS:
        available = ', '.join(EXAMPLE_CONFIGS.keys())
        raise KeyError(f"Unknown config '{config_name}'. Available: {available}")
    
    return EXAMPLE_CONFIGS[config_name]['config']


def list_example_configs() -> Dict[str, str]:
    """
    List all available example configurations
    
    Returns:
        Dictionary mapping config names to descriptions
    """
    return {name: config['description'] for name, config in EXAMPLE_CONFIGS.items()}


def create_streaming_config_template() -> str:
    """
    Create a template configuration file for streaming
    
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
                "type": "streaming",
                "class": "ELKStreamingHandler",
                "elasticsearch_hosts": ["localhost:9200"],
                "index_pattern": "amzurlog-{date}",
                "batch_size": 100,
                "batch_timeout": 5.0,
                "level": "INFO",
                "formatter": {
                    "type": "json",
                    "options": {
                        "indent": None
                    }
                }
            }
        ]
    }
    
    return json.dumps(template, indent=2)