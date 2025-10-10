"""Integration tests for workflow execution and composition.

Consolidated from:
- test_phase1_integration.py (workflow discovery and execution)
- test_integration_phase2.py (variable resolution and conditionals)
- test_phase4_tool_integration.py (MCP tool integration)

Tests verify end-to-end functionality including:
- Workflow discovery and loading from templates
- Basic and complex workflow execution
- Variable resolution across blocks
- Conditional block execution
- Parallel execution patterns
- Error handling
- Performance benchmarks
"""

from pathlib import Path

import pytest

from workflows_mcp.engine.executor import WorkflowDefinition
from workflows_mcp.engine.loader import load_workflow_from_file
from workflows_mcp.server import execute_workflow, get_workflow_info, list_workflows

# ============================================================================
# Workflow Execution Tests
# ============================================================================


class TestWorkflowExecution:
    """End-to-end workflow execution tests."""

    @pytest.mark.asyncio
    async def test_hello_world_workflow(self):
        """Test hello-world workflow execution."""
        result = await execute_workflow(
            workflow="hello-world", inputs={"name": "Integration Test"}
        )
        assert result["status"] == "success", f"hello-world failed: {result.get('error')}"
        assert "blocks" in result["outputs"], "Missing blocks in outputs"
        assert "greet" in result["outputs"]["blocks"], "Missing 'greet' block output"

    @pytest.mark.asyncio
    async def test_sequential_echo_workflow(self):
        """Test sequential-echo workflow with 3 sequential blocks."""
        result = await execute_workflow(workflow="sequential-echo", inputs={})
        assert result["status"] == "success", f"sequential-echo failed: {result.get('error')}"
        assert result["outputs"]["total_blocks"] == 3, "Expected 3 blocks"
        assert result["outputs"]["execution_waves"] == 3, "Expected 3 waves (sequential)"

    @pytest.mark.asyncio
    async def test_parallel_echo_workflow(self):
        """Test parallel-echo workflow with diamond pattern."""
        result = await execute_workflow(workflow="parallel-echo", inputs={})
        assert result["status"] == "success", f"parallel-echo failed: {result.get('error')}"
        assert result["outputs"]["total_blocks"] == 4, "Expected 4 blocks"
        assert result["outputs"]["execution_waves"] == 3, "Expected 3 waves (diamond pattern)"

    @pytest.mark.asyncio
    async def test_input_substitution_workflow(self):
        """Test input-substitution workflow with multiple inputs."""
        result = await execute_workflow(
            workflow="input-substitution",
            inputs={
                "user_name": "Claude",
                "project_name": "MCP Workflows",
                "iterations": 5,
                "verbose": True,
            },
        )
        assert result["status"] == "success", f"input-substitution failed: {result.get('error')}"
        assert result["outputs"]["total_blocks"] == 6, "Expected 6 blocks"

    @pytest.mark.asyncio
    async def test_complex_workflow(self):
        """Test complex-workflow with parallel execution."""
        result = await execute_workflow(
            workflow="complex-workflow",
            inputs={
                "project_name": "test-project",
                "environment": "staging",
            },
        )
        assert result["status"] == "success", f"complex-workflow failed: {result.get('error')}"
        assert result["outputs"]["total_blocks"] == 8, "Expected 8 blocks"
        # Complex workflow should have parallel stages (waves < blocks)
        assert (
            result["outputs"]["execution_waves"] < 8
        ), f"Expected parallel execution, got {result['outputs']['execution_waves']} waves"

    @pytest.mark.asyncio
    async def test_variable_resolution_across_blocks(self, executor):
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

        executor.load_workflow(workflow_def)
        result = await executor.execute_workflow("test-variable-resolution", {})

        assert result.is_success
        outputs = result.value

        # Verify both blocks executed
        assert "echo1" in outputs["blocks"], "echo1 should have executed"
        assert outputs["blocks"]["echo1"]["echoed"] == "Echo: Hello"
        assert outputs["blocks"]["echo2"]["echoed"] == "Echo: Echo from echo1: Echo: Hello"

    @pytest.mark.asyncio
    async def test_variable_resolution_with_workflow_inputs(self, executor):
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

        executor.load_workflow(workflow_def)
        result = await executor.execute_workflow("test-workflow-inputs", {"name": "Alice"})

        assert result.is_success
        outputs = result.value

        assert outputs["blocks"]["greet"]["echoed"] == "Echo: Hello Alice!"

    @pytest.mark.asyncio
    async def test_chained_variable_resolution(self, executor):
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

        executor.load_workflow(workflow_def)
        result = await executor.execute_workflow("test-chained-variables", {})

        assert result.is_success
        outputs = result.value

        assert (
            outputs["blocks"]["block3"]["echoed"]
            == "Echo: Echo: Echo: first-second-third"
        )

    @pytest.mark.asyncio
    async def test_nested_variable_resolution(self, executor):
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

        executor.load_workflow(workflow_def)
        result = await executor.execute_workflow("test-nested-variables", {})

        assert result.is_success
        outputs = result.value

        assert outputs["blocks"]["process"]["echoed"] == "Echo: Processing with Echo: config"


# ============================================================================
# Workflow Composition Tests
# ============================================================================


class TestWorkflowComposition:
    """Workflow composition and nesting tests."""

    @pytest.mark.asyncio
    async def test_workflow_discovery(self):
        """Test workflow discovery - MCP server loads workflows from templates."""
        workflows = await list_workflows()
        assert len(workflows) > 0, "Should discover workflows from templates"

        # Verify all 5 example workflows are loaded
        expected_workflows = {
            "hello-world",
            "sequential-echo",
            "parallel-echo",
            "input-substitution",
            "complex-workflow",
        }
        actual_workflows = {wf["name"] for wf in workflows}

        assert expected_workflows.issubset(
            actual_workflows
        ), f"Missing workflows: {expected_workflows - actual_workflows}"

    @pytest.mark.asyncio
    async def test_list_workflows_by_category(self):
        """Test list_workflows by category - Filters workflows correctly."""
        # Test valid tag filter
        test_workflows = await list_workflows(tags=["test"])
        assert len(test_workflows) >= 5, (
            f"Expected at least 5 test workflows, got {len(test_workflows)}"
        )

        # Test empty tags (all workflows)
        all_workflows = await list_workflows(tags=[])
        assert len(all_workflows) >= len(
            test_workflows
        ), "empty tags should return at least as many as 'test'"

        # Test non-existent tag
        invalid_result = await list_workflows(tags=["invalid_tag_xyz"])
        assert isinstance(invalid_result, list), "Should return list even for invalid tag"

    @pytest.mark.asyncio
    async def test_get_workflow_info(self):
        """Test get_workflow_info - Returns correct metadata for each workflow."""
        test_cases = [
            ("hello-world", 1),
            ("sequential-echo", 3),
            ("parallel-echo", 4),
            ("input-substitution", 6),
            ("complex-workflow", 8),
        ]

        for workflow_name, expected_blocks in test_cases:
            info = await get_workflow_info(workflow=workflow_name)

            assert info["name"] == workflow_name, (
                f"Name mismatch: {info['name']} != {workflow_name}"
            )
            assert (
                info["total_blocks"] == expected_blocks
            ), f"{workflow_name}: Expected {expected_blocks} blocks, got {info['total_blocks']}"

            # Verify blocks structure
            assert "blocks" in info, f"{workflow_name}: Missing 'blocks' field"
            assert len(info["blocks"]) == expected_blocks, f"{workflow_name}: Block count mismatch"

            for block in info["blocks"]:
                assert "id" in block, f"{workflow_name}: Block missing 'id'"
                assert "type" in block, f"{workflow_name}: Block missing 'type'"
                assert "depends_on" in block, f"{workflow_name}: Block missing 'depends_on'"

    @pytest.mark.asyncio
    async def test_workflow_metadata(self):
        """Test workflow metadata - Verify YAML schema fields are loaded correctly."""
        workflows = await list_workflows()

        for workflow in workflows:
            name = workflow["name"]

            # Get detailed info
            info = await get_workflow_info(workflow=name)

            # Verify metadata fields
            assert "name" in info, f"{name}: Missing 'name'"
            assert "description" in info, f"{name}: Missing 'description'"
            assert "total_blocks" in info, f"{name}: Missing 'total_blocks'"
            assert "blocks" in info, f"{name}: Missing 'blocks'"

            # Verify blocks have required fields
            for block in info["blocks"]:
                assert "id" in block, f"{name}: Block missing 'id'"
                assert "type" in block, f"{name}: Block missing 'type'"
                assert "depends_on" in block, f"{name}: Block missing 'depends_on'"


# ============================================================================
# Conditional Execution Tests
# ============================================================================


class TestConditionalExecution:
    """Conditional block execution tests."""

    @pytest.mark.asyncio
    async def test_conditional_execution_skip_block(self, executor):
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

        executor.load_workflow(workflow_def)
        result = await executor.execute_workflow("test-conditional-skip", {})

        assert result.is_success
        # The workflow should complete but deploy should be skipped

    @pytest.mark.asyncio
    async def test_conditional_execution_run_block(self, executor):
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

        executor.load_workflow(workflow_def)
        result = await executor.execute_workflow("test-conditional-run", {})

        assert result.is_success
        outputs = result.value

        # Both blocks should execute
        assert outputs["blocks"]["execute"]["echoed"] == "Echo: executing"

    @pytest.mark.asyncio
    async def test_conditional_branches(self, executor):
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

        executor.load_workflow(workflow_def)
        result = await executor.execute_workflow("test-conditional-branches", {})

        assert result.is_success
        outputs = result.value

        # on_failure should execute, on_success should skip
        assert outputs["blocks"]["on_failure"]["echoed"] == "Echo: failure path"

    @pytest.mark.asyncio
    async def test_complex_condition_with_multiple_variables(self, executor):
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
                    "condition": (
                        "${test_result.echoed} == 'Echo: passed' and "
                        "${lint_result.echoed} == 'Echo: passed'"
                    ),
                },
            ],
        )

        executor.load_workflow(workflow_def)
        result = await executor.execute_workflow("test-complex-condition", {})

        assert result.is_success
        outputs = result.value

        # Deploy should execute since both conditions are true
        assert outputs["blocks"]["deploy"]["echoed"] == "Echo: deploying"

    @pytest.mark.asyncio
    async def test_convergence_after_conditional(self, executor):
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

        executor.load_workflow(workflow_def)
        result = await executor.execute_workflow("test-convergence", {})

        assert result.is_success
        outputs = result.value

        # Converge should execute after branch_b
        assert outputs["blocks"]["converge"]["echoed"] == "Echo: converged"

    @pytest.mark.asyncio
    async def test_conditional_with_workflow_input(self, executor):
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

        executor.load_workflow(workflow_def)

        # Test with should_process=True
        result = await executor.execute_workflow(
            "test-conditional-input", {"should_process": True}
        )

        assert result.is_success
        outputs = result.value

        assert outputs["blocks"]["process"]["echoed"] == "Echo: processing"

    @pytest.mark.asyncio
    async def test_condition_with_numeric_comparison(self, executor):
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

        executor.load_workflow(workflow_def)
        result = await executor.execute_workflow("test-numeric-condition", {})

        assert result.is_success
        outputs = result.value

        # Block should execute (string '85' >= '80')
        assert outputs["blocks"]["check_threshold"]["echoed"] == "Echo: above threshold"

    @pytest.mark.asyncio
    async def test_multiple_conditional_paths_parallel(self, executor):
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

        executor.load_workflow(workflow_def)
        result = await executor.execute_workflow("test-parallel-conditionals", {})

        assert result.is_success
        outputs = result.value

        # All three paths should execute
        assert outputs["blocks"]["path1"]["echoed"] == "Echo: path1"
        assert outputs["blocks"]["path2"]["echoed"] == "Echo: path2"
        assert outputs["blocks"]["path3"]["echoed"] == "Echo: path3"


# ============================================================================
# Async Execution Tests
# ============================================================================


class TestAsyncExecution:
    """Async workflow execution tests."""

    @pytest.mark.asyncio
    async def test_parallel_execution(self):
        """Test parallel execution - parallel-echo executes waves correctly."""
        # Execute parallel-echo and verify wave structure
        result = await execute_workflow(workflow="parallel-echo", inputs={})
        assert result["status"] == "success", f"parallel-echo failed: {result.get('error')}"

        waves = result["outputs"]["execution_waves"]

        # Diamond pattern should have exactly 3 waves
        assert waves == 3, f"Expected 3 waves for diamond pattern, got {waves}"

        # Verify execution order makes sense
        blocks = result["outputs"]["blocks"]
        assert "start_block" in blocks, "Missing start_block"
        assert "parallel_a" in blocks, "Missing parallel_a"
        assert "parallel_b" in blocks, "Missing parallel_b"
        assert "final_merge" in blocks, "Missing final_merge"

    @pytest.mark.asyncio
    async def test_complex_workflow_parallel_execution(self):
        """Test complex workflow parallel execution."""
        result = await execute_workflow(
            workflow="complex-workflow",
            inputs={"project_name": "test", "environment": "dev"},
        )
        assert result["status"] == "success", f"complex-workflow failed: {result.get('error')}"

        waves = result["outputs"]["execution_waves"]
        total_blocks = result["outputs"]["total_blocks"]

        # Complex workflow (8 blocks) should have parallel stages
        assert waves < total_blocks, (
            f"Expected parallel execution (waves < blocks), "
            f"got {waves} waves for {total_blocks} blocks"
        )


# ============================================================================
# Error Handling Tests
# ============================================================================


class TestErrorHandling:
    """Error handling and recovery tests."""

    @pytest.mark.asyncio
    async def test_missing_workflow(self):
        """Test error handling - Missing workflow."""
        result = await execute_workflow(workflow="nonexistent-workflow-xyz", inputs={})
        assert result["status"] == "failure", "Expected failure for missing workflow"
        assert "error" in result, "Missing error message"

    @pytest.mark.asyncio
    async def test_nonexistent_tag(self):
        """Test error handling - Non-existent tag in list_workflows."""
        result = await list_workflows(tags=["invalid_xyz"])
        assert isinstance(result, list), "Should return list"
        # Empty list is acceptable for non-existent tags

    @pytest.mark.asyncio
    async def test_invalid_workflow_info_request(self):
        """Test error handling - Invalid workflow name in get_workflow_info."""
        try:
            result = await get_workflow_info(workflow="nonexistent-xyz")
            # If it doesn't raise an exception, check for error in result
            if isinstance(result, dict) and "error" in result:
                pass  # Expected error in result
            else:
                pytest.fail(f"get_workflow_info returned unexpected result: {result}")
        except Exception:
            # Expected exception
            pass


# ============================================================================
# Tool Integration Tests (Phase 4)
# ============================================================================


# Templates directory
TEMPLATES_DIR = Path(__file__).parent.parent.parent / "src" / "workflows_mcp" / "templates"


def load_workflow(workflow_path: str):
    """Helper to load a workflow and handle Result."""
    file_path = TEMPLATES_DIR / workflow_path
    result = load_workflow_from_file(file_path)
    if not result.is_success:
        pytest.fail(f"Failed to load workflow {workflow_path}: {result.error}")
    return result.value


class TestBackwardCompatibility:
    """Test that existing behavior is preserved when auto_install is not used."""

    def test_run_pytest_without_auto_install(self):
        """run-pytest works as before when auto_install is not specified."""
        workflow_def = load_workflow("python/run-pytest.yaml")
        assert workflow_def is not None

        # Verify auto_install has default value of true
        assert "auto_install" in workflow_def.inputs
        assert workflow_def.inputs["auto_install"]["default"] is True

        # Verify ensure_pytest block exists and has condition
        ensure_block = next(
            (b for b in workflow_def.blocks if b["id"] == "ensure_pytest"), None
        )
        assert ensure_block is not None
        assert ensure_block["condition"] == "${auto_install}"

    def test_lint_python_without_auto_install(self):
        """lint-python works as before when auto_install is not specified."""
        workflow_def = load_workflow("python/lint-python.yaml")
        assert workflow_def is not None

        # Verify auto_install has default value of true
        assert "auto_install" in workflow_def.inputs
        assert workflow_def.inputs["auto_install"]["default"] is True

        # Verify ensure blocks exist with proper conditions
        ensure_ruff = next(
            (b for b in workflow_def.blocks if b["id"] == "ensure_ruff"), None
        )
        assert ensure_ruff is not None
        assert ensure_ruff["condition"] == "${auto_install}"

        ensure_mypy = next(
            (b for b in workflow_def.blocks if b["id"] == "ensure_mypy"), None
        )
        assert ensure_mypy is not None
        assert ensure_mypy["condition"] == "${auto_install} and not ${skip_mypy}"

    def test_conditional_deploy_without_auto_install(self):
        """conditional-deploy works as before when auto_install is not specified."""
        workflow_def = load_workflow("ci/conditional-deploy.yaml")
        assert workflow_def is not None

        # Verify auto_install has default value of false
        assert "auto_install" in workflow_def.inputs
        assert workflow_def.inputs["auto_install"]["default"] is False

        # Verify run_tests block passes through auto_install
        run_tests = next(
            (b for b in workflow_def.blocks if b["id"] == "run_tests"), None
        )
        assert run_tests is not None
        assert run_tests["type"] == "ExecuteWorkflow"
        assert "auto_install" in run_tests["inputs"]["inputs"]


class TestAutoInstallParameter:
    """Test that auto_install parameter is properly defined and validated."""

    def test_run_pytest_auto_install_parameter(self):
        """run-pytest accepts auto_install parameter."""
        workflow_def = load_workflow("python/run-pytest.yaml")

        # Verify parameter exists and has correct type
        auto_install_input = workflow_def.inputs["auto_install"]
        assert auto_install_input["type"] == "boolean"
        assert auto_install_input["default"] is True
        assert "auto" in auto_install_input["description"].lower()

    def test_lint_python_auto_install_parameter(self):
        """lint-python accepts auto_install parameter."""
        workflow_def = load_workflow("python/lint-python.yaml")

        # Verify parameter exists and has correct type
        auto_install_input = workflow_def.inputs["auto_install"]
        assert auto_install_input["type"] == "boolean"
        assert auto_install_input["default"] is True
        assert "auto" in auto_install_input["description"].lower()

    def test_conditional_deploy_auto_install_parameter(self):
        """conditional-deploy accepts auto_install parameter."""
        workflow_def = load_workflow("ci/conditional-deploy.yaml")

        # Verify parameter exists and has correct type
        auto_install_input = workflow_def.inputs["auto_install"]
        assert auto_install_input["type"] == "boolean"
        assert auto_install_input["default"] is False
        assert "auto" in auto_install_input["description"].lower()


class TestEnsureToolIntegration:
    """Test ensure-tool workflow integration."""

    def test_run_pytest_ensure_block_configuration(self):
        """run-pytest ensure_pytest block is properly configured."""
        workflow_def = load_workflow("python/run-pytest.yaml")

        ensure_block = next(
            (b for b in workflow_def.blocks if b["id"] == "ensure_pytest"), None
        )
        assert ensure_block is not None
        assert ensure_block["type"] == "ExecuteWorkflow"

        # Verify it calls the correct workflow
        assert ensure_block["inputs"]["workflow"] == "ensure-tool"

        # Verify inputs are properly configured
        inputs = ensure_block["inputs"]["inputs"]
        assert inputs["tool_name"] == "pytest"
        assert inputs["tool_type"] == "python_package"
        assert inputs["version"] == ">=7.0.0"
        assert inputs["venv_path"] == "${venv_path}"
        assert inputs["auto_install"] is True

    def test_lint_python_ensure_blocks_configuration(self):
        """lint-python ensure blocks are properly configured."""
        workflow_def = load_workflow("python/lint-python.yaml")

        # Check ensure_ruff
        ensure_ruff = next(
            (b for b in workflow_def.blocks if b["id"] == "ensure_ruff"), None
        )
        assert ensure_ruff is not None
        assert ensure_ruff["inputs"]["workflow"] == "ensure-tool"
        ruff_inputs = ensure_ruff["inputs"]["inputs"]
        assert ruff_inputs["tool_name"] == "ruff"
        assert ruff_inputs["tool_type"] == "python_package"

        # Check ensure_mypy
        ensure_mypy = next(
            (b for b in workflow_def.blocks if b["id"] == "ensure_mypy"), None
        )
        assert ensure_mypy is not None
        assert ensure_mypy["inputs"]["workflow"] == "ensure-tool"
        mypy_inputs = ensure_mypy["inputs"]["inputs"]
        assert mypy_inputs["tool_name"] == "mypy"
        assert mypy_inputs["tool_type"] == "python_package"


class TestConditionalExecutionInTools:
    """Test that ensure-tool blocks only run when conditions are met."""

    def test_ensure_blocks_have_proper_conditions(self):
        """Ensure blocks should only run when auto_install=true."""
        workflow_def = load_workflow("python/run-pytest.yaml")

        ensure_block = next(
            (b for b in workflow_def.blocks if b["id"] == "ensure_pytest"), None
        )
        assert ensure_block["condition"] == "${auto_install}"

    def test_mypy_ensure_respects_skip_flag(self):
        """ensure_mypy should respect both auto_install and skip_mypy."""
        workflow_def = load_workflow("python/lint-python.yaml")

        ensure_mypy = next(
            (b for b in workflow_def.blocks if b["id"] == "ensure_mypy"), None
        )
        # Should only run if auto_install=true AND skip_mypy=false
        assert ensure_mypy["condition"] == "${auto_install} and not ${skip_mypy}"


class TestDocumentation:
    """Test that workflows are properly documented with auto-install capability."""

    def test_run_pytest_mentions_auto_install(self):
        """run-pytest description mentions auto-install support."""
        workflow_def = load_workflow("python/run-pytest.yaml")
        assert "auto-install" in workflow_def.description.lower()

    def test_lint_python_mentions_auto_install(self):
        """lint-python description mentions auto-install support."""
        workflow_def = load_workflow("python/lint-python.yaml")
        assert "auto-install" in workflow_def.description.lower()
