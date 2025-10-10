"""FastMCP server initialization for workflows-mcp.

This module initializes the MCP server and registers workflow execution tools
following the official Anthropic Python SDK patterns.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

from .engine import (
    WorkflowExecutor,
    WorkflowRegistry,
)

# Configure logging to stderr (MCP requirement)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)

# Initialize MCP server with descriptive name
mcp = FastMCP("workflows")

# Initialize workflow registry
workflow_registry = WorkflowRegistry()

# Initialize workflow executor (will be loaded with registry workflows)
executor = WorkflowExecutor()


# =============================================================================
# Workflow Loading and Initialization
# =============================================================================


def load_workflows() -> None:
    """
    Load workflows from built-in templates and optional user-provided directories.

    This function:
    1. Parses WORKFLOWS_TEMPLATE_PATHS environment variable (comma-separated paths)
    2. Builds directory list: [built_in_templates, ...user_template_paths]
    3. Uses workflow_registry.load_from_directories() with on_duplicate="overwrite"
    4. Loads workflows from registry into executor
    5. Logs clearly which templates are built-in vs user-provided

    Priority: User templates OVERRIDE built-in templates by name.

    Environment Variables:
        WORKFLOWS_TEMPLATE_PATHS: Comma-separated list of additional template directories.
            Paths can use ~ for home directory. Empty or missing variable is handled gracefully.

    Example:
        WORKFLOWS_TEMPLATE_PATHS="~/my-workflows,/opt/company-workflows"
        # Load order:
        # 1. Built-in: src/workflows_mcp/templates/
        # 2. User: ~/my-workflows (overrides built-in by name)
        # 3. User: /opt/company-workflows (overrides both by name)
    """
    import os

    # Built-in templates directory
    built_in_templates = Path(__file__).parent / "templates"

    # Parse WORKFLOWS_TEMPLATE_PATHS environment variable
    env_paths_str = os.getenv("WORKFLOWS_TEMPLATE_PATHS", "")
    user_template_paths: list[Path] = []

    if env_paths_str.strip():
        # Split by comma, strip whitespace, expand ~, and convert to Path
        for path_str in env_paths_str.split(","):
            path_str = path_str.strip()
            if path_str:
                # Expand ~ for home directory
                expanded_path = Path(path_str).expanduser()
                user_template_paths.append(expanded_path)

        logger.info(f"User template paths from WORKFLOWS_TEMPLATE_PATHS: {user_template_paths}")

    # Build directory list: built-in first, then user paths (user paths override)
    # Cast to list[Path | str] for type compatibility with load_from_directories
    directories_to_load: list[Path | str] = [built_in_templates]
    directories_to_load.extend(user_template_paths)

    logger.info(f"Loading workflows from {len(directories_to_load)} directories")
    logger.info(f"  Built-in: {built_in_templates}")
    for idx, user_path in enumerate(user_template_paths, 1):
        logger.info(f"  User {idx}: {user_path}")

    # Load workflows from all directories with overwrite policy (user templates override)
    result = workflow_registry.load_from_directories(directories_to_load, on_duplicate="overwrite")

    if not result.is_success:
        logger.error(f"Failed to load workflows: {result.error}")
        return

    # Log loading results per directory
    load_counts = result.value
    if load_counts:
        logger.info("Workflow loading summary:")
        built_in_count = load_counts.get(str(built_in_templates), 0)
        logger.info(f"  Built-in templates: {built_in_count} workflows")

        for user_path in user_template_paths:
            user_count = load_counts.get(str(user_path), 0)
            logger.info(f"  User templates ({user_path}): {user_count} workflows")

    # Load all registry workflows into executor
    total_workflows = 0
    for workflow in workflow_registry.list_all():
        executor.load_workflow(workflow)
        total_workflows += 1

    logger.info(f"Successfully loaded {total_workflows} total workflows into executor")


# Load workflows on server initialization
load_workflows()


# =============================================================================
# MCP Tools (following official SDK decorator pattern)
# =============================================================================


@mcp.tool()
async def execute_workflow(
    workflow: str,
    inputs: dict[str, Any] | None = None,
    async_execution: bool = False,
) -> dict[str, Any]:
    """Execute a DAG-based workflow with inputs.

    Supports git operations, bash commands, templates, and workflow composition.

    Args:
        workflow: Workflow name (e.g., 'sequential-echo', 'parallel-echo')
        inputs: Runtime inputs as key-value pairs for block variable substitution
        async_execution: Run workflow in background and return immediately
            (not implemented in Phase 0)

    Returns:
        Dictionary with workflow execution results including status, outputs, and timing
    """
    if async_execution:
        return {
            "status": "error",
            "error": "Async execution not implemented in Phase 0",
        }

    # Execute workflow
    result = await executor.execute_workflow(workflow, inputs)

    if result.is_success:
        # Type narrowing: result.value is dict[str, Any] when is_success is True
        outputs: dict[str, Any] = result.value  # type: ignore[assignment]
        return {
            "status": "success",
            "outputs": outputs,
            "execution_time": outputs.get("execution_time_seconds", 0),
        }
    else:
        return {"status": "failure", "error": result.error, "execution_time": 0}


@mcp.tool()
async def list_workflows(
    tags: list[str] | None = None,
) -> list[dict[str, str | list[str]]]:
    """List all available workflows with descriptions.

    Discover available workflow templates filtered by tags.

    Args:
        tags: Optional list of tags to filter by. Uses AND semantics:
            workflow must have ALL specified tags.

    Returns:
        List of workflow metadata dictionaries with name, description, tags, etc.

    Examples:
        # All workflows
        list_workflows()

        # All Python-related workflows
        list_workflows(tags=["python"])

        # All workflows with both "linting" and "python" tags
        list_workflows(tags=["python", "linting"])

        # All quality workflows
        list_workflows(tags=["quality"])
    """
    # Get all workflows
    if workflow_registry and len(workflow_registry) > 0:
        metadata_list = workflow_registry.list_all_metadata()
    else:
        # Fallback to executor if registry is empty (example workflows)
        workflows: list[dict[str, str | list[str]]] = []
        for name, workflow_def in executor.workflows.items():
            workflows.append(
                {
                    "name": name,
                    "description": workflow_def.description,
                    "blocks": str(len(workflow_def.blocks)),
                }
            )
        return workflows

    # Apply tag filtering if tags are provided
    if tags:
        # Filter the metadata_list by tags (AND semantics)
        filtered_list: list[dict[str, str | list[str]]] = []
        for workflow_metadata in metadata_list:
            # Check if workflow has tags field
            workflow_tags = workflow_metadata.get("tags", [])
            if not isinstance(workflow_tags, list):
                continue

            # Check if workflow has ALL specified tags (AND semantics)
            workflow_tags_set = set(workflow_tags)
            if all(tag in workflow_tags_set for tag in tags):
                filtered_list.append(workflow_metadata)

        return filtered_list

    return metadata_list


@mcp.tool()
async def get_workflow_info(workflow: str) -> dict[str, Any]:
    """Get detailed information about a specific workflow.

    Retrieve comprehensive metadata about a workflow including block structure and dependencies.

    Args:
        workflow: Workflow name/identifier to retrieve information about

    Returns:
        Dictionary with workflow metadata: name, description, version, tags, blocks, etc.
        Returns error dict if workflow not found.
    """
    # Try to get from registry first (includes schema metadata)
    if workflow_registry and workflow in workflow_registry:
        try:
            # Get metadata from registry
            metadata = workflow_registry.get_workflow_metadata(workflow)

            # Get workflow definition for block details
            workflow_def = workflow_registry.get(workflow)

            # Get schema if available for input/output information
            schema = workflow_registry.get_schema(workflow)

            # Build comprehensive info dictionary
            info: dict[str, Any] = {
                "name": metadata["name"],
                "description": metadata["description"],
                "version": metadata.get("version", "1.0"),
                "total_blocks": len(workflow_def.blocks),
                "blocks": [
                    {
                        "id": block["id"],
                        "type": block["type"],
                        "depends_on": block.get("depends_on", []),
                    }
                    for block in workflow_def.blocks
                ],
            }

            # Add optional metadata fields
            if "author" in metadata:
                info["author"] = metadata["author"]
            if "tags" in metadata:
                info["tags"] = metadata["tags"]

            # Add input/output schema if available
            if schema:
                # Convert input declarations to simple type mapping
                if schema.inputs:
                    info["inputs"] = {
                        name: {"type": decl.type.value, "description": decl.description}
                        for name, decl in schema.inputs.items()
                    }

                # Add output mappings if available
                if schema.outputs:
                    info["outputs"] = schema.outputs

            return info

        except KeyError:
            return {
                "error": f"Workflow not found: {workflow}",
                "available_workflows": workflow_registry.list_names(),
            }

    # Fallback to executor if not in registry (example workflows)
    elif workflow in executor.workflows:
        workflow_def = executor.workflows[workflow]

        return {
            "name": workflow_def.name,
            "description": workflow_def.description,
            "total_blocks": len(workflow_def.blocks),
            "blocks": [
                {
                    "id": block["id"],
                    "type": block["type"],
                    "depends_on": block.get("depends_on", []),
                }
                for block in workflow_def.blocks
            ],
        }
    else:
        # Workflow not found anywhere
        available = sorted(executor.workflows.keys())
        return {
            "error": f"Workflow not found: {workflow}",
            "available_workflows": available,
        }


# =============================================================================
# Checkpoint Management Tools
# =============================================================================


@mcp.tool()
async def resume_workflow(
    checkpoint_id: str,
    llm_response: str = "",
) -> dict[str, Any]:
    """Resume a paused or checkpointed workflow.

    Use this to continue a workflow that was paused for interactive input,
    or to restart a workflow from a crash recovery checkpoint.

    Args:
        checkpoint_id: Checkpoint token from pause or list_checkpoints
        llm_response: Your response to the pause prompt (required for paused workflows)

    Returns:
        Workflow execution result (same format as execute_workflow)

    Example:
        # Resume paused workflow with confirmation
        resume_workflow(
            checkpoint_id="pause_abc123",
            llm_response="yes"
        )
    """
    # Check executor has resume capability
    if not hasattr(executor, "resume_workflow"):
        return {"status": "error", "error": "Executor not properly initialized"}

    # Resume workflow
    result = await executor.resume_workflow(checkpoint_id, llm_response)

    if result.is_paused and result.pause_data:
        # Paused again
        return {
            "status": "paused",
            "checkpoint_id": result.pause_data.checkpoint_id,
            "prompt": result.pause_data.prompt,
            "message": "Workflow paused again - use resume_workflow to continue",
        }
    elif result.is_success:
        return {
            "status": "success",
            "outputs": result.value,
            "message": "Workflow completed successfully",
        }
    else:
        return {"status": "failure", "error": result.error, "message": "Workflow execution failed"}


@mcp.tool()
async def list_checkpoints(workflow_name: str = "") -> dict[str, Any]:
    """List available workflow checkpoints.

    Shows all checkpoints, including both automatic checkpoints (for crash recovery)
    and pause checkpoints (for interactive workflows).

    Args:
        workflow_name: Filter by workflow name (empty = all workflows)

    Returns:
        List of checkpoint metadata with creation time, pause status, etc.

    Example:
        list_checkpoints(workflow_name="python-ci-pipeline")
    """
    # Check executor exists and has checkpoint_store
    try:
        if not hasattr(executor, "checkpoint_store"):
            return {"checkpoints": [], "total": 0}
    except NameError:
        return {"checkpoints": [], "total": 0}

    filter_name = workflow_name if workflow_name else None
    checkpoints = await executor.checkpoint_store.list_checkpoints(filter_name)

    return {
        "checkpoints": [
            {
                "checkpoint_id": c.checkpoint_id,
                "workflow": c.workflow_name,
                "created_at": c.created_at,
                "created_at_iso": datetime.fromtimestamp(c.created_at).isoformat(),
                "is_paused": c.paused_block_id is not None,
                "pause_prompt": c.pause_prompt,
                "type": "pause" if c.paused_block_id is not None else "automatic",
            }
            for c in checkpoints
        ],
        "total": len(checkpoints),
    }


@mcp.tool()
async def get_checkpoint_info(checkpoint_id: str) -> dict[str, Any]:
    """Get detailed information about a specific checkpoint.

    Useful for inspecting checkpoint state before resuming.

    Args:
        checkpoint_id: Checkpoint token

    Returns:
        Detailed checkpoint information
    """
    if not hasattr(executor, "checkpoint_store"):
        return {"found": False, "error": "Executor not initialized"}

    state = await executor.checkpoint_store.load_checkpoint(checkpoint_id)
    if state is None:
        return {"found": False, "error": f"Checkpoint {checkpoint_id} not found or expired"}

    # Calculate progress percentage
    total_blocks = sum(len(wave) for wave in state.execution_waves)
    if total_blocks > 0:
        progress_percentage = len(state.completed_blocks) / total_blocks * 100
    else:
        progress_percentage = 0

    return {
        "found": True,
        "checkpoint_id": state.checkpoint_id,
        "workflow_name": state.workflow_name,
        "created_at": state.created_at,
        "created_at_iso": datetime.fromtimestamp(state.created_at).isoformat(),
        "is_paused": state.paused_block_id is not None,
        "paused_block_id": state.paused_block_id,
        "pause_prompt": state.pause_prompt,
        "completed_blocks": state.completed_blocks,
        "current_wave": state.current_wave_index,
        "total_waves": len(state.execution_waves),
        "progress_percentage": round(progress_percentage, 1),
    }


@mcp.tool()
async def delete_checkpoint(checkpoint_id: str) -> dict[str, Any]:
    """Delete a checkpoint.

    Useful for cleaning up paused workflows that are no longer needed.

    Args:
        checkpoint_id: Checkpoint token to delete

    Returns:
        Deletion status
    """
    if not hasattr(executor, "checkpoint_store"):
        return {"deleted": False, "error": "Executor not initialized"}

    deleted = await executor.checkpoint_store.delete_checkpoint(checkpoint_id)

    return {
        "deleted": deleted,
        "checkpoint_id": checkpoint_id,
        "message": "Checkpoint deleted successfully" if deleted else "Checkpoint not found",
    }


# =============================================================================
# Server Entry Point
# =============================================================================


def main() -> None:
    """Entry point for running the MCP server.

    This function is called when the server is run directly via:
    - uv run python -m workflows_mcp
    - python -m workflows_mcp
    - uv run workflows-mcp (if entry point is configured in pyproject.toml)

    Defaults to stdio transport for MCP protocol communication.
    """
    mcp.run()  # Defaults to stdio transport


__all__ = [
    "mcp",
    "main",
    "execute_workflow",
    "list_workflows",
    "get_workflow_info",
    "resume_workflow",
    "list_checkpoints",
    "get_checkpoint_info",
    "delete_checkpoint",
    "executor",
    "workflow_registry",
]
