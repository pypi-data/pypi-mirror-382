"""
AmzurLog Package Setup
======================

Setup configuration for the AmzurLog package.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="amzurlog",
    version="1.2.0",
    author="AmzurATG",
    author_email="support@amzur.com",
    description="A powerful, flexible, and easy-to-use logging library built from scratch",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AmzurATG/amzurlog",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Logging",
    ],
    python_requires=">=3.7",
    install_requires=[
        # Core dependencies
        "typing-extensions>=3.7.4; python_version<'3.8'",
        # Streaming dependencies (ELK, Grafana, Kafka, Redis)
        "elasticsearch>=7.0.0,<10.0.0",
        "kafka-python>=2.0.0,<3.0.0",
        "redis>=4.0.0,<7.0.0",
        "requests>=2.25.0,<3.0.0",
        # Exception tracking dependencies (Sentry, Rollbar)
        "sentry-sdk>=1.0.0,<3.0.0",
        "rollbar>=0.16.0,<2.0.0",
        # Performance monitoring
        "psutil>=5.0.0,<6.0.0",
    ],
    extras_require={
        "minimal": [
            # Only core dependencies for basic logging
        ],
        "streaming": [
            "elasticsearch>=7.0.0",
            "kafka-python>=2.0.0",
            "redis>=4.0.0",
            "requests>=2.25.0",
        ],
        "exceptions": [
            "sentry-sdk>=1.0.0",
            "rollbar>=0.16.0",
        ],
        "performance": [
            "psutil>=5.0.0",
        ],
        "all": [
            "elasticsearch>=7.0.0",
            "kafka-python>=2.0.0",
            "redis>=4.0.0",
            "requests>=2.25.0",
            "sentry-sdk>=1.0.0",
            "rollbar>=0.16.0",
            "psutil>=5.0.0",
        ],
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
            "twine>=3.0.0",
            "wheel>=0.36.0",
            "build>=0.7.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "amzurlog-test=amzurlog.test_amzurlog:main",
        ],
    },
    keywords="logging logger structured json performance monitoring context",
    project_urls={
        "Bug Reports": "https://github.com/AmzurATG/amzurlog/issues",
        "Source": "https://github.com/AmzurATG/amzurlog",
        "Documentation": "https://github.com/AmzurATG/amzurlog/blob/main/README.md",
    },
)