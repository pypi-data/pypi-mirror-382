#!/usr/bin/env python3
"""
AmzurLog Event Streaming Example
================================

This example demonstrates how to use AmzurLog's event streaming features
to send logs to monitoring platforms like ELK Stack and Grafana.

Run this example to see event streaming in action!
"""

import time
import json
from datetime import datetime
from amzurlog import (
    AmzurLogger, LogLevel,
    ELKStreamingHandler, KafkaStreamingHandler, RedisStreamingHandler,
    MultiStreamingHandler, JSONFormatter
)


def example_elk_streaming():
    """Example of streaming to ELK Stack"""
    print("=== ELK Stack Streaming Example ===")
    
    # Create logger
    logger = AmzurLogger("elk-example")
    logger.set_level(LogLevel.INFO)
    
    # Add console handler for local viewing
    from amzurlog import ConsoleHandler, ColoredFormatter
    console_handler = ConsoleHandler()
    console_handler.set_formatter(ColoredFormatter())
    logger.add_handler(console_handler)
    
    # Add ELK streaming handler
    try:
        elk_handler = ELKStreamingHandler(
            elasticsearch_hosts=['localhost:9200'],
            index_pattern='amzurlog-example-{date}',
            batch_size=5,  # Small batch for demo
            batch_timeout=3.0
        )
        elk_handler.set_formatter(JSONFormatter())
        logger.add_handler(elk_handler)
        
        print("Sending events to Elasticsearch...")
        
        # Log some example events
        logger.info("Application started", 
                   service="example-app", 
                   version="1.0.0",
                   environment="demo")
        
        logger.info("User activity", 
                   user_id="user_123",
                   action="login",
                   ip_address="192.168.1.100")
        
        logger.warning("High memory usage", 
                      memory_usage=87.5,
                      threshold=80.0,
                      host="web-server-01")
        
        logger.error("Database connection timeout", 
                    database="users_db",
                    timeout_duration=30,
                    retry_count=3)
        
        # Wait for events to be sent
        time.sleep(5)
        elk_handler.flush()
        
        # Show metrics
        metrics = elk_handler.get_metrics()
        print("\nStreaming Metrics:")
        es_metrics = metrics.get('streamers', {}).get('elasticsearch', {}).get('metrics', {})
        print(f"Events sent: {es_metrics.get('events_sent', 0)}")
        print(f"Events failed: {es_metrics.get('events_failed', 0)}")
        
        elk_handler.close()
        print("✓ ELK streaming example completed!")
        
    except Exception as e:
        print(f"✗ ELK streaming failed: {e}")
        print("Make sure Elasticsearch is running on localhost:9200")


def example_kafka_streaming():
    """Example of streaming to Kafka"""
    print("\n=== Kafka Streaming Example ===")
    
    # Create logger
    logger = AmzurLogger("kafka-example")
    logger.set_level(LogLevel.INFO)
    
    try:
        kafka_handler = KafkaStreamingHandler(
            bootstrap_servers=['localhost:9092'],
            topic='amzurlog-events',
            batch_size=3,  # Small batch for demo
            batch_timeout=2.0
        )
        kafka_handler.set_formatter(JSONFormatter())
        logger.add_handler(kafka_handler)
        
        print("Sending events to Kafka...")
        
        # Log business events
        logger.info("Order created", 
                   order_id="ORD-12345",
                   customer_id="CUST-789",
                   amount=299.99,
                   currency="USD")
        
        logger.info("Payment processed", 
                   order_id="ORD-12345",
                   payment_method="credit_card",
                   transaction_id="TXN-ABC123")
        
        logger.error("Inventory shortage", 
                    product_id="PROD-456",
                    available_quantity=0,
                    requested_quantity=5)
        
        # Wait for events to be sent
        time.sleep(3)
        kafka_handler.flush()
        
        # Show metrics
        metrics = kafka_handler.get_metrics()
        print("\nStreaming Metrics:")
        kafka_metrics = metrics.get('streamers', {}).get('kafka', {}).get('metrics', {})
        print(f"Events sent: {kafka_metrics.get('events_sent', 0)}")
        print(f"Events failed: {kafka_metrics.get('events_failed', 0)}")
        
        kafka_handler.close()
        print("✓ Kafka streaming example completed!")
        
    except Exception as e:
        print(f"✗ Kafka streaming failed: {e}")
        print("Make sure Kafka is running on localhost:9092")


def example_redis_streaming():
    """Example of streaming to Redis"""
    print("\n=== Redis Streaming Example ===")
    
    # Create logger
    logger = AmzurLogger("redis-example")
    logger.set_level(LogLevel.INFO)
    
    try:
        redis_handler = RedisStreamingHandler(
            redis_host='localhost',
            redis_port=6379,
            stream_name='amzurlog:example',
            batch_size=3,  # Small batch for demo
            batch_timeout=2.0
        )
        redis_handler.set_formatter(JSONFormatter())
        logger.add_handler(redis_handler)
        
        print("Sending events to Redis Streams...")
        
        # Log real-time events
        logger.info("User session started", 
                   session_id="sess_abc123",
                   user_id="user_456",
                   timestamp=datetime.now().isoformat())
        
        logger.info("API request", 
                   endpoint="/api/users",
                   method="GET",
                   response_time=125,
                   status_code=200)
        
        logger.warning("Rate limit approaching", 
                      client_id="client_789",
                      current_requests=950,
                      limit=1000)
        
        # Wait for events to be sent
        time.sleep(3)
        redis_handler.flush()
        
        # Show metrics
        metrics = redis_handler.get_metrics()
        print("\nStreaming Metrics:")
        redis_metrics = metrics.get('streamers', {}).get('redis', {}).get('metrics', {})
        print(f"Events sent: {redis_metrics.get('events_sent', 0)}")
        print(f"Events failed: {redis_metrics.get('events_failed', 0)}")
        
        redis_handler.close()
        print("✓ Redis streaming example completed!")
        
    except Exception as e:
        print(f"✗ Redis streaming failed: {e}")
        print("Make sure Redis is running on localhost:6379")


def example_multi_streaming():
    """Example of streaming to multiple destinations"""
    print("\n=== Multi-Destination Streaming Example ===")
    
    # Create logger
    logger = AmzurLogger("multi-example")
    logger.set_level(LogLevel.INFO)
    
    # Configure multiple destinations
    streamers_config = {
        'mock_analytics': {
            'enabled': True,
            'type': 'http',
            'url': 'https://httpbin.org/post',  # Mock endpoint for demo
            'timeout': 10
        }
        # Note: In a real setup, you'd configure multiple actual destinations
        # like Elasticsearch, Kafka, Redis, etc.
    }
    
    try:
        multi_handler = MultiStreamingHandler(
            streamers_config=streamers_config,
            batch_size=2,  # Small batch for demo
            batch_timeout=2.0
        )
        multi_handler.set_formatter(JSONFormatter())
        logger.add_handler(multi_handler)
        
        print("Sending events to multiple destinations...")
        
        # Log critical events that should go everywhere
        logger.critical("System alert", 
                       alert_type="HIGH_CPU",
                       affected_services=["api", "web"],
                       cpu_usage=95.2)
        
        logger.error("Database connection pool exhausted", 
                    pool_size=100,
                    active_connections=100,
                    waiting_requests=25)
        
        # Wait for events to be sent
        time.sleep(3)
        multi_handler.flush()
        
        # Show status and metrics
        status = multi_handler.get_status()
        print(f"\nStreaming Status:")
        for streamer_name, streamer_status in status.get('streamers', {}).items():
            print(f"{streamer_name}: {streamer_status}")
        
        multi_handler.close()
        print("✓ Multi-destination streaming example completed!")
        
    except Exception as e:
        print(f"✗ Multi-destination streaming failed: {e}")


def example_streaming_with_config():
    """Example using configuration-based setup"""
    print("\n=== Configuration-Based Streaming Example ===")
    
    from amzurlog import AmzurLogConfig
    
    # Configuration for streaming
    config_dict = {
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
                "class": "StreamingHandler",
                "stream_config": {
                    "batch_size": 3,
                    "batch_timeout": 2.0,
                    "streamers": {
                        "http_endpoint": {
                            "enabled": True,
                            "type": "http",
                            "url": "https://httpbin.org/post"
                        }
                    }
                },
                "level": "INFO",
                "formatter": {
                    "type": "json"
                }
            }
        ]
    }
    
    try:
        # Create configuration and logger
        config = AmzurLogConfig(config_dict)
        logger = config.setup_logger("config-example")
        
        print("Sending events using configuration-based setup...")
        
        # Log events
        logger.info("Configuration test", 
                   config_type="streaming",
                   test_case="configuration_based")
        
        logger.warning("Test warning message", 
                      test_id="warn_001")
        
        # Wait and cleanup
        time.sleep(3)
        
        print("✓ Configuration-based streaming example completed!")
        
    except Exception as e:
        print(f"✗ Configuration-based streaming failed: {e}")


def main():
    """Run all streaming examples"""
    print("🚀 AmzurLog Event Streaming Examples")
    print("=" * 50)
    print("This demo shows how to stream logs to various monitoring platforms.")
    print("Note: Some examples require external services to be running.")
    print("=" * 50)
    
    # Run examples
    try:
        example_elk_streaming()
        example_kafka_streaming()
        example_redis_streaming()
        example_multi_streaming()
        example_streaming_with_config()
        
        print("\n🎉 All streaming examples completed!")
        print("\nNext steps:")
        print("- Check your monitoring platforms for the streamed events")
        print("- Explore the configuration options in streaming_configs.py")
        print("- Run the interactive demos with: python -m amzurlog.streaming_demos")
        print("- Read the full documentation in STREAMING_GUIDE.md")
        
    except KeyboardInterrupt:
        print("\n\nExamples interrupted by user.")
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")


if __name__ == "__main__":
    main()