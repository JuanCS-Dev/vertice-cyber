"""
Vertice Cyber - Per-Agent Memory Pool
Memória local para cada tool.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


@dataclass
class MemoryEntry:
    """Uma entrada na memória."""

    key: str
    value: Any
    created_at: datetime = field(default_factory=datetime.utcnow)
    access_count: int = 0
    ttl_seconds: Optional[int] = None


class AgentMemory:
    """Memória local para um agent/tool."""

    def __init__(self, agent_name: str, max_entries: int = 10000):
        self.agent_name = agent_name
        self.max_entries = max_entries
        self._store: Dict[str, MemoryEntry] = {}

    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        """Armazena valor."""
        if len(self._store) >= self.max_entries:
            self._evict_oldest()

        self._store[key] = MemoryEntry(key=key, value=value, ttl_seconds=ttl_seconds)

    def get(self, key: str, default: Any = None) -> Any:
        """Recupera valor."""
        entry = self._store.get(key)
        if entry is None:
            return default

        if entry.ttl_seconds is not None:
            age = (datetime.utcnow() - entry.created_at).total_seconds()
            if age > entry.ttl_seconds:
                del self._store[key]
                return default

        entry.access_count += 1
        return entry.value

    def delete(self, key: str) -> bool:
        """Remove entrada."""
        if key in self._store:
            del self._store[key]
            return True
        return False

    def _evict_oldest(self) -> None:
        """Remove entrada mais antiga."""
        if self._store:
            oldest = min(self._store.keys(), key=lambda k: self._store[k].created_at)
            del self._store[oldest]


class MemoryPool:
    """Pool de memórias para todos os agents."""

    def __init__(self):
        self._memories: Dict[str, AgentMemory] = {}

    def get_memory(self, agent_name: str) -> AgentMemory:
        """Retorna memória para um agent."""
        if agent_name not in self._memories:
            self._memories[agent_name] = AgentMemory(agent_name)
        return self._memories[agent_name]


_memory_pool: Optional[MemoryPool] = None


def get_memory_pool() -> MemoryPool:
    """Retorna singleton do memory pool."""
    global _memory_pool
    if _memory_pool is None:
        _memory_pool = MemoryPool()
    return _memory_pool


def get_agent_memory(agent_name: str) -> AgentMemory:
    """Atalho para obter memória de um agent."""
    return get_memory_pool().get_memory(agent_name)
