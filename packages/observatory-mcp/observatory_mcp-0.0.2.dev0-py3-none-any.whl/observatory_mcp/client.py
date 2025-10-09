"""HTTP client for Observatory backend API."""

import asyncio
import logging
from typing import Any

import httpx

from .exceptions import AuthenticationError, ConnectionError, ObservatoryError
from .models import (
    HeartbeatData,
    Message,
    Request,
    ServerRegistration,
    ServerUpdate,
)

logger = logging.getLogger(__name__)


class ObservatoryClient:
    """HTTP client for Observatory backend REST API."""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        timeout: float = 30.0,
        max_retries: int = 3,
    ):
        """Initialize Observatory client.

        Args:
            base_url: Base URL of Observatory backend
            api_key: API key for authentication
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries

        self._client: httpx.AsyncClient | None = None
        self._session_active = False

    async def __aenter__(self) -> "ObservatoryClient":
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()

    async def start(self) -> None:
        """Start the HTTP client session."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "User-Agent": "Observatory-Python-SDK/0.1.0",
                },
            )
            self._session_active = True
            logger.debug("Observatory client started")

    async def close(self) -> None:
        """Close the HTTP client session."""
        if self._client:
            await self._client.aclose()
            self._client = None
            self._session_active = False
            logger.debug("Observatory client closed")

    async def register_server(
        self,
        name: str,
        version: str,
        description: str | None = None,
        capabilities: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        observatory_config: dict[str, Any] | None = None,
    ) -> ServerRegistration:
        """Register a new MCP server with Observatory.

        Args:
            name: Server name
            version: Server version
            description: Server description
            capabilities: List of server capabilities
            metadata: Additional metadata
            observatory_config: Observatory configuration

        Returns:
            ServerRegistration object

        Raises:
            AuthenticationError: If authentication fails
            ConnectionError: If connection fails
        """
        payload = {
            "name": name,
            "version": version,
            "description": description or f"MCP Server {name}",
            "capabilities": capabilities or ["tools", "resources", "prompts"],
            "metadata": metadata or {},
            "observatory_config": observatory_config or {},
        }

        response = await self._request("POST", "/api/v1/servers", json=payload)
        data = response.get("data", {})

        return ServerRegistration(
            server_id=data["server_id"],
            name=data["name"],
            version=data["version"],
            status=data["status"],
            api_key=data.get("api_key", self.api_key),
            capabilities=data.get("capabilities", []),
            created_at=data["created_at"],
            registration_url=data.get("registration_url", ""),
        )

    async def stream_message(self, server_id: str, message: Message) -> dict[str, Any]:
        """Stream a protocol message to Observatory.

        Args:
            server_id: Server ID
            message: Message to stream

        Returns:
            Response data
        """
        payload = {
            "message_id": message.message_id,
            "message_type": message.message_type,
            "direction": message.direction,
            "payload": message.payload,
            "timestamp": message.timestamp.isoformat(),
            "size": message.size,
            "session_id": message.session_id,
            "correlation_id": message.correlation_id,
            "transport": message.transport,
            "metadata": message.metadata,
        }

        return await self._request("POST", f"/api/v1/tracking/stream/{server_id}", json=payload)

    async def log_request(self, server_id: str, request: Request) -> dict[str, Any]:
        """Log a request to Observatory.

        Args:
            server_id: Server ID
            request: Request to log

        Returns:
            Response data
        """
        payload = {
            "request_id": request.request_id,
            "method": request.method,
            "start_time": request.start_time.isoformat(),
            "end_time": request.end_time.isoformat(),
            "duration": request.duration,
            "success": request.success,
            "request_size": request.request_size,
            "response_size": request.response_size,
            "session_id": request.session_id,
            "error_code": request.error_code,
            "error_message": request.error_message,
            "metadata": request.metadata,
        }

        return await self._request("POST", f"/api/v1/tracking/requests/{server_id}", json=payload)

    async def send_heartbeat(self, server_id: str, heartbeat: HeartbeatData) -> dict[str, Any]:
        """Send heartbeat to Observatory.

        Args:
            server_id: Server ID
            heartbeat: Heartbeat data

        Returns:
            Response data
        """
        payload = {
            "sdk_version": heartbeat.sdk_version,
            "status": heartbeat.status,
            "uptime_seconds": heartbeat.uptime_seconds,
            "active_connections": heartbeat.active_connections,
            "memory_usage_mb": heartbeat.memory_usage_mb,
            "cpu_usage_percent": heartbeat.cpu_usage_percent,
            "last_error": heartbeat.last_error,
            "metadata": heartbeat.metadata,
        }

        return await self._request("POST", f"/api/v1/tracking/heartbeat/{server_id}", json=payload)

    async def update_server(self, server_id: str, update: ServerUpdate) -> dict[str, Any]:
        """Update server configuration.

        Args:
            server_id: Server ID
            update: Server updates

        Returns:
            Response data
        """
        payload = update.model_dump(exclude_none=True)
        return await self._request("PUT", f"/api/v1/servers/{server_id}", json=payload)

    async def get_server(self, server_id: str) -> dict[str, Any]:
        """Get server information.

        Args:
            server_id: Server ID

        Returns:
            Server data
        """
        return await self._request("GET", f"/api/v1/servers/{server_id}")

    async def health_check(self) -> dict[str, Any]:
        """Check Observatory backend health.

        Returns:
            Health status
        """
        return await self._request("GET", "/health")

    async def _request(
        self,
        method: str,
        path: str,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make an HTTP request to Observatory backend.

        Args:
            method: HTTP method
            path: API path
            json: JSON payload
            params: Query parameters

        Returns:
            Response data

        Raises:
            AuthenticationError: If authentication fails
            ConnectionError: If connection fails
            ObservatoryError: For other errors
        """
        if not self._session_active:
            await self.start()

        for attempt in range(self.max_retries):
            try:
                response = await self._client.request(  # type: ignore[union-attr]
                    method, path, json=json, params=params
                )

                if response.status_code == 401:
                    raise AuthenticationError("Invalid API key")
                elif response.status_code == 403:
                    raise AuthenticationError("Access forbidden")
                elif response.status_code >= 500:
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(2**attempt)  # Exponential backoff
                        continue
                    raise ConnectionError(f"Server error: {response.status_code}")
                elif response.status_code >= 400:
                    error_data = response.json() if response.text else {}
                    error_msg = error_data.get("error", f"HTTP {response.status_code}")
                    raise ObservatoryError(error_msg)

                response.raise_for_status()
                return response.json() if response.text else {}

            except httpx.TimeoutException as e:
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2**attempt)
                    continue
                raise ConnectionError("Request timeout") from e
            except httpx.ConnectError as e:
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2**attempt)
                    continue
                raise ConnectionError(f"Connection failed: {str(e)}") from e
            except (AuthenticationError, ObservatoryError):
                raise
            except Exception as e:
                logger.error(f"Unexpected error in request: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2**attempt)
                    continue
                raise ObservatoryError(f"Request failed: {str(e)}") from e

        raise ConnectionError("Max retries exceeded")
