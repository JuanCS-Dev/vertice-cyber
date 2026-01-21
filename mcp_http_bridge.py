"""
MCP HTTP Bridge - Modular Entry Point.
=====================================

Exposes Vértice Cyber tools via REST API and WebSockets.
Adheres to Maximus 2.0 Code Constitution (Modular & Semantic).
"""

import logging
import time

from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Bridge Modules
from core.bridge.models import (
    ToolExecuteRequest,
    ToolExecuteResponse,
    ToolListResponse,
    HealthResponse,
)
from core.bridge.registry import TOOL_REGISTRY, TOOL_METADATA
from core.bridge.context import create_mock_context
from core.bridge.ws_manager import websocket_event_stream

# Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("mcp_bridge")

app = FastAPI(
    title="Vertice Cyber Bridge",
    version="2.4.0",
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restricted in production
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """System health status."""
    return HealthResponse(
        status="healthy",
        service="mcp-bridge-modular",
        version="2.4.0",
        tools_available=len(TOOL_REGISTRY),
    )


@app.get("/mcp/tools/list", response_model=ToolListResponse)
async def list_tools():
    """List available MCP tools."""
    return ToolListResponse(tools=TOOL_METADATA, total=len(TOOL_METADATA))


@app.post("/mcp/tools/execute", response_model=ToolExecuteResponse)
async def execute_tool(request: ToolExecuteRequest):
    """Execute requested tool via internal registry."""
    start_time = time.perf_counter()

    tool_func = TOOL_REGISTRY.get(request.tool_name)
    if not tool_func:
        raise HTTPException(
            status_code=404, detail=f"Tool {request.tool_name} not found"
        )

    ctx = create_mock_context()
    try:
        result = await tool_func(ctx, **request.arguments)
        latency = (time.perf_counter() - start_time) * 1000

        return ToolExecuteResponse(
            success=True, result=result, logs=ctx.get_logs(), execution_time_ms=latency
        )
    except Exception as e:
        logger.error(f"Execution failed: {e}")
        return ToolExecuteResponse(success=False, error=str(e), logs=ctx.get_logs())


@app.websocket("/mcp/events")
async def websocket_endpoint(websocket: WebSocket):
    """Event streaming endpoint."""
    await websocket_event_stream(websocket)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Vértice Bridge")
    parser.add_argument("--port", type=int, default=8001)
    args = parser.parse_args()
    uvicorn.run(app, host="0.0.0.0", port=args.port)
