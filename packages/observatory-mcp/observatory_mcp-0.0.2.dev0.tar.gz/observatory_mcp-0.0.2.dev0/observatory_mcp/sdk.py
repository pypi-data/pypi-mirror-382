"""Main Observatory SDK class."""

import asyncio
import logging
import time
from typing import Any

try:
    from mcp.server import Server
except ImportError:
    Server = None  # type: ignore  # MCP not installed

from . import __version__
from .client import ObservatoryClient
from .config import ObservatoryConfig
from .exceptions import ConfigurationError, ObservatoryError
from .interceptor import MessageInterceptor
from .models import HeartbeatData, TrackingEvent
from .privacy import PrivacyManager

logger = logging.getLogger(__name__)


class ObservatorySDK:
    """Main SDK class for Observatory MCP integration."""

    def __init__(
        self,
        api_key: str,
        server_name: str,
        server_version: str,
        description: str | None = None,
        capabilities: list[str] | None = None,
        config: ObservatoryConfig | None = None,
        base_url: str = "http://localhost:8081",
    ):
        """Initialize Observatory SDK.

        Args:
            api_key: Observatory API key
            server_name: MCP server name
            server_version: MCP server version
            description: Server description
            capabilities: Server capabilities
            config: Observatory configuration
            base_url: Observatory backend URL

        Raises:
            ConfigurationError: If configuration is invalid
        """
        if not api_key:
            raise ConfigurationError("API key is required")
        if not server_name:
            raise ConfigurationError("Server name is required")
        if not server_version:
            raise ConfigurationError("Server version is required")

        self.api_key = api_key
        self.server_name = server_name
        self.server_version = server_version
        self.description = description or f"MCP Server {server_name}"
        self.capabilities = capabilities or ["tools", "resources", "prompts"]
        self.config = config or ObservatoryConfig.create_default()
        self.base_url = base_url

        # Components
        self.client = ObservatoryClient(base_url, api_key)
        self.privacy_manager = PrivacyManager(self.config.privacy)
        self.interceptor: MessageInterceptor | None = None

        # State
        self.server_id: str | None = None
        self._started = False
        self._start_time = time.time()
        self._event_queue: asyncio.Queue | None = None
        self._worker_task: asyncio.Task | None = None
        self._heartbeat_task: asyncio.Task | None = None
        self._shutdown_event: asyncio.Event | None = None

        # Set logging level
        if self.config.debug:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=getattr(logging, self.config.log_level))

    async def start(self) -> str:
        """Start the Observatory SDK.

        Returns:
            Server ID assigned by Observatory

        Raises:
            ObservatoryError: If start fails
        """
        if self._started:
            logger.warning("SDK already started")
            return self.server_id  # type: ignore[return-value]

        try:
            logger.info(f"Starting Observatory SDK v{__version__}")

            # Initialize async objects
            if self._event_queue is None:
                self._event_queue = asyncio.Queue(maxsize=self.config.performance.max_queue_size)
            if self._shutdown_event is None:
                self._shutdown_event = asyncio.Event()

            # Start HTTP client
            await self.client.start()

            # Register server
            logger.info(f"Registering server: {self.server_name}")
            registration = await self.client.register_server(
                name=self.server_name,
                version=self.server_version,
                description=self.description,
                capabilities=self.capabilities,
            )
            self.server_id = registration.server_id
            logger.info(f"Server registered with ID: {self.server_id}")

            # Initialize interceptor
            self.interceptor = MessageInterceptor(
                server_id=self.server_id,
                config=self.config,
                privacy_manager=self.privacy_manager,
                event_callback=self._handle_event,
            )

            # Start background workers
            if self.config.performance.async_processing:
                self._worker_task = asyncio.create_task(self._process_events())
                logger.debug("Event processing worker started")

            # Start heartbeat
            self._heartbeat_task = asyncio.create_task(self._send_heartbeats())
            logger.debug("Heartbeat worker started")

            self._started = True
            logger.info("Observatory SDK started successfully")

            return self.server_id

        except Exception as e:
            logger.error(f"Failed to start Observatory SDK: {e}", exc_info=True)
            raise ObservatoryError(f"SDK start failed: {str(e)}") from e

    async def stop(self) -> None:
        """Stop the Observatory SDK."""
        if not self._started:
            return

        logger.info("Stopping Observatory SDK")
        self._shutdown_event.set()  # type: ignore[union-attr]

        # Cancel background tasks
        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass

        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass

        # Process remaining events
        await self._flush_events()

        # Close client
        await self.client.close()

        self._started = False
        logger.info("Observatory SDK stopped")

    def wrap_server(self, server: Any) -> Any:
        """Wrap an MCP server with Observatory tracking.

        This is the main integration point - wrap your MCP Server
        instance with this method to enable automatic tracking.

        Args:
            server: MCP Server instance

        Returns:
            Wrapped server (same instance, modified)

        Raises:
            ConfigurationError: If MCP package not installed or SDK not started
        """
        if Server is None:
            raise ConfigurationError("MCP package not installed. Install with: pip install mcp")

        if not isinstance(server, Server):
            raise ConfigurationError(f"Expected mcp.server.Server instance, got {type(server)}")

        if not self._started:
            # Auto-start if not started
            logger.warning("SDK not started, starting now...")
            asyncio.create_task(self.start())

        # Wrap server methods to intercept messages
        # This is a simplified approach - actual implementation would
        # need to hook into the MCP transport layer
        logger.info(f"Wrapping MCP server: {server.name}")

        # Store reference to interceptor in server for manual tracking if needed
        server._observatory_sdk = self  # type: ignore[attr-defined]
        server._observatory_interceptor = self.interceptor  # type: ignore[attr-defined]

        return server

    async def track_message(self, message: dict[str, Any], session_id: str | None = None) -> None:
        """Manually track a message (for advanced usage).

        Args:
            message: Message data
            session_id: Optional session ID
        """
        if self.interceptor:
            if message.get("method"):  # Request
                await self.interceptor.intercept_request(message, session_id)
            else:  # Response
                await self.interceptor.intercept_response(message, session_id)

    def _handle_event(self, event: TrackingEvent) -> None:
        """Handle a tracking event.

        Args:
            event: Tracking event to handle
        """
        if not self._event_queue:
            logger.warning("Event queue not initialized, dropping event")
            return

        if self.config.performance.async_processing:
            # Queue for background processing
            try:
                self._event_queue.put_nowait(event)
            except asyncio.QueueFull:
                logger.warning("Event queue full, dropping event")
        else:
            # Process synchronously
            asyncio.create_task(self._process_event(event))

    async def _process_events(self) -> None:
        """Background worker to process events."""
        batch = []
        last_flush = time.time()

        while not self._shutdown_event.is_set():  # type: ignore[union-attr]
            try:
                # Wait for event or timeout
                try:
                    event = await asyncio.wait_for(self._event_queue.get(), timeout=1.0)  # type: ignore[union-attr]
                    batch.append(event)
                except asyncio.TimeoutError:
                    pass

                # Flush batch if size or time threshold reached
                now = time.time()
                should_flush = (
                    len(batch) >= self.config.performance.batch_size
                    or (now - last_flush) >= self.config.performance.flush_interval
                )

                if should_flush and batch:
                    await self._flush_batch(batch)
                    batch.clear()
                    last_flush = now

            except Exception as e:
                logger.error(f"Error in event processing worker: {e}", exc_info=True)
                await asyncio.sleep(1)

        # Process remaining events
        if batch:
            await self._flush_batch(batch)

    async def _flush_batch(self, batch: list[TrackingEvent]) -> None:
        """Flush a batch of events to Observatory.

        Args:
            batch: List of events to flush
        """
        for event in batch:
            try:
                await self._process_event(event)
            except Exception as e:
                logger.error(f"Error processing event: {e}", exc_info=True)

    async def _process_event(self, event: TrackingEvent) -> None:
        """Process a single tracking event.

        Args:
            event: Event to process
        """
        try:
            if event.event_type == "message":
                from .models import Message

                message = Message(**event.data)
                await self.client.stream_message(self.server_id, message)  # type: ignore[arg-type]

            elif event.event_type == "request":
                from .models import Request

                request = Request(**event.data)
                await self.client.log_request(self.server_id, request)  # type: ignore[arg-type]

        except Exception as e:
            logger.error(f"Failed to process event: {e}", exc_info=True)

    async def _flush_events(self) -> None:
        """Flush all pending events."""
        logger.debug("Flushing pending events")
        batch = []
        while not self._event_queue.empty():  # type: ignore[union-attr]
            try:
                event = self._event_queue.get_nowait()  # type: ignore[union-attr]
                batch.append(event)
            except asyncio.QueueEmpty:
                break

        if batch:
            await self._flush_batch(batch)

    async def _send_heartbeats(self) -> None:
        """Background worker to send heartbeats."""
        while not self._shutdown_event.is_set():  # type: ignore[union-attr]
            try:
                await asyncio.sleep(self.config.performance.heartbeat_interval)

                if not self.server_id:
                    continue

                # Collect system metrics
                uptime = time.time() - self._start_time

                # Get memory usage
                try:
                    import psutil

                    process = psutil.Process()
                    memory_mb = process.memory_info().rss / 1024 / 1024
                    cpu_percent = process.cpu_percent(interval=0.1)
                except ImportError:
                    memory_mb = None
                    cpu_percent = None

                # Get stats from interceptor
                stats = self.interceptor.get_stats() if self.interceptor else {}

                heartbeat = HeartbeatData(
                    sdk_version=__version__,
                    status="healthy",
                    uptime_seconds=uptime,
                    active_connections=stats.get("active_sessions", 0),
                    memory_usage_mb=memory_mb,
                    cpu_usage_percent=cpu_percent,
                    metadata={
                        "queue_size": self._event_queue.qsize() if self._event_queue else 0,
                        "stats": stats,
                    },
                )

                await self.client.send_heartbeat(self.server_id, heartbeat)
                logger.debug("Heartbeat sent")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error sending heartbeat: {e}", exc_info=True)

    def is_enabled(self) -> bool:
        """Check if SDK is enabled and started.

        Returns:
            True if SDK is started
        """
        return self._started

    def get_server_id(self) -> str | None:
        """Get the server ID.

        Returns:
            Server ID or None if not started
        """
        return self.server_id

    def get_stats(self) -> dict[str, Any]:
        """Get SDK statistics.

        Returns:
            Statistics dictionary
        """
        return {
            "started": self._started,
            "server_id": self.server_id,
            "uptime_seconds": time.time() - self._start_time,
            "queue_size": self._event_queue.qsize() if self._event_queue else 0,
            "interceptor_stats": self.interceptor.get_stats() if self.interceptor else {},
        }

    async def __aenter__(self) -> "ObservatorySDK":
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.stop()
