"""Test MCP checkpoint management tools.

Tests for the MCP tools that expose checkpoint/pause/resume functionality to Claude.
"""

import time

import pytest

from workflows_mcp.engine.checkpoint import CheckpointState
from workflows_mcp.engine.checkpoint_store import InMemoryCheckpointStore
from workflows_mcp.engine.executor import WorkflowDefinition, WorkflowExecutor


@pytest.fixture
async def setup_test_environment():
    """Setup test environment with executor and checkpoint store."""

    store = InMemoryCheckpointStore()
    executor = WorkflowExecutor(checkpoint_store=store)

    # Load test workflow
    workflow = WorkflowDefinition(
        name="test-workflow",
        description="Test workflow",
        blocks=[
            {"id": "block1", "type": "EchoBlock", "inputs": {"message": "Test"}, "depends_on": []}
        ],
        inputs={},
    )
    executor.load_workflow(workflow)

    # Create some test checkpoints
    block_def = {
        "id": "block1",
        "type": "EchoBlock",
        "inputs": {"message": "Test"},
        "depends_on": [],
    }
    checkpoint1 = CheckpointState(
        checkpoint_id="chk_test_1",
        workflow_name="test-workflow",
        created_at=time.time(),
        runtime_inputs={},
        context={},
        completed_blocks=[],
        current_wave_index=0,
        execution_waves=[["block1"]],
        block_definitions={"block1": block_def},
        workflow_stack=[],
    )

    checkpoint2 = CheckpointState(
        checkpoint_id="pause_test_2",
        workflow_name="test-workflow",
        created_at=time.time() - 100,
        runtime_inputs={},
        context={},
        completed_blocks=[],
        current_wave_index=0,
        execution_waves=[],
        block_definitions={},
        workflow_stack=[],
        paused_block_id="confirm1",
        pause_prompt="Confirm operation?",
    )

    await store.save_checkpoint(checkpoint1)
    await store.save_checkpoint(checkpoint2)

    return {"executor": executor, "store": store}


@pytest.mark.asyncio
async def test_resume_workflow_tool_with_checkpoint(setup_test_environment):
    """resume_workflow tool must work with valid checkpoint."""
    from workflows_mcp import server

    # Set global executor for tool access
    server.executor = setup_test_environment["executor"]

    # Call resume_workflow tool
    result = await server.resume_workflow(checkpoint_id="chk_test_1", llm_response="")

    assert isinstance(result, dict)
    assert result["status"] in ["success", "failure"]
    # Should either succeed or have clear error message


@pytest.mark.asyncio
async def test_resume_workflow_tool_with_pause(setup_test_environment):
    """resume_workflow tool must handle paused checkpoints."""
    from workflows_mcp import server

    server.executor = setup_test_environment["executor"]

    # Resume paused checkpoint with response
    result = await server.resume_workflow(checkpoint_id="pause_test_2", llm_response="yes")

    assert isinstance(result, dict)
    assert result["status"] in ["success", "failure", "paused"]


@pytest.mark.asyncio
async def test_resume_workflow_tool_missing_checkpoint(setup_test_environment):
    """resume_workflow tool must handle missing checkpoint."""
    from workflows_mcp import server

    server.executor = setup_test_environment["executor"]

    result = await server.resume_workflow(checkpoint_id="nonexistent", llm_response="")

    assert isinstance(result, dict)
    assert result["status"] == "failure"
    assert "error" in result
    assert "not found" in result["error"].lower()


@pytest.mark.asyncio
async def test_list_checkpoints_tool_all(setup_test_environment):
    """list_checkpoints tool must list all checkpoints."""
    from workflows_mcp import server

    server.executor = setup_test_environment["executor"]

    result = await server.list_checkpoints(workflow_name="")

    assert isinstance(result, dict)
    assert "checkpoints" in result
    assert isinstance(result["checkpoints"], list)
    assert len(result["checkpoints"]) >= 2  # At least our 2 test checkpoints
    assert "total" in result
    assert result["total"] >= 2


@pytest.mark.asyncio
async def test_list_checkpoints_tool_filtered(setup_test_environment):
    """list_checkpoints tool must filter by workflow name."""
    from workflows_mcp import server

    server.executor = setup_test_environment["executor"]

    result = await server.list_checkpoints(workflow_name="test-workflow")

    assert isinstance(result, dict)
    assert "checkpoints" in result
    assert all(c["workflow"] == "test-workflow" for c in result["checkpoints"])


@pytest.mark.asyncio
async def test_list_checkpoints_shows_pause_status(setup_test_environment):
    """list_checkpoints must indicate which checkpoints are paused."""
    from workflows_mcp import server

    server.executor = setup_test_environment["executor"]

    result = await server.list_checkpoints(workflow_name="test-workflow")

    checkpoints = result["checkpoints"]

    # Find paused checkpoint
    paused_checkpoints = [c for c in checkpoints if c.get("is_paused")]
    assert len(paused_checkpoints) >= 1

    # Paused checkpoint should have pause_prompt
    paused = paused_checkpoints[0]
    assert "pause_prompt" in paused
    assert paused["pause_prompt"] is not None


@pytest.mark.asyncio
async def test_get_checkpoint_info_tool(setup_test_environment):
    """get_checkpoint_info tool must return checkpoint details."""
    from workflows_mcp import server

    server.executor = setup_test_environment["executor"]

    result = await server.get_checkpoint_info(checkpoint_id="chk_test_1")

    assert isinstance(result, dict)
    assert result["found"] is True
    assert result["checkpoint_id"] == "chk_test_1"
    assert "workflow_name" in result
    assert "created_at" in result
    assert "is_paused" in result
    assert "completed_blocks" in result
    assert "current_wave" in result
    assert "total_waves" in result


@pytest.mark.asyncio
async def test_get_checkpoint_info_not_found(setup_test_environment):
    """get_checkpoint_info must handle missing checkpoint."""
    from workflows_mcp import server

    server.executor = setup_test_environment["executor"]

    result = await server.get_checkpoint_info(checkpoint_id="nonexistent")

    assert isinstance(result, dict)
    assert result["found"] is False
    assert "error" in result


@pytest.mark.asyncio
async def test_get_checkpoint_info_shows_progress(setup_test_environment):
    """get_checkpoint_info must show execution progress percentage."""
    from workflows_mcp import server

    server.executor = setup_test_environment["executor"]

    result = await server.get_checkpoint_info(checkpoint_id="chk_test_1")

    assert "progress_percentage" in result
    assert isinstance(result["progress_percentage"], (int, float))
    assert 0 <= result["progress_percentage"] <= 100


@pytest.mark.asyncio
async def test_delete_checkpoint_tool(setup_test_environment):
    """delete_checkpoint tool must delete checkpoint."""
    from workflows_mcp import server

    server.executor = setup_test_environment["executor"]

    result = await server.delete_checkpoint(checkpoint_id="chk_test_1")

    assert isinstance(result, dict)
    assert result["deleted"] is True
    assert result["checkpoint_id"] == "chk_test_1"

    # Verify it's gone
    info = await server.get_checkpoint_info("chk_test_1")
    assert info["found"] is False


@pytest.mark.asyncio
async def test_delete_checkpoint_not_found(setup_test_environment):
    """delete_checkpoint tool must handle missing checkpoint."""
    from workflows_mcp import server

    server.executor = setup_test_environment["executor"]

    result = await server.delete_checkpoint(checkpoint_id="nonexistent")

    assert isinstance(result, dict)
    assert result["deleted"] is False


@pytest.mark.asyncio
async def test_tools_handle_no_executor_gracefully():
    """Tools must handle case when executor is not initialized."""
    from workflows_mcp import server

    # Save original executor
    original = getattr(server, "executor", None)

    try:
        # Clear executor
        if hasattr(server, "executor"):
            delattr(server, "executor")

        # Tools should handle gracefully
        result = await server.list_checkpoints("")
        assert isinstance(result, dict)
        # Should return empty list or error, not crash

    finally:
        # Restore
        if original:
            server.executor = original
