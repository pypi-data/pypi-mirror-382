# AmzurLog

[![PyPI version](https://badge.fury.io/py/amzurlog.svg)](https://badge.fury.io/py/amzurlog)
[![Python versions](https://img.shields.io/pypi/pyversions/amzurlog.svg)](https://pypi.org/project/amzurlog/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://pepy.tech/badge/amzurlog)](https://pepy.tech/project/amzurlog)

A powerful, flexible, and easy-to-use logging library built from scratch for Python applications with built-in streaming and exception tracking capabilities.

## ✨ Features

🚀 **Core Features**
- Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Thread-safe logging operations
- Structured logging with JSON support
- Custom formatters and filters
- File rotation and log management
- Performance monitoring decorators
- Context-aware logging

📡 **Event Streaming** 
- Real-time event streaming to monitoring platforms
- ELK Stack integration (Elasticsearch, Logstash, Kibana)
- Grafana Loki integration for log aggregation
- Apache Kafka streaming support
- Redis Streams integration
- HTTP webhook streaming
- Circuit breaker and rate limiting

🛡️ **Exception Tracking**
- Comprehensive exception capture and reporting
- Sentry integration for error monitoring
- Rollbar integration for error tracking
- Custom webhook integrations
- Exception fingerprinting and deduplication
- Context enrichment with breadcrumbs

## 🚀 Quick Start

### Installation

```bash
pip install amzurlog
```

**That's it!** All features (streaming, exception tracking, performance monitoring) are included by default.

### Basic Usage

```python
import amzurlog

# Quick logging
amzurlog.info("Application started")
amzurlog.error("Something went wrong", extra={"user_id": 123})
```

### Advanced Usage

```python
from amzurlog import AmzurLogger, JSONFormatter, FileHandler

# Create custom logger
logger = AmzurLogger("my_app")

# Add file handler with JSON formatting
handler = FileHandler("app.log")
handler.set_formatter(JSONFormatter())
logger.add_handler(handler)

# Log with structured data
logger.info("User action", extra={
    "action": "login",
    "user_id": 123,
    "ip": "192.168.1.1"
})
```

### Stream to ELK Stack

```python
from amzurlog import AmzurLogger
from amzurlog.streaming_handlers import ELKStreamingHandler

logger = AmzurLogger("my_app")

# Add ELK streaming
elk_handler = ELKStreamingHandler(
    elasticsearch_host="localhost:9200",
    index_name="app_logs"
)
logger.add_handler(elk_handler)

logger.info("This goes to both console AND ELK Stack!")
```

### Exception Tracking with Sentry

```python
from amzurlog import AmzurLogger
from amzurlog.exception_handlers import SentryHandler

logger = AmzurLogger("sentry_app")

# Add Sentry exception tracking
sentry_handler = SentryHandler(dsn="your-sentry-dsn")
logger.add_handler(sentry_handler)

try:
    risky_operation()
except Exception:
    logger.error("Operation failed", exc_info=True)
```

## 📚 Documentation

- **[Installation Guide](INSTALLATION_GUIDE.md)** - Different installation options
- **[Complete Documentation](README.md)** - Full feature documentation
- **[Packaging Guide](PACKAGING_GUIDE.md)** - For contributors
- **[Dependency Strategy](DEPENDENCY_STRATEGY.md)** - Understanding dependencies

## 🛠️ Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/Iswarya-Amzur/amzurlog.git
cd amzurlog

# Install in development mode with all dependencies
pip install -e .[dev]

# Run tests
python test_default_install.py
```

### Building the Package

```bash
# Build the package
python build_package.py

# Publish to PyPI
python publish_package.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with ❤️ by AmzurATG
- Inspired by the need for better logging in Python applications
- Thanks to all contributors and users

## 📞 Support

- 🐛 [Report bugs](https://github.com/Iswarya-Amzur/amzurlog/issues)
- 💡 [Request features](https://github.com/Iswarya-Amzur/amzurlog/issues)
- 📧 [Email support](mailto:support@amzur.com)

---

**Made with ❤️ by AmzurATG**