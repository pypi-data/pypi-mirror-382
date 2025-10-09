# Changelog

All notable changes to the Observatory Python SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-10-09

### Added
- Initial release of Observatory Python SDK
- Core SDK functionality (`ObservatorySDK` class)
- HTTP client for Observatory backend API (`ObservatoryClient`)
- Message interceptor for MCP protocol tracking (`MessageInterceptor`)
- Privacy manager with PII detection and masking (`PrivacyManager`)
- Comprehensive configuration system (`ObservatoryConfig`)
- Smart sampling with adaptive strategies
- Async event processing with batching
- Automatic heartbeat reporting
- Type hints for all public APIs
- Full test coverage for core functionality
- Examples for basic, advanced, and custom configurations
- Complete documentation and quickstart guide
- GitHub Actions for CI/CD
- PyPI package configuration

### Features
- 2-line integration for MCP servers
- <1ms overhead per message
- Privacy-first design with automatic PII detection
- Smart sampling (adaptive, error-prioritized)
- Real-time tracking and analytics
- Configurable data retention
- Error tracking and reporting
- Performance metrics collection
- Session analytics
- Transport-agnostic (stdio, HTTP, WebSocket)

### Documentation
- Comprehensive README with examples
- Quick start guide
- API reference
- Configuration guide
- Examples for common use cases

### Testing
- Unit tests for all core modules
- Integration tests
- Coverage reporting
- CI/CD via GitHub Actions

[0.1.0]: https://github.com/observatory/observatory/releases/tag/v0.1.0
