
import sqlite3
import logging
from typing import Any, List, Optional, Tuple, Dict

logger = logging.getLogger(__name__)

DB_PATH = "vertice.db"

SCHEMA = """
PRAGMA foreign_keys = ON;

-- AGENTS REGISTRY
CREATE TABLE IF NOT EXISTS agents (
    agent_id TEXT PRIMARY KEY,
    agent_type TEXT NOT NULL CHECK(length(agent_type) > 0),
    state TEXT NOT NULL CHECK(state IN ('IDLE', 'SPAWNED', 'RUNNING', 'PAUSED', 'TERMINATED', 'ERROR')),
    config JSON NOT NULL DEFAULT '{}',
    spawned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_heartbeat TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSON DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS idx_agents_state ON agents(state);

-- JOBS & CHECKPOINTS
CREATE TABLE IF NOT EXISTS jobs (
    job_id TEXT PRIMARY KEY,
    agent_id TEXT NOT NULL REFERENCES agents(agent_id) ON DELETE CASCADE,
    job_type TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('PENDING', 'RUNNING', 'PAUSED', 'COMPLETED', 'FAILED', 'CANCELLED')),
    progress INTEGER CHECK(progress BETWEEN 0 AND 100) DEFAULT 0,
    checkpoint_data JSON DEFAULT '{}',
    result_data JSON,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_jobs_agent ON jobs(agent_id);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);

-- SYSTEM EVENTS (Circular Buffer Audit Trail attempt - implementing as standard table for now)
CREATE TABLE IF NOT EXISTS events (
    event_id TEXT PRIMARY KEY,
    correlation_id TEXT,
    event_type TEXT NOT NULL,
    source TEXT NOT NULL,
    payload JSON NOT NULL,
    level TEXT CHECK(level IN ('INFO', 'WARN', 'ERROR', 'CRITICAL', 'DEBUG')),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_events_ts ON events(timestamp DESC);

-- HUMAN DECISIONS
CREATE TABLE IF NOT EXISTS decisions (
    decision_id TEXT PRIMARY KEY,
    job_id TEXT NOT NULL REFERENCES jobs(job_id) ON DELETE CASCADE,
    decision_type TEXT NOT NULL,
    context_data JSON NOT NULL,
    options JSON NOT NULL,
    status TEXT CHECK(status IN ('PENDING', 'APPROVED', 'REJECTED', 'EXPIRED')),
    selected_option TEXT,
    approver_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);

-- GENERIC MEMORY STORE (Phase 3)
CREATE TABLE IF NOT EXISTS memory_store (
    agent_name TEXT,
    key TEXT,
    value JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ttl_seconds INTEGER,
    access_count INTEGER DEFAULT 0,
    PRIMARY KEY (agent_name, key)
);

-- TRIGGERS (Recreating validation to prevent errors if they exist)
DROP TRIGGER IF EXISTS update_jobs_timestamp;
CREATE TRIGGER update_jobs_timestamp AFTER UPDATE ON jobs
BEGIN
    UPDATE jobs SET updated_at = CURRENT_TIMESTAMP WHERE job_id = NEW.job_id;
END;
"""

class Database:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize database schema."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.executescript(SCHEMA)
            logger.info(f"Database initialized at {self.db_path}")
        except Exception as e:
            logger.critical(f"Failed to initialize database: {e}")
            raise

    def get_connection(self) -> sqlite3.Connection:
        """Get a raw sqlite3 connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    async def execute(self, query: str, params: Tuple = ()) -> sqlite3.Cursor:
        """Execute a query (simulated async wrapper)."""
        # Note: SQLite is blocking by default. For high concurrency, 
        # consider running in a separate thread pool if this bottlenecks.
        # adhering to Code Constitution: No mocks, but SQLite driver is sync.
        # In a real async/await app, we might use aiosqlite, but standard lib is required for Phase 0 simplicity unless specified.
        # The plan didn't strictly mandate aiosqlite, just "SQLite".
        # We will use sync execution for now as it's robust and simple for file-based DB.
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                return cursor
        except Exception as e:
            logger.error(f"DB Execute Error: {e} | Query: {query}")
            raise

    async def fetch_one(self, query: str, params: Tuple = ()) -> Optional[Dict[str, Any]]:
        """Fetch single row."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(query, params)
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"DB FetchOne Error: {e}")
            raise

    async def fetch_all(self, query: str, params: Tuple = ()) -> List[Dict[str, Any]]:
        """Fetch all rows."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"DB FetchAll Error: {e}")
            raise

# Singleton
_db = None

def get_db() -> Database:
    global _db
    if _db is None:
        _db = Database()
    return _db
