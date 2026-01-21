
import asyncio
import logging
import re
import json
from typing import Callable, Dict, Set, Pattern
from core.events.types import Event
from core.database import get_db

logger = logging.getLogger(__name__)

# Type alias for handlers
EventHandler = Callable[[Event], asyncio.Task]

class EventBus:
    def __init__(self):
        self._subscribers: Dict[Pattern, Set[EventHandler]] = {}
        self._db = get_db()
        self._ws_manager = None  # To be injected

    def set_ws_manager(self, ws_manager):
        self._ws_manager = ws_manager

    def subscribe(self, pattern: str, handler: EventHandler):
        """Subscribe to events matching regex pattern."""
        regex = re.compile(pattern)
        if regex not in self._subscribers:
            self._subscribers[regex] = set()
        self._subscribers[regex].add(handler)
        logger.debug(f"Subscribed handler to pattern: {pattern}")

    async def emit(self, event: Event):
        """
        Process event:
        1. Persist to SQLite
        2. Broadcast via WebSocket
        3. Notify internal subscribers
        """
        # 1. Persist
        try:
            await self._persist_event(event)
        except Exception as e:
            logger.error(f"Failed to persist event {event.event_id}: {e}")

        # 2. WebSocket Broadcast
        if self._ws_manager:
            try:
                # We can implement room filtering here if needed
                await self._ws_manager.broadcast(event.to_dict())
            except Exception as e:
                logger.error(f"WS Broadcast failed: {e}")

        # 3. Internal Subscribers
        tasks = []
        for pattern, handlers in self._subscribers.items():
            if pattern.match(event.event_type):
                for handler in handlers:
                    tasks.append(asyncio.create_task(self._safe_handle(handler, event)))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _persist_event(self, event: Event):
        """Save event to database."""
        await self._db.execute(
            """
            INSERT INTO events (event_id, correlation_id, event_type, source, payload, level, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event.event_id,
                event.correlation_id,
                event.event_type,
                event.source,
                json.dumps(event.payload),
                event.level,
                event.timestamp
            )
        )

    async def _safe_handle(self, handler: EventHandler, event: Event):
        try:
            await handler(event)
        except Exception as e:
            logger.error(f"Error in event handler: {e}")

# Singleton
_event_bus = None

def get_event_bus() -> EventBus:
    global _event_bus
    if _event_bus is None:
        _event_bus = EventBus()
    return _event_bus
