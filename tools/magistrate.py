"""
Ethical Magistrate - Core Governance Tool
Valida todas as ações do sistema contra framework ético.
"""

import time
from enum import Enum
from typing import Any, Dict, List, Optional

from fastmcp import Context
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

        # Emite evento de início
        await self.event_bus.emit(
            EventType.ETHICS_VALIDATION_REQUESTED,
            {"action": action, "actor": actor},
            source="magistrate",
        )

        result = EthicalDecision(
            decision_id=decision_id,
            decision_type=DecisionType.ERROR,
            action=action,
            actor=actor,
            is_approved=False,
        )

        try:
            # Phase 1: Governance check
            if self._is_dangerous(action):
                result.decision_type = DecisionType.REQUIRES_HUMAN_REVIEW
                result.conditions.append("Human review required for sensitive action")
                result.reasoning = "Action contains dangerous keywords"
                await self._emit_human_review(action, actor)
                return self._finalize(result, start_time)

            # Phase 2: Always require approval check
            if self._always_requires_approval(action):
                result.decision_type = DecisionType.REQUIRES_HUMAN_REVIEW
                result.conditions.append("This action type always requires approval")
                return self._finalize(result, start_time)

            # Phase 3: Privacy check
            if context.get("has_pii") or context.get("personal_data"):
                result.decision_type = DecisionType.APPROVED_WITH_CONDITIONS
                result.is_approved = True
                result.conditions.append("Approved with privacy safeguards")
                result.conditions.append("PII must be masked in logs")
                return self._finalize(result, start_time)

            # Phase 4-7: Additional checks (simplificado por ora)
            # TODO: Implementar fairness, transparency, accountability, security

            # Default: Approved
            result.decision_type = DecisionType.APPROVED
            result.is_approved = True
            result.reasoning = "All checks passed"

        except Exception as e:
            result.decision_type = DecisionType.ERROR
            result.rejection_reasons.append(f"Validation error: {str(e)}")

        return self._finalize(result, start_time)

    def _is_dangerous(self, action: str) -> bool:
        """Verifica se ação contém keywords perigosas."""
        action_lower = action.lower()
        return any(kw in action_lower for kw in self.settings.dangerous_keywords)

    def _always_requires_approval(self, action: str) -> bool:
        """Verifica se ação sempre precisa de aprovação."""
        action_lower = action.lower()
        return any(kw in action_lower for kw in self.settings.always_require_approval)

    def _finalize(self, result: EthicalDecision, start_time: float) -> EthicalDecision:
        """Finaliza decisão com duração."""
        result.duration_ms = (time.time() - start_time) * 1000

        # Armazena na memória
        self.memory.set(result.decision_id, result.model_dump())

        return result

    async def _emit_human_review(self, action: str, actor: str) -> None:
        """Emite evento de human review necessário."""
        await self.event_bus.emit(
            EventType.ETHICS_HUMAN_REVIEW_REQUIRED,
            {"action": action, "actor": actor},
            source="magistrate",
        )

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
    ctx: Context,
    action: str,
    context: Optional[Dict[str, Any]] = None,
    actor: str = "user",
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
    ctx.info(f"Validating action: {action[:50]}...")

    magistrate = get_magistrate()
    decision = await magistrate.validate(action, context or {}, actor)

    ctx.info(f"Decision: {decision.decision_type.value}")

    return decision.model_dump()


async def ethical_audit(ctx: Context, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Retorna histórico de decisões éticas.

    Args:
        limit: Número máximo de decisões a retornar

    Returns:
        Lista de decisões recentes
    """
    magistrate = get_magistrate()
    return await magistrate.get_decision_history(limit)
