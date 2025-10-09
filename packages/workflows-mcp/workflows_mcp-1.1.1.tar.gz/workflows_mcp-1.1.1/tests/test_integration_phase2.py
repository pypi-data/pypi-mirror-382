"""
Integration tests for Phase 2.0: Variable Resolution + Conditionals.

These tests verify end-to-end functionality including:
- Variable resolution across blocks
- Conditional block execution
- DAG with conditional branches
- Context accumulation with dot notation
- Convergence after conditional execution
"""

import pytest

from workflows_mcp.engine.executor import WorkflowDefinition, WorkflowExecutor


@pytest.mark.asyncio
class TestPhase2Integration:
    """Integration tests for Phase 2.0 features."""

    async def test_variable_resolution_across_blocks(self):
        """Test variable resolution from one block to another."""
        workflow_def = WorkflowDefinition(
            name="test-variable-resolution",
            description="Test variable resolution",
            blocks=[
                {
                    "id": "echo1",
                    "type": "EchoBlock",
                    "inputs": {"message": "Hello"},
                    "depends_on": [],
                },
                {
                    "id": "echo2",
                    "type": "EchoBlock",
                    "inputs": {"message": "Echo from echo1: ${echo1.echoed}"},
                    "depends_on": ["echo1"],
                },
            ],
        )

        executor = WorkflowExecutor()
        executor.load_workflow(workflow_def)

        result = await executor.execute_workflow("test-variable-resolution", {})

        assert result.is_success
        outputs = result.value

        # Verify both blocks executed
        assert "echo1" in outputs["blocks"], "echo1 should have executed"
        assert outputs["blocks"]["echo1"]["echoed"] == "Echo: Hello"
        assert outputs["blocks"]["echo2"]["echoed"] == "Echo: Echo from echo1: Echo: Hello"

    async def test_conditional_execution_skip_block(self):
        """Test conditional execution that skips a block."""
        workflow_def = WorkflowDefinition(
            name="test-conditional-skip",
            description="Test conditional skip",
            blocks=[
                {
                    "id": "check",
                    "type": "EchoBlock",
                    "inputs": {"message": "checking"},
                    "depends_on": [],
                },
                {
                    "id": "deploy",
                    "type": "EchoBlock",
                    "inputs": {"message": "deploying"},
                    "depends_on": ["check"],
                    "condition": "${check.echoed} == 'Echo: success'",  # Will be false
                },
            ],
        )

        executor = WorkflowExecutor()
        executor.load_workflow(workflow_def)

        result = await executor.execute_workflow("test-conditional-skip", {})

        assert result.is_success

        # The workflow should complete but deploy should be skipped
        # We can't directly verify skipped blocks in current implementation
        # but the workflow should succeed

    async def test_conditional_execution_run_block(self):
        """Test conditional execution that runs a block."""
        workflow_def = WorkflowDefinition(
            name="test-conditional-run",
            description="Test conditional run",
            blocks=[
                {
                    "id": "setup",
                    "type": "EchoBlock",
                    "inputs": {"message": "ready"},
                    "depends_on": [],
                },
                {
                    "id": "execute",
                    "type": "EchoBlock",
                    "inputs": {"message": "executing"},
                    "depends_on": ["setup"],
                    "condition": "${setup.echoed} == 'Echo: ready'",  # Will be true
                },
            ],
        )

        executor = WorkflowExecutor()
        executor.load_workflow(workflow_def)

        result = await executor.execute_workflow("test-conditional-run", {})

        assert result.is_success
        outputs = result.value

        # Both blocks should execute
        assert outputs["blocks"]["execute"]["echoed"] == "Echo: executing"

    async def test_conditional_branches(self):
        """Test DAG with conditional branches (if-else pattern)."""
        workflow_def = WorkflowDefinition(
            name="test-conditional-branches",
            description="Test conditional branches",
            blocks=[
                {
                    "id": "check_status",
                    "type": "EchoBlock",
                    "inputs": {"message": "failed"},
                    "depends_on": [],
                },
                {
                    "id": "on_success",
                    "type": "EchoBlock",
                    "inputs": {"message": "success path"},
                    "depends_on": ["check_status"],
                    "condition": "${check_status.echoed} == 'Echo: success'",
                },
                {
                    "id": "on_failure",
                    "type": "EchoBlock",
                    "inputs": {"message": "failure path"},
                    "depends_on": ["check_status"],
                    "condition": "${check_status.echoed} == 'Echo: failed'",
                },
            ],
        )

        executor = WorkflowExecutor()
        executor.load_workflow(workflow_def)

        result = await executor.execute_workflow("test-conditional-branches", {})

        assert result.is_success
        outputs = result.value

        # on_failure should execute, on_success should skip
        assert outputs["blocks"]["on_failure"]["echoed"] == "Echo: failure path"

    async def test_variable_resolution_with_workflow_inputs(self):
        """Test variable resolution from workflow inputs."""
        workflow_def = WorkflowDefinition(
            name="test-workflow-inputs",
            description="Test workflow inputs",
            blocks=[
                {
                    "id": "greet",
                    "type": "EchoBlock",
                    "inputs": {"message": "Hello ${name}!"},
                    "depends_on": [],
                },
            ],
        )

        executor = WorkflowExecutor()
        executor.load_workflow(workflow_def)

        result = await executor.execute_workflow(
            "test-workflow-inputs", {"name": "Alice"}
        )

        assert result.is_success
        outputs = result.value

        assert outputs["blocks"]["greet"]["echoed"] == "Echo: Hello Alice!"

    async def test_complex_condition_with_multiple_variables(self):
        """Test complex condition referencing multiple block outputs."""
        workflow_def = WorkflowDefinition(
            name="test-complex-condition",
            description="Test complex condition",
            blocks=[
                {
                    "id": "test_result",
                    "type": "EchoBlock",
                    "inputs": {"message": "passed"},
                    "depends_on": [],
                },
                {
                    "id": "lint_result",
                    "type": "EchoBlock",
                    "inputs": {"message": "passed"},
                    "depends_on": [],
                },
                {
                    "id": "deploy",
                    "type": "EchoBlock",
                    "inputs": {"message": "deploying"},
                    "depends_on": ["test_result", "lint_result"],
                    "condition": "${test_result.echoed} == 'Echo: passed' and ${lint_result.echoed} == 'Echo: passed'",
                },
            ],
        )

        executor = WorkflowExecutor()
        executor.load_workflow(workflow_def)

        result = await executor.execute_workflow("test-complex-condition", {})

        assert result.is_success
        outputs = result.value

        # Deploy should execute since both conditions are true
        assert outputs["blocks"]["deploy"]["echoed"] == "Echo: deploying"

    async def test_convergence_after_conditional(self):
        """Test convergence point after conditional branches."""
        workflow_def = WorkflowDefinition(
            name="test-convergence",
            description="Test convergence after conditionals",
            blocks=[
                {
                    "id": "start",
                    "type": "EchoBlock",
                    "inputs": {"message": "starting"},
                    "depends_on": [],
                },
                {
                    "id": "branch_a",
                    "type": "EchoBlock",
                    "inputs": {"message": "branch a"},
                    "depends_on": ["start"],
                    "condition": "${start.echoed} == 'Echo: success'",  # Will skip
                },
                {
                    "id": "branch_b",
                    "type": "EchoBlock",
                    "inputs": {"message": "branch b"},
                    "depends_on": ["start"],
                    "condition": "${start.echoed} == 'Echo: starting'",  # Will execute
                },
                {
                    "id": "converge",
                    "type": "EchoBlock",
                    "inputs": {"message": "converged"},
                    "depends_on": ["branch_a", "branch_b"],
                },
            ],
        )

        executor = WorkflowExecutor()
        executor.load_workflow(workflow_def)

        result = await executor.execute_workflow("test-convergence", {})

        assert result.is_success
        outputs = result.value

        # Converge should execute after branch_b
        assert outputs["blocks"]["converge"]["echoed"] == "Echo: converged"

    async def test_nested_variable_resolution(self):
        """Test variable resolution in nested structures."""
        workflow_def = WorkflowDefinition(
            name="test-nested-variables",
            description="Test nested variable resolution",
            blocks=[
                {
                    "id": "setup",
                    "type": "EchoBlock",
                    "inputs": {"message": "config"},
                    "depends_on": [],
                },
                {
                    "id": "process",
                    "type": "EchoBlock",
                    "inputs": {
                        "message": "Processing with ${setup.echoed}",
                    },
                    "depends_on": ["setup"],
                },
            ],
        )

        executor = WorkflowExecutor()
        executor.load_workflow(workflow_def)

        result = await executor.execute_workflow("test-nested-variables", {})

        assert result.is_success
        outputs = result.value

        assert outputs["blocks"]["process"]["echoed"] == "Echo: Processing with Echo: config"

    async def test_conditional_with_workflow_input(self):
        """Test conditional that depends on workflow input."""
        workflow_def = WorkflowDefinition(
            name="test-conditional-input",
            description="Test conditional with input",
            blocks=[
                {
                    "id": "process",
                    "type": "EchoBlock",
                    "inputs": {"message": "processing"},
                    "depends_on": [],
                    "condition": "${should_process} == True",
                },
            ],
        )

        executor = WorkflowExecutor()
        executor.load_workflow(workflow_def)

        # Test with should_process=True
        result = await executor.execute_workflow(
            "test-conditional-input", {"should_process": True}
        )

        assert result.is_success
        outputs = result.value

        assert outputs["blocks"]["process"]["echoed"] == "Echo: processing"

    async def test_chained_variable_resolution(self):
        """Test variable resolution across multiple blocks in chain."""
        workflow_def = WorkflowDefinition(
            name="test-chained-variables",
            description="Test chained variable resolution",
            blocks=[
                {
                    "id": "block1",
                    "type": "EchoBlock",
                    "inputs": {"message": "first"},
                    "depends_on": [],
                },
                {
                    "id": "block2",
                    "type": "EchoBlock",
                    "inputs": {"message": "${block1.echoed}-second"},
                    "depends_on": ["block1"],
                },
                {
                    "id": "block3",
                    "type": "EchoBlock",
                    "inputs": {"message": "${block2.echoed}-third"},
                    "depends_on": ["block2"],
                },
            ],
        )

        executor = WorkflowExecutor()
        executor.load_workflow(workflow_def)

        result = await executor.execute_workflow("test-chained-variables", {})

        assert result.is_success
        outputs = result.value

        assert (
            outputs["blocks"]["block3"]["echoed"]
            == "Echo: Echo: Echo: first-second-third"
        )

    async def test_condition_with_numeric_comparison(self):
        """Test conditional with numeric comparison."""
        workflow_def = WorkflowDefinition(
            name="test-numeric-condition",
            description="Test numeric condition",
            blocks=[
                {
                    "id": "setup",
                    "type": "EchoBlock",
                    "inputs": {"message": "85"},
                    "depends_on": [],
                },
                {
                    "id": "check_threshold",
                    "type": "EchoBlock",
                    "inputs": {"message": "above threshold"},
                    "depends_on": ["setup"],
                    "condition": "${setup.echoed} >= 'Echo: 80'",  # String comparison
                },
            ],
        )

        executor = WorkflowExecutor()
        executor.load_workflow(workflow_def)

        result = await executor.execute_workflow("test-numeric-condition", {})

        assert result.is_success
        outputs = result.value

        # Block should execute (string '85' >= '80')
        assert outputs["blocks"]["check_threshold"]["echoed"] == "Echo: above threshold"

    async def test_multiple_conditional_paths_parallel(self):
        """Test multiple independent conditional paths executing in parallel."""
        workflow_def = WorkflowDefinition(
            name="test-parallel-conditionals",
            description="Test parallel conditional paths",
            blocks=[
                {
                    "id": "start",
                    "type": "EchoBlock",
                    "inputs": {"message": "ready"},
                    "depends_on": [],
                },
                {
                    "id": "path1",
                    "type": "EchoBlock",
                    "inputs": {"message": "path1"},
                    "depends_on": ["start"],
                    "condition": "${start.echoed} == 'Echo: ready'",
                },
                {
                    "id": "path2",
                    "type": "EchoBlock",
                    "inputs": {"message": "path2"},
                    "depends_on": ["start"],
                    "condition": "${start.echoed} == 'Echo: ready'",
                },
                {
                    "id": "path3",
                    "type": "EchoBlock",
                    "inputs": {"message": "path3"},
                    "depends_on": ["start"],
                    "condition": "${start.echoed} == 'Echo: ready'",
                },
            ],
        )

        executor = WorkflowExecutor()
        executor.load_workflow(workflow_def)

        result = await executor.execute_workflow("test-parallel-conditionals", {})

        assert result.is_success
        outputs = result.value

        # All three paths should execute
        assert outputs["blocks"]["path1"]["echoed"] == "Echo: path1"
        assert outputs["blocks"]["path2"]["echoed"] == "Echo: path2"
        assert outputs["blocks"]["path3"]["echoed"] == "Echo: path3"
