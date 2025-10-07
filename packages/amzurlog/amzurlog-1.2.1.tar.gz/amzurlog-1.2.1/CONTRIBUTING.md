# Contributing to AmzurLog

Thank you for your interest in contributing to AmzurLog! This document provides guidelines for contributing to this project.

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Basic understanding of logging systems

### Development Setup

1. **Fork the repository**
   ```bash
   # Fork on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/amzurlog.git
   cd amzurlog
   ```

2. **Set up development environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install in development mode
   pip install -e .[dev]
   ```

3. **Run tests**
   ```bash
   python test_default_install.py
   python test_comprehensive.py
   ```

## 📝 How to Contribute

### Reporting Bugs

1. **Check existing issues** first to avoid duplicates
2. **Use the bug report template** when creating issues
3. **Include:**
   - Python version
   - AmzurLog version
   - Operating system
   - Minimal code example
   - Error messages and stack traces

### Suggesting Features

1. **Check existing feature requests** first
2. **Use the feature request template**
3. **Explain:**
   - The problem you're trying to solve
   - Your proposed solution
   - Any alternative solutions considered
   - Examples of how it would be used

### Code Contributions

#### 1. Choose an Issue
- Look for issues labeled `good first issue` for beginners
- Comment on the issue to let others know you're working on it

#### 2. Create a Branch
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

#### 3. Make Changes
- Follow the existing code style
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass

#### 4. Commit Guidelines
```bash
# Use conventional commit format
git commit -m "feat: add kafka batch streaming support"
git commit -m "fix: resolve thread safety issue in file handler"
git commit -m "docs: update installation guide"
```

**Commit Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

#### 5. Submit Pull Request
1. Push your branch to your fork
2. Create a pull request against the main branch
3. Fill out the pull request template
4. Wait for review and address feedback

## 🧪 Testing

### Running Tests
```bash
# Run all tests
python test_default_install.py
python test_comprehensive.py

# Test specific features
python -c "from amzurlog.tests import test_streaming; test_streaming()"
```

### Writing Tests
- Add tests for new features in the appropriate test file
- Use descriptive test names
- Test both success and failure cases
- Mock external dependencies when needed

### Test Coverage
- Aim for high test coverage on new code
- Run coverage reports locally before submitting

## 📚 Documentation

### Types of Documentation
1. **Code comments** - For complex logic
2. **Docstrings** - For all public functions and classes
3. **README updates** - For new features
4. **Examples** - In `examples/` directory

### Documentation Style
- Use clear, concise language
- Include code examples
- Follow existing documentation patterns
- Update relevant sections when making changes

## 🎨 Code Style

### Python Style Guidelines
- Follow PEP 8
- Use type hints where appropriate
- Keep functions small and focused
- Use descriptive variable names

### Example Code Style
```python
from typing import Optional, Dict, Any
import logging

class AmzurLogger:
    """A powerful logging class with streaming capabilities.
    
    Args:
        name: Logger name
        level: Logging level (default: INFO)
        config: Optional configuration dictionary
    """
    
    def __init__(
        self, 
        name: str, 
        level: int = logging.INFO,
        config: Optional[Dict[str, Any]] = None
    ) -> None:
        self.name = name
        self.level = level
        self.config = config or {}
```

## 🏗️ Development Workflow

### Branch Strategy
- `main` - Stable releases
- `develop` - Development branch
- `feature/*` - New features
- `fix/*` - Bug fixes
- `hotfix/*` - Critical fixes

### Release Process
1. Create release branch from develop
2. Update version numbers
3. Update CHANGELOG.md
4. Test thoroughly
5. Merge to main and tag
6. Build and publish to PyPI

## 🔧 Setting Up Integrations

### Local Testing with External Services

#### Elasticsearch (Optional)
```bash
# Using Docker
docker run -d -p 9200:9200 -e "discovery.type=single-node" elasticsearch:7.17.0
```

#### Redis (Optional)
```bash
# Using Docker
docker run -d -p 6379:6379 redis:latest
```

#### Kafka (Optional)
```bash
# Using Docker Compose
docker-compose up -d kafka
```

## 📋 Pull Request Checklist

Before submitting your pull request, ensure:

- [ ] Code follows the project style guidelines
- [ ] Tests pass locally
- [ ] New features have tests
- [ ] Documentation is updated
- [ ] CHANGELOG.md is updated (for significant changes)
- [ ] Commit messages follow conventional format
- [ ] No unnecessary dependencies added
- [ ] Performance considerations addressed

## 🤝 Code Review Process

1. **Automated checks** run first (CI/CD)
2. **Maintainer review** for code quality and design
3. **Testing** in different environments
4. **Documentation review** for clarity
5. **Final approval** and merge

## 🎯 Areas for Contribution

### High Priority
- Performance optimizations
- Additional streaming integrations
- Better error handling
- Enhanced documentation

### Medium Priority
- More formatter options
- Additional filter types
- Metrics and monitoring improvements
- Configuration management

### Low Priority
- Code style improvements
- Minor feature enhancements
- Example applications

## 📞 Getting Help

- **GitHub Discussions** - For questions and ideas
- **Issues** - For bugs and feature requests
- **Email** - support@amzur.com for private matters

## 🏆 Recognition

Contributors will be:
- Added to the contributors list
- Mentioned in release notes
- Given credit in documentation

Thank you for helping make AmzurLog better! 🎉