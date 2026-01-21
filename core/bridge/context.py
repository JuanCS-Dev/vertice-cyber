"""
Bridge Context - Mock Context for MCP Tool Execution.
====================================================

Simulates FastMCP Context for tools called via HTTP Bridge.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

logger = logging.getLogger("mcp_bridge.context")


class MockContext:
    """
    Mock of FastMCP Context for use in the HTTP Bridge.

    Implements mandatory async methods: info, warn, error.
    """

    def __init__(self, request_id: Optional[str] = None):
        """
        Initialize the context.

        Args:
            request_id: Unique ID for the request.
        """
        self.request_id = request_id or str(uuid4())
        self.logs: List[Dict[str, Any]] = []
        self._start_time = datetime.utcnow()

    async def info(self, message: str) -> None:
        """Log info message."""
        self._add_log("INFO", message)
        logger.info(f"[{self.request_id[:8]}] {message}")

    async def warn(self, message: str) -> None:
        """Log warning message."""
        self._add_log("WARN", message)
        logger.warning(f"[{self.request_id[:8]}] {message}")

    async def warning(self, message: str) -> None:
        """Alias for warn."""
        await self.warn(message)

    async def error(self, message: str) -> None:
        """Log error message."""
        self._add_log("ERROR", message)
        logger.error(f"[{self.request_id[:8]}] {message}")

    def _add_log(self, level: str, message: str) -> None:
        """Internal helper to add log entry."""
        self.logs.append(
            {
                "level": level,
                "message": message,
                "request_id": self.request_id,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    def get_logs(self) -> List[Dict[str, Any]]:
        """Return all logs captured in this context."""
        return self.logs


def create_mock_context(request_id: Optional[str] = None) -> MockContext:
    """
    Factory to create a new MockContext.

    Args:
        request_id: Optional UUID.

    Returns:
        A configured MockContext instance.
    """
    return MockContext(request_id)
