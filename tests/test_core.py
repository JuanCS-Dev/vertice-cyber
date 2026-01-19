"""
Tests for Vertice Cyber core modules.
"""

import pytest
from core.settings import get_settings
from core.memory import get_agent_memory, AgentMemory, get_memory_pool
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

    def test_get_memory_pool_returns_singleton(self):
        """Test that get_memory_pool returns singleton."""
        pool1 = get_memory_pool()
        pool2 = get_memory_pool()
        assert pool1 is pool2

    def test_memory_pool_get_memory(self):
        """Test memory pool creates agent memories."""
        pool = get_memory_pool()
        memory1 = pool.get_memory("agent1")
        memory2 = pool.get_memory("agent1")
        assert memory1 is memory2  # Same instance for same agent
        assert memory1.agent_name == "agent1"

    def test_agent_memory_operations(self):
        """Test agent memory operations."""
        memory = AgentMemory("test_agent", max_entries=10)

        # Test set/get
        memory.set("key1", "value1")
        assert memory.get("key1") == "value1"

        # Test default value
        assert memory.get("nonexistent", "default") == "default"

        # Test delete
        assert memory.delete("key1") is True
        assert memory.get("key1") is None
        assert memory.delete("key1") is False  # Already deleted

        # Test TTL
        import time

        memory.set("ttl_key", "ttl_value", ttl_seconds=1)
        assert memory.get("ttl_key") == "ttl_value"
        time.sleep(1.1)  # Wait for TTL to expire
        assert memory.get("ttl_key") is None

    def test_agent_memory_eviction(self):
        """Test memory eviction when max_entries is reached."""
        memory = AgentMemory("test_agent", max_entries=2)

        memory.set("key1", "value1")
        memory.set("key2", "value2")
        memory.set("key3", "value3")  # Should evict oldest (key1)

        assert memory.get("key1") is None  # Evicted
        assert memory.get("key2") == "value2"
        assert memory.get("key3") == "value3"

    @pytest.mark.asyncio
    async def test_event_bus_subscribe_and_emit(self):
        """Test event bus subscribe and emit functionality."""
        bus = EventBus()
        events_received = []

        async def handler(event):
            events_received.append(event)

        # Subscribe to event
        bus.subscribe(EventType.SYSTEM_HEALTH_CHECK, handler)

        # Emit event
        event = await bus.emit(
            EventType.SYSTEM_HEALTH_CHECK, {"status": "ok"}, "test_source"
        )

        # Check event was created correctly
        assert event.event_type == EventType.SYSTEM_HEALTH_CHECK
        assert event.data == {"status": "ok"}
        assert event.source == "test_source"

        # Check handler was called (allow some time for async)
        import asyncio

        await asyncio.sleep(0.1)
        assert len(events_received) == 1
        assert events_received[0].data == {"status": "ok"}

    def test_event_bus_get_history(self):
        """Test event bus history retrieval."""
        bus = EventBus()

        # Get empty history
        history = bus.get_history()
        assert len(history) == 0

        # Get history with limit
        history = bus.get_history(limit=5)
        assert len(history) == 0

    def test_event_bus_decorator(self):
        """Test event bus decorator functionality."""
        bus = EventBus()
        events_received = []

        @bus.on(EventType.SYSTEM_ERROR)
        async def error_handler(event):
            events_received.append(event)

        # Check handler was registered
        assert EventType.SYSTEM_ERROR in bus._handlers
        assert len(bus._handlers[EventType.SYSTEM_ERROR]) == 1

    @pytest.mark.asyncio
    async def test_event_bus_max_history(self):
        """Test event bus history limit."""
        bus = EventBus()
        bus._max_history = 2

        # Emit multiple events
        await bus.emit(EventType.SYSTEM_HEALTH_CHECK, {"test": 1}, "source1")
        await bus.emit(EventType.SYSTEM_HEALTH_CHECK, {"test": 2}, "source2")
        await bus.emit(EventType.SYSTEM_HEALTH_CHECK, {"test": 3}, "source3")

        # Check only last 2 events are kept
        history = bus.get_history()
        assert len(history) == 2
        assert history[0].data == {"test": 2}
        assert history[1].data == {"test": 3}

    @pytest.mark.asyncio
    async def test_event_bus_exception_handling(self):
        """Test event bus handles handler exceptions."""
        bus = EventBus()
        events_processed = []

        async def good_handler(event):
            events_processed.append("good")

        async def bad_handler(event):
            raise Exception("Handler failed")

        async def another_good_handler(event):
            events_processed.append("another_good")

        # Subscribe handlers
        bus.subscribe(EventType.SYSTEM_ERROR, good_handler)
        bus.subscribe(EventType.SYSTEM_ERROR, bad_handler)
        bus.subscribe(EventType.SYSTEM_ERROR, another_good_handler)

        # Emit event - should not crash despite bad handler
        event = await bus.emit(EventType.SYSTEM_ERROR, {"error": "test"}, "source")

        # Check event was created
        assert event.event_type == EventType.SYSTEM_ERROR

        # Check good handlers still ran (async timing)
        import asyncio

        await asyncio.sleep(0.1)
        assert "good" in events_processed
        assert "another_good" in events_processed
