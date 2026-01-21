
"""
Bridge WebSocket Manager - Neural Mesh Uplink.
============================================================

Manages connections and broadcasts Neural Mesh events to connected clients.
Supports Room-based subscription logic (Phase 1).
"""

import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Set
from fastapi import WebSocket, WebSocketDisconnect

from core.events.event_bus import get_event_bus

logger = logging.getLogger("mcp_bridge.ws")

class ConnectionManager:
    """
    Manages WebSocket connections and channel subscriptions.
    """

    def __init__(self):
        self.active_connections: List[WebSocket] = []
        # Room logic: room_id -> Set[WebSocket]
        self.rooms: Dict[str, Set[WebSocket]] = {}
        self._lock = asyncio.Lock()
        
        # Inject self into EventBus
        event_bus = get_event_bus()
        event_bus.set_ws_manager(self)

    async def connect(self, websocket: WebSocket) -> None:
        """Accept a new connection."""
        await websocket.accept()
        async with self._lock:
            self.active_connections.append(websocket)
        logger.info(f"Neural Link established. Total nodes: {len(self.active_connections)}")

    async def disconnect(self, websocket: WebSocket) -> None:
        """Remove a connection."""
        async with self._lock:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
            
            # Remove from all rooms
            for room_clients in self.rooms.values():
                if websocket in room_clients:
                    room_clients.remove(websocket)
                    
        logger.info(f"Neural Link severed. Total nodes: {len(self.active_connections)}")

    async def join_room(self, websocket: WebSocket, room_id: str) -> None:
        """Subscribe socket to a specific room/channel."""
        async with self._lock:
            if room_id not in self.rooms:
                self.rooms[room_id] = set()
            self.rooms[room_id].add(websocket)
        logger.debug(f"Node joined room: {room_id}")

    async def broadcast(self, message: dict) -> None:
        """
        Send a message to all connected clients.
        Future optimization: Implement granular room filtering based on message topic.
        """
        disconnected = []
        
        # For Phase 1, we broadcast "global" events to everyone.
        # Future: Filter by message['topic'] vs subscribed rooms.
        async with self._lock:
            for connection in self.active_connections:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Broadcast packet loss: {e}")
                    disconnected.append(connection)

        for conn in disconnected:
            await self.disconnect(conn)

    @property
    def connection_count(self) -> int:
        return len(self.active_connections)


# Singleton manager
connection_manager = ConnectionManager()

async def websocket_event_stream(websocket: WebSocket) -> None:
    """
    WebSocket handler for MCP events.
    Handles the connection lifecycle and incoming control commands.
    """
    await connection_manager.connect(websocket)

    try:
        # Send handshake
        await websocket.send_json({
            "type": "system.connected",
            "message": "Neural Mesh Uplink Active",
            "timestamp": datetime.utcnow().isoformat(),
        })

        while True:
            try:
                # Wait for commands from Frontend (C2)
                # Keepalive / Command parsing
                data = await websocket.receive_json()
                
                cmd_type = data.get("type")
                if cmd_type == "subscribe":
                    room = data.get("channel")
                    if room:
                        await connection_manager.join_room(websocket, room)
                
                elif cmd_type == "heartbeat":
                    await websocket.send_json({"type": "system.heartbeat_ack"})
                    
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Uplink error: {e}")
                break

    finally:
        await connection_manager.disconnect(websocket)
