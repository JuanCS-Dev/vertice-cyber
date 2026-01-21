
import logging
import json
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ValidationError

from core.database import get_db
from core.events.event_bus import get_event_bus
from core.events.types import Event

logger = logging.getLogger(__name__)

class CheckpointData(BaseModel):
    step_index: int = 0
    accumulated_results: Dict[str, Any] = Field(default_factory=dict)
    memory_snapshot: Dict[str, Any] = Field(default_factory=dict)
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class CheckpointSaveFailed(Exception):
    pass

class CheckpointCorruptedError(Exception):
    pass

class CheckpointManager:
    """Handles versioned checkpoint save/load/cleanup"""
    
    def __init__(self):
        self.db = get_db()
        self.checkpoint_version = "v1"
        self.event_bus = get_event_bus()
    
    async def save_checkpoint(
        self,
        job_id: str,
        checkpoint: CheckpointData
    ) -> bool:
        """
        Save checkpoint with versioning.
        """
        try:
            # Add version to checkpoint
            versioned_data = {
                "version": self.checkpoint_version,
                "data": checkpoint.dict(),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Serialize
            # Pydantic's .json() is deprecated in v2, use model_dump_json() if v2, or .json() if v1.
            # Assuming v1 compat based on legacy context, but standard is dict() generally safer for json.dumps
            # Using verify convert of datetime manually if needed, but Pydantic handles it.
            json_data = json.dumps(versioned_data, default=str)
            
            # Atomic update
            # We use the sync execute wrapper but in a real scenario this might be blocking.
            # Phase 0 requires functionality.
            cursor = await self.db.execute(
                """
                UPDATE jobs 
                SET checkpoint_data = ?,
                    progress = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE job_id = ?
                """,
                (json_data, checkpoint.step_index, job_id)
            )
            
            if cursor.rowcount == 0:
                raise CheckpointSaveFailed(f"Job {job_id} not found")
            
            # Emit event
            await self.event_bus.emit(Event(
                event_type="job.checkpoint_saved",
                source="checkpoint_manager",
                payload={"job_id": job_id, "progress": checkpoint.step_index}
            ))
            
            return True
            
        except Exception as e:
            logger.error(f"Checkpoint save failed for {job_id}: {e}")
            raise CheckpointSaveFailed(str(e))
    
    async def load_checkpoint(
        self,
        job_id: str
    ) -> Optional[CheckpointData]:
        """
        Load and validate checkpoint.
        """
        row = await self.db.fetch_one(
            "SELECT checkpoint_data FROM jobs WHERE job_id = ?",
            (job_id,)
        )
        
        if not row or not row['checkpoint_data']:
            return None
        
        try:
            versioned_data = json.loads(row['checkpoint_data'])
            
            # Version migration logic could go here
            if versioned_data.get('version') != self.checkpoint_version:
                logger.warning(f"Checkpoint version mismatch: {versioned_data.get('version')} vs {self.checkpoint_version}")
                # For now, simplistic backward compat if keys allow
            
            return CheckpointData(**versioned_data['data'])
            
        except (json.JSONDecodeError, ValidationError) as e:
            raise CheckpointCorruptedError(f"Invalid checkpoint: {e}")
    
    async def cleanup_old_checkpoints(self, days: int = 7):
        """Delete checkpoints from completed jobs older than N days"""
        await self.db.execute(
            """
            UPDATE jobs 
            SET checkpoint_data = NULL
            WHERE status IN ('COMPLETED', 'FAILED', 'CANCELLED')
              AND updated_at < datetime('now', '-{} days')
            """.format(days)
        )
