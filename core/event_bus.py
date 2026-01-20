"""
Vertice Cyber - Async Event Bus
Comunicação in-memory entre tools usando pub/sub pattern.
"""

import asyncio
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Coroutine, Dict, List, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)


class EventType(str, Enum):
    """Tipos de eventos suportados."""

    # Governance
    ETHICS_VALIDATION_REQUESTED = "ethics.validation.requested"
    ETHICS_VALIDATION_COMPLETED = "ethics.validation.completed"
    ETHICS_HUMAN_REVIEW_REQUIRED = "ethics.human_review.required"

    # Intelligence
    OSINT_INVESTIGATION_STARTED = "osint.investigation.started"
    OSINT_INVESTIGATION_COMPLETED = "osint.investigation.completed"
    OSINT_BREACH_DETECTED = "osint.breach.detected"

    # Threat
    THREAT_DETECTED = "threat.detected"
    THREAT_PREDICTED = "threat.predicted"
    THREAT_MITRE_MAPPED = "threat.mitre.mapped"

    # Immune
    IMMUNE_RESPONSE_TRIGGERED = "immune.response.triggered"
    IMMUNE_ANTIBODY_DEPLOYED = "immune.antibody.deployed"

    # Offensive - Wargame
    WARGAME_SIMULATION_STARTED = "wargame.simulation.started"
    WARGAME_SIMULATION_COMPLETED = "wargame.simulation.completed"

    # Offensive - Patch ML
    PATCH_VALIDATION_REQUESTED = "patch.validation.requested"
    PATCH_VALIDATION_COMPLETED = "patch.validation.completed"

    # CyberSec Basic
    RECON_STARTED = "cybersec.recon.started"
    RECON_COMPLETED = "cybersec.recon.completed"
    VULN_SCAN_STARTED = "cybersec.vuln_scan.started"
    VULN_SCAN_COMPLETED = "cybersec.vuln_scan.completed"

    # System
    SYSTEM_HEALTH_CHECK = "system.health.check"
    SYSTEM_ERROR = "system.error"
    SYSTEM_TOOL_CALLED = "system.tool.called"


@dataclass
class Event:
    """Estrutura de um evento."""

    event_type: EventType
    data: Dict[str, Any]
    source: str
    event_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    correlation_id: Optional[str] = None


EventHandler = Callable[[Event], Coroutine[Any, Any, None]]


class EventBus:
    """Event Bus assíncrono para comunicação entre tools."""

    def __init__(self):
        self._handlers: Dict[EventType, List[EventHandler]] = defaultdict(list)
        self._event_history: List[Event] = []
        self._max_history: int = 1000

    def on(self, event_type: EventType):
        """Decorator para registrar handler."""

        def decorator(handler: EventHandler) -> EventHandler:
            self._handlers[event_type].append(handler)
            return handler

        return decorator

    def subscribe(self, event_type: EventType, handler: EventHandler) -> None:
        """Registra handler programaticamente."""
        self._handlers[event_type].append(handler)

    async def emit(
        self,
        event_type: EventType,
        data: Dict[str, Any],
        source: str,
        correlation_id: Optional[str] = None,
    ) -> Event:
        """Emite evento para handlers."""
        event = Event(
            event_type=event_type,
            data=data,
            source=source,
            correlation_id=correlation_id,
        )

        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history.pop(0)

        handlers = self._handlers.get(event_type, [])
        for handler in handlers:
            asyncio.create_task(self._safe_call(handler, event))

        return event

    async def _safe_call(self, handler: EventHandler, event: Event) -> None:
        """Chama handler com tratamento de erro."""
        try:
            await handler(event)
        except Exception as e:
            logger.error(f"Error in handler {handler.__name__}: {e}")

    def get_history(
        self, event_type: Optional[EventType] = None, limit: int = 100
    ) -> List[Event]:
        """Retorna histórico filtrado."""
        events = self._event_history
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        return events[-limit:]


_event_bus: Optional[EventBus] = None


def get_event_bus() -> EventBus:
    """Retorna singleton do event bus."""
    global _event_bus
    if _event_bus is None:
        _event_bus = EventBus()
    return _event_bus
