
"""
Bridge Context - Live Context for MCP Tool Execution.
====================================================

Authentic FastMCP Context proxy that streams events to the Neural Mesh.
"""

import logging
from typing import Any, Dict, List, Optional
from uuid import uuid4
from datetime import datetime

from core.events.event_bus import get_event_bus
from core.events.types import Event, EventType

logger = logging.getLogger("mcp_bridge.context")

class LiveContext:
    """
    Real-time Context connecting backend execution to EventBus.
    
    Streams logs immediately via WebSocket while keeping local buffer
    for generic HTTP responses.
    """
    
    def __init__(self, request_id: Optional[str] = None, agent_id: Optional[str] = None):
        self.request_id = request_id or str(uuid4())
        self.agent_id = agent_id or "system"
        self.logs: List[Dict[str, Any]] = []
        self.event_bus = get_event_bus()

    async def info(self, message: str) -> None:
        await self._emit("INFO", message)

    async def warn(self, message: str) -> None:
        await self._emit("WARN", message)

    async def warning(self, message: str) -> None:
        await self.warn(message)

    async def error(self, message: str) -> None:
        await self._emit("ERROR", message)

    async def _emit(self, level: str, message: str) -> None:
        # 1. Local Buffer (Legacy HTTP Support)
        log_entry = {
            "level": level,
            "message": message,
            "request_id": self.request_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.logs.append(log_entry)
        
        # 2. Neural Mesh Broadcast (Real-Time)
        try:
            await self.event_bus.emit(Event(
                event_type=EventType.LOG, # Using "agent.log" from types
                source=self.agent_id,
                level=level,
                payload={
                    "message": message,
                    "agent_id": self.agent_id,
                    "request_id": self.request_id
                }
            ))
            logger.debug(f"Streamed log: {message}")
        except Exception as e:
            logger.error(f"Failed to stream log: {e}")

    def get_logs(self) -> List[Dict[str, Any]]:
        return self.logs

def create_live_context(request_id: Optional[str] = None, agent_id: Optional[str] = None) -> LiveContext:
    return LiveContext(request_id, agent_id)

# Backward Compatibility
create_mock_context = create_live_context
