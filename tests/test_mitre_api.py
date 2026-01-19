"""
Testes para MITRE ATT&CK API Client.

Testa integração com API oficial TAXII do MITRE ATT&CK.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
from datetime import datetime

from tools.mitre_api import (
    MITREAttackAPI,
    MITRETechnique,
    MITRETactic,
    MITREActor,
    get_mitre_client
)


class TestMITREAttackAPI:
    """Testes para MITREAttackAPI."""

    @pytest.fixture
    def api_client(self):
        """Fixture para cliente MITRE API."""
        return MITREAttackAPI(domain="enterprise")

    @pytest.mark.asyncio
    async def test_initialization(self, api_client):
        """Testa inicialização do cliente."""
        assert api_client.domain == "enterprise"
        assert api_client.collection_id == "95ecc380-afe9-11e3-96b9-12313b01b281"
        assert api_client.base_url == "https://cti-taxii.mitre.org/taxii/"

    @pytest.mark.asyncio
    async def test_get_collection_id(self, api_client):
        """Testa mapeamento de domínios para collection IDs."""
        assert api_client._get_collection_id("enterprise") == "95ecc380-afe9-11e3-96b9-12313b01b281"
        assert api_client._get_collection_id("mobile") == "2f669986-b40c-4423-b917-a8e15bb3c0b7"
        assert api_client._get_collection_id("ics") == "02c3ef24-9cd4-48f3-a99f-b74ce24ca1e5"
        assert api_client._get_collection_id("unknown") == "95ecc380-afe9-11e3-96b9-12313b01b281"  # default

    @pytest.mark.asyncio
    async def test_singleton_pattern(self):
        """Testa padrão singleton."""
        client1 = get_mitre_client("enterprise")
        client2 = get_mitre_client("enterprise")
        assert client1 is client2

        client3 = get_mitre_client("mobile")
        assert client1 is not client3

    @pytest.mark.asyncio
    async def test_get_technique_not_found(self, api_client):
        """Testa busca de técnica inexistente."""
        with patch.object(api_client, '_ensure_data_loaded', return_value=None):
            api_client._techniques = {}
            result = await api_client.get_technique("T9999")
            assert result is None

    @pytest.mark.asyncio
    async def test_get_techniques_by_tactic(self, api_client):
        """Testa busca de técnicas por tática."""
        mock_technique = MITRETechnique(
            technique_id="T1056",
            name="Input Capture",
            description="Test description",
            tactics=["Credential Access", "Collection"],
            platforms=["Windows", "Linux"]
        )

        with patch.object(api_client, '_ensure_data_loaded', return_value=None):
            api_client._techniques = {"T1056": mock_technique}

            # Busca por tática existente
            results = await api_client.get_techniques_by_tactic("Credential Access")
            assert len(results) == 1
            assert results[0].technique_id == "T1056"

            # Busca por tática inexistente
            results = await api_client.get_techniques_by_tactic("Nonexistent Tactic")
            assert len(results) == 0

    @pytest.mark.asyncio
    async def test_get_techniques_by_platform(self, api_client):
        """Testa busca de técnicas por plataforma."""
        mock_technique = MITRETechnique(
            technique_id="T1056",
            name="Input Capture",
            description="Test description",
            tactics=["Credential Access"],
            platforms=["Windows", "Linux"]
        )

        with patch.object(api_client, '_ensure_data_loaded', return_value=None):
            api_client._techniques = {"T1056": mock_technique}

            # Busca por plataforma existente
            results = await api_client.get_techniques_by_platform("Windows")
            assert len(results) == 1
            assert results[0].technique_id == "T1056"

            # Busca por plataforma inexistente
            results = await api_client.get_techniques_by_platform("Android")
            assert len(results) == 0

    @pytest.mark.asyncio
    async def test_search_techniques(self, api_client):
        """Testa busca de técnicas por query."""
        mock_technique1 = MITRETechnique(
            technique_id="T1056",
            name="Input Capture",
            description="Adversaries may use methods of capturing user input",
            tactics=["Credential Access"],
            platforms=["Windows"]
        )

        mock_technique2 = MITRETechnique(
            technique_id="T1566",
            name="Phishing",
            description="Adversaries may send phishing messages",
            tactics=["Initial Access"],
            platforms=["Windows"]
        )

        with patch.object(api_client, '_ensure_data_loaded', return_value=None):
            api_client._techniques = {
                "T1056": mock_technique1,
                "T1566": mock_technique2
            }

            # Busca por nome
            results = await api_client.search_techniques("Input Capture")
            assert len(results) == 1
            assert results[0].technique_id == "T1056"

            # Busca por descrição
            results = await api_client.search_techniques("phishing")
            assert len(results) == 1
            assert results[0].technique_id == "T1566"

            # Busca sem resultados
            results = await api_client.search_techniques("nonexistent")
            assert len(results) == 0

    @pytest.mark.asyncio
    async def test_get_all_techniques(self, api_client):
        """Testa retorno de todas as técnicas."""
        mock_technique = MITRETechnique(
            technique_id="T1056",
            name="Input Capture",
            description="Test",
            tactics=["Credential Access"],
            platforms=["Windows"]
        )

        with patch.object(api_client, '_ensure_data_loaded', return_value=None):
            api_client._techniques = {"T1056": mock_technique}

            results = await api_client.get_all_techniques()
            assert len(results) == 1
            assert results[0].technique_id == "T1056"

    @pytest.mark.asyncio
    async def test_get_all_tactics(self, api_client):
        """Testa retorno de todas as táticas."""
        mock_tactic = MITRETactic(
            tactic_id="TA0001",
            name="Initial Access",
            description="Test",
            shortname="initial-access"
        )

        with patch.object(api_client, '_ensure_data_loaded', return_value=None):
            api_client._tactics = {"TA0001": mock_tactic}

            results = await api_client.get_all_tactics()
            assert len(results) == 1
            assert results[0].tactic_id == "TA0001"

    @pytest.mark.asyncio
    async def test_get_all_actors(self, api_client):
        """Testa retorno de todos os atores."""
        mock_actor = MITREActor(
            actor_id="G001",
            name="Test Actor",
            description="Test actor",
            aliases=["Test"],
            techniques=[],
            countries=["Country"],
            motivations=["Test"]
        )

        with patch.object(api_client, '_ensure_data_loaded', return_value=None):
            api_client._actors = {"G001": mock_actor}

            results = await api_client.get_all_actors()
            assert len(results) == 1
            assert results[0].actor_id == "G001"

    @pytest.mark.asyncio
    async def test_get_stats(self, api_client):
        """Testa retorno de estatísticas."""
        with patch.object(api_client, '_ensure_data_loaded', return_value=None):
            api_client._techniques = {"T1": Mock(is_subtechnique=False)}
            api_client._tactics = {"TA1": Mock()}
            api_client._actors = {"G1": Mock()}
            api_client._last_update = datetime(2024, 1, 1, 12, 0, 0)

            stats = await api_client.get_stats()
            assert stats['techniques'] == 1
            assert stats['tactics'] == 1
            assert stats['actors'] == 1
            assert stats['subtechniques'] == 0
            assert stats['last_update'] is not None


class TestMITREModels:
    """Testes para modelos de dados MITRE."""

    def test_mitre_technique_model(self):
        """Testa modelo MITRETechnique."""
        technique = MITRETechnique(
            technique_id="T1056",
            name="Input Capture",
            description="Test description",
            tactics=["Credential Access"],
            platforms=["Windows", "Linux"],
            detection="Monitor for unusual processes",
            mitigations=["Multi-factor authentication"],
            data_sources=["Process monitoring"],
            is_subtechnique=False
        )

        assert technique.technique_id == "T1056"
        assert technique.name == "Input Capture"
        assert technique.tactics == ["Credential Access"]
        assert technique.platforms == ["Windows", "Linux"]
        assert technique.is_subtechnique is False

    def test_mitre_tactic_model(self):
        """Testa modelo MITRETactic."""
        tactic = MITRETactic(
            tactic_id="TA0001",
            name="Initial Access",
            description="Test description",
            shortname="initial-access",
            techniques=["T1566", "T1190"]
        )

        assert tactic.tactic_id == "TA0001"
        assert tactic.name == "Initial Access"
        assert tactic.shortname == "initial-access"
        assert tactic.techniques == ["T1566", "T1190"]

    def test_mitre_actor_model(self):
        """Testa modelo MITREActor."""
        actor = MITREActor(
            actor_id="G001",
            name="Test Actor",
            description="Test actor description",
            aliases=["Test", "TestGroup"],
            techniques=["T1566"],
            countries=["Country A", "Country B"],
            motivations=["Financial gain"],
            first_seen="2020-01-01",
            last_seen="2024-01-01"
        )

        assert actor.actor_id == "G001"
        assert actor.name == "Test Actor"
        assert actor.aliases == ["Test", "TestGroup"]
        assert actor.techniques == ["T1566"]
        assert actor.countries == ["Country A", "Country B"]
        assert actor.motivations == ["Financial gain"]
        assert actor.first_seen == "2020-01-01"
        assert actor.last_seen == "2024-01-01"</content>
<parameter name="filePath">tests/test_mitre_api.py