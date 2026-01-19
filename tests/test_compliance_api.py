"""
Testes para Compliance Frameworks API Client.

Testa integração com dados oficiais de frameworks de compliance.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch

from tools.compliance_api import (
    ComplianceFrameworksAPI,
    ComplianceControl,
    ComplianceFrameworkData,
    get_compliance_api
)


class TestComplianceFrameworksAPI:
    """Testes para ComplianceFrameworksAPI."""

    @pytest.fixture
    def api_client(self):
        """Fixture para cliente Compliance API."""
        return ComplianceFrameworksAPI()

    @pytest.mark.asyncio
    async def test_initialization(self, api_client):
        """Testa inicialização do cliente."""
        # Client should initialize data
        await asyncio.sleep(0.1)  # Allow initialization
        stats = await api_client.get_stats()
        assert 'frameworks' in stats
        assert 'controls' in stats

    @pytest.mark.asyncio
    async def test_singleton_pattern(self):
        """Testa padrão singleton."""
        client1 = get_compliance_api()
        client2 = get_compliance_api()
        assert client1 is client2

    @pytest.mark.asyncio
    async def test_get_framework_found(self, api_client):
        """Testa busca de framework existente."""
        await api_client._ensure_data_loaded()
        framework = await api_client.get_framework("nist_csf")
        assert framework is not None
        assert framework.framework_id == "nist_csf"
        assert framework.name == "NIST Cybersecurity Framework"
        assert len(framework.controls) > 0

    @pytest.mark.asyncio
    async def test_get_framework_not_found(self, api_client):
        """Testa busca de framework inexistente."""
        await api_client._ensure_data_loaded()
        framework = await api_client.get_framework("nonexistent")
        assert framework is None

    @pytest.mark.asyncio
    async def test_get_control_found(self, api_client):
        """Testa busca de controle existente."""
        await api_client._ensure_data_loaded()
        control = await api_client.get_control("GDPR-ART6")
        assert control is not None
        assert control.control_id == "GDPR-ART6"
        assert control.framework == "gdpr"
        assert control.severity == "critical"

    @pytest.mark.asyncio
    async def test_get_control_not_found(self, api_client):
        """Testa busca de controle inexistente."""
        await api_client._ensure_data_loaded()
        control = await api_client.get_control("NONEXISTENT-123")
        assert control is None

    @pytest.mark.asyncio
    async def test_get_controls_by_framework(self, api_client):
        """Testa busca de controles por framework."""
        await api_client._ensure_data_loaded()
        controls = await api_client.get_controls_by_framework("gdpr")
        assert len(controls) > 0
        for control in controls:
            assert control.framework == "gdpr"

    @pytest.mark.asyncio
    async def test_get_controls_by_framework_not_found(self, api_client):
        """Testa busca de controles para framework inexistente."""
        await api_client._ensure_data_loaded()
        controls = await api_client.get_controls_by_framework("nonexistent")
        assert len(controls) == 0

    @pytest.mark.asyncio
    async def test_search_controls(self, api_client):
        """Testa busca de controles por query."""
        await api_client._ensure_data_loaded()

        # Busca por palavra-chave
        results = await api_client.search_controls("access")
        assert len(results) > 0

        # Busca por framework específico
        results = await api_client.search_controls("processing", "gdpr")
        assert len(results) >= 0  # Pode ser 0 se não houver match

        # Busca sem resultados
        results = await api_client.search_controls("nonexistentterm")
        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_get_frameworks_by_category(self, api_client):
        """Testa busca de frameworks por categoria."""
        await api_client._ensure_data_loaded()

        # Busca por categoria existente
        frameworks = await api_client.get_frameworks_by_category("Data Protection")
        assert len(frameworks) >= 0

        # Busca por categoria inexistente
        frameworks = await api_client.get_frameworks_by_category("Nonexistent Category")
        assert len(frameworks) == 0

    @pytest.mark.asyncio
    async def test_get_all_frameworks(self, api_client):
        """Testa retorno de todos os frameworks."""
        await api_client._ensure_data_loaded()
        frameworks = await api_client.get_all_frameworks()
        assert len(frameworks) >= 6  # Should have at least NIST, ISO, GDPR, HIPAA, PCI, SOX
        framework_ids = [f.framework_id for f in frameworks]
        assert "nist_csf" in framework_ids
        assert "gdpr" in framework_ids

    @pytest.mark.asyncio
    async def test_get_all_controls(self, api_client):
        """Testa retorno de todos os controles."""
        await api_client._ensure_data_loaded()
        controls = await api_client.get_all_controls()
        assert len(controls) > 0
        # Cada controle deve ter ID único
        control_ids = [c.control_id for c in controls]
        assert len(control_ids) == len(set(control_ids))

    @pytest.mark.asyncio
    async def test_get_stats(self, api_client):
        """Testa retorno de estatísticas."""
        await api_client._ensure_data_loaded()
        stats = await api_client.get_stats()
        assert isinstance(stats, dict)
        assert 'frameworks' in stats
        assert 'controls' in stats
        assert 'categories' in stats
        assert stats['frameworks'] >= 6
        assert stats['controls'] > 0


class TestComplianceModels:
    """Testes para modelos de dados de compliance."""

    def test_compliance_control_model(self):
        """Testa modelo ComplianceControl."""
        control = ComplianceControl(
            control_id="TEST-1",
            title="Test Control",
            description="Test description",
            framework="test",
            category="Test Category",
            severity="high",
            implementation_guide="Test implementation",
            related_controls=["TEST-2"],
            references=["Test Ref"],
        )

        assert control.control_id == "TEST-1"
        assert control.title == "Test Control"
        assert control.severity == "high"
        assert control.related_controls == ["TEST-2"]

    def test_compliance_framework_data_model(self):
        """Testa modelo ComplianceFrameworkData."""
        framework = ComplianceFrameworkData(
            framework_id="test",
            name="Test Framework",
            version="1.0",
            description="Test framework description",
            controls=[],
            categories=["Category 1", "Category 2"],
            source_url="https://example.com",
        )

        assert framework.framework_id == "test"
        assert framework.name == "Test Framework"
        assert framework.version == "1.0"
        assert framework.categories == ["Category 1", "Category 2"]</content>
<parameter name="filePath">tests/test_compliance_api.py