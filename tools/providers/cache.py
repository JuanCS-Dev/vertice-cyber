"""Cache Provider com Redis e JSON fallback."""

import os
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime

from core.feature_flags import get_feature_flags

logger = logging.getLogger(__name__)


class RedisBackend:
    """Backend Redis."""

    def __init__(self):
        self._client = None
        self._available = self._try_connect()

    def _try_connect(self) -> bool:
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        try:
            import redis

            self._client = redis.from_url(redis_url, decode_responses=True)
            self._client.ping()
            return True
        except Exception:
            return False

    @property
    def is_available(self) -> bool:
        return self._available

    def get(self, key: str) -> Optional[str]:
        if not self._available:
            return None
        try:
            return self._client.get(f"vertice:cache:{key}")
        except Exception:
            self._available = False
            return None

    def set(self, key: str, value: str, ttl: int) -> None:
        if self._available:
            try:
                self._client.setex(f"vertice:cache:{key}", ttl, value)
            except Exception:
                self._available = False


class JSONFileBackend:
    """Backend JSON file."""

    CACHE_FILE = Path.home() / ".vertice" / "cache.json"

    def __init__(self):
        self.CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        self._cache = self._load()

    def _load(self) -> Dict:
        if self.CACHE_FILE.exists():
            try:
                return json.loads(self.CACHE_FILE.read_text())
            except Exception:
                return {}
        return {}

    def _save(self) -> None:
        try:
            self.CACHE_FILE.write_text(json.dumps(self._cache, indent=2))
        except Exception as e:
            logger.error(f"Failed to save cache file: {e}")

    def get(self, key: str) -> Optional[str]:
        entry = self._cache.get(key)
        if entry and entry.get("expires_at", 0) > datetime.utcnow().timestamp():
            return entry.get("value")
        return None

    def set(self, key: str, value: str, ttl: int) -> None:
        self._cache[key] = {
            "value": value,
            "expires_at": datetime.utcnow().timestamp() + ttl,
        }
        self._save()


class SmartCache:
    """Cache inteligente: Redis se disponível, senão JSON."""

    def __init__(self):
        self.flags = get_feature_flags()
        self._redis = RedisBackend()
        self._json = JSONFileBackend()
        # Seleciona backend dinamicamente

    @property
    def _backend(self):
        if self._redis.is_available:
            return self._redis
        return self._json

    def get(self, key: str) -> Optional[Any]:
        raw = self._backend.get(key)
        return json.loads(raw) if raw else None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        ttl = ttl or self.flags.osint_cache_ttl_seconds
        try:
            self._backend.set(key, json.dumps(value), ttl)
        except Exception as e:
            logger.error(f"Cache set failed: {e}")


_cache: Optional[SmartCache] = None


def get_cache() -> SmartCache:
    global _cache
    if _cache is None:
        _cache = SmartCache()
    return _cache
