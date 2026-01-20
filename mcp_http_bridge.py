#!/usr/bin/env python3
"""
MCP HTTP Bridge - Expõe MCP Tools via HTTP REST API

Permite o dashboard web chamar tools do Vertice Cyber diretamente.
Resolve GAP 1 (Tool Registry), GAP 2 (MockContext), GAP 3 (Event Streaming).

Usage:
    python mcp_http_bridge.py
    # Or integrated with mcp_server.py:
    python mcp_server.py --dual-mode
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Callable, Coroutine, Dict, List, Optional, Set
from uuid import uuid4

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# =============================================================================
# TOOL IMPORTS (Complete Registry - GAP 1 RESOLVED)
# =============================================================================

# Governance Tools
from tools.magistrate import ethical_validate, ethical_audit

# OSINT Tools
from tools.osint import osint_investigate, osint_breach_check, osint_google_dork

# Threat Intelligence Tools
from tools.threat import threat_analyze, threat_intelligence, threat_predict

# Compliance Tools
from tools.compliance import compliance_assess, compliance_report, compliance_check

# Offensive Tools
from tools.wargame import wargame_list_scenarios, wargame_run_simulation
from tools.patch_ml import patch_validate

# CyberSec Basic
from tools.cybersec_basic import cybersec_recon

# AI Tools (Vertex AI)
from tools.mcp_ai_tools import (
    ai_threat_analysis,
    ai_compliance_assessment,
    ai_osint_analysis,
    ai_stream_analysis,
    ai_integrated_assessment,
)

# Event Bus
from core.event_bus import get_event_bus, EventType, Event

# =============================================================================
# LOGGING
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("mcp_http_bridge")

# =============================================================================
# MOCK CONTEXT (GAP 2 RESOLVED)
# =============================================================================


class MockContext:
    """
    Mock do FastMCP Context para uso no HTTP Bridge.
    
    Simula os métodos que tools MCP esperam do objeto Context:
    - await ctx.info(message)
    - await ctx.warn(message) / await ctx.warning(message)
    - await ctx.error(message)
    
    Métodos são async para compatibilidade com tools que usam await.
    """

    def __init__(self, request_id: Optional[str] = None):
        self.request_id = request_id or str(uuid4())
        self.logs: List[Dict[str, Any]] = []
        self._start_time = datetime.utcnow()

    async def info(self, message: str) -> None:
        """Log info message (async for compatibility)."""
        log = {
            "level": "INFO",
            "message": message,
            "request_id": self.request_id,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self.logs.append(log)
        logger.info(f"[{self.request_id[:8]}] {message}")

    async def warn(self, message: str) -> None:
        """Log warning message (async for compatibility)."""
        log = {
            "level": "WARN",
            "message": message,
            "request_id": self.request_id,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self.logs.append(log)
        logger.warning(f"[{self.request_id[:8]}] {message}")

    # Alias for compatibility
    async def warning(self, message: str) -> None:
        await self.warn(message)

    async def error(self, message: str) -> None:
        """Log error message (async for compatibility)."""
        log = {
            "level": "ERROR",
            "message": message,
            "request_id": self.request_id,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self.logs.append(log)
        logger.error(f"[{self.request_id[:8]}] {message}")

    def get_logs(self) -> List[Dict[str, Any]]:
        """Retorna todos os logs desta request."""
        return self.logs


def create_mock_context(request_id: Optional[str] = None) -> MockContext:
    """Factory para criar MockContext."""
    return MockContext(request_id)


# =============================================================================
# TOOL REGISTRY (GAP 1 RESOLVED - Complete Mapping)
# =============================================================================

# Type alias for tool functions
ToolFunction = Callable[..., Coroutine[Any, Any, Any]]


class ToolInfo(BaseModel):
    """Metadata sobre uma tool."""

    name: str
    agent: str
    category: str
    description: str
    parameters: Dict[str, str]


# Complete tool registry mapping name -> function
TOOL_REGISTRY: Dict[str, ToolFunction] = {
    # Governance
    "ethical_validate": ethical_validate,
    "ethical_audit": ethical_audit,
    # OSINT
    "osint_investigate": osint_investigate,
    "osint_breach_check": osint_breach_check,
    "osint_google_dork": osint_google_dork,
    # Threat
    "threat_analyze": threat_analyze,
    "threat_intelligence": threat_intelligence,
    "threat_predict": threat_predict,
    # Compliance
    "compliance_assess": compliance_assess,
    "compliance_report": compliance_report,
    "compliance_check": compliance_check,
    # Wargame
    "wargame_list_scenarios": wargame_list_scenarios,
    "wargame_run_simulation": wargame_run_simulation,
    # Patch ML
    "patch_validate": patch_validate,
    # CyberSec
    "cybersec_recon": cybersec_recon,
    # AI Tools
    "ai_threat_analysis": ai_threat_analysis,
    "ai_compliance_assessment": ai_compliance_assessment,
    "ai_osint_analysis": ai_osint_analysis,
    "ai_stream_analysis": ai_stream_analysis,
    "ai_integrated_assessment": ai_integrated_assessment,
}

# Tool metadata for /mcp/tools/list endpoint
TOOL_METADATA: List[ToolInfo] = [
    # Governance
    ToolInfo(
        name="ethical_validate",
        agent="Ethical Magistrate",
        category="governance",
        description="Validates actions against 7-phase ethical framework",
        parameters={"action": "string", "context": "object (optional)"},
    ),
    ToolInfo(
        name="ethical_audit",
        agent="Ethical Magistrate",
        category="governance",
        description="Returns history of ethical decisions",
        parameters={"limit": "integer (default: 10)"},
    ),
    # OSINT
    ToolInfo(
        name="osint_investigate",
        agent="OSINT Hunter",
        category="intelligence",
        description="Executes OSINT investigation on target (email, domain, IP)",
        parameters={"target": "string", "depth": "string (basic|deep|exhaustive)"},
    ),
    ToolInfo(
        name="osint_breach_check",
        agent="OSINT Hunter",
        category="intelligence",
        description="Checks if email appears in known breaches",
        parameters={"email": "string"},
    ),
    ToolInfo(
        name="osint_google_dork",
        agent="OSINT Hunter",
        category="intelligence",
        description="Generates Google dorks for domain reconnaissance",
        parameters={"target_domain": "string"},
    ),
    # Threat
    ToolInfo(
        name="threat_analyze",
        agent="Threat Prophet",
        category="intelligence",
        description="Executes complete threat analysis with MITRE ATT&CK mapping",
        parameters={"target": "string", "include_predictions": "boolean"},
    ),
    ToolInfo(
        name="threat_intelligence",
        agent="Threat Prophet",
        category="intelligence",
        description="Searches threat intelligence by query",
        parameters={"query": "string"},
    ),
    ToolInfo(
        name="threat_predict",
        agent="Threat Prophet",
        category="intelligence",
        description="Generates future threat predictions for target",
        parameters={"target": "string"},
    ),
    # Compliance
    ToolInfo(
        name="compliance_assess",
        agent="Compliance Guardian",
        category="governance",
        description="Assesses compliance against specific framework",
        parameters={"target": "string", "framework": "string (gdpr|hipaa|pci_dss|...)"},
    ),
    ToolInfo(
        name="compliance_report",
        agent="Compliance Guardian",
        category="governance",
        description="Generates compliance report across multiple frameworks",
        parameters={"target": "string", "frameworks": "string[]"},
    ),
    ToolInfo(
        name="compliance_check",
        agent="Compliance Guardian",
        category="governance",
        description="Checks specific compliance requirement",
        parameters={"requirement_id": "string", "target": "string"},
    ),
    # Wargame
    ToolInfo(
        name="wargame_list_scenarios",
        agent="Wargame Executor",
        category="offensive",
        description="Lists available attack scenarios for simulation",
        parameters={},
    ),
    ToolInfo(
        name="wargame_run_simulation",
        agent="Wargame Executor",
        category="offensive",
        description="Executes attack simulation (wargame)",
        parameters={"scenario_id": "string", "target": "string (default: local)"},
    ),
    # Patch ML
    ToolInfo(
        name="patch_validate",
        agent="Patch Validator ML",
        category="offensive",
        description="Validates code patch for security risks using ML",
        parameters={"diff_content": "string", "language": "string (default: python)"},
    ),
    # CyberSec
    ToolInfo(
        name="cybersec_recon",
        agent="CyberSec Investigator",
        category="offensive",
        description="Basic reconnaissance (port scan, web headers)",
        parameters={
            "target": "string",
            "scan_ports": "boolean",
            "scan_web": "boolean",
        },
    ),
    # AI Tools
    ToolInfo(
        name="ai_threat_analysis",
        agent="AI Threat Analyzer",
        category="ai",
        description="Intelligent threat analysis using Vertex AI",
        parameters={
            "target": "string",
            "context_data": "object",
            "analysis_type": "string",
        },
    ),
    ToolInfo(
        name="ai_compliance_assessment",
        agent="AI Compliance Assessor",
        category="ai",
        description="AI-powered compliance assessment",
        parameters={"target": "string", "framework": "string", "current_state": "object"},
    ),
    ToolInfo(
        name="ai_osint_analysis",
        agent="AI OSINT Analyzer",
        category="ai",
        description="Intelligent OSINT findings analysis",
        parameters={"target": "string", "findings": "object[]", "analysis_focus": "string"},
    ),
    ToolInfo(
        name="ai_stream_analysis",
        agent="AI Stream Analyzer",
        category="ai",
        description="Real-time streaming analysis using Vertex AI",
        parameters={"analysis_type": "string", "data": "object", "stream_format": "string"},
    ),
    ToolInfo(
        name="ai_integrated_assessment",
        agent="AI Integrated Assessor",
        category="ai",
        description="Integrated assessment using all agents with AI",
        parameters={"target": "string", "assessment_scope": "string"},
    ),
]

# =============================================================================
# FASTAPI APP
# =============================================================================

app = FastAPI(
    title="Vertice Cyber MCP Bridge",
    description="HTTP Bridge para MCP Tools - Conecta dashboard web aos Meta-Agents",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS para dashboard (dev + prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================


class ToolExecuteRequest(BaseModel):
    """Request para executar uma tool."""

    tool_name: str
    arguments: Dict[str, Any] = {}


class ToolExecuteResponse(BaseModel):
    """Response de execução de tool."""

    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    logs: List[Dict[str, Any]] = []
    execution_time_ms: Optional[float] = None


class ToolListResponse(BaseModel):
    """Response com lista de tools."""

    tools: List[ToolInfo]
    total: int


class HealthResponse(BaseModel):
    """Response do health check."""

    status: str
    service: str
    version: str
    tools_available: int


# =============================================================================
# ENDPOINTS
# =============================================================================


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check do servidor."""
    return HealthResponse(
        status="healthy",
        service="mcp-http-bridge",
        version="1.0.0",
        tools_available=len(TOOL_REGISTRY),
    )


@app.get("/mcp/tools/list", response_model=ToolListResponse)
async def list_tools():
    """Lista todas as tools disponíveis com metadata."""
    return ToolListResponse(tools=TOOL_METADATA, total=len(TOOL_METADATA))


@app.post("/mcp/tools/execute", response_model=ToolExecuteResponse)
async def execute_tool(request: ToolExecuteRequest):
    """
    Executa uma MCP tool.
    
    Example:
        POST /mcp/tools/execute
        {
          "tool_name": "ethical_validate",
          "arguments": {"action": "test action", "context": {}}
        }
    """
    import time

    start_time = time.time()

    # Find tool
    tool_func = TOOL_REGISTRY.get(request.tool_name)
    if not tool_func:
        available = list(TOOL_REGISTRY.keys())
        raise HTTPException(
            status_code=404,
            detail=f"Tool '{request.tool_name}' not found. Available: {available}",
        )

    # Create mock context
    ctx = create_mock_context()

    try:
        # Execute tool with context + arguments
        result = await tool_func(ctx, **request.arguments)

        execution_time = (time.time() - start_time) * 1000

        return ToolExecuteResponse(
            success=True,
            result=result,
            logs=ctx.get_logs(),
            execution_time_ms=execution_time,
        )

    except TypeError as e:
        # Parameter mismatch
        logger.error(f"Parameter error for {request.tool_name}: {e}")
        return ToolExecuteResponse(
            success=False,
            error=f"Invalid parameters: {str(e)}",
            logs=ctx.get_logs(),
        )

    except Exception as e:
        logger.error(f"Tool execution failed: {e}")
        return ToolExecuteResponse(
            success=False,
            error=str(e),
            logs=ctx.get_logs(),
        )


# =============================================================================
# WEBSOCKET - EVENT STREAMING (GAP 3 RESOLVED)
# =============================================================================


class ConnectionManager:
    """
    Gerencia conexões WebSocket de múltiplos clientes.
    
    Features:
    - Broadcast para todos os clientes
    - Auto-cleanup em disconnect
    - Thread-safe operations
    """
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self._lock = asyncio.Lock()
    
    async def connect(self, websocket: WebSocket):
        """Aceita nova conexão."""
        await websocket.accept()
        async with self._lock:
            self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total: {len(self.active_connections)}")
    
    async def disconnect(self, websocket: WebSocket):
        """Remove conexão."""
        async with self._lock:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict):
        """Envia mensagem para todos os clientes."""
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Broadcast error: {e}")
                disconnected.append(connection)
        
        for conn in disconnected:
            await self.disconnect(conn)
    
    @property
    def connection_count(self) -> int:
        """Número de conexões ativas."""
        return len(self.active_connections)


# Singleton manager
connection_manager = ConnectionManager()

# Eventos que serão streamados para o dashboard
STREAMABLE_EVENTS = [
    # Threat
    EventType.THREAT_DETECTED,
    EventType.THREAT_PREDICTED,
    EventType.THREAT_MITRE_MAPPED,
    # Ethics
    EventType.ETHICS_VALIDATION_REQUESTED,
    EventType.ETHICS_VALIDATION_COMPLETED,
    EventType.ETHICS_HUMAN_REVIEW_REQUIRED,
    # OSINT
    EventType.OSINT_INVESTIGATION_STARTED,
    EventType.OSINT_INVESTIGATION_COMPLETED,
    EventType.OSINT_BREACH_DETECTED,
    # Wargame
    EventType.WARGAME_SIMULATION_STARTED,
    EventType.WARGAME_SIMULATION_COMPLETED,
    # Patch
    EventType.PATCH_VALIDATION_REQUESTED,
    EventType.PATCH_VALIDATION_COMPLETED,
    # CyberSec
    EventType.RECON_STARTED,
    EventType.RECON_COMPLETED,
    # Immune
    EventType.IMMUNE_RESPONSE_TRIGGERED,
    EventType.IMMUNE_ANTIBODY_DEPLOYED,
    # System
    EventType.SYSTEM_TOOL_CALLED,
    EventType.SYSTEM_ERROR,
]


@app.websocket("/mcp/events")
async def websocket_events(websocket: WebSocket):
    """
    WebSocket endpoint para streaming de eventos MCP.
    
    Protocol:
    1. Client connects → Server accepts + sends welcome
    2. Server streams events from EventBus
    3. Heartbeat every 30s se sem eventos
    4. Graceful cleanup on disconnect
    """
    await connection_manager.connect(websocket)

    event_bus = get_event_bus()
    event_queue: asyncio.Queue[Event] = asyncio.Queue()

    # Callback para enqueue eventos do EventBus
    async def on_event(event: Event):
        await event_queue.put(event)

    # Register handlers for all streamable events
    for event_type in STREAMABLE_EVENTS:
        event_bus.subscribe(event_type, on_event)

    logger.info(f"WebSocket ready. Streaming {len(STREAMABLE_EVENTS)} event types")

    # Send welcome message with available events
    try:
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to MCP Event Stream",
            "available_events": [e.value for e in STREAMABLE_EVENTS],
            "active_connections": connection_manager.connection_count,
            "timestamp": datetime.utcnow().isoformat(),
        })
    except Exception as e:
        logger.error(f"Failed to send welcome message: {e}")

    try:
        while True:
            try:
                # Wait for event with 30s timeout (heartbeat)
                event = await asyncio.wait_for(event_queue.get(), timeout=30.0)

                # Serialize event to JSON
                event_data = {
                    "type": event.event_type.value,
                    "data": event.data,
                    "source": event.source,
                    "event_id": event.event_id,
                    "timestamp": event.timestamp.isoformat(),
                    "correlation_id": event.correlation_id,
                }

                await websocket.send_json(event_data)

            except asyncio.TimeoutError:
                # Heartbeat if no events for 30s
                await websocket.send_json({"type": "heartbeat", "timestamp": datetime.utcnow().isoformat()})

    except WebSocketDisconnect:
        logger.info("Client disconnected normally")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await connection_manager.disconnect(websocket)
        logger.info("WebSocket cleanup completed")


# =============================================================================
# STARTUP/SHUTDOWN
# =============================================================================


@app.on_event("startup")
async def startup():
    """Startup event handler."""
    logger.info("🌉 MCP HTTP Bridge starting...")
    logger.info(f"📦 Loaded {len(TOOL_REGISTRY)} tools")
    logger.info("📡 WebSocket endpoint: /mcp/events")


@app.on_event("shutdown")
async def shutdown():
    """Shutdown event handler."""
    logger.info("🔌 MCP HTTP Bridge shutting down...")
    # Close all WebSocket connections
    for ws in list(active_connections):
        try:
            await ws.close()
        except Exception:
            pass


# =============================================================================
# MAIN
# =============================================================================


def run_http_bridge(host: str = "0.0.0.0", port: int = 8001):
    """Roda HTTP bridge standalone."""
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_http_bridge()
