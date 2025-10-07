# AmzurLog Package Distribution Guide

This guide will help you convert AmzurLog into a pip package and distribute it so everyone can install and use it.

## 📋 Prerequisites

1. **Python 3.7+** installed
2. **Git** for version control
3. **PyPI account** (create at https://pypi.org/)
4. **TestPyPI account** (create at https://test.pypi.org/) - Optional but recommended

## 🛠️ Setup Steps

### 1. Install Build Tools

```bash
pip install build twine wheel setuptools
```

### 2. Package Structure

Your package now has the proper structure:

```
amzurlog/
├── amzurlog/                 # Main package directory
│   ├── __init__.py          # Package initialization with exports
│   ├── core.py              # Core logging functionality  
│   ├── handlers.py          # Log handlers
│   ├── formatters.py        # Log formatters
│   ├── streaming.py         # Event streaming features
│   ├── exception_tracking.py # Exception tracking
│   └── ...                  # Other modules
├── setup.py                 # Legacy setup configuration
├── pyproject.toml          # Modern Python packaging
├── MANIFEST.in             # Include additional files
├── LICENSE                 # MIT License
├── README.md               # Documentation
├── .gitignore              # Git ignore rules
├── build_package.py        # Build automation script
└── publish_package.py      # Publishing automation script
```

## 🚀 Building the Package

### Option 1: Using the Build Script (Recommended)

**Windows:**
```cmd
python build_package.py
```

**Or use the batch file:**
```cmd
build_package.bat
```

### Option 2: Manual Build

```bash
# Clean previous builds
rm -rf build/ dist/ *.egg-info/

# Install dependencies
pip install build twine wheel

# Build the package
python -m build

# Check the package
python -m twine check dist/*
```

## 📦 What Gets Built

The build process creates:

- **Source Distribution** (`amzurlog-1.0.0.tar.gz`) - Contains source code
- **Wheel Distribution** (`amzurlog-1.0.0-py3-none-any.whl`) - Pre-built package

## 🧪 Testing Before Publishing

### 1. Test Locally

```bash
# Install from local wheel
pip install dist/amzurlog-1.0.0-py3-none-any.whl

# Test the package
python -c "import amzurlog; amzurlog.info('Test message')"
```

### 2. Test on TestPyPI (Recommended)

```bash
# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# Install from TestPyPI
pip install -i https://test.pypi.org/simple/ amzurlog

# Test functionality
python -c "import amzurlog; print('AmzurLog version:', amzurlog.__version__)"
```

## 🌐 Publishing to PyPI

### Option 1: Using the Publish Script (Recommended)

```bash
python publish_package.py
```

This script provides options for:
- TestPyPI upload (testing)
- PyPI upload (production)
- Both (recommended workflow)

### Option 2: Manual Publishing

```bash
# Upload to PyPI
python -m twine upload dist/*
```

You'll need:
- PyPI username/password, or
- API token (recommended)

## 🔐 Authentication

### Using API Tokens (Recommended)

1. **Create API Token:**
   - Go to https://pypi.org/manage/account/token/
   - Create a new token
   - Copy the token (starts with `pypi-`)

2. **Configure credentials:**
   ```bash
   # Create ~/.pypirc file
   [distutils]
   index-servers = pypi testpypi

   [pypi]
   username = __token__
   password = pypi-your-token-here

   [testpypi]
   repository = https://test.pypi.org/legacy/
   username = __token__
   password = pypi-your-testpypi-token-here
   ```

## 📖 Installation for Users

Once published, users can install AmzurLog with:

### Basic Installation
```bash
pip install amzurlog
```

### With Optional Features
```bash
# Install with streaming capabilities
pip install amzurlog[streaming]

# Install with exception tracking
pip install amzurlog[exceptions]

# Install with performance monitoring
pip install amzurlog[performance]

# Install everything
pip install amzurlog[all]

# Install development dependencies
pip install amzurlog[dev]
```

## 💡 Usage Examples for Users

### Basic Usage
```python
import amzurlog

# Quick start
amzurlog.info("Hello from AmzurLog!")
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

# Log with context
logger.info("User login", extra={
    "user_id": 123,
    "ip_address": "192.168.1.1",
    "timestamp": "2024-01-01T10:00:00Z"
})
```

### With Streaming (ELK Stack)
```python
from amzurlog import AmzurLogger
from amzurlog.streaming_handlers import ELKStreamingHandler

logger = AmzurLogger("elk_app")

# Add ELK streaming
elk_handler = ELKStreamingHandler(
    elasticsearch_host="localhost:9200",
    index_name="app_logs"
)
logger.add_handler(elk_handler)

logger.info("This will be sent to ELK Stack!")
```

### With Exception Tracking (Sentry)
```python
from amzurlog import AmzurLogger
from amzurlog.exception_handlers import SentryHandler

logger = AmzurLogger("sentry_app")

# Add Sentry exception tracking
sentry_handler = SentryHandler(
    dsn="your-sentry-dsn-here"
)
logger.add_handler(sentry_handler)

try:
    # Some code that might fail
    1 / 0
except Exception as e:
    logger.error("Division by zero", exc_info=True)
```

## 🔄 Package Updates

### Version Management

1. **Update version in `amzurlog/__init__.py`:**
   ```python
   __version__ = "1.1.0"
   ```

2. **Rebuild and republish:**
   ```bash
   python build_package.py
   python publish_package.py
   ```

### Automated Versioning (Optional)

You can use tools like `bumpversion` or `setuptools_scm` for automatic version management.

## 📊 Package Statistics

Once published, you can track your package:

- **PyPI Stats:** https://pypistats.org/packages/amzurlog
- **Package Page:** https://pypi.org/project/amzurlog/
- **Download Stats:** Available in PyPI dashboard

## 🛡️ Security Best Practices

1. **Use API tokens** instead of passwords
2. **Enable 2FA** on your PyPI account
3. **Scan for vulnerabilities:**
   ```bash
   pip install safety
   safety check
   ```

4. **Code signing** (optional but recommended for popular packages)

## 🆘 Troubleshooting

### Common Issues

1. **"Package already exists"**
   - You can't upload the same version twice
   - Increment the version number

2. **"Invalid credentials"**
   - Check your PyPI credentials
   - Ensure API token is correctly configured

3. **"File not found"**
   - Make sure you've built the package first
   - Check that dist/ directory exists

4. **Import errors after installation**
   - Check dependencies in setup.py
   - Verify __init__.py exports

### Getting Help

- **PyPI Help:** https://packaging.python.org/
- **Twine Documentation:** https://twine.readthedocs.io/
- **AmzurLog Issues:** https://github.com/AmzurATG/amzurlog/issues

## 🎉 Success!

Once published, your package will be available to millions of Python developers worldwide!

Users can now install it with:
```bash
pip install amzurlog
```

And use it in their projects:
```python
import amzurlog
amzurlog.info("Hello World!")
```

## 📈 Next Steps

1. **Documentation:** Create comprehensive docs (Sphinx, MkDocs)
2. **CI/CD:** Set up automated testing and publishing
3. **Community:** Create GitHub issues/discussions
4. **Examples:** Provide more usage examples
5. **Integrations:** Create plugins for popular frameworks