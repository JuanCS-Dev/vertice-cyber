import asyncio
import uuid
import logging
import json
from typing import Optional, Dict
from core.database import get_db
from core.events.event_bus import get_event_bus
from core.events.types import Event
from core.jobs.checkpoint import CheckpointManager, CheckpointData

logger = logging.getLogger(__name__)

class JobManager:
    """Manages lifecycle and persistence of long-running agent jobs."""

    def __init__(self):
        self.db = get_db()
        self.event_bus = get_event_bus()
        self.checkpoint_manager = CheckpointManager()

    async def create_job(self, agent_id: str, job_type: str) -> str:
        job_id = str(uuid.uuid4())
        await self.db.execute(
            "INSERT INTO jobs (job_id, agent_id, job_type, status) VALUES (?, ?, ?, ?)",
            (job_id, agent_id, job_type, "PENDING")
        )
        
        await self.event_bus.emit(Event(
            event_type="job.created",
            source="job_manager",
            payload={"job_id": job_id, "agent_id": agent_id, "job_type": job_type}
        ))
        
        return job_id

    async def set_status(self, job_id: str, status: str, result: Optional[Dict] = None, error: Optional[str] = None):
        """Update job status."""
        query = "UPDATE jobs SET status = ?, updated_at = CURRENT_TIMESTAMP"
        params = [status]
        
        if result:
            query += ", result_data = ?"
            params.append(json.dumps(result, default=str))
        
        if error:
            query += ", error_message = ?"
            params.append(error)
            
        query += " WHERE job_id = ?"
        params.append(job_id)
        
        await self.db.execute(query, tuple(params))
        
        await self.event_bus.emit(Event(
            event_type=f"job.{status.lower()}",
            source="job_manager",
            payload={"job_id": job_id, "status": status, "error": error}
        ))

    async def should_yield(self, job_id: str) -> bool:
        """
        Cooperative multitasking check.
        Returns True if PAUSE or CANCEL signal received.
        """
        row = await self.db.fetch_one("SELECT status FROM jobs WHERE job_id = ?", (job_id,))
        if not row:
            return False
        return row['status'] in ['PAUSED', 'CANCELLED']

    async def wait_for_resume(self, job_id: str):
        """Blocks until status becomes RUNNING."""
        while True:
            row = await self.db.fetch_one("SELECT status FROM jobs WHERE job_id = ?", (job_id,))
            if not row:
                raise ValueError(f"Job {job_id} vanished")
            
            status = row['status']
            if status == 'RUNNING':
                return
            if status == 'CANCELLED':
                raise asyncio.CancelledError("Job cancelled by operator")
            
            # Exponential backoff or simpler sleep? Simple sleep is fine for Phase 0.
            await asyncio.sleep(1)

    # Proxy to CheckpointManager
    async def save_checkpoint(self, job_id: str, data: CheckpointData):
        await self.checkpoint_manager.save_checkpoint(job_id, data)

    async def load_checkpoint(self, job_id: str) -> Optional[CheckpointData]:
        return await self.checkpoint_manager.load_checkpoint(job_id)
