"""
Wargame Executor - Offensive Security Simulation Tool
Executa cenários de ataque simulados para validar defesas.
"""

import logging
import time
from enum import Enum
from typing import Any, Dict, List, Optional

from fastmcp import Context
from pydantic import BaseModel, Field

from core.settings import get_settings
from core.event_bus import get_event_bus, EventType
from core.memory import get_agent_memory

logger = logging.getLogger(__name__)


class ScenarioDifficulty(str, Enum):
    """Dificuldade do cenário."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class ScenarioType(str, Enum):
    """Tipo de cenário."""
    RED_TEAM = "red_team"
    PURPLE_TEAM = "purple_team"
    TABLETOP = "tabletop"
    BREACH_SIMULATION = "breach_simulation"


class WargameScenario(BaseModel):
    """Definição de um cenário de wargame."""
    id: str
    name: str
    description: str
    difficulty: ScenarioDifficulty
    scenario_type: ScenarioType
    tactics: List[str]  # MITRE ATT&CK Tactics
    techniques: List[str]  # MITRE ATT&CK Techniques
    estimated_duration_s: int


class WargameResult(BaseModel):
    """Resultado de uma simulação."""
    scenario_id: str
    execution_id: str
    timestamp: float
    success: bool
    detection_rate: float  # % de ações detectadas
    logs: List[str] = Field(default_factory=list)
    artifacts: Dict[str, Any] = Field(default_factory=dict)


class WargameExecutor:
    """
    Executor de Wargames.
    
    Gerencia e executa simulações de ataque para testar a resposta
    do sistema imunológico e dos analistas.
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.memory = get_agent_memory("wargame_executor")
        self.event_bus = get_event_bus()
        self._scenarios = self._load_default_scenarios()
    
    def _load_default_scenarios(self) -> Dict[str, WargameScenario]:
        """Carrega cenários padrão."""
        scenarios = [
            WargameScenario(
                id="scenario_001",
                name="Data Exfiltration Simulation",
                description="Simulates data exfiltration via DNS tunneling.",
                difficulty=ScenarioDifficulty.INTERMEDIATE,
                scenario_type=ScenarioType.BREACH_SIMULATION,
                tactics=["Exfiltration", "Command and Control"],
                techniques=["T1048", "T1071"],
                estimated_duration_s=60
            ),
            WargameScenario(
                id="scenario_002",
                name="Ransomware Behavior",
                description="Simulates rapid file encryption and note dropping.",
                difficulty=ScenarioDifficulty.ADVANCED,
                scenario_type=ScenarioType.RED_TEAM,
                tactics=["Impact"],
                techniques=["T1486"],
                estimated_duration_s=120
            ),
            WargameScenario(
                id="scenario_003",
                name="Privilege Escalation",
                description="Simulates attempts to gain root/admin access.",
                difficulty=ScenarioDifficulty.INTERMEDIATE,
                scenario_type=ScenarioType.PURPLE_TEAM,
                tactics=["Privilege Escalation"],
                techniques=["T1068"],
                estimated_duration_s=45
            )
        ]
        return {s.id: s for s in scenarios}
    
    async def list_scenarios(self) -> List[WargameScenario]:
        """Lista cenários disponíveis."""
        return list(self._scenarios.values())
    
    async def run_simulation(
        self,
        scenario_id: str,
        target: str = "local"
    ) -> WargameResult:
        """
        Executa um cenário de wargame.
        
        Args:
            scenario_id: ID do cenário
            target: Alvo da simulação
            
        Returns:
            Resultado da simulação
        """
        scenario = self._scenarios.get(scenario_id)
        if not scenario:
            raise ValueError(f"Scenario {scenario_id} not found")
        
        execution_id = f"exec_{int(time.time())}"
        
        await self.event_bus.emit(
            EventType.WARGAME_SIMULATION_STARTED,
            {"scenario_id": scenario_id, "target": target, "execution_id": execution_id},
            source="wargame_executor"
        )
        
        # Simulação da execução (Placeholder logic for safe environment)
        # Em um ambiente real, isso chamaria ferramentas como Atomic Red Team
        # ou scripts de ataque controlados.
        
        logs = []
        logs.append(f"Target: {target}")
        logs.append("Initializing attack vectors...")

        for tech in scenario.techniques:
            logs.append(f"Executing technique {tech}...")
        
        logs.append("Simulation completed.")
        
        # Simula resultado
        success = True  # O ataque "rodou" com sucesso (simulado)
        detection_rate = 0.85  # Simula que o sistema detectou 85%
        
        result = WargameResult(
            scenario_id=scenario_id,
            execution_id=execution_id,
            timestamp=time.time(),
            success=success,
            detection_rate=detection_rate,
            logs=logs,
            artifacts={"report_path": f"/tmp/wargame_{execution_id}.json"}
        )
        
        # Salva na memória
        self.memory.set(execution_id, result.model_dump(), ttl_seconds=86400)
        
        await self.event_bus.emit(
            EventType.WARGAME_SIMULATION_COMPLETED,
            {"execution_id": execution_id, "success": success, "detection_rate": detection_rate},
            source="wargame_executor"
        )
        
        return result


# Singleton
_wargame_executor: Optional[WargameExecutor] = None


def get_wargame_executor() -> WargameExecutor:
    """Retorna singleton do Wargame Executor."""
    global _wargame_executor
    if _wargame_executor is None:
        _wargame_executor = WargameExecutor()
    return _wargame_executor


# =============================================================================
# MCP TOOL FUNCTIONS
# =============================================================================

async def wargame_list_scenarios(
    ctx: Context
) -> List[Dict[str, Any]]:
    """
    Lista os cenários de ataque disponíveis para simulação.
    
    Returns:
        Lista de cenários com detalhes de táticas e técnicas.
    """
    executor = get_wargame_executor()
    scenarios = await executor.list_scenarios()
    return [s.model_dump() for s in scenarios]


async def wargame_run_simulation(
    ctx: Context,
    scenario_id: str,
    target: str = "local"
) -> Dict[str, Any]:
    """
    Executa uma simulação de ataque (Wargame).
    
    Args:
        scenario_id: ID do cenário (obter via wargame_list_scenarios)
        target: Alvo da simulação (IP, domínio ou 'local')
    
    Returns:
        Resultado da simulação incluindo logs e taxa de detecção.
    """
    await ctx.info(f"Running wargame scenario {scenario_id} against {target}")
    
    executor = get_wargame_executor()
    try:
        result = await executor.run_simulation(scenario_id, target)
        return result.model_dump()
    except ValueError as e:
        return {"error": str(e)}
