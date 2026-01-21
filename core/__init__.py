"""
Vertice Cyber Core Package
"""

# Monkeypatch RichHandler to fix FastMCP/Rich version incompatibility
# This treats the 'cause' of the logging errors in FastMCP 2.x with older Rich versions
try:
    from rich.logging import RichHandler

    _original_init = RichHandler.__init__

    def _patched_init(self, *args, **kwargs):
        # Remove unsupported argument for older rich versions (< 13.0)
        kwargs.pop("tracebacks_max_frames", None)
        _original_init(self, *args, **kwargs)

    RichHandler.__init__ = _patched_init
except ImportError:
    pass

from .settings import settings
from .event_bus import get_event_bus, EventType
from .memory import get_agent_memory

__all__ = [
    "Settings",
    "get_settings",
    "settings",
    "EventBus",
    "EventType",
    "Event",
    "get_event_bus",
    "MemoryPool",
    "AgentMemory",
    "get_memory_pool",
    "get_agent_memory",
]
