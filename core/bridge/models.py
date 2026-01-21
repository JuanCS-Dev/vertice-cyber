"""
Bridge Models - Pydantic Models for HTTP/MCP Bridge.
===================================================

Defines request and response schemas for tool execution and metadata.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class ToolInfo(BaseModel):
    """Metadata about an MCP tool."""

    name: str
    agent: str
    category: str
    description: str
    parameters: Dict[str, str]


class ToolExecuteRequest(BaseModel):
    """Request to execute an MCP tool."""

    tool_name: str
    arguments: Dict[str, Any] = {}


class ToolExecuteResponse(BaseModel):
    """Response from an MCP tool execution."""

    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    logs: List[Dict[str, Any]] = []
    execution_time_ms: Optional[float] = None


class ToolListResponse(BaseModel):
    """Response containing a list of available tools."""

    tools: List[ToolInfo]
    total: int


class HealthResponse(BaseModel):
    """Health check response schema."""

    status: str
    service: str
    version: str
    tools_available: int
