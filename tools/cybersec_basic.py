"""
CyberSec Basic - Reconnaissance and Basic Pentesting Tool
Realiza varreduras de portas, análise de headers HTTP e wrappers para ferramentas externas.
"""

import asyncio
import logging
import shutil
import socket
import time
from typing import Any, Dict, List, Optional

import httpx
from fastmcp import Context
from pydantic import BaseModel, Field

from core.settings import get_settings
from core.event_bus import get_event_bus, EventType
from core.memory import get_agent_memory

logger = logging.getLogger(__name__)


class PortResult(BaseModel):
    """Resultado de scan de porta."""
    port: int
    state: str  # open, closed, filtered
    service: str
    banner: Optional[str] = None


class ReconResult(BaseModel):
    """Resultado de reconhecimento."""
    target: str
    timestamp: float
    open_ports: List[PortResult] = Field(default_factory=list)
    http_headers: Dict[str, str] = Field(default_factory=dict)
    security_issues: List[str] = Field(default_factory=list)
    tool_outputs: Dict[str, Any] = Field(default_factory=dict)


class CyberSecAgent:
    """
    Agente de Cibersegurança Básica.
    
    Capacidades:
    - Port Scanning (Async)
    - HTTP Header Analysis
    - Tool Wrappers (Nuclei, Subfinder - se disponíveis)
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.memory = get_agent_memory("cybersec_agent")
        self.event_bus = get_event_bus()
    
    async def run_recon(
        self,
        target: str,
        scan_ports: bool = True,
        scan_web: bool = True
    ) -> ReconResult:
        """Executa reconhecimento básico no alvo."""
        start_time = time.time()
        
        await self.event_bus.emit(
            EventType.RECON_STARTED,
            {"target": target, "scan_ports": scan_ports, "scan_web": scan_web},
            source="cybersec_agent"
        )
        
        result = ReconResult(target=target, timestamp=start_time)
        
        # 1. Port Scan
        if scan_ports:
            # Verifica se é IP ou domínio
            try:
                ip = socket.gethostbyname(target)
                result.open_ports = await self._scan_ports(ip)
            except socket.gaierror:
                logger.error(f"Could not resolve host: {target}")
                result.security_issues.append(f"DNS resolution failed for {target}")

        # 2. Web Analysis
        if scan_web:
            await self._analyze_web(target, result)
            
        # 3. External Tools (if available)
        await self._run_external_tools(target, result)
        
        # Cache result
        self.memory.set(f"recon:{target}", result.model_dump(), ttl_seconds=3600)
        
        await self.event_bus.emit(
            EventType.RECON_COMPLETED,
            {"target": target, "issues_found": len(result.security_issues)},
            source="cybersec_agent"
        )
        
        return result

    async def _scan_ports(self, ip: str, ports: List[int] = None) -> List[PortResult]:
        """Scan de portas assíncrono."""
        if ports is None:
            # Top 20 common ports
            ports = [21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 443, 445, 993, 995, 1433, 3306, 3389, 5432, 5900, 8080]
            
        results = []
        
        async def check_port(p: int):
            conn = asyncio.open_connection(ip, p)
            try:
                reader, writer = await asyncio.wait_for(conn, timeout=1.0)
                writer.close()
                await writer.wait_closed()
                return p, True
            except (asyncio.TimeoutError, ConnectionRefusedError, OSError):
                return p, False

        tasks = [check_port(p) for p in ports]
        scan_results = await asyncio.gather(*tasks)
        
        for port, is_open in scan_results:
            if is_open:
                service_name = "unknown"
                try:
                    service_name = socket.getservbyport(port)
                except OSError:
                    pass
                    
                results.append(PortResult(
                    port=port,
                    state="open",
                    service=service_name
                ))
                
        return results

    async def _analyze_web(self, target: str, result: ReconResult) -> None:
        """Analisa headers HTTP e segurança básica."""
        url = target if target.startswith("http") else f"https://{target}"
        
        try:
            async with httpx.AsyncClient(verify=False, timeout=5.0) as client:
                response = await client.get(url)
                
                # Armazena headers
                result.http_headers = dict(response.headers)
                
                # Security Headers Checks
                missing_headers = []
                security_headers = [
                    "Strict-Transport-Security",
                    "Content-Security-Policy",
                    "X-Frame-Options",
                    "X-Content-Type-Options"
                ]
                
                for header in security_headers:
                    if header not in response.headers:
                        missing_headers.append(header)
                
                if missing_headers:
                    result.security_issues.append(f"Missing security headers: {', '.join(missing_headers)}")
                    
                # Server leakage
                if "Server" in response.headers:
                    result.security_issues.append(f"Server header exposed: {response.headers['Server']}")
                    
        except Exception as e:
            logger.warning(f"Web analysis failed: {e}")
            result.tool_outputs["web_analysis_error"] = str(e)

    async def _run_external_tools(self, target: str, result: ReconResult) -> None:
        """Executa ferramentas externas se disponíveis."""
        # Check for Nuclei
        nuclei_path = shutil.which("nuclei")
        if nuclei_path:
            # Simulação de chamada segura - em produção, executaríamos o processo
            # result.tool_outputs["nuclei"] = await self._run_subprocess([nuclei_path, "-u", target, ...])
            result.tool_outputs["nuclei_status"] = "installed (execution disabled in basic agent)"
        else:
            result.tool_outputs["nuclei_status"] = "not_installed"


# Singleton
_cybersec_agent: Optional[CyberSecAgent] = None


def get_cybersec_agent() -> CyberSecAgent:
    """Retorna singleton do CyberSec Agent."""
    global _cybersec_agent
    if _cybersec_agent is None:
        _cybersec_agent = CyberSecAgent()
    return _cybersec_agent


# =============================================================================
# MCP TOOL FUNCTIONS
# =============================================================================

async def cybersec_recon(
    ctx: Context,
    target: str,
    scan_ports: bool = True,
    scan_web: bool = True
) -> Dict[str, Any]:
    """
    Realiza reconhecimento básico de cibersegurança (port scan, web headers).
    
    Args:
        target: IP ou domínio alvo
        scan_ports: Se deve escanear portas comuns (Top 20)
        scan_web: Se deve verificar headers HTTP de segurança
        
    Returns:
        Relatório de reconhecimento com portas abertas e issues encontrados.
    """
    ctx.info(f"Starting reconnaissance on {target}")
    
    agent = get_cybersec_agent()
    result = await agent.run_recon(target, scan_ports, scan_web)
    
    return result.model_dump()
