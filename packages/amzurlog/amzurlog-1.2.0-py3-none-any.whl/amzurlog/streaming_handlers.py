"""
AmzurLog Streaming Handler
==========================

Handler that integrates event streaming capabilities with the AmzurLog handler system.
"""

import threading
import time
from typing import Optional, Dict, Any, List
from .handlers import BaseHandler
from .core import LogRecord
from .streaming import StreamManager, StreamEvent


class StreamingHandler(BaseHandler):
    """Handler that streams log events to configured destinations"""
    
    def __init__(
        self,
        stream_config: Dict[str, Any],
        level=None,
        buffer_size: int = 1000,
        flush_interval: float = 5.0,
        async_mode: bool = True
    ):
        """
        Initialize streaming handler
        
        Args:
            stream_config: Configuration for stream manager
            level: Log level filter
            buffer_size: Size of internal buffer
            flush_interval: Interval to flush buffer (seconds)
            async_mode: Whether to stream asynchronously
        """
        super().__init__(level)
        self.stream_config = stream_config
        self.buffer_size = buffer_size
        self.flush_interval = flush_interval
        self.async_mode = async_mode
        
        # Initialize stream manager
        self.stream_manager = StreamManager(stream_config)
        
        # Buffer for async mode
        self._buffer: List[StreamEvent] = []
        self._buffer_lock = threading.Lock()
        self._last_flush = time.time()
        
        # Start stream manager
        self.stream_manager.start()
        
        # Start flush timer for async mode
        if async_mode:
            self._start_flush_timer()
    
    def emit(self, formatted_message: str, record: LogRecord):
        """Emit a log record to streams"""
        try:
            # Create stream event
            stream_event = StreamEvent.from_log_record(record)
            
            if self.async_mode:
                # Add to buffer
                with self._buffer_lock:
                    self._buffer.append(stream_event)
                    
                    # Check if buffer needs flushing
                    if len(self._buffer) >= self.buffer_size:
                        self._flush_buffer()
            else:
                # Stream immediately
                self.stream_manager.stream_event(stream_event)
                
        except Exception as e:
            self.handle_error(e, record)
    
    def _start_flush_timer(self):
        """Start the buffer flush timer"""
        def flush_timer():
            while True:
                try:
                    time.sleep(self.flush_interval)
                    current_time = time.time()
                    
                    with self._buffer_lock:
                        if (self._buffer and 
                            current_time - self._last_flush >= self.flush_interval):
                            self._flush_buffer()
                            
                except Exception as e:
                    print(f"Error in flush timer: {e}")
        
        timer_thread = threading.Thread(target=flush_timer, daemon=True)
        timer_thread.start()
    
    def _flush_buffer(self):
        """Flush the current buffer"""
        if not self._buffer:
            return
            
        # Move current buffer to local variable
        events_to_send = self._buffer.copy()
        self._buffer.clear()
        self._last_flush = time.time()
        
        # Send events
        for event in events_to_send:
            self.stream_manager.stream_event(event)
    
    def flush(self):
        """Manually flush the buffer"""
        if self.async_mode:
            with self._buffer_lock:
                self._flush_buffer()
    
    def close(self):
        """Close the streaming handler"""
        # Flush any remaining events
        self.flush()
        
        # Stop stream manager
        self.stream_manager.stop()
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get streaming metrics"""
        base_metrics = self.stream_manager.get_metrics()
        
        if self.async_mode:
            with self._buffer_lock:
                base_metrics['buffer_size'] = len(self._buffer)
                base_metrics['last_flush'] = self._last_flush
        
        return base_metrics
    
    def get_status(self) -> Dict[str, Any]:
        """Get streaming status"""
        return self.stream_manager.get_status()


class ELKStreamingHandler(StreamingHandler):
    """Specialized handler for ELK Stack integration"""
    
    def __init__(
        self,
        elasticsearch_hosts: List[str] = None,
        index_pattern: str = "amzurlog-{date}",
        level=None,
        **kwargs
    ):
        """
        Initialize ELK streaming handler
        
        Args:
            elasticsearch_hosts: List of Elasticsearch hosts
            index_pattern: Index pattern for Elasticsearch
            level: Log level filter
            **kwargs: Additional arguments for StreamingHandler
        """
        elasticsearch_hosts = elasticsearch_hosts or ['localhost:9200']
        
        stream_config = {
            'batch_size': kwargs.get('batch_size', 100),
            'batch_timeout': kwargs.get('batch_timeout', 5.0),
            'queue_size': kwargs.get('queue_size', 10000),
            'worker_threads': kwargs.get('worker_threads', 2),
            'streamers': {
                'elasticsearch': {
                    'enabled': True,
                    'type': 'elasticsearch',
                    'hosts': elasticsearch_hosts,
                    'index_pattern': index_pattern,
                    'timeout': kwargs.get('timeout', 30),
                    'max_retries': kwargs.get('max_retries', 3)
                }
            }
        }
        
        # Add authentication if provided
        if 'username' in kwargs and 'password' in kwargs:
            stream_config['streamers']['elasticsearch']['username'] = kwargs['username']
            stream_config['streamers']['elasticsearch']['password'] = kwargs['password']
        
        # Add SSL config if provided
        if kwargs.get('use_ssl', False):
            stream_config['streamers']['elasticsearch']['use_ssl'] = True
            stream_config['streamers']['elasticsearch']['verify_certs'] = kwargs.get('verify_certs', True)
            if 'ca_certs' in kwargs:
                stream_config['streamers']['elasticsearch']['ca_certs'] = kwargs['ca_certs']
        
        super().__init__(stream_config, level, **kwargs)


class GrafanaStreamingHandler(StreamingHandler):
    """Specialized handler for Grafana integration via various backends"""
    
    def __init__(
        self,
        backend: str = 'prometheus',
        backend_config: Dict[str, Any] = None,
        level=None,
        **kwargs
    ):
        """
        Initialize Grafana streaming handler
        
        Args:
            backend: Backend type (prometheus, influxdb, loki)
            backend_config: Backend-specific configuration
            level: Log level filter
            **kwargs: Additional arguments for StreamingHandler
        """
        backend_config = backend_config or {}
        
        if backend == 'prometheus':
            # For Prometheus, we'll use HTTP endpoint
            stream_config = self._create_prometheus_config(backend_config, **kwargs)
        elif backend == 'influxdb':
            # For InfluxDB, we'll use HTTP API
            stream_config = self._create_influxdb_config(backend_config, **kwargs)
        elif backend == 'loki':
            # For Grafana Loki, we'll use HTTP API
            stream_config = self._create_loki_config(backend_config, **kwargs)
        else:
            raise ValueError(f"Unsupported Grafana backend: {backend}")
        
        super().__init__(stream_config, level, **kwargs)
    
    def _create_prometheus_config(self, backend_config: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Create configuration for Prometheus pushgateway"""
        url = backend_config.get('pushgateway_url', 'http://localhost:9091/metrics/job/amzurlog')
        
        return {
            'batch_size': kwargs.get('batch_size', 50),
            'batch_timeout': kwargs.get('batch_timeout', 10.0),
            'queue_size': kwargs.get('queue_size', 5000),
            'worker_threads': kwargs.get('worker_threads', 1),
            'streamers': {
                'prometheus': {
                    'enabled': True,
                    'type': 'http',
                    'url': url,
                    'timeout': kwargs.get('timeout', 30),
                    'headers': {
                        'Content-Type': 'text/plain'
                    }
                }
            }
        }
    
    def _create_influxdb_config(self, backend_config: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Create configuration for InfluxDB"""
        host = backend_config.get('host', 'localhost')
        port = backend_config.get('port', 8086)
        database = backend_config.get('database', 'amzurlog')
        
        url = f"http://{host}:{port}/write?db={database}"
        
        config = {
            'batch_size': kwargs.get('batch_size', 100),
            'batch_timeout': kwargs.get('batch_timeout', 5.0),
            'queue_size': kwargs.get('queue_size', 10000),
            'worker_threads': kwargs.get('worker_threads', 2),
            'streamers': {
                'influxdb': {
                    'enabled': True,
                    'type': 'http',
                    'url': url,
                    'timeout': kwargs.get('timeout', 30),
                    'headers': {
                        'Content-Type': 'application/x-www-form-urlencoded'
                    }
                }
            }
        }
        
        # Add authentication if provided
        if 'username' in backend_config and 'password' in backend_config:
            config['streamers']['influxdb']['auth'] = {
                'type': 'basic',
                'username': backend_config['username'],
                'password': backend_config['password']
            }
        
        return config
    
    def _create_loki_config(self, backend_config: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Create configuration for Grafana Loki"""
        url = backend_config.get('url', 'http://localhost:3100/loki/api/v1/push')
        
        config = {
            'batch_size': kwargs.get('batch_size', 100),
            'batch_timeout': kwargs.get('batch_timeout', 5.0),
            'queue_size': kwargs.get('queue_size', 10000),
            'worker_threads': kwargs.get('worker_threads', 2),
            'streamers': {
                'loki': {
                    'enabled': True,
                    'type': 'http',
                    'url': url,
                    'timeout': kwargs.get('timeout', 30),
                    'headers': {
                        'Content-Type': 'application/json'
                    }
                }
            }
        }
        
        # Add authentication if provided
        if 'username' in backend_config and 'password' in backend_config:
            config['streamers']['loki']['auth'] = {
                'type': 'basic',
                'username': backend_config['username'],
                'password': backend_config['password']
            }
        elif 'bearer_token' in backend_config:
            config['streamers']['loki']['auth'] = {
                'type': 'bearer',
                'token': backend_config['bearer_token']
            }
        
        return config


class KafkaStreamingHandler(StreamingHandler):
    """Specialized handler for Kafka streaming"""
    
    def __init__(
        self,
        bootstrap_servers: List[str] = None,
        topic: str = 'amzurlog-events',
        level=None,
        **kwargs
    ):
        """
        Initialize Kafka streaming handler
        
        Args:
            bootstrap_servers: List of Kafka bootstrap servers
            topic: Kafka topic name
            level: Log level filter
            **kwargs: Additional arguments for StreamingHandler
        """
        bootstrap_servers = bootstrap_servers or ['localhost:9092']
        
        stream_config = {
            'batch_size': kwargs.get('batch_size', 100),
            'batch_timeout': kwargs.get('batch_timeout', 5.0),
            'queue_size': kwargs.get('queue_size', 10000),
            'worker_threads': kwargs.get('worker_threads', 2),
            'streamers': {
                'kafka': {
                    'enabled': True,
                    'type': 'kafka',
                    'bootstrap_servers': bootstrap_servers,
                    'topic': topic,
                    'retries': kwargs.get('retries', 3),
                    'batch_size': kwargs.get('kafka_batch_size', 16384),
                    'linger_ms': kwargs.get('linger_ms', 10),
                    'compression_type': kwargs.get('compression_type', 'gzip')
                }
            }
        }
        
        # Add additional Kafka configuration
        kafka_config = kwargs.get('kafka_config', {})
        if kafka_config:
            stream_config['streamers']['kafka']['kafka_config'] = kafka_config
        
        super().__init__(stream_config, level, **kwargs)


class RedisStreamingHandler(StreamingHandler):
    """Specialized handler for Redis Streams"""
    
    def __init__(
        self,
        redis_host: str = 'localhost',
        redis_port: int = 6379,
        redis_db: int = 0,
        stream_name: str = 'amzurlog:events',
        level=None,
        **kwargs
    ):
        """
        Initialize Redis streaming handler
        
        Args:
            redis_host: Redis server host
            redis_port: Redis server port
            redis_db: Redis database number
            stream_name: Redis stream name
            level: Log level filter
            **kwargs: Additional arguments for StreamingHandler
        """
        stream_config = {
            'batch_size': kwargs.get('batch_size', 100),
            'batch_timeout': kwargs.get('batch_timeout', 5.0),
            'queue_size': kwargs.get('queue_size', 10000),
            'worker_threads': kwargs.get('worker_threads', 2),
            'streamers': {
                'redis': {
                    'enabled': True,
                    'type': 'redis',
                    'host': redis_host,
                    'port': redis_port,
                    'db': redis_db,
                    'stream_name': stream_name
                }
            }
        }
        
        # Add password if provided
        if 'password' in kwargs:
            stream_config['streamers']['redis']['password'] = kwargs['password']
        
        # Add additional Redis configuration
        redis_config = kwargs.get('redis_config', {})
        if redis_config:
            stream_config['streamers']['redis']['redis_config'] = redis_config
        
        super().__init__(stream_config, level, **kwargs)


class MultiStreamingHandler(StreamingHandler):
    """Handler that can stream to multiple destinations simultaneously"""
    
    def __init__(
        self,
        streamers_config: Dict[str, Dict[str, Any]],
        level=None,
        **kwargs
    ):
        """
        Initialize multi-streaming handler
        
        Args:
            streamers_config: Configuration for multiple streamers
            level: Log level filter
            **kwargs: Additional arguments for StreamingHandler
        """
        stream_config = {
            'batch_size': kwargs.get('batch_size', 100),
            'batch_timeout': kwargs.get('batch_timeout', 5.0),
            'queue_size': kwargs.get('queue_size', 10000),
            'worker_threads': kwargs.get('worker_threads', 2),
            'streamers': streamers_config
        }
        
        super().__init__(stream_config, level, **kwargs)