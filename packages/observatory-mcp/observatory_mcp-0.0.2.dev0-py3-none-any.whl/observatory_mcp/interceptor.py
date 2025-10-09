"""Message interceptor for MCP protocol tracking."""

import asyncio
import logging
import random
import time
from collections.abc import Callable
from datetime import datetime
from typing import Any

from .config import ObservatoryConfig
from .models import Message, Request, TrackingEvent
from .privacy import PrivacyManager
from .utils import calculate_duration_ns, current_timestamp, generate_id, get_message_size

logger = logging.getLogger(__name__)


class MessageInterceptor:
    """Intercepts and tracks MCP protocol messages."""

    def __init__(
        self,
        server_id: str,
        config: ObservatoryConfig,
        privacy_manager: PrivacyManager,
        event_callback: Callable[[TrackingEvent], None] | None = None,
    ):
        """Initialize message interceptor.

        Args:
            server_id: Server ID for attribution
            config: Observatory configuration
            privacy_manager: Privacy manager instance
            event_callback: Callback for tracking events
        """
        self.server_id = server_id
        self.config = config
        self.privacy_manager = privacy_manager
        self.event_callback = event_callback

        self._request_map: dict[str, float] = {}  # request_id -> start_time
        self._session_counters: dict[str, int] = {}  # session_id -> request_count
        self._sample_counter = 0
        self._error_count = 0
        self._total_count = 0

    def should_sample(self, message: dict[str, Any], is_error: bool = False) -> bool:
        """Determine if message should be sampled.

        Args:
            message: Message data
            is_error: Whether this is an error case

        Returns:
            True if message should be sampled
        """
        # Always sample errors if configured
        if is_error and self.config.sampling.prioritize_errors:
            return True

        # Check session-based sampling (first/last N)
        session_id = message.get("session_id")
        if session_id:
            count = self._session_counters.get(session_id, 0)
            self._session_counters[session_id] = count + 1

            # Always sample first N per session
            if count < self.config.sampling.always_sample_first_n:
                return True

        # Standard sampling rate
        self._sample_counter += 1
        self._total_count += 1

        # Adaptive sampling: increase rate if error rate is high
        if self.config.sampling.adaptive_sampling:
            error_rate = self._error_count / max(self._total_count, 1)
            if error_rate > 0.05:  # 5% error rate
                # Double the sampling rate
                effective_rate = min(self.config.sampling.rate * 2, 1.0)
            else:
                effective_rate = self.config.sampling.rate
        else:
            effective_rate = self.config.sampling.rate

        # Deterministic sampling based on counter
        if effective_rate >= 1.0:
            return True
        elif effective_rate <= 0.0:
            return False
        else:
            return random.random() < effective_rate

    async def intercept_request(
        self, message: dict[str, Any], session_id: str | None = None
    ) -> dict[str, Any]:
        """Intercept and track a request message.

        Args:
            message: JSON-RPC request message
            session_id: Optional session ID

        Returns:
            Original message (passthrough)
        """
        if not self.config.track_protocol_messages:
            return message

        try:
            request_id = message.get("id", generate_id("req"))
            method = message.get("method", "unknown")
            start_time = time.time()

            # Store timing for response correlation
            self._request_map[str(request_id)] = start_time

            # Check if should sample
            if not self.should_sample(message):
                return message

            # Create message tracking event
            message_data = Message(
                message_id=generate_id("msg"),
                message_type=method,
                direction="client_to_server",
                payload=self.privacy_manager.mask_data(message),
                timestamp=current_timestamp(),
                size=get_message_size(message),
                session_id=session_id,
                correlation_id=str(request_id),
                transport="stdio",  # Default, can be overridden
                metadata={"method": method, "sampled": True},
            )

            # Create tracking event
            event = TrackingEvent(
                event_type="message",
                timestamp=current_timestamp(),
                data=message_data.model_dump(),
                sampled=True,
                priority=1,
            )

            # Send to callback
            if self.event_callback:
                await self._safe_callback(event)

        except Exception as e:
            logger.error(f"Error intercepting request: {e}", exc_info=True)

        return message

    async def intercept_response(
        self, message: dict[str, Any], session_id: str | None = None
    ) -> dict[str, Any]:
        """Intercept and track a response message.

        Args:
            message: JSON-RPC response message
            session_id: Optional session ID

        Returns:
            Original message (passthrough)
        """
        if not self.config.track_protocol_messages:
            return message

        try:
            request_id = str(message.get("id", ""))
            is_error = "error" in message
            if is_error:
                self._error_count += 1

            # Check if should sample
            if not self.should_sample(message, is_error=is_error):
                return message

            # Calculate request duration if we tracked the request
            duration_ns = None
            start_time = self._request_map.pop(request_id, None)
            if start_time:
                duration_ns = calculate_duration_ns(start_time)

            # Create message tracking event
            message_data = Message(
                message_id=generate_id("msg"),
                message_type="response",
                direction="server_to_client",
                payload=self.privacy_manager.mask_data(message),
                timestamp=current_timestamp(),
                size=get_message_size(message),
                session_id=session_id,
                correlation_id=request_id,
                transport="stdio",
                metadata={
                    "is_error": is_error,
                    "duration_ns": duration_ns,
                    "sampled": True,
                },
            )

            # Create tracking event
            event = TrackingEvent(
                event_type="message",
                timestamp=current_timestamp(),
                data=message_data.model_dump(),
                sampled=True,
                priority=2 if is_error else 1,
            )

            # Send to callback
            if self.event_callback:
                await self._safe_callback(event)

            # Track as request if we have timing
            if duration_ns is not None and self.config.track_performance_metrics:
                await self._track_request(  # type: ignore[arg-type]
                    request_id=request_id,
                    method=message.get("method", "response"),
                    start_time=start_time or time.time(),
                    duration_ns=duration_ns,
                    success=not is_error,
                    session_id=session_id,
                    error=message.get("error"),
                )

        except Exception as e:
            logger.error(f"Error intercepting response: {e}", exc_info=True)

        return message

    async def _track_request(
        self,
        request_id: str,
        method: str,
        start_time: float,
        duration_ns: int,
        success: bool,
        session_id: str | None = None,
        error: dict[str, Any] | None = None,
    ) -> None:
        """Track a request with performance metrics.

        Args:
            request_id: Request ID
            method: Request method
            start_time: Start timestamp
            duration_ns: Duration in nanoseconds
            success: Whether request succeeded
            session_id: Optional session ID
            error: Optional error information
        """
        try:
            start_dt = datetime.fromtimestamp(start_time)
            end_dt = current_timestamp()

            request = Request(
                request_id=request_id,
                method=method,
                start_time=start_dt,
                end_time=end_dt,
                duration=duration_ns,
                success=success,
                session_id=session_id,
                error_code=str(error.get("code")) if error else None,
                error_message=(
                    self.privacy_manager.sanitize_error_message(error.get("message", ""))
                    if error
                    else None
                ),
                metadata={"sampled": True},
            )

            event = TrackingEvent(
                event_type="request",
                timestamp=current_timestamp(),
                data=request.model_dump(),
                sampled=True,
                priority=2 if not success else 1,
            )

            if self.event_callback:
                await self._safe_callback(event)

        except Exception as e:
            logger.error(f"Error tracking request: {e}", exc_info=True)

    async def _safe_callback(self, event: TrackingEvent) -> None:
        """Safely call event callback.

        Args:
            event: Tracking event
        """
        try:
            if asyncio.iscoroutinefunction(self.event_callback):
                await self.event_callback(event)  # type: ignore
            else:
                self.event_callback(event)  # type: ignore
        except Exception as e:
            logger.error(f"Error in event callback: {e}", exc_info=True)

    def get_stats(self) -> dict[str, Any]:
        """Get interceptor statistics.

        Returns:
            Statistics dictionary
        """
        return {
            "total_count": self._total_count,
            "sample_counter": self._sample_counter,
            "error_count": self._error_count,
            "error_rate": self._error_count / max(self._total_count, 1),
            "active_sessions": len(self._session_counters),
            "pending_requests": len(self._request_map),
        }
