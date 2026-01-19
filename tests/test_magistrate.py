"""
Tests for Ethical Magistrate tool.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from tools.magistrate import (
    EthicalMagistrate,
    DecisionType,
    EthicalDecision,
    get_magistrate,
    ethical_validate,
    ethical_audit,
)


class TestEthicalMagistrate:
    """Test Ethical Magistrate functionality."""

    @pytest.fixture
    def magistrate(self):
        """Create magistrate instance for testing."""
        mag = EthicalMagistrate()
        # Mock dependencies
        mag.memory = MagicMock()
        mag.event_bus = MagicMock()
        mag.event_bus.emit = AsyncMock()
        return mag

    @pytest.mark.asyncio
    async def test_get_magistrate_returns_singleton(self):
        """Test that get_magistrate returns singleton."""
        mag1 = get_magistrate()
        mag2 = get_magistrate()
        assert mag1 is mag2

    @pytest.mark.asyncio
    async def test_validate_safe_action_approved(self, magistrate):
        """Test validation of safe action."""
        result = await magistrate.validate("read file", {}, "user")

        assert result.decision_type == DecisionType.APPROVED
        assert result.is_approved is True
        assert result.reasoning == "All checks passed"

    @pytest.mark.asyncio
    async def test_validate_dangerous_action_requires_review(self, magistrate):
        """Test dangerous action requires human review."""
        result = await magistrate.validate("exploit vulnerability", {}, "user")

        assert result.decision_type == DecisionType.REQUIRES_HUMAN_REVIEW
        assert result.is_approved is False
        assert "dangerous keywords" in result.reasoning.lower()

    @pytest.mark.asyncio
    async def test_validate_always_requires_approval(self, magistrate):
        """Test actions that always require approval."""
        result = await magistrate.validate("delete_data", {}, "user")

        assert result.decision_type == DecisionType.REQUIRES_HUMAN_REVIEW
        assert result.is_approved is False
        assert "always requires approval" in result.conditions[0].lower()

    @pytest.mark.asyncio
    async def test_validate_privacy_sensitive_action(self, magistrate):
        """Test action with PII gets conditions."""
        context = {"has_pii": True}
        result = await magistrate.validate("process user data", context, "user")

        assert result.decision_type == DecisionType.APPROVED_WITH_CONDITIONS
        assert result.is_approved is True
        assert any("privacy safeguards" in cond.lower() for cond in result.conditions)

    def test_is_dangerous_detects_keywords(self, magistrate):
        """Test dangerous keyword detection."""
        assert magistrate._is_dangerous("exploit this system") is True
        assert magistrate._is_dangerous("attack the server") is True
        assert magistrate._is_dangerous("read a file") is False

    def test_always_requires_approval_detects_keywords(self, magistrate):
        """Test always require approval keyword detection."""
        assert magistrate._always_requires_approval("delete_data") is True
        assert magistrate._always_requires_approval("modify_firewall") is True
        assert magistrate._always_requires_approval("execute_payload") is True
        assert magistrate._always_requires_approval("read file") is False

    def test_finalize_stores_in_memory(self, magistrate):
        """Test finalize stores decision in memory."""
        decision = EthicalDecision(
            decision_id="test_123",
            decision_type=DecisionType.APPROVED,
            action="test action",
            actor="test",
            is_approved=True,
        )

        result = magistrate._finalize(decision, 1000.0)

        assert result.duration_ms > 0
        magistrate.memory.set.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_decision_history(self, magistrate):
        """Test getting decision history."""
        mock_events = [
            MagicMock(data={"action": "test1"}),
            MagicMock(data={"action": "test2"}),
        ]
        magistrate.event_bus.get_history.return_value = mock_events

        history = await magistrate.get_decision_history(5)

        assert len(history) == 2
        assert history[0]["action"] == "test1"
        magistrate.event_bus.get_history.assert_called_once()

    def test_check_fairness_pass(self, magistrate):
        """Test fairness check passes for neutral actions."""
        assert magistrate._check_fairness("read file", {}) is True
        assert (
            magistrate._check_fairness(
                "process data", {"involves_data_processing": True}
            )
            is True
        )

    def test_check_fairness_fail(self, magistrate):
        """Test fairness check fails for discriminatory actions."""
        assert magistrate._check_fairness("bias against users", {}) is False
        assert (
            magistrate._check_fairness(
                "discriminate data", {"involves_data_processing": True}
            )
            is False
        )

    def test_check_transparency_pass(self, magistrate):
        """Test transparency check passes."""
        assert magistrate._check_transparency("read file", {}) is True
        assert (
            magistrate._check_transparency(
                "deploy system", {"transparency_measures": True}
            )
            is True
        )

    def test_check_transparency_fail(self, magistrate):
        """Test transparency check fails for high-risk actions without measures."""
        assert magistrate._check_transparency("deploy system", {}) is False
        assert magistrate._check_transparency("modify critical system", {}) is False

    def test_check_accountability_pass(self, magistrate):
        """Test accountability check passes for non-critical actions."""
        assert magistrate._check_accountability("read file", {}) is True
        assert magistrate._check_accountability("update config", {}) is True

    def test_check_accountability_fail(self, magistrate):
        """Test accountability check fails for critical actions."""
        assert magistrate._check_accountability("delete permanent", {}) is False
        assert magistrate._check_accountability("modify critical system", {}) is False

    def test_check_security_pass(self, magistrate):
        """Test security check passes for safe actions."""
        assert magistrate._check_security("read file", {}) is True
        assert magistrate._check_security("process data", {}) is True

    def test_check_security_fail(self, magistrate):
        """Test security check fails for dangerous actions."""
        assert magistrate._check_security("eval(malicious_code)", {}) is False
        assert magistrate._check_security("exec(dangerous)", {}) is False
        assert magistrate._check_security("subprocess.call", {}) is False

    @pytest.mark.asyncio
    async def test_validate_fairness_check_fails(self, magistrate):
        """Test validation fails on fairness check."""
        result = await magistrate.validate(
            "bias against users", {"involves_data_processing": True}, "user"
        )

        assert result.decision_type == DecisionType.REJECTED_BY_ETHICS
        assert "fairness" in result.reasoning.lower()

    @pytest.mark.asyncio
    async def test_validate_transparency_requires_conditions(self, magistrate):
        """Test validation adds transparency conditions."""
        result = await magistrate.validate("deploy critical system", {}, "user")

        assert result.decision_type == DecisionType.APPROVED_WITH_CONDITIONS
        assert any("transparency" in cond.lower() for cond in result.conditions)
        assert any("audit" in cond.lower() for cond in result.conditions)

    @pytest.mark.asyncio
    async def test_validate_accountability_requires_human_review(self, magistrate):
        """Test critical actions require human review."""
        result = await magistrate.validate("delete permanent data", {}, "user")

        assert result.decision_type == DecisionType.REQUIRES_HUMAN_REVIEW
        assert "accountability" in result.reasoning.lower()

    @pytest.mark.asyncio
    async def test_validate_security_fails(self, magistrate):
        """Test validation fails on security check."""
        result = await magistrate.validate("exec(malicious)", {}, "user")

        assert result.decision_type == DecisionType.REJECTED_BY_GOVERNANCE
        assert "security" in result.reasoning.lower()

    @pytest.mark.asyncio
    async def test_validate_handles_exceptions(self, magistrate):
        """Test validation handles exceptions gracefully."""
        # Make event_bus.emit raise an exception
        magistrate.event_bus.emit.side_effect = Exception("Test exception")

        result = await magistrate.validate("safe action", {}, "user")

        assert result.decision_type == DecisionType.ERROR
        assert "Validation error: Test exception" in result.rejection_reasons[0]


class TestMagistrateTools:
    """Test MCP tool functions."""

    @pytest.fixture
    def mock_ctx(self):
        """Create mock context."""
        ctx = MagicMock()
        ctx.info = MagicMock()
        return ctx

    @pytest.mark.asyncio
    async def test_ethical_validate_tool_safe_action(self, mock_ctx):
        """Test ethical_validate tool with safe action."""
        result = await ethical_validate(mock_ctx, "read file", {}, "user")

        assert result["decision_type"] == "approved"
        assert result["is_approved"] is True
        mock_ctx.info.assert_called()

    @pytest.mark.asyncio
    async def test_ethical_validate_tool_dangerous_action(self, mock_ctx):
        """Test ethical_validate tool with dangerous action."""
        result = await ethical_validate(mock_ctx, "exploit vulnerability", {}, "user")

        assert result["decision_type"] == "requires_human_review"
        assert result["is_approved"] is False
        mock_ctx.info.assert_called()

    @pytest.mark.asyncio
    async def test_ethical_audit_tool(self, mock_ctx):
        """Test ethical_audit tool."""
        result = await ethical_audit(mock_ctx, 5)

        assert isinstance(result, list)
        # Should return empty list initially since no decisions made
