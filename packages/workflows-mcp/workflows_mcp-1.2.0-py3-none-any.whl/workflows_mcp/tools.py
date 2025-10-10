"""MCP tool implementations for workflow execution.

This module contains Pydantic models and tool implementations that expose workflow
execution functionality to Claude Code via the MCP protocol.

Following official Anthropic MCP Python SDK patterns:
- Type hints for automatic schema generation
- Pydantic v2 models for validation
- Async functions for all tools
- Clear docstrings (become tool descriptions)
"""

from typing import Any

from pydantic import BaseModel, Field

# =============================================================================
# Tool Input/Output Models (Pydantic v2)
# =============================================================================


class ExecuteWorkflowInput(BaseModel):
    """Input schema for execute_workflow tool.

    Defines the parameters required to execute a DAG-based workflow.
    """

    workflow: str = Field(
        description="Workflow name to execute (e.g., 'generate-prp', 'python-setup')"
    )
    inputs: dict[str, Any] = Field(
        default_factory=dict,
        description="Runtime inputs as key-value pairs for workflow execution",
    )
    async_execution: bool = Field(
        default=False,
        description="Run workflow in background and return immediately (not yet implemented)",
    )


class ExecuteWorkflowOutput(BaseModel):
    """Output schema for execute_workflow tool.

    Contains workflow execution results, status, and performance metrics.
    """

    status: str = Field(
        description="Execution status: 'success', 'failure', or 'running' (for async)"
    )
    outputs: dict[str, Any] = Field(
        default_factory=dict,
        description="Workflow execution results as key-value pairs from block outputs",
    )
    execution_time: float = Field(description="Total execution time in seconds")
    error: str | None = Field(
        default=None,
        description="Error message if execution failed, null if successful",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional execution metadata (e.g., block_count, waves)",
    )


class WorkflowInfo(BaseModel):
    """Workflow metadata information for list_workflows.

    Provides basic workflow discovery information.
    """

    name: str = Field(description="Workflow name/identifier")
    description: str = Field(description="Human-readable workflow description")
    tags: list[str] = Field(
        description="Searchable workflow tags (e.g., ['python', 'test', 'quality'])"
    )


class WorkflowDetailedInfo(BaseModel):
    """Detailed workflow metadata for get_workflow_info.

    Provides comprehensive information about a specific workflow including
    inputs, outputs, and block structure.
    """

    name: str = Field(description="Workflow name/identifier")
    description: str = Field(description="Detailed workflow description")
    inputs: dict[str, str] = Field(
        description=(
            "Required workflow inputs with type descriptions (e.g., {'issue_ref': 'string'})"
        )
    )
    outputs: dict[str, str] = Field(
        description=(
            "Expected workflow outputs with type descriptions (e.g., {'worktree_path': 'string'})"
        )
    )
    blocks: list[str] = Field(description="List of block IDs in topological execution order")
    dependencies: dict[str, list[str]] = Field(
        default_factory=dict,
        description="Block dependency graph (block_id -> [dependency_ids])",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Searchable workflow tags for organization and discovery",
    )


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "ExecuteWorkflowInput",
    "ExecuteWorkflowOutput",
    "WorkflowInfo",
    "WorkflowDetailedInfo",
]
