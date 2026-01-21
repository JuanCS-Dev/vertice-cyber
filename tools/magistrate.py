"""
Ethical Magistrate - Core Governance Tool
Valida todas as ações do sistema contra framework ético.
"""

import time
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from core.settings import get_settings
from core.event_bus import get_event_bus, EventType
from core.memory import get_agent_memory


class DecisionType(str, Enum):
    """Tipos de decisão ética."""

    APPROVED = "approved"
    APPROVED_WITH_CONDITIONS = "approved_with_conditions"
    REJECTED_BY_GOVERNANCE = "rejected_by_governance"
    REJECTED_BY_ETHICS = "rejected_by_ethics"
    REJECTED_BY_PRIVACY = "rejected_by_privacy"
    REQUIRES_HUMAN_REVIEW = "requires_human_review"
    ERROR = "error"


class EthicalDecision(BaseModel):
    """Resultado de validação ética."""

    decision_id: str
    decision_type: DecisionType
    action: str
    actor: str
    is_approved: bool
    conditions: List[str] = Field(default_factory=list)
    rejection_reasons: List[str] = Field(default_factory=list)
    reasoning: str = ""
    duration_ms: float = 0.0


class EthicalMagistrate:
    """
    Magistrado Ético - Juiz supremo do sistema.

    Valida ações através de pipeline de 7 fases:
    1. Governance check (keywords perigosas)
    2. Privacy check (PII)
    3. Fairness check
    4. Transparency check
    5. Accountability check
    6. Security check
    7. Final approval
    """

    def __init__(self):
        self.settings = get_settings().ethics
        self.memory = get_agent_memory("ethical_magistrate")
        self.event_bus = get_event_bus()

    async def validate(
        self, action: str, context: Dict[str, Any], actor: str = "system"
    ) -> EthicalDecision:
        """
        Valida ação contra framework ético.

        Args:
            action: Descrição da ação a ser validada
            context: Contexto adicional (has_pii, target, etc.)
            actor: Quem está solicitando

        Returns:
            EthicalDecision com resultado
        """
        start_time = time.time()
        decision_id = f"decision_{int(time.time() * 1000)}"

        result = EthicalDecision(
            decision_id=decision_id,
            decision_type=DecisionType.ERROR,
            action=action,
            actor=actor,
            is_approved=False,
        )

        try:
            # Emite evento de início
            await self.event_bus.emit(
                EventType.ETHICS_VALIDATION_REQUESTED,
                {"action": action, "actor": actor},
                source="magistrate",
            )
            # Phase 1: Governance check
            if self._is_dangerous(action):
                result.decision_type = DecisionType.REQUIRES_HUMAN_REVIEW
                result.conditions.append("Human review required for sensitive action")
                result.reasoning = "Action contains dangerous keywords"
                await self._emit_human_review(action, actor)
                return await self._finalize(result, start_time)

            # Phase 2: Always require approval check
            if self._always_requires_approval(action):
                result.decision_type = DecisionType.REQUIRES_HUMAN_REVIEW
                result.conditions.append("This action type always requires approval")
                return await self._finalize(result, start_time)

            # Phase 3: Privacy check
            if context.get("has_pii") or context.get("personal_data"):
                result.decision_type = DecisionType.APPROVED_WITH_CONDITIONS
                result.is_approved = True
                result.conditions.append("Approved with privacy safeguards")
                result.conditions.append("PII must be masked in logs")
                return await self._finalize(result, start_time)

            # Phase 4: Fairness check - ensure no discrimination
            if not self._check_fairness(action, context):
                result.decision_type = DecisionType.REJECTED_BY_ETHICS
                result.conditions.append("Action may introduce unfair bias")
                result.reasoning = "Fairness check failed"
                return await self._finalize(result, start_time)

            # Phase 5: Transparency check - ensure explainability
            if not self._check_transparency(action, context):
                result.decision_type = DecisionType.APPROVED_WITH_CONDITIONS
                result.conditions.append("Enhanced logging required for transparency")
                result.conditions.append("Audit trail must be maintained")
                return await self._finalize(result, start_time)

            # Phase 6: Accountability check - ensure responsibility
            if not self._check_accountability(action, context):
                result.decision_type = DecisionType.REQUIRES_HUMAN_REVIEW
                result.conditions.append("Human accountability required")
                result.reasoning = "Accountability check requires human oversight"
                await self._emit_human_review(action, actor)
                return await self._finalize(result, start_time)

            # Phase 7: Security check - final security validation
            if not self._check_security(action, context):
                result.decision_type = DecisionType.REJECTED_BY_GOVERNANCE
                result.conditions.append("Security vulnerability detected")
                result.reasoning = "Security check failed"
                return await self._finalize(result, start_time)

            # Default: Approved
            result.decision_type = DecisionType.APPROVED
            result.is_approved = True
            result.reasoning = "All checks passed"

        except Exception as e:
            result.decision_type = DecisionType.ERROR
            result.rejection_reasons.append(f"Validation error: {str(e)}")

        return await self._finalize(result, start_time)

    def _is_dangerous(self, action: str) -> bool:
        """Verifica se ação contém keywords perigosas."""
        action_lower = action.lower()
        return any(kw in action_lower for kw in self.settings.dangerous_keywords)

    def _always_requires_approval(self, action: str) -> bool:
        """Verifica se ação sempre precisa de aprovação."""
        action_lower = action.lower()
        return any(kw in action_lower for kw in self.settings.always_require_approval)

    async def _finalize(self, result: EthicalDecision, start_time: float) -> EthicalDecision:
        """Finaliza decisão com duração."""
        result.duration_ms = (time.time() - start_time) * 1000

        # Armazena na memória
        await self.memory.set(result.decision_id, result.model_dump())

        return result

    async def _emit_human_review(self, action: str, actor: str) -> None:
        """Emite evento de human review necessário."""
        await self.event_bus.emit(
            EventType.ETHICS_HUMAN_REVIEW_REQUIRED,
            {"action": action, "actor": actor},
            source="magistrate",
        )

    def _check_fairness(self, action: str, context: Dict[str, Any]) -> bool:
        """Verifica se ação não introduz viés ou discriminação."""
        # Check for potentially discriminatory keywords
        fairness_keywords = ["bias", "discriminate", "exclude", "favor", "unfair"]
        action_lower = action.lower()

        has_discriminatory_terms = any(kw in action_lower for kw in fairness_keywords)

        # If action involves data processing, ensure fairness considerations
        if context.get("involves_data_processing"):
            return not has_discriminatory_terms

        # Even for non-data processing, flag discriminatory actions
        return not has_discriminatory_terms

    def _check_transparency(self, action: str, context: Dict[str, Any]) -> bool:
        """Verifica se ação pode ser explicada e auditada."""
        # Actions requiring high transparency
        high_risk_actions = [
            "deploy",
            "modify_system",
            "access_sensitive_data",
            "critical",
        ]

        action_lower = action.lower()
        is_high_risk = any(risk in action_lower for risk in high_risk_actions)

        # High risk actions require explicit transparency measures
        if is_high_risk and not context.get("transparency_measures"):
            return False

        return True

    def _check_accountability(self, action: str, context: Dict[str, Any]) -> bool:
        """Verifica se há responsabilidade clara pela ação."""
        # Actions requiring human accountability
        critical_actions = [
            "delete_permanent",
            "modify_critical_system",
            "access_confidential",
            "make_decision_impact_users",
            "delete permanent",
            "modify critical",
            "permanent data",
        ]

        action_lower = action.lower()
        is_critical = any(critical in action_lower for critical in critical_actions)

        # Critical actions always require human review
        if is_critical:
            return False  # Forces REQUIRES_HUMAN_REVIEW

        return True

    def _check_security(self, action: str, context: Dict[str, Any]) -> bool:
        """Verifica se ação não apresenta vulnerabilidades de segurança."""
        # Security-sensitive keywords that might indicate vulnerabilities
        security_risks = [
            "eval(",
            "exec(",
            "pickle",
            "subprocess",
            "shell=true",
            "dangerous_function",
        ]

        action_lower = action.lower()
        has_security_risk = any(risk in action_lower for risk in security_risks)

        return not has_security_risk

    async def get_decision_history(self, limit: int = 10) -> List[Dict]:
        """Retorna histórico de decisões."""
        events = self.event_bus.get_history(
            EventType.ETHICS_VALIDATION_COMPLETED, limit=limit
        )
        return [e.data for e in events]


# Instância global
_magistrate: Optional[EthicalMagistrate] = None


def get_magistrate() -> EthicalMagistrate:
    """Retorna singleton do magistrate."""
    global _magistrate
    if _magistrate is None:
        _magistrate = EthicalMagistrate()
    return _magistrate


# =============================================================================
# MCP TOOL FUNCTIONS (registrar no mcp_server.py)
# =============================================================================


async def ethical_validate(
    ctx, action: str, context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Valida uma ação contra o framework ético de 7 fases.

    Args:
        action: Descrição da ação a ser validada
        context: Contexto adicional (has_pii, target, etc.)
        actor: Quem está solicitando a ação

    Returns:
        Decisão ética com approved, conditions, reasoning
    """
    await ctx.info(f"Validating action: {action[:50]}...")

    magistrate = get_magistrate()
    decision = await magistrate.validate(action, context or {}, "system")

    await ctx.info(f"Decision: {decision.decision_type.value}")

    return decision.model_dump()


async def ethical_audit(ctx, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Retorna histórico de decisões éticas.

    Args:
        limit: Número máximo de decisões a retornar

    Returns:
        Lista de decisões recentes
    """
    magistrate = get_magistrate()
    return await magistrate.get_decision_history(limit)
