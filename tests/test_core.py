"""
Tests for Vertice Cyber core modules.
"""

import pytest
from core.settings import get_settings, Settings
from core.memory import get_agent_memory, AgentMemory
from core.event_bus import get_event_bus, EventBus, EventType


class TestSettings:
    """Test settings management."""

    def test_get_settings_returns_singleton(self):
        """Test that get_settings returns a singleton."""
        settings1 = get_settings()
        settings2 = get_settings()
        assert settings1 is settings2

    def test_settings_has_required_attributes(self):
        """Test that settings has all required attributes."""
        settings = get_settings()
        assert hasattr(settings, "project_name")
        assert hasattr(settings, "version")
        assert hasattr(settings, "api_keys")
        assert hasattr(settings, "server")
        assert hasattr(settings, "ethics")


class TestMemory:
    """Test memory management."""

    def test_get_agent_memory_creates_instance(self):
        """Test that get_agent_memory creates an AgentMemory instance."""
        memory = get_agent_memory("test_agent")
        assert isinstance(memory, AgentMemory)
        assert memory.agent_name == "test_agent"

    def test_agent_memory_set_get(self):
        """Test basic set/get operations."""
        memory = AgentMemory("test")
        memory.set("key", "value")
        assert memory.get("key") == "value"

    def test_agent_memory_get_default(self):
        """Test get with default value."""
        memory = AgentMemory("test")
        assert memory.get("nonexistent", "default") == "default"


class TestEventBus:
    """Test event bus."""

    def test_get_event_bus_returns_singleton(self):
        """Test that get_event_bus returns a singleton."""
        bus1 = get_event_bus()
        bus2 = get_event_bus()
        assert bus1 is bus2

    def test_event_bus_creation(self):
        """Test event bus creation."""
        bus = EventBus()
        assert isinstance(bus, EventBus)
        assert len(bus._handlers) == 0

    @pytest.mark.asyncio
    async def test_event_emit_without_handlers(self):
        """Test emitting event without handlers."""
        bus = EventBus()
        event = await bus.emit(
            EventType.SYSTEM_HEALTH_CHECK, {"test": "data"}, "test_source"
        )
        assert event.event_type == EventType.SYSTEM_HEALTH_CHECK
        assert event.data == {"test": "data"}
        assert event.source == "test_source"
