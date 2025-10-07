"""
AmzurLog Event Streaming
========================

This module provides event streaming capabilities for real-time log monitoring
and integration with platforms like ELK Stack, Grafana, and other monitoring systems.

Features:
- Multiple streaming destinations (Kafka, Redis, HTTP endpoints)
- Batching and buffering for performance
- Retry mechanisms with exponential backoff
- Circuit breaker pattern for fault tolerance
- Metrics collection for monitoring
- ELK Stack integration
- Grafana integration
"""

import json
import time
import threading
import queue
import logging
import requests
from abc import ABC, abstractmethod
from collections import deque
from typing import Dict, List, Any, Optional, Callable, Union
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, Future
from dataclasses import dataclass, asdict
from enum import Enum

from .core import LogRecord, LogLevel


class StreamDestinationType(Enum):
    """Types of streaming destinations"""
    KAFKA = "kafka"
    REDIS = "redis"
    HTTP = "http"
    ELASTICSEARCH = "elasticsearch"
    WEBSOCKET = "websocket"
    FILE = "file"


class StreamStatus(Enum):
    """Stream status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    CIRCUIT_OPEN = "circuit_open"


@dataclass
class StreamEvent:
    """Represents a streaming event"""
    id: str
    timestamp: datetime
    level: str
    logger: str
    message: str
    extra: Dict[str, Any]
    source: str = "amzurlog"
    version: str = "1.0.0"
    
    @classmethod
    def from_log_record(cls, record: LogRecord, event_id: Optional[str] = None) -> 'StreamEvent':
        """Create StreamEvent from LogRecord"""
        import uuid
        return cls(
            id=event_id or str(uuid.uuid4()),
            timestamp=record.timestamp,
            level=record.level.name,
            logger=record.logger_name,
            message=record.message,
            extra=record.extra.copy()
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        return result
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), default=str)


@dataclass
class StreamMetrics:
    """Stream metrics for monitoring"""
    events_sent: int = 0
    events_failed: int = 0
    events_retried: int = 0
    bytes_sent: int = 0
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    average_latency: float = 0.0
    circuit_breaker_trips: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = asdict(self)
        if self.last_success:
            result['last_success'] = self.last_success.isoformat()
        if self.last_failure:
            result['last_failure'] = self.last_failure.isoformat()
        return result


class CircuitBreaker:
    """Circuit breaker pattern implementation"""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = StreamStatus.ACTIVE
        self._lock = threading.Lock()
    
    def call(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        with self._lock:
            if self.state == StreamStatus.CIRCUIT_OPEN:
                if time.time() - self.last_failure_time > self.timeout:
                    self.state = StreamStatus.ACTIVE
                    self.failure_count = 0
                else:
                    raise Exception("Circuit breaker is open")
        
        try:
            result = func(*args, **kwargs)
            with self._lock:
                self.failure_count = 0
                self.state = StreamStatus.ACTIVE
            return result
        except Exception as e:
            with self._lock:
                self.failure_count += 1
                self.last_failure_time = time.time()
                if self.failure_count >= self.failure_threshold:
                    self.state = StreamStatus.CIRCUIT_OPEN
            raise e
    
    def get_state(self) -> StreamStatus:
        """Get current circuit breaker state"""
        return self.state


class BaseStreamer(ABC):
    """Base class for all streamers"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.metrics = StreamMetrics()
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=config.get('circuit_breaker_threshold', 5),
            timeout=config.get('circuit_breaker_timeout', 60)
        )
        self.status = StreamStatus.INACTIVE
        self._lock = threading.Lock()
    
    @abstractmethod
    def connect(self) -> bool:
        """Connect to the streaming destination"""
        pass
    
    @abstractmethod
    def send_event(self, event: StreamEvent) -> bool:
        """Send a single event"""
        pass
    
    @abstractmethod
    def send_batch(self, events: List[StreamEvent]) -> bool:
        """Send a batch of events"""
        pass
    
    @abstractmethod
    def disconnect(self):
        """Disconnect from the streaming destination"""
        pass
    
    def get_metrics(self) -> StreamMetrics:
        """Get streaming metrics"""
        return self.metrics
    
    def get_status(self) -> StreamStatus:
        """Get streamer status"""
        return self.status


class KafkaStreamer(BaseStreamer):
    """Kafka event streamer"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.producer = None
        self.topic = config.get('topic', 'amzurlog-events')
        
    def connect(self) -> bool:
        """Connect to Kafka"""
        try:
            # Try to import kafka-python
            from kafka import KafkaProducer
            
            kafka_config = {
                'bootstrap_servers': self.config.get('bootstrap_servers', ['localhost:9092']),
                'value_serializer': lambda v: json.dumps(v).encode('utf-8'),
                'key_serializer': lambda k: k.encode('utf-8') if k else None,
                'retries': self.config.get('retries', 3),
                'batch_size': self.config.get('batch_size', 16384),
                'linger_ms': self.config.get('linger_ms', 10),
                'compression_type': self.config.get('compression_type', 'gzip')
            }
            
            # Add any additional kafka config
            kafka_config.update(self.config.get('kafka_config', {}))
            
            self.producer = KafkaProducer(**kafka_config)
            self.status = StreamStatus.ACTIVE
            return True
            
        except ImportError:
            logging.error("kafka-python is not installed. Install with: pip install kafka-python")
            self.status = StreamStatus.ERROR
            return False
        except Exception as e:
            logging.error(f"Failed to connect to Kafka: {e}")
            self.status = StreamStatus.ERROR
            return False
    
    def send_event(self, event: StreamEvent) -> bool:
        """Send a single event to Kafka"""
        if not self.producer:
            return False
            
        try:
            def _send():
                future = self.producer.send(
                    self.topic,
                    value=event.to_dict(),
                    key=event.logger
                )
                future.get(timeout=self.config.get('send_timeout', 10))
                return True
            
            self.circuit_breaker.call(_send)
            
            with self._lock:
                self.metrics.events_sent += 1
                self.metrics.bytes_sent += len(event.to_json())
                self.metrics.last_success = datetime.now()
            
            return True
            
        except Exception as e:
            with self._lock:
                self.metrics.events_failed += 1
                self.metrics.last_failure = datetime.now()
            logging.error(f"Failed to send event to Kafka: {e}")
            return False
    
    def send_batch(self, events: List[StreamEvent]) -> bool:
        """Send a batch of events to Kafka"""
        if not self.producer or not events:
            return False
            
        success_count = 0
        for event in events:
            if self.send_event(event):
                success_count += 1
        
        return success_count == len(events)
    
    def disconnect(self):
        """Disconnect from Kafka"""
        if self.producer:
            self.producer.close()
            self.producer = None
        self.status = StreamStatus.INACTIVE


class RedisStreamer(BaseStreamer):
    """Redis event streamer"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.redis_client = None
        self.stream_name = config.get('stream_name', 'amzurlog:events')
        
    def connect(self) -> bool:
        """Connect to Redis"""
        try:
            import redis
            
            redis_config = {
                'host': self.config.get('host', 'localhost'),
                'port': self.config.get('port', 6379),
                'db': self.config.get('db', 0),
                'decode_responses': True
            }
            
            # Add password if provided
            if 'password' in self.config:
                redis_config['password'] = self.config['password']
            
            # Add any additional redis config
            redis_config.update(self.config.get('redis_config', {}))
            
            self.redis_client = redis.Redis(**redis_config)
            
            # Test connection
            self.redis_client.ping()
            self.status = StreamStatus.ACTIVE
            return True
            
        except ImportError:
            logging.error("redis is not installed. Install with: pip install redis")
            self.status = StreamStatus.ERROR
            return False
        except Exception as e:
            logging.error(f"Failed to connect to Redis: {e}")
            self.status = StreamStatus.ERROR
            return False
    
    def send_event(self, event: StreamEvent) -> bool:
        """Send a single event to Redis Stream"""
        if not self.redis_client:
            return False
            
        try:
            def _send():
                event_data = event.to_dict()
                # Flatten nested dictionaries for Redis
                flattened_data = self._flatten_dict(event_data)
                self.redis_client.xadd(self.stream_name, flattened_data)
                return True
            
            self.circuit_breaker.call(_send)
            
            with self._lock:
                self.metrics.events_sent += 1
                self.metrics.bytes_sent += len(event.to_json())
                self.metrics.last_success = datetime.now()
            
            return True
            
        except Exception as e:
            with self._lock:
                self.metrics.events_failed += 1
                self.metrics.last_failure = datetime.now()
            logging.error(f"Failed to send event to Redis: {e}")
            return False
    
    def _flatten_dict(self, d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, str]:
        """Flatten nested dictionary for Redis"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, str(v)))
        return dict(items)
    
    def send_batch(self, events: List[StreamEvent]) -> bool:
        """Send a batch of events to Redis"""
        if not self.redis_client or not events:
            return False
            
        try:
            pipe = self.redis_client.pipeline()
            for event in events:
                event_data = event.to_dict()
                flattened_data = self._flatten_dict(event_data)
                pipe.xadd(self.stream_name, flattened_data)
            
            def _send_batch():
                pipe.execute()
                return True
            
            self.circuit_breaker.call(_send_batch)
            
            with self._lock:
                self.metrics.events_sent += len(events)
                self.metrics.bytes_sent += sum(len(event.to_json()) for event in events)
                self.metrics.last_success = datetime.now()
            
            return True
            
        except Exception as e:
            with self._lock:
                self.metrics.events_failed += len(events)
                self.metrics.last_failure = datetime.now()
            logging.error(f"Failed to send batch to Redis: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from Redis"""
        if self.redis_client:
            self.redis_client.close()
            self.redis_client = None
        self.status = StreamStatus.INACTIVE


class HTTPStreamer(BaseStreamer):
    """HTTP endpoint event streamer"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.session = None
        self.endpoint_url = config.get('url')
        
    def connect(self) -> bool:
        """Initialize HTTP session"""
        try:
            self.session = requests.Session()
            
            # Set headers
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'AmzurLog-Streamer/1.0.0'
            }
            headers.update(self.config.get('headers', {}))
            self.session.headers.update(headers)
            
            # Set authentication
            auth_config = self.config.get('auth')
            if auth_config:
                if auth_config.get('type') == 'basic':
                    from requests.auth import HTTPBasicAuth
                    self.session.auth = HTTPBasicAuth(
                        auth_config['username'],
                        auth_config['password']
                    )
                elif auth_config.get('type') == 'bearer':
                    self.session.headers['Authorization'] = f"Bearer {auth_config['token']}"
            
            # Set timeout
            self.timeout = self.config.get('timeout', 30)
            
            self.status = StreamStatus.ACTIVE
            return True
            
        except Exception as e:
            logging.error(f"Failed to initialize HTTP streamer: {e}")
            self.status = StreamStatus.ERROR
            return False
    
    def send_event(self, event: StreamEvent) -> bool:
        """Send a single event via HTTP"""
        if not self.session or not self.endpoint_url:
            return False
            
        try:
            def _send():
                response = self.session.post(
                    self.endpoint_url,
                    json=event.to_dict(),
                    timeout=self.timeout
                )
                response.raise_for_status()
                return True
            
            self.circuit_breaker.call(_send)
            
            with self._lock:
                self.metrics.events_sent += 1
                self.metrics.bytes_sent += len(event.to_json())
                self.metrics.last_success = datetime.now()
            
            return True
            
        except Exception as e:
            with self._lock:
                self.metrics.events_failed += 1
                self.metrics.last_failure = datetime.now()
            logging.error(f"Failed to send event via HTTP: {e}")
            return False
    
    def send_batch(self, events: List[StreamEvent]) -> bool:
        """Send a batch of events via HTTP"""
        if not self.session or not self.endpoint_url or not events:
            return False
            
        try:
            batch_data = {
                'events': [event.to_dict() for event in events],
                'count': len(events),
                'timestamp': datetime.now().isoformat()
            }
            
            def _send_batch():
                response = self.session.post(
                    self.endpoint_url,
                    json=batch_data,
                    timeout=self.timeout
                )
                response.raise_for_status()
                return True
            
            self.circuit_breaker.call(_send_batch)
            
            with self._lock:
                self.metrics.events_sent += len(events)
                self.metrics.bytes_sent += len(json.dumps(batch_data))
                self.metrics.last_success = datetime.now()
            
            return True
            
        except Exception as e:
            with self._lock:
                self.metrics.events_failed += len(events)
                self.metrics.last_failure = datetime.now()
            logging.error(f"Failed to send batch via HTTP: {e}")
            return False
    
    def disconnect(self):
        """Close HTTP session"""
        if self.session:
            self.session.close()
            self.session = None
        self.status = StreamStatus.INACTIVE


class ElasticsearchStreamer(BaseStreamer):
    """Elasticsearch event streamer for ELK Stack integration"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.es_client = None
        self.index_pattern = config.get('index_pattern', 'amzurlog-{date}')
        
    def connect(self) -> bool:
        """Connect to Elasticsearch"""
        try:
            from elasticsearch import Elasticsearch
            
            es_config = {
                'hosts': self.config.get('hosts', ['localhost:9200']),
                'timeout': self.config.get('timeout', 30),
                'max_retries': self.config.get('max_retries', 3),
                'retry_on_timeout': True
            }
            
            # Add authentication if provided
            if 'username' in self.config and 'password' in self.config:
                es_config['http_auth'] = (self.config['username'], self.config['password'])
            
            # Add SSL/TLS config
            if self.config.get('use_ssl', False):
                es_config['use_ssl'] = True
                es_config['verify_certs'] = self.config.get('verify_certs', True)
                if 'ca_certs' in self.config:
                    es_config['ca_certs'] = self.config['ca_certs']
            
            # Add any additional ES config
            es_config.update(self.config.get('es_config', {}))
            
            self.es_client = Elasticsearch(**es_config)
            
            # Test connection
            self.es_client.info()
            self.status = StreamStatus.ACTIVE
            return True
            
        except ImportError:
            logging.error("elasticsearch is not installed. Install with: pip install elasticsearch")
            self.status = StreamStatus.ERROR
            return False
        except Exception as e:
            logging.error(f"Failed to connect to Elasticsearch: {e}")
            self.status = StreamStatus.ERROR
            return False
    
    def _get_index_name(self, timestamp: datetime) -> str:
        """Generate index name based on timestamp"""
        return self.index_pattern.format(
            date=timestamp.strftime('%Y.%m.%d'),
            year=timestamp.strftime('%Y'),
            month=timestamp.strftime('%m'),
            day=timestamp.strftime('%d')
        )
    
    def send_event(self, event: StreamEvent) -> bool:
        """Send a single event to Elasticsearch"""
        if not self.es_client:
            return False
            
        try:
            def _send():
                index_name = self._get_index_name(event.timestamp)
                self.es_client.index(
                    index=index_name,
                    body=event.to_dict(),
                    id=event.id
                )
                return True
            
            self.circuit_breaker.call(_send)
            
            with self._lock:
                self.metrics.events_sent += 1
                self.metrics.bytes_sent += len(event.to_json())
                self.metrics.last_success = datetime.now()
            
            return True
            
        except Exception as e:
            with self._lock:
                self.metrics.events_failed += 1
                self.metrics.last_failure = datetime.now()
            logging.error(f"Failed to send event to Elasticsearch: {e}")
            return False
    
    def send_batch(self, events: List[StreamEvent]) -> bool:
        """Send a batch of events to Elasticsearch using bulk API"""
        if not self.es_client or not events:
            return False
            
        try:
            def _send_batch():
                from elasticsearch.helpers import bulk
                
                actions = []
                for event in events:
                    index_name = self._get_index_name(event.timestamp)
                    actions.append({
                        '_index': index_name,
                        '_id': event.id,
                        '_source': event.to_dict()
                    })
                
                bulk(self.es_client, actions)
                return True
            
            self.circuit_breaker.call(_send_batch)
            
            with self._lock:
                self.metrics.events_sent += len(events)
                self.metrics.bytes_sent += sum(len(event.to_json()) for event in events)
                self.metrics.last_success = datetime.now()
            
            return True
            
        except Exception as e:
            with self._lock:
                self.metrics.events_failed += len(events)
                self.metrics.last_failure = datetime.now()
            logging.error(f"Failed to send batch to Elasticsearch: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from Elasticsearch"""
        if self.es_client:
            self.es_client.close()
            self.es_client = None
        self.status = StreamStatus.INACTIVE


class StreamManager:
    """Manages multiple event streamers with buffering and batching"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.streamers: Dict[str, BaseStreamer] = {}
        self.event_queue = queue.Queue(maxsize=config.get('queue_size', 10000))
        self.batch_size = config.get('batch_size', 100)
        self.batch_timeout = config.get('batch_timeout', 5.0)
        self.worker_threads = config.get('worker_threads', 2)
        
        self._running = False
        self._workers = []
        self._batch_timer = None
        self._current_batch = []
        self._last_batch_time = time.time()
        self._lock = threading.Lock()
        
        # Initialize streamers
        self._initialize_streamers()
    
    def _initialize_streamers(self):
        """Initialize configured streamers"""
        streamers_config = self.config.get('streamers', {})
        
        for name, streamer_config in streamers_config.items():
            if not streamer_config.get('enabled', True):
                continue
                
            streamer_type = streamer_config.get('type')
            
            try:
                if streamer_type == StreamDestinationType.KAFKA.value:
                    streamer = KafkaStreamer(streamer_config)
                elif streamer_type == StreamDestinationType.REDIS.value:
                    streamer = RedisStreamer(streamer_config)
                elif streamer_type == StreamDestinationType.HTTP.value:
                    streamer = HTTPStreamer(streamer_config)
                elif streamer_type == StreamDestinationType.ELASTICSEARCH.value:
                    streamer = ElasticsearchStreamer(streamer_config)
                else:
                    logging.warning(f"Unknown streamer type: {streamer_type}")
                    continue
                
                if streamer.connect():
                    self.streamers[name] = streamer
                    logging.info(f"Initialized streamer: {name} ({streamer_type})")
                else:
                    logging.error(f"Failed to connect streamer: {name}")
                    
            except Exception as e:
                logging.error(f"Failed to initialize streamer {name}: {e}")
    
    def start(self):
        """Start the stream manager"""
        if self._running:
            return
            
        self._running = True
        
        # Start worker threads
        for i in range(self.worker_threads):
            worker = threading.Thread(target=self._worker_loop, name=f"StreamWorker-{i}")
            worker.daemon = True
            worker.start()
            self._workers.append(worker)
        
        # Start batch timer
        self._start_batch_timer()
        
        logging.info(f"StreamManager started with {len(self.streamers)} streamers")
    
    def stop(self):
        """Stop the stream manager"""
        if not self._running:
            return
            
        self._running = False
        
        # Process remaining events
        self._flush_current_batch()
        
        # Stop batch timer
        if self._batch_timer:
            self._batch_timer.cancel()
        
        # Wait for workers to finish
        for worker in self._workers:
            worker.join(timeout=5.0)
        
        # Disconnect all streamers
        for streamer in self.streamers.values():
            try:
                streamer.disconnect()
            except Exception as e:
                logging.error(f"Error disconnecting streamer: {e}")
        
        logging.info("StreamManager stopped")
    
    def stream_event(self, event: StreamEvent) -> bool:
        """Add an event to the streaming queue"""
        if not self._running:
            return False
            
        try:
            self.event_queue.put_nowait(event)
            return True
        except queue.Full:
            logging.warning("Stream queue is full, dropping event")
            return False
    
    def _worker_loop(self):
        """Worker thread loop for processing events"""
        while self._running:
            try:
                # Get event from queue
                try:
                    event = self.event_queue.get(timeout=1.0)
                except queue.Empty:
                    continue
                
                # Add to current batch
                with self._lock:
                    self._current_batch.append(event)
                    
                    # Check if batch is ready
                    if len(self._current_batch) >= self.batch_size:
                        self._process_batch()
                
                self.event_queue.task_done()
                
            except Exception as e:
                logging.error(f"Error in stream worker: {e}")
    
    def _start_batch_timer(self):
        """Start the batch timeout timer"""
        if self._running:
            self._batch_timer = threading.Timer(self.batch_timeout, self._batch_timeout_handler)
            self._batch_timer.start()
    
    def _batch_timeout_handler(self):
        """Handle batch timeout"""
        with self._lock:
            if self._current_batch:
                self._process_batch()
        
        # Restart timer
        self._start_batch_timer()
    
    def _process_batch(self):
        """Process the current batch of events"""
        if not self._current_batch:
            return
            
        batch = self._current_batch.copy()
        self._current_batch.clear()
        self._last_batch_time = time.time()
        
        # Send batch to all streamers
        for name, streamer in self.streamers.items():
            try:
                success = streamer.send_batch(batch)
                if not success:
                    logging.warning(f"Failed to send batch to streamer: {name}")
            except Exception as e:
                logging.error(f"Error sending batch to {name}: {e}")
    
    def _flush_current_batch(self):
        """Flush any remaining events in the current batch"""
        with self._lock:
            if self._current_batch:
                self._process_batch()
    
    def add_streamer(self, name: str, streamer: BaseStreamer) -> bool:
        """Add a new streamer"""
        if streamer.connect():
            self.streamers[name] = streamer
            return True
        return False
    
    def remove_streamer(self, name: str) -> bool:
        """Remove a streamer"""
        if name in self.streamers:
            try:
                self.streamers[name].disconnect()
                del self.streamers[name]
                return True
            except Exception as e:
                logging.error(f"Error removing streamer {name}: {e}")
        return False
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get metrics for all streamers"""
        metrics = {
            'queue_size': self.event_queue.qsize(),
            'current_batch_size': len(self._current_batch),
            'streamers': {}
        }
        
        for name, streamer in self.streamers.items():
            metrics['streamers'][name] = {
                'status': streamer.get_status().value,
                'metrics': streamer.get_metrics().to_dict()
            }
        
        return metrics
    
    def get_status(self) -> Dict[str, Any]:
        """Get overall status"""
        return {
            'running': self._running,
            'streamers_count': len(self.streamers),
            'queue_size': self.event_queue.qsize(),
            'streamers': {name: streamer.get_status().value for name, streamer in self.streamers.items()}
        }