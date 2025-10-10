"""Serialization utilities for checkpoint data.

Handles conversion between Python objects and JSON-serializable formats,
with special handling for non-JSON types like Path and datetime.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from workflows_mcp.engine.checkpoint import CheckpointState


def serialize_context(context: dict[str, Any]) -> dict[str, Any]:
    """Serialize workflow context to JSON-compatible format.

    Converts special types:
    - Path → str
    - datetime → ISO format string
    - Filters out __executor__ reference

    Args:
        context: Raw workflow context with potentially non-JSON types

    Returns:
        JSON-serializable dictionary
    """
    serialized = {}

    for key, value in context.items():
        # Skip executor reference
        if key == "__executor__":
            continue

        # Convert Path to string
        if isinstance(value, Path):
            serialized[key] = str(value)
        # Convert datetime to ISO format
        elif isinstance(value, datetime):
            serialized[key] = value.isoformat()
        # Keep everything else as-is
        else:
            serialized[key] = value

    return serialized


def deserialize_context(
    serialized: dict[str, Any], executor: Any
) -> dict[str, Any]:
    """Deserialize context and restore executor reference.

    Args:
        serialized: JSON-deserialized context
        executor: Executor instance to restore in context

    Returns:
        Context dictionary with executor reference restored
    """
    context = serialized.copy()
    context["__executor__"] = executor
    return context


def validate_checkpoint_size(state: CheckpointState, max_size_mb: float) -> bool:
    """Validate checkpoint size is within acceptable limits.

    Args:
        state: Checkpoint state to validate
        max_size_mb: Maximum allowed size in megabytes

    Returns:
        True if size is acceptable, False otherwise
    """
    # Serialize state to JSON to measure size
    serialized = {
        "checkpoint_id": state.checkpoint_id,
        "workflow_name": state.workflow_name,
        "created_at": state.created_at,
        "runtime_inputs": state.runtime_inputs,
        "context": serialize_context(state.context),
        "completed_blocks": state.completed_blocks,
        "current_wave_index": state.current_wave_index,
        "execution_waves": state.execution_waves,
        "block_definitions": state.block_definitions,
        "workflow_stack": state.workflow_stack,
    }

    # Convert to JSON string and measure bytes
    json_str = json.dumps(serialized)
    size_bytes = len(json_str.encode("utf-8"))
    size_mb = size_bytes / (1024 * 1024)

    return size_mb <= max_size_mb
