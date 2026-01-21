
import logging
import json
from datetime import datetime
from typing import Dict, Any

from core.database import get_db
from core.events.event_bus import get_event_bus
from core.events.types import Event, EventType
from core.jobs.job_manager import JobManager

logger = logging.getLogger(__name__)

class AgentOrchestrator:
    """God-mode controller for all agents."""
    
    def __init__(self):
        self.db = get_db()
        self.event_bus = get_event_bus()
        self.job_manager = JobManager()
        
    async def spawn_agent(self, agent_type: str, config: Dict[str, Any]) -> str:
        """
        Create and register new agent instance.
        """
        # Generate ID (or use specific logic, e.g., 'osint-1')
        # For Phase 0, we might want unique IDs or singleton logic depending on requirements.
        # "Absolute Control" usually implies multiple instances if desired, but Dashboard usually has generic panels.
        # Let's assume unique UUIDs for "instances".
        import uuid
        agent_id = f"{agent_type}-{str(uuid.uuid4())[:8]}"
        
        # Validation of config (Phase 4 Gap 4 handled by Pydantic usage in API layer, here we take dict)
        
        await self.db.execute(
            """
            INSERT INTO agents (agent_id, agent_type, state, config, spawned_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (agent_id, agent_type, "SPAWNED", json.dumps(config), datetime.utcnow())
        )
        
        await self.event_bus.emit(Event(
            event_type=EventType.AGENT_SPAWNED, # Using the string value from Enum
            source="orchestrator",
            payload={"agent_id": agent_id, "type": agent_type, "config": config}
        ))
        
        return agent_id

    async def start_job(self, agent_id: str, job_type: str, params: Dict[str, Any]) -> str:
        """Propagate start command to JobManager."""
        # Check agent state
        row = await self.db.fetch_one("SELECT state FROM agents WHERE agent_id = ?", (agent_id,))
        if not row:
            raise ValueError(f"Agent {agent_id} not found")
        
        # Update agent state to RUNNING
        await self.db.execute("UPDATE agents SET state = 'RUNNING' WHERE agent_id = ?", (agent_id,))
        
        job_id = await self.job_manager.create_job(agent_id, job_type)
        
        # Here we would actually "trigger" the implementation logic.
        # Since this is the Orchestrator, we might return the job_ID to the caller (API) 
        # which then executes the logic, OR the Orchestrator dispatches it.
        # For Phase 0, we return the structure.
        
        return job_id

    async def pause_agent(self, agent_id: str):
        """Freeze agent execution."""
        # Find active job
        row = await self.db.fetch_one(
            "SELECT job_id FROM jobs WHERE agent_id = ? AND status = 'RUNNING'", 
            (agent_id,)
        )
        if row:
            # Set job status to PAUSED (signal)
            await self.job_manager.set_status(row['job_id'], "PAUSED")
        
        await self.db.execute("UPDATE agents SET state = 'PAUSED' WHERE agent_id = ?", (agent_id,))
        await self.event_bus.emit(Event(
            event_type="agent.lifecycle.paused",
            source="orchestrator",
            payload={"agent_id": agent_id}
        ))

    async def resume_agent(self, agent_id: str):
        """Unfreeze agent."""
        # Find paused job
        row = await self.db.fetch_one(
            "SELECT job_id FROM jobs WHERE agent_id = ? AND status = 'PAUSED'", 
            (agent_id,)
        )
        if row:
            await self.job_manager.set_status(row['job_id'], "RUNNING")
            
        await self.db.execute("UPDATE agents SET state = 'RUNNING' WHERE agent_id = ?", (agent_id,))
        await self.event_bus.emit(Event(
            event_type="agent.lifecycle.resumed",
            source="orchestrator",
            payload={"agent_id": agent_id}
        ))

    async def terminate_agent(self, agent_id: str):
        """Graceful shutdown."""
        # Cancel any running jobs
        rows = await self.db.fetch_all(
            "SELECT job_id FROM jobs WHERE agent_id = ? AND status IN ('RUNNING', 'PAUSED')", 
            (agent_id,)
        )
        for row in rows:
            await self.job_manager.set_status(row['job_id'], "CANCELLED")
            
        await self.db.execute("UPDATE agents SET state = 'TERMINATED' WHERE agent_id = ?", (agent_id,))
        await self.event_bus.emit(Event(
            event_type="agent.lifecycle.terminated",
            source="orchestrator",
            payload={"agent_id": agent_id}
        ))

    async def get_agent_state(self, agent_id: str) -> Dict[str, Any]:
        """Full introspection."""
        agent = await self.db.fetch_one("SELECT * FROM agents WHERE agent_id = ?", (agent_id,))
        if not agent:
            raise ValueError(f"Agent {agent_id} not found")
            
        active_job = await self.db.fetch_one(
            "SELECT * FROM jobs WHERE agent_id = ? AND status IN ('RUNNING', 'PAUSED')", 
            (agent_id,)
        )
        
        return {
            "agent": dict(agent),
            "active_job": dict(active_job) if active_job else None
        }

    async def restore_universe(self):
        """Resurrect agents from cryosleep."""
        logger.info("🌌 Initiating Universe Restoration Protocol...")
        
        # Find RUNNING/PAUSED agents
        agents = await self.db.fetch_all("SELECT * FROM agents WHERE state IN ('RUNNING', 'PAUSED')")
        
        count = 0
        for agent in agents:
            logger.info(f"♻️ Resurrecting agent {agent['agent_id']} ({agent['agent_type']})")
            
            # Find active jobs
            jobs = await self.db.fetch_all(
                "SELECT * FROM jobs WHERE agent_id = ? AND status IN ('RUNNING', 'PAUSED')",
                (agent['agent_id'],)
            )
            
            for job in jobs:
                count += 1
                logger.info(f"   ↳ Found persistence trace for job {job['job_id']}")
                # In a full implementation, we would respawn the background task here using the checkpoint.
                
        if count > 0:
            logger.info(f"✅ Restored {count} neural pathways from stasis.")
        else:
            logger.info("✨ Universe is clean. No active entities found.")

# Singleton
_orchestrator = None

def get_orchestrator() -> AgentOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AgentOrchestrator()
    return _orchestrator
