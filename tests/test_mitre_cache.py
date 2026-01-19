"""
MITRE Cache Tests
Testes para o sistema de cache MITRE.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch

from tools.mitre_cache import MITRECache
from tools.mitre_models import MITRETechnique, MITRETactic


class TestMITRECache:
    """Test MITRE cache functionality."""

    @pytest.fixture
    def cache(self, tmp_path):
        """Create cache instance with temporary directory."""
        cache_dir = tmp_path / "mitre_cache"
        return MITRECache(cache_dir)

    def test_cache_initialization(self, cache):
        """Test cache initialization creates directory."""
        assert cache.cache_dir.exists()
        assert cache.cache_duration == timedelta(hours=24)

    def test_cache_file_properties(self, cache):
        """Test cache file property paths."""
        assert cache.techniques_cache_file.name == "techniques.json"
        assert cache.tactics_cache_file.name == "tactics.json"
        assert cache.actors_cache_file.name == "actors.json"
        assert cache.frameworks_cache_file.name == "frameworks.json"

    @pytest.mark.asyncio
    async def test_is_cache_valid_no_file(self, cache):
        """Test cache validity when file doesn't exist."""
        result = await cache.is_cache_valid(cache.techniques_cache_file)
        assert result is False

    @pytest.mark.asyncio
    async def test_is_cache_valid_expired(self, cache):
        """Test cache validity when file is expired."""
        # Create an expired file
        expired_file = cache.techniques_cache_file
        expired_file.write_text('{"test": "data"}')

        # Mock time to make it expired
        with patch("tools.mitre_cache.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime.now()
            mock_datetime.fromtimestamp.return_value = datetime.now() - timedelta(
                hours=25
            )

            result = await cache.is_cache_valid(expired_file)
            assert result is False

    @pytest.mark.asyncio
    async def test_load_cache_valid(self, cache):
        """Test loading valid cache data."""
        test_data = {"technique1": {"id": "T001", "name": "Test"}}
        cache_file = cache.techniques_cache_file

        # Write test data
        import json

        with open(cache_file, "w") as f:
            json.dump(test_data, f)

        result = await cache.load_cache(cache_file)
        assert result == test_data

    @pytest.mark.asyncio
    async def test_save_cache(self, cache):
        """Test saving cache data."""
        test_data = {"technique1": {"id": "T001", "name": "Test"}}

        result = await cache.save_cache(cache.techniques_cache_file, test_data)
        assert result is True
        assert cache.techniques_cache_file.exists()

    @pytest.mark.asyncio
    async def test_load_techniques_cache(self, cache):
        """Test loading techniques from cache."""
        technique_data = {
            "T1056": {
                "technique_id": "T1056",
                "name": "Input Capture",
                "description": "Test technique",
                "tactics": ["Credential Access"],
                "platforms": ["Windows"],
                "is_subtechnique": False,
            }
        }

        # Save technique data
        result = await cache.save_cache(cache.techniques_cache_file, technique_data)
        assert result is True

        # Load techniques
        techniques = await cache.load_techniques_cache()
        assert techniques is not None
        assert "T1056" in techniques
        assert isinstance(techniques["T1056"], MITRETechnique)
        assert techniques["T1056"].technique_id == "T1056"

    @pytest.mark.asyncio
    async def test_save_techniques_cache(self, cache):
        """Test saving techniques to cache."""
        techniques = {
            "T1056": MITRETechnique(
                technique_id="T1056",
                name="Input Capture",
                description="Test technique",
                tactics=["Credential Access"],
                platforms=["Windows"],
                is_subtechnique=False,
            )
        }

        result = await cache.save_techniques_cache(techniques)
        assert result is True
        assert cache.techniques_cache_file.exists()

    @pytest.mark.asyncio
    async def test_load_tactics_cache(self, cache):
        """Test loading tactics from cache."""
        tactic_data = {
            "TA0001": {
                "tactic_id": "TA0001",
                "name": "Initial Access",
                "description": "Test tactic",
                "techniques": ["T1566"],
            }
        }

        await cache.save_cache(cache.tactics_cache_file, tactic_data)
        tactics = await cache.load_tactics_cache()

        assert tactics is not None
        assert "TA0001" in tactics
        assert isinstance(tactics["TA0001"], MITRETactic)
        assert tactics["TA0001"].tactic_id == "TA0001"

    @pytest.mark.asyncio
    async def test_clear_all_cache(self, cache):
        """Test clearing all cache files."""
        # Create some cache files
        cache.techniques_cache_file.write_text('{"test": "data"}')
        cache.tactics_cache_file.write_text('{"test": "data"}')

        assert cache.techniques_cache_file.exists()
        assert cache.tactics_cache_file.exists()

        result = await cache.clear_all_cache()
        assert result is True

        # Files should be gone
        assert not cache.techniques_cache_file.exists()
        assert not cache.tactics_cache_file.exists()
