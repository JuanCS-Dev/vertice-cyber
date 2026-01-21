"""
Wargame Safety Manager - Múltiplas camadas de proteção.

NUNCA execute código de ataque sem passar por TODAS as camadas.
"""

import logging
from pathlib import Path
from typing import Optional, Set
from datetime import datetime

from pydantic import BaseModel, Field

from core.feature_flags import get_feature_flags
from tools.magistrate import get_magistrate

logger = logging.getLogger(__name__)


class WargameSafetyError(Exception):
    """Erro de segurança no wargame."""

    pass


class SafetyCheckResult(BaseModel):
    """Resultado de verificação de segurança."""

    is_safe: bool
    blocked_by: Optional[str] = None
    reason: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class WargameSafetyManager:
    """
    Gerenciador de segurança para execuções de wargame.

    Implementa 5 camadas de proteção:
    1. Feature Flag
    2. Ethical Magistrate
    3. Target Whitelist
    4. Sandbox Mode
    5. Audit Log
    """

    APPROVED_TARGETS_FILE = Path.home() / ".vertice" / "wargame_approved_targets.txt"
    AUDIT_LOG_FILE = Path.home() / ".vertice" / "wargame_audit.log"

    def __init__(self):
        self.flags = get_feature_flags()
        self._approved_targets: Set[str] = self._load_approved_targets()

    def _load_approved_targets(self) -> Set[str]:
        """Carrega lista de targets aprovados."""
        try:
            if not self.APPROVED_TARGETS_FILE.exists():
                self.APPROVED_TARGETS_FILE.parent.mkdir(parents=True, exist_ok=True)
                self.APPROVED_TARGETS_FILE.write_text(
                    "# Targets aprovados para wargame\n# Um por linha\nlocal\nlocalhost\n127.0.0.1\n"
                )

            targets = set()
            for line in self.APPROVED_TARGETS_FILE.read_text().splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    targets.add(line.lower())

            return targets
        except Exception as e:
            logger.error(f"Failed to load approved targets: {e}")
            return {"localhost", "127.0.0.1"}

    async def check_all_layers(
        self, scenario_id: str, target: str, actor: str = "system"
    ) -> SafetyCheckResult:
        """
        Verifica TODAS as camadas de segurança.

        Args:
            scenario_id: ID do cenário a executar
            target: Alvo da execução
            actor: Quem está solicitando

        Returns:
            SafetyCheckResult indicando se pode prosseguir
        """
        # Layer 1: Feature Flag
        if not self.flags.wargame_allow_real_execution:
            return SafetyCheckResult(
                is_safe=False,
                blocked_by="feature_flag",
                reason="Real wargame execution is disabled. Set FF_WARGAME_ALLOW_REAL_EXECUTION=true to enable.",
            )

        # Layer 2: Target Whitelist
        if target.lower() not in self._approved_targets:
            return SafetyCheckResult(
                is_safe=False,
                blocked_by="target_whitelist",
                reason=f"Target '{target}' not in approved list. Add to {self.APPROVED_TARGETS_FILE}",
            )

        # Layer 3: Ethical Magistrate
        try:
            magistrate = get_magistrate()
            decision = await magistrate.validate(
                action=f"Execute wargame scenario {scenario_id} against {target}",
                context={
                    "has_explicit_consent": self.flags.wargame_require_explicit_consent,
                    "target": target,
                    "scenario_id": scenario_id,
                    "requires_human_approval": True,
                },
                actor=actor,
            )

            if not decision.is_approved:
                return SafetyCheckResult(
                    is_safe=False,
                    blocked_by="ethical_magistrate",
                    reason=f"Ethical validation failed: {decision.reasoning}",
                )
        except Exception as e:
            logger.error(f"Magistrate validation failed: {e}")
            return SafetyCheckResult(
                is_safe=False,
                blocked_by="ethical_magistrate",
                reason=f"Safety check error: {str(e)}",
            )

        # Layer 4: Audit Log
        self._audit_log(f"APPROVED: Scenario {scenario_id} on {target} by {actor}")

        return SafetyCheckResult(is_safe=True)

    def _audit_log(self, message: str) -> None:
        """Escreve no log de auditoria (append-only)."""
        try:
            self.AUDIT_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.utcnow().isoformat()
            log_line = f"[{timestamp}] {message}\n"

            with open(self.AUDIT_LOG_FILE, "a") as f:
                f.write(log_line)
        except Exception as e:
            logger.error(f"Failed to write to audit log: {e}")

        logger.info(f"WARGAME AUDIT: {message}")

    def get_sandbox_command(self, command: list[str]) -> list[str]:
        """
        Wraps comando em sandbox Docker.

        Args:
            command: Comando original

        Returns:
            Comando wrapped em container
        """
        if self.flags.wargame_sandbox_mode == "none":
            logger.warning("SANDBOX DISABLED - Running command directly!")
            return command

        # Docker sandbox
        timeout = self.flags.wargame_max_duration_seconds

        return [
            "docker",
            "run",
            "--rm",
            "--network=none",  # Sem acesso à rede
            "--memory=512m",  # Limite de memória
            f"--stop-timeout={timeout}",
            "wargame-sandbox:latest",  # Imagem pré-configurada
            *command,
        ]


# Singleton
_safety_manager: Optional[WargameSafetyManager] = None


def get_wargame_safety() -> WargameSafetyManager:
    """Retorna singleton do safety manager."""
    global _safety_manager
    if _safety_manager is None:
        _safety_manager = WargameSafetyManager()
    return _safety_manager
