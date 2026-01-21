
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional
from uuid import uuid4

class EventType(str, Enum):
    # Lifecycle
    AGENT_SPAWNED = "agent.lifecycle.spawned"
    AGENT_STARTED = "agent.lifecycle.started"
    AGENT_PAUSED = "agent.lifecycle.paused"
    AGENT_RESUMED = "agent.lifecycle.resumed"
    AGENT_TERMINATED = "agent.lifecycle.terminated"
    
    # Decisions
    DECISION_REQUESTED = "agent.decision.requested"
    DECISION_APPROVED = "agent.decision.approved"
    DECISION_REJECTED = "agent.decision.rejected"
    
    # Tools
    TOOL_STARTED = "agent.tool.started"
    TOOL_PROGRESS = "agent.tool.progress"
    TOOL_COMPLETED = "agent.tool.completed"
    TOOL_FAILED = "agent.tool.failed"
    
    # System
    LOG = "agent.log"
    ERROR = "system.error"
    ALERT = "system.alert"
    HEARTBEAT = "system.heartbeat"

@dataclass
class Event:
    event_type: str  # Can be string to allow flexibility beyond Enum for now
    source: str
    payload: Dict[str, Any]
    level: str = "INFO"
    correlation_id: Optional[str] = None
    event_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.event_type,
            "id": self.event_id,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "level": self.level,
            "correlation_id": self.correlation_id,
            "payload": self.payload
        }
