# Observatory MCP Python SDK

[![PyPI version](https://badge.fury.io/py/observatory-mcp.svg)](https://badge.fury.io/py/observatory-mcp)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Add comprehensive analytics and monitoring to your MCP servers with just 2-3 lines of code.**

Observatory SDK provides lightweight, zero-configuration observability for Model Context Protocol (MCP) servers. Track performance metrics, protocol messages, errors, and user behavior without modifying your existing MCP server implementation.

## ✨ Features

- 🚀 **2-Line Integration**: Add observability with minimal code changes
- 📊 **Complete Analytics**: Protocol messages, performance metrics, error tracking
- 🔒 **Privacy-First**: Built-in PII detection and data masking
- ⚡ **Lightweight**: <1ms overhead per message, async processing
- 🎯 **Smart Sampling**: Adaptive sampling with error prioritization
- 🔌 **Zero Server Modification**: Works via protocol message interception
- 📈 **Real-Time Monitoring**: Live dashboards and alerting
- 🐍 **Type-Safe**: Full type hints for IDE autocomplete

## 📦 Installation

```bash
pip install observatory-mcp
```

For MCP server integration:
```bash
pip install observatory-mcp[mcp]
```

For development:
```bash
pip install observatory-mcp[dev]
```

## 🚀 Quick Start

### Basic Integration (2 lines!)

```python
from mcp.server import Server
from observatory_mcp import ObservatorySDK

# Create your MCP server as usual
app = Server("my-awesome-mcp-server")

# Add Observatory with 2 lines!
observatory = ObservatorySDK(
    api_key="obs_live_xyz123",
    server_name="my-awesome-mcp-server",
    server_version="1.0.0"
)
app = observatory.wrap_server(app)

# Your handlers work exactly the same - Observatory tracks automatically!
@app.list_tools()
async def list_tools():
    return [...]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    return [...]
```

That's it! Observatory now tracks all your MCP protocol messages, performance metrics, and errors.

### With Context Manager

```python
from observatory_mcp import ObservatorySDK, ObservatoryConfig

async def main():
    # Configure Observatory
    config = ObservatoryConfig.create_default()
    
    async with ObservatorySDK(
        api_key="obs_live_xyz123",
        server_name="my-server",
        server_version="1.0.0",
        config=config
    ) as observatory:
        # SDK starts automatically
        app = Server("my-server")
        app = observatory.wrap_server(app)
        
        # Run your server
        await app.run()
    
    # SDK stops automatically
```

## 📊 What Gets Tracked?

### Protocol Messages
- All JSON-RPC requests and responses
- Message types, sizes, and timing
- Client-to-server and server-to-client messages
- Request/response correlation

### Performance Metrics
- Request latency (p50, p95, p99)
- Throughput and message rates
- Error rates and types
- Memory and CPU usage

### Error Tracking
- All exceptions and JSON-RPC errors
- Error patterns and frequencies
- Stack traces (sanitized)
- Error recovery metrics

### Behavioral Analytics
- Tool usage patterns
- Resource access patterns
- Session analytics
- Feature adoption rates

## ⚙️ Configuration

### Preset Configurations

```python
from observatory_mcp import ObservatoryConfig

# Default (recommended)
config = ObservatoryConfig.create_default()

# Minimal overhead
config = ObservatoryConfig.create_minimal()

# High-volume servers
config = ObservatoryConfig.create_high_performance()
```

### Custom Configuration

```python
from observatory_mcp import (
    ObservatoryConfig,
    SamplingConfig,
    PrivacyConfig,
    PerformanceConfig
)

config = ObservatoryConfig(
    # Tracking controls
    track_protocol_messages=True,
    track_performance_metrics=True,
    track_behavioral_analytics=False,
    
    # Sampling
    sampling=SamplingConfig(
        rate=1.0,  # 100% sampling
        adaptive_sampling=True,
        prioritize_errors=True,
        max_events_per_second=1000
    ),
    
    # Privacy
    privacy=PrivacyConfig(
        enable_pii_detection=True,
        hash_identifiers=True,
        sensitive_field_masks=["password", "token", "api_key"],
        max_message_size_capture=10_000,
        data_retention_days=90
    ),
    
    # Performance
    performance=PerformanceConfig(
        async_processing=True,
        batch_size=10,
        flush_interval=5.0,
        heartbeat_interval=30.0,
        memory_limit_mb=100
    ),
    
    # Debug
    debug=False,
    log_level="INFO"
)

observatory = ObservatorySDK(
    api_key="obs_live_xyz123",
    server_name="my-server",
    server_version="1.0.0",
    config=config
)
```

## 🔒 Privacy & Security

Observatory is designed with privacy in mind:

- **PII Detection**: Automatic detection of emails, SSNs, credit cards, phone numbers
- **Data Masking**: Sensitive fields are automatically masked
- **Identifier Hashing**: User/session IDs can be hashed with SHA-256
- **Configurable Retention**: Set data retention policies (default: 90 days)
- **Error Sanitization**: Stack traces and error messages are sanitized

```python
from observatory_mcp import PrivacyConfig

privacy = PrivacyConfig(
    enable_pii_detection=True,
    hash_identifiers=True,
    sensitive_field_masks=[
        "password", "token", "api_key", "secret",
        "authorization", "ssn", "credit_card"
    ],
    redact_errors=True
)
```

## 📈 Performance

Observatory is designed to be lightweight:

- **<1ms overhead** per message with default settings
- **Async processing** - tracking doesn't block your server
- **Smart sampling** - reduce overhead with adaptive sampling
- **Batching** - efficient batch processing of events
- **Memory efficient** - configurable memory limits

### Benchmarks

| Operation | Overhead | Notes |
|-----------|----------|-------|
| Message tracking | <0.5ms | With 100% sampling |
| Request logging | <0.1ms | Async processing |
| Privacy scanning | <0.2ms | PII detection enabled |
| **Total** | **<1ms** | Per tracked message |

## 🎯 Smart Sampling

Reduce overhead while maintaining visibility:

```python
from observatory_mcp import SamplingConfig

sampling = SamplingConfig(
    rate=0.1,  # Sample 10% of messages
    adaptive_sampling=True,  # Increase rate when errors occur
    prioritize_errors=True,  # Always sample error cases
    always_sample_first_n=10,  # First 10 per session
    always_sample_last_n=10,   # Last 10 per session
)
```

## 🔌 Manual Tracking (Advanced)

For advanced use cases, you can manually track messages:

```python
observatory = ObservatorySDK(...)
await observatory.start()

# Track a message
await observatory.track_message({
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {...},
    "id": 1
}, session_id="sess_123")

# Get statistics
stats = observatory.get_stats()
print(f"Tracked {stats['interceptor_stats']['total_count']} messages")
```

## 📚 API Reference

### ObservatorySDK

The main SDK class.

```python
class ObservatorySDK:
    def __init__(
        self,
        api_key: str,
        server_name: str,
        server_version: str,
        description: Optional[str] = None,
        capabilities: Optional[List[str]] = None,
        config: Optional[ObservatoryConfig] = None,
        base_url: str = "http://localhost:8081"
    )
    
    async def start(self) -> str  # Returns server_id
    async def stop(self)
    def wrap_server(self, server: Server) -> Server
    async def track_message(self, message: dict, session_id: Optional[str] = None)
    
    def is_enabled(self) -> bool
    def get_server_id(self) -> Optional[str]
    def get_stats(self) -> Dict[str, Any]
```

### Configuration Classes

See [Configuration](#configuration) section for detailed configuration options.

## 🧪 Testing

Run the test suite:

```bash
pytest
```

With coverage:

```bash
pytest --cov=observatory_mcp --cov-report=html
```

## 📖 Examples

See the [examples/](examples/) directory for complete examples:

- [basic_integration.py](examples/basic_integration.py) - Simple integration
- [advanced_config.py](examples/advanced_config.py) - Custom configuration
- [custom_sampling.py](examples/custom_sampling.py) - Sampling strategies

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Documentation**: https://observatory.dev/docs/python-sdk
- **GitHub**: https://github.com/observatory/observatory
- **PyPI**: https://pypi.org/project/observatory-mcp/
- **Observatory Backend**: https://github.com/observatory/observatory-backend

## 💬 Support

- **Issues**: https://github.com/observatory/observatory/issues
- **Discord**: https://discord.gg/observatory
- **Email**: support@observatory.dev

## 🙏 Acknowledgments

Built with ❤️ for the MCP community.

Special thanks to:
- [Anthropic](https://www.anthropic.com/) for creating the Model Context Protocol
- The MCP community for feedback and contributions
