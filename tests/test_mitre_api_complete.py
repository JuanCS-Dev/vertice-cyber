"""
Test MITRE API Client
Testes adicionais para melhorar cobertura do MITRE API.
"""

import pytest
from unittest.mock import AsyncMock
from datetime import datetime

from tools.mitre_api import MITREAttackAPI


class TestMITREAPI:
    """Test MITRE API functionality."""

    @pytest.fixture
    def mitre_client(self):
        """Create MITRE client for testing with mocked data."""
        client = MITREAttackAPI("enterprise")

        # Clear any cached data to avoid interference
        client._frameworks = {}
        client._last_update = None

        # Mock _ensure_data_loaded to do nothing (prevent data loading)
        client._ensure_data_loaded = AsyncMock()

        # Mock data to avoid real API calls
        client._techniques = {
            "T1056": type(
                "MockTechnique",
                (),
                {
                    "technique_id": "T1056",
                    "name": "Input Capture",
                    "description": "Test technique",
                    "tactics": ["Credential Access", "Collection"],
                    "platforms": ["Windows", "Linux"],
                    "is_subtechnique": False,
                },
            )()
        }
        client._tactics = {
            "TA0006": type(
                "MockTactic",
                (),
                {
                    "tactic_id": "TA0006",
                    "name": "Credential Access",
                    "description": "Test tactic",
                    "shortname": "credential-access",
                },
            )()
        }
        client._actors = {}
        client._last_update = datetime.now()

        return client

    @pytest.mark.asyncio
    async def test_get_technique_found(self, mitre_client):
        """Test getting existing technique."""
        technique = await mitre_client.get_technique("T1056")
        assert technique is not None
        assert technique.technique_id == "T1056"
        assert technique.name == "Input Capture"

    @pytest.mark.asyncio
    async def test_get_technique_not_found(self, mitre_client):
        """Test getting non-existent technique."""
        technique = await mitre_client.get_technique("NONEXISTENT")
        assert technique is None

    @pytest.mark.asyncio
    async def test_get_techniques_by_tactic_found(self, mitre_client):
        """Test getting techniques by existing tactic."""
        techniques = await mitre_client.get_techniques_by_tactic("Credential Access")
        assert len(techniques) == 1
        assert techniques[0].technique_id == "T1056"

    @pytest.mark.asyncio
    async def test_get_techniques_by_tactic_not_found(self, mitre_client):
        """Test getting techniques by non-existent tactic."""
        techniques = await mitre_client.get_techniques_by_tactic("NonExistent Tactic")
        assert len(techniques) == 0

    @pytest.mark.asyncio
    async def test_get_techniques_by_platform_found(self, mitre_client):
        """Test getting techniques by existing platform."""
        techniques = await mitre_client.get_techniques_by_platform("Windows")
        assert len(techniques) == 1
        assert techniques[0].technique_id == "T1056"

    @pytest.mark.asyncio
    async def test_get_techniques_by_platform_not_found(self, mitre_client):
        """Test getting techniques by non-existent platform."""
        techniques = await mitre_client.get_techniques_by_platform("Android")
        assert len(techniques) == 0

    @pytest.mark.asyncio
    async def test_search_techniques_found(self, mitre_client):
        """Test searching techniques with matching query."""
        techniques = await mitre_client.search_techniques("Input")
        assert len(techniques) == 1
        assert techniques[0].technique_id == "T1056"

    @pytest.mark.asyncio
    async def test_search_techniques_not_found(self, mitre_client):
        """Test searching techniques with non-matching query."""
        techniques = await mitre_client.search_techniques("nonexistent")
        assert len(techniques) == 0

    @pytest.mark.asyncio
    async def test_get_all_techniques(self, mitre_client):
        """Test getting all techniques."""
        techniques = await mitre_client.get_all_techniques()
        assert len(techniques) == 1
        assert techniques[0].technique_id == "T1056"

    @pytest.mark.asyncio
    async def test_get_all_tactics(self, mitre_client):
        """Test getting all tactics."""
        tactics = await mitre_client.get_all_tactics()
        assert len(tactics) == 1
        assert tactics[0].tactic_id == "TA0006"

    @pytest.mark.asyncio
    async def test_get_all_actors_empty(self, mitre_client):
        """Test getting all actors when empty."""
        actors = await mitre_client.get_all_actors()
        assert len(actors) == 0

    @pytest.mark.asyncio
    async def test_get_stats(self, mitre_client):
        """Test getting statistics."""
        stats = await mitre_client.get_stats()
        assert isinstance(stats, dict)
        assert "last_update" in stats
        assert stats["techniques"] == 1
        assert stats["tactics"] == 1
        assert stats["actors"] == 0

    def test_collection_id_mapping(self):
        """Test collection ID mapping for different domains."""
        client = MITREAttackAPI("enterprise")
        assert (
            client._get_collection_id("enterprise")
            == "95ecc380-afe9-11e3-96b9-12313b01b281"
        )
        assert (
            client._get_collection_id("mobile")
            == "2f669986-b40c-4423-b917-a8e15bb3c0b7"
        )
        assert (
            client._get_collection_id("ics") == "02c3ef24-9cd4-48f3-a99f-b74ce24ca1e5"
        )
        assert (
            client._get_collection_id("unknown")
            == "95ecc380-afe9-11e3-96b9-12313b01b281"
        )

    def test_initialization_attributes(self):
        """Test MITRE client initialization attributes."""
        client = MITREAttackAPI("enterprise")
        assert client.domain == "enterprise"
        assert "cti-taxii.mitre.org" in client.collection_url
        assert "95ecc380-afe9-11e3-96b9-12313b01b281" in client.collection_url
        assert hasattr(client, "cache_file")
        assert hasattr(client, "_techniques")
        assert hasattr(client, "_tactics")
        assert hasattr(client, "_actors")
