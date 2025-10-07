# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2024-12-19

### Changed
- Made all dependencies required by default for better user experience
- Updated dependency version constraints to minimize conflicts:
  - `requests>=2.25.0,<3.0.0`
  - `redis>=4.0.0,<6.0.0`
  - `elasticsearch>=7.0.0,<10.0.0`
  - `kafka-python>=2.0.0,<3.0.0`
  - `sentry-sdk>=1.0.0,<3.0.0`
  - `psutil>=5.8.0,<7.0.0`

### Fixed
- Reduced dependency conflicts in complex environments
- Improved compatibility with AI/ML frameworks

### Documentation
- Added comprehensive dependency strategy guide
- Created installation troubleshooting guide
- Updated packaging documentation

## [1.1.0] - 2024-12-19

### Added
- Included all streaming and exception tracking dependencies by default
- Optional dependency groups for modular installation

### Fixed
- Resolved installation issues with missing dependencies

## [1.0.0] - 2024-12-19

### Added
- Initial release with core logging functionality
- ELK Stack integration
- Grafana Loki support
- Apache Kafka streaming
- Redis Streams integration
- Sentry exception tracking
- Rollbar integration
- Performance monitoring decorators
- Thread-safe operations
- JSON structured logging
- File rotation and management
- HTTP webhook streaming
- Circuit breaker pattern
- Rate limiting
- Context-aware logging

### Features
- Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Custom formatters and filters
- Exception fingerprinting
- Breadcrumb tracking
- Performance metrics
- Memory usage monitoring
- CPU utilization tracking