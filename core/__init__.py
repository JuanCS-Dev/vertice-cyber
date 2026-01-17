# Vertice Cyber - Core Module
"""
Core utilities for Vertice Cyber MCP Tools.

Modules:
- settings.py: Pydantic Settings management
- event_bus.py: Async event bus for tool communication
- memory.py: Per-agent memory pool
"""

from typing import Any, Dict
import logging

logger = logging.getLogger(__name__)

# Version
__version__ = "2.0.0"
