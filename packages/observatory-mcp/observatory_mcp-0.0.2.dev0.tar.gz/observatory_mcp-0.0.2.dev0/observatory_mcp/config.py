"""Configuration classes for Observatory SDK."""

from dataclasses import dataclass, field


@dataclass
class SamplingConfig:
    """Configuration for event sampling."""

    rate: float = 1.0  # 0.0 to 1.0 (100% default)
    adaptive_sampling: bool = True
    prioritize_errors: bool = True
    max_events_per_second: int = 1000
    always_sample_first_n: int = 10  # Per session
    always_sample_last_n: int = 10  # Per session

    def __post_init__(self) -> None:
        """Validate configuration."""
        if not 0.0 <= self.rate <= 1.0:
            raise ValueError("Sampling rate must be between 0.0 and 1.0")
        if self.max_events_per_second < 1:
            raise ValueError("max_events_per_second must be at least 1")


@dataclass
class PrivacyConfig:
    """Configuration for privacy and data protection."""

    enable_pii_detection: bool = True
    hash_identifiers: bool = True
    sensitive_field_masks: list[str] = field(
        default_factory=lambda: [
            "password",
            "token",
            "api_key",
            "secret",
            "authorization",
            "ssn",
            "credit_card",
        ]
    )
    max_message_size_capture: int = 10_000  # bytes
    data_retention_days: int = 90
    redact_errors: bool = True  # Redact PII from error messages


@dataclass
class PerformanceConfig:
    """Configuration for performance optimization."""

    async_processing: bool = True
    batch_size: int = 10
    flush_interval: float = 5.0  # seconds
    heartbeat_interval: float = 30.0  # seconds
    compression_enabled: bool = False
    memory_limit_mb: int = 100
    max_queue_size: int = 1000


@dataclass
class OutputConfig:
    """Configuration for data output."""

    local_storage: bool = False
    local_storage_path: str | None = None
    export_format: str = "json"  # json, prometheus, custom
    real_time_streaming: bool = True


@dataclass
class AlertConfig:
    """Configuration for alerting thresholds."""

    error_rate_threshold: float = 0.05  # 5%
    latency_threshold_ms: float = 1000.0
    memory_threshold_mb: float = 500.0
    custom_thresholds: dict[str, float] = field(default_factory=dict)


@dataclass
class ObservatoryConfig:
    """Main configuration for Observatory SDK."""

    # Tracking controls
    track_protocol_messages: bool = True
    track_performance_metrics: bool = True
    track_behavioral_analytics: bool = False
    track_security_monitoring: bool = False

    # Sub-configurations
    sampling: SamplingConfig = field(default_factory=SamplingConfig)
    privacy: PrivacyConfig = field(default_factory=PrivacyConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    alerts: AlertConfig = field(default_factory=AlertConfig)

    # Debugging
    debug: bool = False
    log_level: str = "INFO"

    @classmethod
    def create_default(cls) -> "ObservatoryConfig":
        """Create default configuration."""
        return cls()

    @classmethod
    def create_minimal(cls) -> "ObservatoryConfig":
        """Create minimal configuration with lower overhead."""
        return cls(
            track_behavioral_analytics=False,
            track_security_monitoring=False,
            sampling=SamplingConfig(rate=0.1, adaptive_sampling=False),
            performance=PerformanceConfig(
                batch_size=50, flush_interval=10.0, heartbeat_interval=60.0
            ),
        )

    @classmethod
    def create_high_performance(cls) -> "ObservatoryConfig":
        """Create configuration optimized for high-volume servers."""
        return cls(
            sampling=SamplingConfig(rate=0.01, adaptive_sampling=True),
            performance=PerformanceConfig(
                batch_size=100,
                flush_interval=1.0,
                heartbeat_interval=60.0,
                memory_limit_mb=200,
                max_queue_size=5000,
            ),
        )
