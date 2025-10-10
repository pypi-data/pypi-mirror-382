# Database Migration Guide: SQLite Checkpoint Storage

## Overview

This guide explains how to migrate from the in-memory checkpoint store to SQLite-based persistent storage for production deployments.

**Why Migrate to SQLite?**

| Feature | InMemoryCheckpointStore | SQLiteCheckpointStore |
|---------|------------------------|----------------------|
| **Persistence** | ❌ Lost on restart | ✅ Survives restarts |
| **Scalability** | ~10k checkpoints | ~100k-1M checkpoints |
| **Crash Recovery** | ❌ Lost on crash | ✅ Full recovery |
| **Multi-Process** | ❌ Single process only | ✅ Shared across processes |
| **Performance** | < 1ms operations | 10-50ms operations |
| **Storage** | RAM-limited | Disk-limited |

**When to Use Each**:
- **InMemory**: Development, testing, simple deployments
- **SQLite**: Production, long-running workflows, crash recovery required
- **PostgreSQL**: Multi-server, high concurrency, enterprise deployments

---

## Quick Start

### 1. Install SQLite Support

```bash
# SQLite is included in Python standard library
# For async support (recommended):
uv add aiosqlite
```

---

### 2. Implement SQLiteCheckpointStore

Create `src/workflows_mcp/engine/checkpoint_store_sqlite.py`:

```python
"""SQLite-based checkpoint storage for production deployments."""

import json
import sqlite3
import time
from collections import defaultdict
from typing import Any, DefaultDict

import aiosqlite

from .checkpoint import CheckpointMetadata, CheckpointState
from .checkpoint_store import CheckpointStore

class SQLiteCheckpointStore(CheckpointStore):
    """SQLite-backed checkpoint storage.

    Features:
    - Persistent storage (survives restarts)
    - Transaction safety
    - Indexed queries for fast lookup
    - Automatic schema migration
    - Concurrent access support

    Schema:
        checkpoints (
            checkpoint_id TEXT PRIMARY KEY,
            workflow_name TEXT NOT NULL,
            created_at REAL NOT NULL,
            is_paused BOOLEAN NOT NULL,
            checkpoint_data TEXT NOT NULL
        )

    Indexes:
        - idx_workflow_name: Fast filtering by workflow
        - idx_created_at: Fast time-based queries
        - idx_is_paused: Fast paused checkpoint lookup
    """

    def __init__(self, db_path: str = "checkpoints.db"):
        """Initialize SQLite checkpoint store.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._connection: aiosqlite.Connection | None = None

    async def _ensure_connection(self) -> aiosqlite.Connection:
        """Ensure database connection is established."""
        if self._connection is None:
            self._connection = await aiosqlite.connect(self.db_path)
            await self._init_schema()
        return self._connection

    async def _init_schema(self) -> None:
        """Create database schema if it doesn't exist."""
        conn = await self._ensure_connection()

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS checkpoints (
                checkpoint_id TEXT PRIMARY KEY,
                workflow_name TEXT NOT NULL,
                created_at REAL NOT NULL,
                is_paused BOOLEAN NOT NULL,
                checkpoint_data TEXT NOT NULL
            )
        """)

        # Create indexes for fast queries
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_workflow_name
            ON checkpoints(workflow_name)
        """)

        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_created_at
            ON checkpoints(created_at)
        """)

        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_is_paused
            ON checkpoints(is_paused)
        """)

        await conn.commit()

    async def save_checkpoint(self, state: CheckpointState) -> str:
        """Save checkpoint to SQLite database.

        Args:
            state: Checkpoint state to save

        Returns:
            checkpoint_id for retrieval
        """
        conn = await self._ensure_connection()

        # Serialize checkpoint data to JSON
        checkpoint_data = json.dumps({
            "runtime_inputs": state.runtime_inputs,
            "context": state.context,
            "completed_blocks": state.completed_blocks,
            "current_wave_index": state.current_wave_index,
            "execution_waves": state.execution_waves,
            "block_definitions": state.block_definitions,
            "workflow_stack": state.workflow_stack,
            "parent_checkpoint_id": state.parent_checkpoint_id,
            "paused_block_id": state.paused_block_id,
            "pause_prompt": state.pause_prompt,
            "pause_metadata": state.pause_metadata,
            "child_checkpoint_id": state.child_checkpoint_id,
            "schema_version": state.schema_version,
        })

        # Insert or replace checkpoint
        await conn.execute(
            """
            INSERT OR REPLACE INTO checkpoints
            (checkpoint_id, workflow_name, created_at, is_paused, checkpoint_data)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                state.checkpoint_id,
                state.workflow_name,
                state.created_at,
                state.paused_block_id is not None,
                checkpoint_data,
            ),
        )

        await conn.commit()
        return state.checkpoint_id

    async def load_checkpoint(self, checkpoint_id: str) -> CheckpointState | None:
        """Load checkpoint from SQLite database.

        Args:
            checkpoint_id: Checkpoint ID to load

        Returns:
            CheckpointState if found, None otherwise
        """
        conn = await self._ensure_connection()
        conn.row_factory = aiosqlite.Row

        async with conn.execute(
            "SELECT * FROM checkpoints WHERE checkpoint_id = ?", (checkpoint_id,)
        ) as cursor:
            row = await cursor.fetchone()

        if row is None:
            return None

        # Deserialize checkpoint data
        data = json.loads(row["checkpoint_data"])

        return CheckpointState(
            checkpoint_id=row["checkpoint_id"],
            workflow_name=row["workflow_name"],
            created_at=row["created_at"],
            **data,
        )

    async def list_checkpoints(
        self, workflow_name: str | None = None
    ) -> list[CheckpointMetadata]:
        """List all checkpoints, optionally filtered by workflow.

        Args:
            workflow_name: Filter by workflow name (None = all)

        Returns:
            List of checkpoint metadata, sorted by created_at descending
        """
        conn = await self._ensure_connection()
        conn.row_factory = aiosqlite.Row

        if workflow_name:
            query = """
                SELECT checkpoint_id, workflow_name, created_at, is_paused, checkpoint_data
                FROM checkpoints
                WHERE workflow_name = ?
                ORDER BY created_at DESC
            """
            params = (workflow_name,)
        else:
            query = """
                SELECT checkpoint_id, workflow_name, created_at, is_paused, checkpoint_data
                FROM checkpoints
                ORDER BY created_at DESC
            """
            params = ()

        async with conn.execute(query, params) as cursor:
            rows = await cursor.fetchall()

        metadata_list = []
        for row in rows:
            # Extract pause_prompt from checkpoint_data if paused
            pause_prompt = None
            if row["is_paused"]:
                data = json.loads(row["checkpoint_data"])
                pause_prompt = data.get("pause_prompt")

            metadata_list.append(
                CheckpointMetadata(
                    checkpoint_id=row["checkpoint_id"],
                    workflow_name=row["workflow_name"],
                    created_at=row["created_at"],
                    is_paused=bool(row["is_paused"]),
                    pause_prompt=pause_prompt,
                )
            )

        return metadata_list

    async def delete_checkpoint(self, checkpoint_id: str) -> bool:
        """Delete checkpoint from database.

        Args:
            checkpoint_id: Checkpoint ID to delete

        Returns:
            True if checkpoint existed and was deleted
        """
        conn = await self._ensure_connection()

        cursor = await conn.execute(
            "DELETE FROM checkpoints WHERE checkpoint_id = ?", (checkpoint_id,)
        )

        await conn.commit()
        return cursor.rowcount > 0

    async def cleanup_expired(self, max_age_seconds: int) -> int:
        """Remove checkpoints older than max_age_seconds.

        Preserves paused checkpoints (is_paused = 1).

        Args:
            max_age_seconds: Age threshold in seconds

        Returns:
            Number of checkpoints deleted
        """
        conn = await self._ensure_connection()
        cutoff_time = time.time() - max_age_seconds

        cursor = await conn.execute(
            """
            DELETE FROM checkpoints
            WHERE created_at < ?
            AND is_paused = 0
            """,
            (cutoff_time,),
        )

        await conn.commit()
        return cursor.rowcount

    async def trim_per_workflow(self, max_per_workflow: int) -> int:
        """Keep only last N checkpoints per workflow.

        Preserves paused checkpoints.

        Args:
            max_per_workflow: Maximum checkpoints to keep per workflow

        Returns:
            Number of checkpoints deleted
        """
        conn = await self._ensure_connection()

        # Get checkpoints to delete (per-workflow logic)
        async with conn.execute("""
            SELECT checkpoint_id, workflow_name, created_at, is_paused
            FROM checkpoints
            ORDER BY workflow_name, created_at DESC
        """) as cursor:
            rows = await cursor.fetchall()

        # Group by workflow and identify excess checkpoints
        by_workflow: DefaultDict[str, list[tuple[float, str, bool]]] = defaultdict(list)
        for row in rows:
            by_workflow[row[1]].append((row[2], row[0], bool(row[3])))

        to_delete = []
        for workflow_name, checkpoints in by_workflow.items():
            # Sort by created_at descending
            checkpoints.sort(reverse=True)

            # Mark excess non-paused checkpoints for deletion
            for i, (created_at, checkpoint_id, is_paused) in enumerate(checkpoints):
                if i >= max_per_workflow and not is_paused:
                    to_delete.append(checkpoint_id)

        # Delete marked checkpoints
        if to_delete:
            placeholders = ",".join("?" * len(to_delete))
            await conn.execute(
                f"DELETE FROM checkpoints WHERE checkpoint_id IN ({placeholders})",
                to_delete,
            )
            await conn.commit()

        return len(to_delete)

    async def close(self) -> None:
        """Close database connection."""
        if self._connection:
            await self._connection.close()
            self._connection = None

    async def vacuum(self) -> None:
        """Optimize database by reclaiming space.

        Run periodically to improve performance.
        """
        conn = await self._ensure_connection()
        await conn.execute("VACUUM")
        await conn.commit()
```

---

## Configuration Changes

### Option 1: Environment Variable

```python
# src/workflows_mcp/server.py
import os
from workflows_mcp.engine.executor import WorkflowExecutor
from workflows_mcp.engine.checkpoint_store import InMemoryCheckpointStore
from workflows_mcp.engine.checkpoint_store_sqlite import SQLiteCheckpointStore

# Choose store based on environment
db_path = os.getenv("CHECKPOINT_DB_PATH", "")
if db_path:
    checkpoint_store = SQLiteCheckpointStore(db_path)
else:
    checkpoint_store = InMemoryCheckpointStore()

executor = WorkflowExecutor(checkpoint_store=checkpoint_store)
```

**Usage**:
```bash
# In-memory (development)
uv run workflows-mcp

# SQLite (production)
CHECKPOINT_DB_PATH=/var/lib/workflows/checkpoints.db uv run workflows-mcp
```

---

### Option 2: Configuration File

```python
# config.py
from dataclasses import dataclass

@dataclass
class StorageConfig:
    storage_type: str = "memory"  # "memory" or "sqlite"
    sqlite_path: str = "checkpoints.db"

# Load from file or environment
config = StorageConfig(
    storage_type=os.getenv("STORAGE_TYPE", "memory"),
    sqlite_path=os.getenv("SQLITE_PATH", "checkpoints.db")
)
```

```python
# server.py
from config import config

if config.storage_type == "sqlite":
    checkpoint_store = SQLiteCheckpointStore(config.sqlite_path)
else:
    checkpoint_store = InMemoryCheckpointStore()
```

---

## Data Migration

### Migrating Existing Checkpoints

If you have checkpoints in InMemoryCheckpointStore that need migration:

```python
"""Migrate checkpoints from in-memory to SQLite."""

import asyncio
from workflows_mcp.engine.checkpoint_store import InMemoryCheckpointStore
from workflows_mcp.engine.checkpoint_store_sqlite import SQLiteCheckpointStore

async def migrate_checkpoints(
    source: InMemoryCheckpointStore,
    target: SQLiteCheckpointStore
) -> int:
    """Migrate all checkpoints from source to target.

    Args:
        source: Source checkpoint store (in-memory)
        target: Target checkpoint store (SQLite)

    Returns:
        Number of checkpoints migrated
    """
    # List all checkpoints in source
    checkpoints = await source.list_checkpoints()

    migrated = 0
    for metadata in checkpoints:
        # Load full checkpoint state
        state = await source.load_checkpoint(metadata.checkpoint_id)

        if state:
            # Save to target
            await target.save_checkpoint(state)
            migrated += 1

    return migrated

async def main():
    """Run migration."""
    source = InMemoryCheckpointStore()
    target = SQLiteCheckpointStore("checkpoints.db")

    # Assume source is populated (load from backup/export)
    # ...

    count = await migrate_checkpoints(source, target)
    print(f"Migrated {count} checkpoints to SQLite")

    await target.close()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Testing the Migration

### 1. Unit Tests

Add tests for SQLiteCheckpointStore:

```python
# tests/test_checkpoint_store_sqlite.py
import pytest
import tempfile
import os

from workflows_mcp.engine.checkpoint_store_sqlite import SQLiteCheckpointStore
from workflows_mcp.engine.checkpoint import CheckpointState

@pytest.mark.asyncio
async def test_sqlite_save_and_load():
    """Test basic save/load functionality."""
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        db_path = tmp.name

    try:
        store = SQLiteCheckpointStore(db_path)

        # Create test checkpoint
        state = CheckpointState(
            checkpoint_id="test_123",
            workflow_name="test",
            created_at=1000.0,
            runtime_inputs={},
            context={"key": "value"},
            completed_blocks=[],
            current_wave_index=0,
            execution_waves=[],
            block_definitions={},
            workflow_stack=[],
        )

        # Save
        checkpoint_id = await store.save_checkpoint(state)
        assert checkpoint_id == "test_123"

        # Load
        loaded = await store.load_checkpoint("test_123")
        assert loaded is not None
        assert loaded.checkpoint_id == "test_123"
        assert loaded.context == {"key": "value"}

        await store.close()
    finally:
        os.unlink(db_path)

@pytest.mark.asyncio
async def test_sqlite_persistence():
    """Test that checkpoints survive store recreation."""
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        db_path = tmp.name

    try:
        # Create and save checkpoint
        store1 = SQLiteCheckpointStore(db_path)
        state = CheckpointState(
            checkpoint_id="persist_test",
            workflow_name="test",
            created_at=1000.0,
            runtime_inputs={},
            context={"data": "persisted"},
            completed_blocks=[],
            current_wave_index=0,
            execution_waves=[],
            block_definitions={},
            workflow_stack=[],
        )
        await store1.save_checkpoint(state)
        await store1.close()

        # Recreate store and load
        store2 = SQLiteCheckpointStore(db_path)
        loaded = await store2.load_checkpoint("persist_test")
        assert loaded is not None
        assert loaded.context["data"] == "persisted"
        await store2.close()
    finally:
        os.unlink(db_path)

@pytest.mark.asyncio
async def test_sqlite_cleanup_expired():
    """Test cleanup of old checkpoints."""
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        db_path = tmp.name

    try:
        store = SQLiteCheckpointStore(db_path)

        # Create old checkpoint
        old_state = CheckpointState(
            checkpoint_id="old",
            workflow_name="test",
            created_at=1000.0,  # Very old
            runtime_inputs={},
            context={},
            completed_blocks=[],
            current_wave_index=0,
            execution_waves=[],
            block_definitions={},
            workflow_stack=[],
        )
        await store.save_checkpoint(old_state)

        # Create recent checkpoint
        import time
        new_state = CheckpointState(
            checkpoint_id="new",
            workflow_name="test",
            created_at=time.time(),
            runtime_inputs={},
            context={},
            completed_blocks=[],
            current_wave_index=0,
            execution_waves=[],
            block_definitions={},
            workflow_stack=[],
        )
        await store.save_checkpoint(new_state)

        # Cleanup old checkpoints (older than 60 seconds)
        deleted = await store.cleanup_expired(60)
        assert deleted == 1

        # Verify old checkpoint deleted, new checkpoint remains
        assert await store.load_checkpoint("old") is None
        assert await store.load_checkpoint("new") is not None

        await store.close()
    finally:
        os.unlink(db_path)
```

---

### 2. Integration Tests

Test with real workflows:

```python
# tests/test_sqlite_integration.py
import pytest
import tempfile
import os

from workflows_mcp.engine.executor import WorkflowExecutor
from workflows_mcp.engine.checkpoint_store_sqlite import SQLiteCheckpointStore

@pytest.mark.asyncio
async def test_workflow_with_sqlite_checkpoints():
    """Test workflow execution with SQLite checkpoint store."""
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        db_path = tmp.name

    try:
        # Create executor with SQLite store
        store = SQLiteCheckpointStore(db_path)
        executor = WorkflowExecutor(checkpoint_store=store)

        # Load test workflow
        # ... (load workflow definition) ...

        # Execute workflow
        result = await executor.execute_workflow("test-workflow", {})
        assert result.is_success

        # Verify checkpoints created
        checkpoints = await store.list_checkpoints()
        assert len(checkpoints) > 0

        await store.close()
    finally:
        os.unlink(db_path)
```

---

## Production Deployment

### Recommended Configuration

```python
# Production configuration
checkpoint_store = SQLiteCheckpointStore(
    db_path="/var/lib/workflows/checkpoints.db"
)

checkpoint_config = CheckpointConfig(
    enabled=True,
    max_per_workflow=50,  # Keep more checkpoints in production
    ttl_seconds=7 * 86400,  # 7 days retention
    keep_paused=True,  # Never auto-delete paused checkpoints
    auto_cleanup=True,
    cleanup_interval_seconds=3600,  # Cleanup every hour
    max_checkpoint_size_mb=10.0
)

executor = WorkflowExecutor(
    checkpoint_store=checkpoint_store,
    checkpoint_config=checkpoint_config
)
```

---

### Background Cleanup Task

Run periodic cleanup in background:

```python
import asyncio

async def cleanup_task(store: SQLiteCheckpointStore, config: CheckpointConfig):
    """Background task for checkpoint cleanup."""
    while True:
        await asyncio.sleep(config.cleanup_interval_seconds)

        # Cleanup expired checkpoints
        expired = await store.cleanup_expired(config.ttl_seconds)
        print(f"Cleaned up {expired} expired checkpoints")

        # Trim per-workflow
        trimmed = await store.trim_per_workflow(config.max_per_workflow)
        print(f"Trimmed {trimmed} excess checkpoints")

        # Vacuum database periodically
        await store.vacuum()
        print("Database vacuumed")

# Start cleanup task
asyncio.create_task(cleanup_task(checkpoint_store, checkpoint_config))
```

---

### Monitoring

Monitor checkpoint storage health:

```python
async def get_checkpoint_stats(store: SQLiteCheckpointStore) -> dict:
    """Get checkpoint storage statistics."""
    checkpoints = await store.list_checkpoints()

    total = len(checkpoints)
    paused = sum(1 for c in checkpoints if c.is_paused)
    automatic = total - paused

    # Workflow distribution
    by_workflow = {}
    for c in checkpoints:
        by_workflow[c.workflow_name] = by_workflow.get(c.workflow_name, 0) + 1

    return {
        "total_checkpoints": total,
        "paused_checkpoints": paused,
        "automatic_checkpoints": automatic,
        "workflows": by_workflow,
        "oldest_checkpoint": min(c.created_at for c in checkpoints) if checkpoints else None,
        "newest_checkpoint": max(c.created_at for c in checkpoints) if checkpoints else None,
    }
```

---

## Rollback Strategy

If migration causes issues, rollback to in-memory:

### 1. Keep Old Configuration

```python
# Save original configuration
OLD_STORAGE_TYPE=memory
NEW_STORAGE_TYPE=sqlite
CHECKPOINT_DB_PATH=/var/lib/workflows/checkpoints.db

# Test with SQLite
STORAGE_TYPE=$NEW_STORAGE_TYPE uv run workflows-mcp

# Rollback if needed
STORAGE_TYPE=$OLD_STORAGE_TYPE uv run workflows-mcp
```

---

### 2. Export Checkpoints

Before migration, export checkpoints:

```python
import json

async def export_checkpoints(store: CheckpointStore, output_file: str):
    """Export all checkpoints to JSON file."""
    checkpoints = await store.list_checkpoints()

    data = []
    for metadata in checkpoints:
        state = await store.load_checkpoint(metadata.checkpoint_id)
        if state:
            data.append({
                "checkpoint_id": state.checkpoint_id,
                "workflow_name": state.workflow_name,
                "created_at": state.created_at,
                "runtime_inputs": state.runtime_inputs,
                "context": state.context,
                "completed_blocks": state.completed_blocks,
                "current_wave_index": state.current_wave_index,
                "execution_waves": state.execution_waves,
                "block_definitions": state.block_definitions,
                "workflow_stack": state.workflow_stack,
                "paused_block_id": state.paused_block_id,
                "pause_prompt": state.pause_prompt,
                "pause_metadata": state.pause_metadata,
            })

    with open(output_file, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Exported {len(data)} checkpoints to {output_file}")
```

---

### 3. Import Checkpoints

Restore from export:

```python
async def import_checkpoints(store: CheckpointStore, input_file: str):
    """Import checkpoints from JSON file."""
    with open(input_file) as f:
        data = json.load(f)

    for checkpoint_data in data:
        state = CheckpointState(**checkpoint_data)
        await store.save_checkpoint(state)

    print(f"Imported {len(data)} checkpoints")
```

---

## Troubleshooting

### Issue: "Database is locked"

**Cause**: Multiple processes accessing SQLite simultaneously.

**Solution**:
- Enable WAL mode for better concurrency:
  ```python
  await conn.execute("PRAGMA journal_mode=WAL")
  ```
- Use connection pooling
- Consider PostgreSQL for multi-process deployments

---

### Issue: Slow checkpoint operations

**Cause**: Large database without indexes or vacuum.

**Solution**:
```python
# Ensure indexes exist
await store._init_schema()

# Vacuum database
await store.vacuum()

# Enable query optimization
await conn.execute("PRAGMA optimize")
```

---

### Issue: Disk space exhaustion

**Cause**: Too many checkpoints or large context sizes.

**Solution**:
- Reduce retention: `ttl_seconds=86400` (1 day)
- Limit per workflow: `max_per_workflow=20`
- Reduce checkpoint size: `max_checkpoint_size_mb=5.0`
- Run cleanup more frequently

---

## PostgreSQL Migration (Advanced)

For enterprise deployments requiring:
- Multi-server support
- High concurrency
- Advanced features (replication, partitioning)

Implement `PostgreSQLCheckpointStore`:

```python
import asyncpg

class PostgreSQLCheckpointStore(CheckpointStore):
    """PostgreSQL checkpoint storage for enterprise deployments."""

    def __init__(self, dsn: str):
        self.dsn = dsn
        self.pool: asyncpg.Pool | None = None

    async def _ensure_pool(self) -> asyncpg.Pool:
        if self.pool is None:
            self.pool = await asyncpg.create_pool(self.dsn)
            await self._init_schema()
        return self.pool

    # ... implement CheckpointStore methods using asyncpg ...
```

See PostgreSQL documentation for connection pooling, schema design, and optimization.

---

## Summary

**Migration Checklist**:

- [ ] Install `aiosqlite` dependency
- [ ] Implement `SQLiteCheckpointStore` class
- [ ] Add configuration option (environment variable or config file)
- [ ] Write unit tests for SQLite store
- [ ] Write integration tests with workflows
- [ ] Test checkpoint persistence across restarts
- [ ] Export existing checkpoints (if any)
- [ ] Deploy with SQLite configuration
- [ ] Monitor checkpoint storage health
- [ ] Configure background cleanup task
- [ ] Document rollback procedure

**Production Recommendations**:
- Use SQLite for persistent storage
- Enable automatic cleanup
- Monitor database size
- Run periodic vacuum
- Keep 50+ checkpoints per workflow
- 7-day retention for automatic checkpoints
- Never expire paused checkpoints
- Export checkpoints weekly for backup

**Performance Tuning**:
- Enable WAL mode for concurrency
- Create indexes on commonly queried fields
- Use connection pooling
- Optimize database with VACUUM and ANALYZE
- Monitor query performance

---

## Related Documentation

- **Architecture**: `CHECKPOINT_ARCHITECTURE.md` - Complete technical design
- **Tutorial**: `INTERACTIVE_BLOCKS_TUTORIAL.md` - Using interactive workflows
- **Quick Start**: `CHECKPOINT_QUICKSTART.md` - TDD implementation guide
- **Project Info**: `CLAUDE.md`, `ARCHITECTURE.md` - Project conventions

---

## Questions?

- SQLite documentation: https://www.sqlite.org/docs.html
- aiosqlite documentation: https://aiosqlite.omnilib.dev/
- PostgreSQL migration: Contact team for enterprise support
