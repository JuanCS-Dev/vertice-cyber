"""
MITRE ATT&CK Cache Management
Gerenciamento de cache local para dados MITRE ATT&CK.
"""

import logging
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import aiofiles

from .mitre_models import (
    MITRETechnique,
    MITRETactic,
    MITREActor,
    ComplianceFrameworkData,
)

logger = logging.getLogger(__name__)


class MITRECache:
    """Gerenciamento de cache para dados MITRE ATT&CK."""

    def __init__(
        self, cache_dir: Path, cache_duration: timedelta = timedelta(hours=24)
    ):
        self.cache_dir = cache_dir
        self.cache_duration = cache_duration
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    @property
    def techniques_cache_file(self) -> Path:
        """Arquivo de cache para técnicas."""
        return self.cache_dir / "techniques.json"

    @property
    def tactics_cache_file(self) -> Path:
        """Arquivo de cache para táticas."""
        return self.cache_dir / "tactics.json"

    @property
    def actors_cache_file(self) -> Path:
        """Arquivo de cache para atores."""
        return self.cache_dir / "actors.json"

    @property
    def frameworks_cache_file(self) -> Path:
        """Arquivo de cache para frameworks."""
        return self.cache_dir / "frameworks.json"

    async def is_cache_valid(self, cache_file: Path) -> bool:
        """Verifica se o cache ainda é válido."""
        if not cache_file.exists():
            return False

        try:
            stat = cache_file.stat()
            file_age = datetime.now() - datetime.fromtimestamp(stat.st_mtime)
            return file_age < self.cache_duration
        except (OSError, ValueError):
            return False

    async def load_cache(self, cache_file: Path) -> Optional[Dict[str, Any]]:
        """Carrega dados do cache."""
        if not await self.is_cache_valid(cache_file):
            return None

        try:
            async with aiofiles.open(cache_file, "r", encoding="utf-8") as f:
                content = await f.read()
                return json.loads(content)
        except (OSError, json.JSONDecodeError, UnicodeDecodeError) as e:
            logger.warning(f"Failed to load cache from {cache_file}: {e}")
            return None

    async def save_cache(self, cache_file: Path, data: Dict[str, Any]) -> bool:
        """Salva dados no cache."""
        try:
            # Adiciona timestamp de cache
            data["_cache_timestamp"] = datetime.now().isoformat()

            async with aiofiles.open(cache_file, "w", encoding="utf-8") as f:
                await f.write(json.dumps(data, indent=2, ensure_ascii=False))

            logger.debug(f"Cache saved to {cache_file}")
            return True
        except (OSError, TypeError) as e:
            logger.error(f"Failed to save cache to {cache_file}: {e}")
            return False

    async def load_techniques_cache(self) -> Optional[Dict[str, MITRETechnique]]:
        """Carrega técnicas do cache."""
        data = await self.load_cache(self.techniques_cache_file)
        if not data or "_cache_timestamp" not in data:
            return None

        try:
            techniques = {}
            for tech_id, tech_data in data.items():
                if tech_id != "_cache_timestamp":
                    techniques[tech_id] = MITRETechnique(**tech_data)
            return techniques
        except Exception as e:
            logger.warning(f"Failed to parse techniques cache: {e}")
            return None

    async def save_techniques_cache(
        self, techniques: Dict[str, MITRETechnique]
    ) -> bool:
        """Salva técnicas no cache."""
        data = {}
        for tech_id, technique in techniques.items():
            data[tech_id] = technique.model_dump()
        return await self.save_cache(self.techniques_cache_file, data)

    async def load_tactics_cache(self) -> Optional[Dict[str, MITRETactic]]:
        """Carrega táticas do cache."""
        data = await self.load_cache(self.tactics_cache_file)
        if not data or "_cache_timestamp" not in data:
            return None

        try:
            tactics = {}
            for tact_id, tact_data in data.items():
                if tact_id != "_cache_timestamp":
                    tactics[tact_id] = MITRETactic(**tact_data)
            return tactics
        except Exception as e:
            logger.warning(f"Failed to parse tactics cache: {e}")
            return None

    async def save_tactics_cache(self, tactics: Dict[str, MITRETactic]) -> bool:
        """Salva táticas no cache."""
        data = {}
        for tact_id, tactic in tactics.items():
            data[tact_id] = tactic.model_dump()
        return await self.save_cache(self.tactics_cache_file, data)

    async def load_actors_cache(self) -> Optional[Dict[str, MITREActor]]:
        """Carrega atores do cache."""
        data = await self.load_cache(self.actors_cache_file)
        if not data or "_cache_timestamp" not in data:
            return None

        try:
            actors = {}
            for act_id, act_data in data.items():
                if act_id != "_cache_timestamp":
                    actors[act_id] = MITREActor(**act_data)
            return actors
        except Exception as e:
            logger.warning(f"Failed to parse actors cache: {e}")
            return None

    async def save_actors_cache(self, actors: Dict[str, MITREActor]) -> bool:
        """Salva atores no cache."""
        data = {}
        for act_id, actor in actors.items():
            data[act_id] = actor.model_dump()
        return await self.save_cache(self.actors_cache_file, data)

    async def load_frameworks_cache(
        self,
    ) -> Optional[Dict[str, ComplianceFrameworkData]]:
        """Carrega frameworks do cache."""
        data = await self.load_cache(self.frameworks_cache_file)
        if not data or "_cache_timestamp" not in data:
            return None

        try:
            frameworks = {}
            for fw_id, fw_data in data.items():
                if fw_id != "_cache_timestamp":
                    frameworks[fw_id] = ComplianceFrameworkData(**fw_data)
            return frameworks
        except Exception as e:
            logger.warning(f"Failed to parse frameworks cache: {e}")
            return None

    async def save_frameworks_cache(
        self, frameworks: Dict[str, ComplianceFrameworkData]
    ) -> bool:
        """Salva frameworks no cache."""
        data = {}
        for fw_id, framework in frameworks.items():
            data[fw_id] = framework.model_dump()
        return await self.save_cache(self.frameworks_cache_file, data)

    async def clear_all_cache(self) -> bool:
        """Limpa todo o cache."""
        try:
            cache_files = [
                self.techniques_cache_file,
                self.tactics_cache_file,
                self.actors_cache_file,
                self.frameworks_cache_file,
            ]

            for cache_file in cache_files:
                if cache_file.exists():
                    cache_file.unlink()

            logger.info("All MITRE cache cleared")
            return True
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return False
