"""Data models for Observatory SDK using Pydantic."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class ServerRegistration(BaseModel):
    """Response from server registration."""

    server_id: str
    name: str
    version: str
    status: str
    api_key: str
    capabilities: list[str]
    created_at: datetime
    registration_url: str


class Message(BaseModel):
    """Protocol message model."""

    message_id: str
    message_type: str
    direction: str  # client_to_server or server_to_client
    payload: dict[str, Any]
    timestamp: datetime
    size: int
    session_id: str | None = None
    correlation_id: str | None = None
    transport: str = "stdio"
    metadata: dict[str, Any] | None = None


class Request(BaseModel):
    """Request tracking model."""

    request_id: str
    method: str
    start_time: datetime
    end_time: datetime
    duration: int  # nanoseconds
    success: bool
    request_size: int | None = None
    response_size: int | None = None
    session_id: str | None = None
    error_code: str | None = None
    error_message: str | None = None
    metadata: dict[str, Any] | None = None


class HeartbeatData(BaseModel):
    """Heartbeat status data."""

    sdk_version: str
    status: str = "healthy"
    uptime_seconds: float
    active_connections: int = 0
    memory_usage_mb: float | None = None
    cpu_usage_percent: float | None = None
    last_error: str | None = None
    metadata: dict[str, Any] | None = None


class ServerUpdate(BaseModel):
    """Server update request."""

    name: str | None = None
    description: str | None = None
    status: str | None = None
    metadata: dict[str, Any] | None = None
    observatory_config: dict[str, Any] | None = None


class TrackingEvent(BaseModel):
    """Internal event for tracking."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    event_type: str  # message, request, error, metric
    timestamp: datetime
    data: dict[str, Any]
    sampled: bool = True
    priority: int = 0  # Higher = more important


class PerformanceMetrics(BaseModel):
    """Performance metrics snapshot."""

    timestamp: datetime
    request_count: int = 0
    error_count: int = 0
    avg_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    memory_usage_mb: float = 0.0
    active_sessions: int = 0
