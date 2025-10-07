# 🚀 AmzurLog Installation Guide

## Installation Options

### Default Installation (Full Features) ⭐ **RECOMMENDED**

```bash
pip install amzurlog
```

**Includes everything by default:**
- ✅ Core logging functionality
- ✅ Event streaming (ELK, Grafana, Kafka, Redis)
- ✅ Exception tracking (Sentry, Rollbar)
- ✅ Performance monitoring
- ✅ All specialized loggers
- ✅ Sensitive data protection

### Minimal Installation (Core Only)

If you only need basic logging without external integrations:

```bash
pip install amzurlog[minimal]
```

**Includes only:**
- ✅ Core logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- ✅ File and console handlers
- ✅ JSON and text formatters
- ✅ Basic context management

## Quick Start Examples

### Full Installation Usage

```python
import amzurlog

# Basic logging (works immediately)
amzurlog.info("Application started")

# Streaming to ELK Stack
from amzurlog.streaming_handlers import ELKStreamingHandler
logger = amzurlog.AmzurLogger("my_app")
elk_handler = ELKStreamingHandler("localhost:9200", "logs")
logger.add_handler(elk_handler)
logger.info("This goes to ELK!")

# Exception tracking with Sentry
from amzurlog.exception_handlers import SentryHandler
sentry_handler = SentryHandler(dsn="your-sentry-dsn")
logger.add_handler(sentry_handler)
```

### Minimal Installation Usage

```python
import amzurlog

# Core logging features
amzurlog.info("Simple logging")
amzurlog.error("Error message", extra={"user_id": 123})

# File logging
from amzurlog import AmzurLogger, FileHandler, JSONFormatter
logger = AmzurLogger("app")
handler = FileHandler("app.log")
handler.set_formatter(JSONFormatter())
logger.add_handler(handler)
```

## Feature Comparison

| Feature | Default Install | Minimal Install |
|---------|----------------|-----------------|
| Core Logging | ✅ | ✅ |
| File/Console Handlers | ✅ | ✅ |
| JSON/Text Formatters | ✅ | ✅ |
| Context Management | ✅ | ✅ |
| ELK Stack Streaming | ✅ | ❌ |
| Grafana Integration | ✅ | ❌ |
| Kafka Streaming | ✅ | ❌ |
| Redis Streaming | ✅ | ❌ |
| Sentry Integration | ✅ | ❌ |
| Rollbar Integration | ✅ | ❌ |
| Performance Monitoring | ✅ | ❌ |
| Specialized Loggers | ✅ | ✅ |
| Install Size | ~50MB | ~5MB |

## Why This Approach?

### Default Full Installation Benefits:
- 🎯 **Ready to use** - All features work immediately
- 🚀 **No configuration** - Just `pip install amzurlog` and go
- 📊 **Enterprise ready** - Monitoring and error tracking included
- 🔧 **No surprises** - All documentation examples work

### Minimal Installation Benefits:
- ⚡ **Lightweight** - Only ~5MB instead of ~50MB
- 🏃 **Fast install** - Quick deployment in minimal environments
- 🧹 **Clean dependencies** - No external service dependencies
- 🐳 **Docker friendly** - Smaller container images

## Installation Commands Summary

```bash
# Full features (recommended for most users)
pip install amzurlog

# Minimal core features only
pip install amzurlog[minimal]

# Legacy specific features (still supported)
pip install amzurlog[streaming]    # Just streaming features
pip install amzurlog[exceptions]   # Just exception tracking
pip install amzurlog[performance]  # Just performance monitoring
pip install amzurlog[all]          # Same as default install
```

## What Changed?

**Before:** Optional dependencies required separate installation
```bash
pip install amzurlog                # Core only
pip install amzurlog[streaming]     # + Streaming
pip install amzurlog[exceptions]    # + Exceptions
```

**Now:** Everything included by default
```bash
pip install amzurlog                # Everything included!
pip install amzurlog[minimal]       # Core only (if needed)
```

This means users get the full power of AmzurLog with a single command! 🎉