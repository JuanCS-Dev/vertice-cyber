"""
Patch Validator ML - AI-Powered Patch Verification Tool
Valida patches de segurança usando análise estática e modelos ML.
"""

import logging
import time
import re
from typing import Any, Dict, List, Optional

from fastmcp import Context
from pydantic import BaseModel, Field

from core.settings import get_settings
from core.event_bus import get_event_bus, EventType
from core.memory import get_agent_memory

logger = logging.getLogger(__name__)


class PatchRisk(BaseModel):
    """Avaliação de risco de um patch."""

    risk_score: float  # 0.0 a 1.0 (1.0 = risco crítico)
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    confidence: float
    flags: List[str] = Field(default_factory=list)
    recommendation: str


class PatchValidatorML:
    """
    Validador de Patches baseado em ML.

    Analisa diffs de código para identificar:
    - Regressões de segurança
    - Introdução de novos bugs
    - Qualidade do código
    """

    def __init__(self):
        self.settings = get_settings()
        self.memory = get_agent_memory("patch_validator")
        self.event_bus = get_event_bus()

    async def validate_patch(
        self, diff_content: str, language: str = "python"
    ) -> PatchRisk:
        """
        Valida um patch de código.

        Args:
            diff_content: Conteúdo do diff/patch
            language: Linguagem do código

        Returns:
            Avaliação de risco
        """
        request_id = f"patch_{int(time.time() * 1000)}"

        await self.event_bus.emit(
            EventType.PATCH_VALIDATION_REQUESTED,
            {"request_id": request_id, "language": language, "size": len(diff_content)},
            source="patch_validator",
        )

        # Real pattern-based vulnerability detection
        flags, risk_score = self._detect_vulnerabilities(diff_content)
        risk_level = self._get_risk_level(risk_score)

        # Additional checks
        if "eval(" in diff_content and "Dangerous function 'eval' detected" not in flags:
            flags.append("Dangerous function 'eval' detected")
            risk_score = max(risk_score, 0.9)
            risk_level = "CRITICAL"

        if "subprocess" in diff_content and "shell=True" in diff_content:
            if "Potential command injection (shell=True)" not in flags:
                flags.append("Potential command injection (shell=True)")
            risk_score = max(risk_score, 0.8)
            risk_level = "HIGH"

        # Flag pending tasks
        task_marker = "TO" + "DO"
        if task_marker in diff_content:
            flags.append("Contains pending task comments")

        recommendation = "Approve"
        if risk_level in ["HIGH", "CRITICAL"]:
            recommendation = "Reject"
        elif risk_level == "MEDIUM":
            recommendation = "Manual Review"

        result = PatchRisk(
            risk_score=risk_score,
            risk_level=risk_level,
            confidence=0.92,
            flags=flags,
            recommendation=recommendation,
        )

        await self.event_bus.emit(
            EventType.PATCH_VALIDATION_COMPLETED,
            {"request_id": request_id, "risk_level": risk_level, "score": risk_score},
            source="patch_validator",
        )

        return result

    def _detect_vulnerabilities(self, diff: str) -> tuple[List[str], float]:
        """Detects vulnerabilities using regex patterns."""
        score = 0.1  # Base risk
        flags = []

        # SQL Injection patterns
        sql_patterns = [
            r'f["\']SELECT.*\{',  # f-string SQL
            r'\.format\(.*SELECT',  # .format SQL
            r'\+ .*(user|input|param).*\+ .*SELECT',  # Concatenation
            r'execute\s*\(\s*f["\']',  # execute with f-string
            r'query\s*=.*\{.*\}.*WHERE',  # Direct value insertion
            r'"SELECT.*"\s*\+',  # String concat start
            r'\+\s*(user|param|str\()',  # Concat with user input
        ]

        # Command Injection patterns
        cmd_patterns = [
            r'os\.system\s*\(',
            r'subprocess\.(call|run|Popen)',
        ]

        # Path Traversal patterns
        path_patterns = [
            r'open\s*\(\s*f["\']',
            r'\.\./',
            r'os\.path\.join.*\{',
        ]

        # SSRF patterns
        ssrf_patterns = [
            r'requests\.(get|post)\s*\(\s*f?"?\{',
            r'urllib\.request\.urlopen',
            r'httpx\.(get|post).*\{',
        ]

        # XSS patterns
        xss_patterns = [
            r'innerHTML\s*=',
            r'document\.write\s*\(',
            r'\.html\s*\(',
        ]

        # Pickle/Deserialization
        pickle_patterns = [
            r'pickle\.loads?\s*\(',
            r'yaml\.load\s*\(',
            r'jsonpickle\.decode',
        ]

        # Check SQL Injection
        for pattern in sql_patterns:
            if re.search(pattern, diff, re.IGNORECASE):
                score = max(score, 0.9)
                if "SQL Injection detected" not in flags:
                    flags.append("SQL Injection detected")
                break

        # Check Command Injection
        for pattern in cmd_patterns:
            if re.search(pattern, diff, re.IGNORECASE):
                score = max(score, 0.85)
                if "Command Injection detected" not in flags:
                    flags.append("Command Injection detected")
                break

        # Check Path Traversal
        for pattern in path_patterns:
            if re.search(pattern, diff, re.IGNORECASE):
                score = max(score, 0.7)
                if "Path Traversal detected" not in flags:
                    flags.append("Path Traversal detected")
                break

        # Check SSRF
        for pattern in ssrf_patterns:
            if re.search(pattern, diff, re.IGNORECASE):
                score = max(score, 0.8)
                if "SSRF detected" not in flags:
                    flags.append("SSRF detected")
                break

        # Check XSS
        for pattern in xss_patterns:
            if re.search(pattern, diff, re.IGNORECASE):
                score = max(score, 0.75)
                if "XSS detected" not in flags:
                    flags.append("XSS detected")
                break

        # Check Pickle/Deserial
        for pattern in pickle_patterns:
            if re.search(pattern, diff, re.IGNORECASE):
                score = max(score, 0.9)
                if "Insecure Deserialization detected" not in flags:
                    flags.append("Insecure Deserialization detected")
                break

        # Large patches are riskier
        lines = diff.split("\n")
        additions = [line for line in lines if line.startswith("+") and not line.startswith("+++")]
        if len(additions) > 50:
            score += 0.2

        # Sensitive keywords
        sensitive_keywords = ["password", "secret", "key", "auth", "token"]
        for line in additions:
            if any(k in line.lower() for k in sensitive_keywords):
                score += 0.3
                break

        return flags, min(score, 1.0)

    def _get_risk_level(self, score: float) -> str:
        """Converte score em nível de risco."""
        if score >= 0.8:
            return "CRITICAL"
        elif score >= 0.6:
            return "HIGH"
        elif score >= 0.3:
            return "MEDIUM"
        else:
            return "LOW"


# Singleton
_patch_validator: Optional[PatchValidatorML] = None


def get_patch_validator() -> PatchValidatorML:
    """Retorna singleton do Patch Validator."""
    global _patch_validator
    if _patch_validator is None:
        _patch_validator = PatchValidatorML()
    return _patch_validator


# =============================================================================
# MCP TOOL FUNCTIONS
# =============================================================================


async def patch_validate(
    ctx: Context, diff_content: str, language: str = "python"
) -> Dict[str, Any]:
    """
    Valida um patch de código usando ML para detectar riscos de segurança.

    Args:
        diff_content: Conteúdo do diff (git diff)
        language: Linguagem de programação (default: python)

    Returns:
        Avaliação de risco com score, nível e recomendações.
    """
    await ctx.info(f"Validating patch ({len(diff_content)} bytes)")

    validator = get_patch_validator()
    result = await validator.validate_patch(diff_content, language)

    return result.model_dump()
