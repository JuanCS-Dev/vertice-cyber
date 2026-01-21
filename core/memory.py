"""
Vertice Cyber - Per-Agent Memory Pool
Memória local para cada tool.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional
import json

from core.database import get_db

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
        self.db = get_db()  # Lazy load or imported? We need import inside method or globally.
        # Assuming generic 'get_db' import available in module scope now.

    async def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        """Armazena valor via SQLite."""
        # import json - REMOVED (Shadows outer scope)
        
        # Enforce max entries (eviction) - skipped for perf in Phase 3 or implement count check?
        # Let's simple insert/replace.
        
        await self.db.execute(
            """
            INSERT OR REPLACE INTO memory_store (agent_name, key, value, ttl_seconds, created_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            """,
            (self.agent_name, key, json.dumps(value, default=str), ttl_seconds)
        )

    async def get(self, key: str, default: Any = None) -> Any:
        """Recupera valor via SQLite."""
        # import json - REMOVED
        row = await self.db.fetch_one(
            "SELECT value, ttl_seconds, created_at FROM memory_store WHERE agent_name = ? AND key = ?",
            (self.agent_name, key)
        )
        if not row:
            return default
            
        # Check TTL
        if row['ttl_seconds']:
            created_at = datetime.strptime(row['created_at'], "%Y-%m-%d %H:%M:%S")
            age = (datetime.utcnow() - created_at).total_seconds()
            if age > row['ttl_seconds']:
                await self.delete(key)
                return default
                
        # Update access count
        await self.db.execute(
            "UPDATE memory_store SET access_count = access_count + 1 WHERE agent_name = ? AND key = ?",
            (self.agent_name, key)
        )
        
        return json.loads(row['value'])

    async def delete(self, key: str) -> bool:
        """Remove entrada."""
        cursor = await self.db.execute(
            "DELETE FROM memory_store WHERE agent_name = ? AND key = ?",
            (self.agent_name, key)
        )
        return cursor.rowcount > 0

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
