"""
Test MITRE API Client - Complete Coverage
Testes para melhorar cobertura do MITRE API client.
"""

import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime, timedelta

from tools.mitre_api import MITREAttackAPI, get_mitre_client


class TestMITREAPICompleteCoverage:
    """Complete tests for MITRE API to reach 100% coverage."""

    @pytest.fixture
    def mitre_client(self):
        """Create MITRE client for testing with mocked data."""
        client = MITREAttackAPI("enterprise")

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
                    "x_mitre_detection": "Monitor for unusual processes",
                    "x_mitre_data_sources": ["Process monitoring"],
                    "kill_chain_phases": [
                        {
                            "kill_chain_name": "mitre-attack-enterprise",
                            "phase_name": "credential-access",
                        },
                        {
                            "kill_chain_name": "mitre-attack-enterprise",
                            "phase_name": "collection",
                        },
                    ],
                    "external_references": [{"external_id": "T1056"}],
                    "created": "2020-01-01T00:00:00.000Z",
                    "modified": "2024-01-01T00:00:00.000Z",
                    "x_mitre_version": "1.0",
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
                    "x_mitre_shortname": "credential-access",
                    "external_references": [{"external_id": "TA0006"}],
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
        assert technique.tactics == ["Credential Access", "Collection"]
        assert technique.platforms == ["Windows", "Linux"]

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
        assert "techniques" in stats
        assert "tactics" in stats
        assert "last_update" in stats
        assert stats["techniques"] == 1
        assert stats["tactics"] == 1
        assert stats["actors"] == 0

        def test_singleton_pattern(self):
            """Test singleton pattern for MITRE clients."""
            # Clear existing clients to test fresh
            import tools.mitre_client as mitre_module
        
            mitre_module._mitre_clients.clear()
        # Mock _ensure_data_loaded to avoid async initialization
        with patch(
            "tools.mitre_api.MITREAttackAPI._ensure_data_loaded", new_callable=AsyncMock
        ):
            client1 = get_mitre_client("enterprise")
            client2 = get_mitre_client("enterprise")
            assert client1 is client2

            # Different domains should be different instances
            client3 = get_mitre_client("mobile")
            assert client1 is not client3

    def test_collection_id_mapping_enterprise(self):
        """Test collection ID mapping for enterprise domain."""
        with patch("tools.mitre_api.MITREAttackAPI._initialize_data"):
            client = MITREAttackAPI("enterprise")
            assert (
                client._get_collection_id("enterprise")
                == "95ecc380-afe9-11e3-96b9-12313b01b281"
            )

    def test_collection_id_mapping_mobile(self):
        """Test collection ID mapping for mobile domain."""
        with patch("tools.mitre_api.MITREAttackAPI._initialize_data"):
            client = MITREAttackAPI("mobile")
            assert (
                client._get_collection_id("mobile")
                == "2f669986-b40c-4423-b917-a8e15bb3c0b7"
            )

    def test_collection_id_mapping_ics(self):
        """Test collection ID mapping for ICS domain."""
        with patch("tools.mitre_api.MITREAttackAPI._initialize_data"):
            client = MITREAttackAPI("ics")
            assert (
                client._get_collection_id("ics")
                == "02c3ef24-9cd4-48f3-a99f-b74ce24ca1e5"
            )

    def test_collection_id_mapping_unknown(self):
        """Test collection ID mapping for unknown domain defaults to enterprise."""
        with patch("tools.mitre_api.MITREAttackAPI._initialize_data"):
            client = MITREAttackAPI("unknown")
            assert (
                client._get_collection_id("unknown")
                == "95ecc380-afe9-11e3-96b9-12313b01b281"
            )

    def test_initialization_attributes(self):
        """Test MITRE client initialization attributes."""
        with patch("tools.mitre_api.MITREAttackAPI._initialize_data"):
            client = MITREAttackAPI("enterprise")
            assert client.domain == "enterprise"
            assert "cti-taxii.mitre.org" in client.collection_url
            assert "95ecc380-afe9-11e3-96b9-12313b01b281" in client.collection_url
            assert hasattr(client, "cache_file")
            assert hasattr(client, "_techniques")
            assert hasattr(client, "_tactics")
            assert hasattr(client, "_actors")

    @pytest.mark.asyncio
    async def test_get_control_found(self, mitre_client):
        """Test getting existing control (technique)."""
        control = await mitre_client.get_control("T1056")
        assert control is not None
        assert control.technique_id == "T1056"

    @pytest.mark.asyncio
    async def test_get_control_not_found(self, mitre_client):
        """Test getting non-existent control."""
        control = await mitre_client.get_control("NONEXISTENT")
        assert control is None

    @pytest.mark.asyncio
    async def test_get_controls_by_framework_enterprise(self, mitre_client):
        """Test getting controls by enterprise framework."""
        controls = await mitre_client.get_controls_by_framework("enterprise")
        # In mock data, should return techniques
        assert isinstance(controls, list)

    @pytest.mark.asyncio
    async def test_get_controls_by_framework_empty(self, mitre_client):
        """Test getting controls by non-existent framework."""
        # implementation defaults to all if not explicitly 'nonexistent'
        controls = await mitre_client.get_controls_by_framework("nonexistent")
        assert len(controls) == 0

    @pytest.mark.asyncio
    async def test_get_framework_found(self, mitre_client):
        """Test getting framework."""
        # mock data uses 'enterprise' ID
        framework = await mitre_client.get_framework("enterprise")
        assert framework is not None

    def test_mitre_client_cache_file_path(self, mitre_client):
        """Test cache file path is correctly set."""
        assert mitre_client.cache_file is not None
        assert "techniques.json" in str(mitre_client.cache_file)

    @pytest.mark.asyncio
    async def test_load_cache_no_file(self, mitre_client):
        """Test _load_cache when file doesn't exist."""
        # Ensure file doesn't exist by mocking Path.exists to return False
        with patch("tools.mitre_client.Path.exists", return_value=False):
            result = await mitre_client._load_cache()
            assert result is False

    @pytest.mark.asyncio
    async def test_load_cache_expired(self, mitre_client):
        """Test _load_cache when file is expired."""
        from datetime import datetime

        expired_time = datetime.now() - timedelta(hours=25)

        with (
            patch("tools.mitre_client.Path.exists", return_value=True),
            patch("tools.mitre_client.Path.stat") as mock_stat,
            patch("tools.mitre_client.datetime") as mock_datetime,
        ):
            mock_stat.return_value.st_mtime = expired_time.timestamp()
            mock_datetime.now.return_value = datetime.now()
            # ... body
            mock_datetime.now.return_value = datetime.now()

            result = await mitre_client._load_cache()
            assert result is False

    def test_mitre_client_initialization_attributes_complete(self, mitre_client):
        """Test all initialization attributes are set."""
        assert mitre_client.domain == "enterprise"
        assert mitre_client.collection_id == "95ecc380-afe9-11e3-96b9-12313b01b281"
        assert "cti-taxii.mitre.org" in mitre_client.base_url
        assert hasattr(mitre_client, "cache_file")
        assert hasattr(mitre_client, "_techniques")
        assert hasattr(mitre_client, "_tactics")
        assert hasattr(mitre_client, "_actors")
        assert hasattr(mitre_client, "_frameworks")
        assert hasattr(mitre_client, "_last_update")

        def test_get_mitre_client_singleton_cleared(self):
            """Test get_mitre_client singleton after clearing."""
            from tools.mitre_api import get_mitre_client
        
            # Clear existing clients
            import tools.mitre_client
        
            tools.mitre_client._mitre_clients.clear()
        # Get first instance
        client1 = get_mitre_client("enterprise")
        assert client1 is not None

        # Get second instance - should be same
        client2 = get_mitre_client("enterprise")
        assert client1 is client2

        # Different domain should be different
        client3 = get_mitre_client("mobile")
        assert client1 is not client3

        def test_mitre_client_different_domains(self):
            """Test different domains create different clients."""
            from tools.mitre_api import get_mitre_client
        
            # Clear existing clients
            import tools.mitre_client
        
            tools.mitre_client._mitre_clients.clear()
        client_enterprise = get_mitre_client("enterprise")
        client_mobile = get_mitre_client("mobile")
        client_ics = get_mitre_client("ics")

        assert client_enterprise is not client_mobile
        assert client_mobile is not client_ics
        assert client_enterprise is not client_ics

        # Verify collection IDs are different
        assert client_enterprise.collection_id != client_mobile.collection_id
        assert client_mobile.collection_id != client_ics.collection_id

    @pytest.mark.asyncio
    async def test_get_all_frameworks(self, mitre_client):
        """Test getting all frameworks."""
        frameworks = await mitre_client.get_all_frameworks()
        assert isinstance(frameworks, list)

    @pytest.mark.asyncio
    async def test_get_all_controls(self, mitre_client):
        """Test getting all controls."""
        controls = await mitre_client.get_all_controls()
        assert isinstance(controls, list)
        assert len(controls) == 1  # Our mock technique
