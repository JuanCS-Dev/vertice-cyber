"""
Bridge WebSocket Manager - Handles real-time event streaming.
============================================================

Manages connections and broadcasts EventBus events to connected clients.
"""

import asyncio
import logging
from datetime import datetime
from typing import List
from fastapi import WebSocket, WebSocketDisconnect

from core.event_bus import get_event_bus, EventType, Event

logger = logging.getLogger("mcp_bridge.ws")


class ConnectionManager:
    """
    Manages WebSocket connections from multiple clients.
    """

    def __init__(self):
        """Initialize the manager."""
        self.active_connections: List[WebSocket] = []
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket) -> None:
        """Accept a new connection."""
        await websocket.accept()
        async with self._lock:
            self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total: {len(self.active_connections)}")

    async def disconnect(self, websocket: WebSocket) -> None:
        """Remove a connection."""
        async with self._lock:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, message: dict) -> None:
        """Send a message to all connected clients."""
        disconnected = []

        async with self._lock:
            for connection in self.active_connections:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Broadcast error: {e}")
                    disconnected.append(connection)

        for conn in disconnected:
            await self.disconnect(conn)

    @property
    def connection_count(self) -> int:
        """Number of active connections."""
        return len(self.active_connections)


# Singleton manager
connection_manager = ConnectionManager()

# Streamable events registry
STREAMABLE_EVENTS = [
    EventType.THREAT_DETECTED,
    EventType.THREAT_PREDICTED,
    EventType.THREAT_MITRE_MAPPED,
    EventType.ETHICS_VALIDATION_REQUESTED,
    EventType.ETHICS_VALIDATION_COMPLETED,
    EventType.ETHICS_HUMAN_REVIEW_REQUIRED,
    EventType.OSINT_INVESTIGATION_STARTED,
    EventType.OSINT_INVESTIGATION_COMPLETED,
    EventType.OSINT_BREACH_DETECTED,
    EventType.WARGAME_SIMULATION_STARTED,
    EventType.WARGAME_SIMULATION_COMPLETED,
    EventType.PATCH_VALIDATION_REQUESTED,
    EventType.PATCH_VALIDATION_COMPLETED,
    EventType.RECON_STARTED,
    EventType.RECON_COMPLETED,
    EventType.SYSTEM_TOOL_CALLED,
    EventType.SYSTEM_ERROR,
]


async def websocket_event_stream(websocket: WebSocket) -> None:
    """
    WebSocket handler for MCP events.
    """
    await connection_manager.connect(websocket)

    event_bus = get_event_bus()
    event_queue: asyncio.Queue[Event] = asyncio.Queue()

    async def on_event(event: Event) -> None:
        await event_queue.put(event)

    # Register handlers
    for event_type in STREAMABLE_EVENTS:
        event_bus.subscribe(event_type, on_event)

    # Send welcome message
    try:
        await websocket.send_json(
            {
                "type": "connected",
                "message": "Vértice Neural Link established",
                "timestamp": datetime.utcnow().isoformat(),
            }
        )
    except Exception:
        pass

    try:
        while True:
            try:
                # Wait for event with 30s heartbeat
                event = await asyncio.wait_for(event_queue.get(), timeout=30.0)
                await websocket.send_json(
                    {
                        "type": event.event_type.value,
                        "data": event.data,
                        "source": event.source,
                        "timestamp": event.timestamp.isoformat(),
                    }
                )
            except asyncio.TimeoutError:
                await websocket.send_json({"type": "heartbeat"})
    except WebSocketDisconnect:
        pass
    finally:
        await connection_manager.disconnect(websocket)
