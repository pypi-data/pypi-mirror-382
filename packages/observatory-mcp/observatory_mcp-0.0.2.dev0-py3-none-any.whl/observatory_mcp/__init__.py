"""Observatory MCP SDK - Python package for MCP server analytics and monitoring.

This SDK enables MCP server developers to add comprehensive observability
with just 2-3 lines of code.

Example:
    >>> from observatory_mcp import ObservatorySDK
    >>> from mcp.server import Server
    >>>
    >>> app = Server("my-mcp-server")
    >>> observatory = ObservatorySDK(
    ...     api_key="obs_live_xyz123",
    ...     server_name="my-mcp-server",
    ...     server_version="1.0.0"
    ... )
    >>> app = observatory.wrap_server(app)
"""

try:
    from importlib.metadata import version

    __version__ = version("observatory-mcp")
except Exception:
    __version__ = "unknown"

__author__ = "Observatory Team"
__license__ = "MIT"

from .config import ObservatoryConfig, PerformanceConfig, PrivacyConfig, SamplingConfig
from .exceptions import (
    AuthenticationError,
    ConfigurationError,
    ConnectionError,
    ObservatoryError,
    SamplingError,
)
from .sdk import ObservatorySDK

__all__ = [
    # Main SDK
    "ObservatorySDK",
    # Configuration
    "ObservatoryConfig",
    "SamplingConfig",
    "PrivacyConfig",
    "PerformanceConfig",
    # Exceptions
    "ObservatoryError",
    "ConfigurationError",
    "AuthenticationError",
    "ConnectionError",
    "SamplingError",
]
