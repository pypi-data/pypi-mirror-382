"""
Integration tests for custom file-based outputs in workflows.

Tests cover:
- Variable resolution with ${block.outputs.field} syntax
- Multi-level path resolution (3+ levels)
- Output composition between blocks
- Workflow-level outputs
- Integration with workflow composition
"""

from pathlib import Path

import pytest

from workflows_mcp.engine.executor import WorkflowDefinition, WorkflowExecutor
from workflows_mcp.engine.variables import VariableNotFoundError, VariableResolver


class TestOutputVariableResolution:
    """Test variable resolution for custom outputs in .outputs. namespace."""

    @pytest.mark.asyncio
    async def test_reference_custom_output_in_next_block(self, tmp_path: Path) -> None:
        """Test referencing custom output from one block in the next block."""
        workflow_def = WorkflowDefinition(
            name="test-workflow",
            description="Test output variable resolution",
            blocks=[
                {
                    "id": "generate_count",
                    "type": "BashCommand",
                    "inputs": {
                        "command": 'echo "42" > $SCRATCH/count.txt',
                        "working_dir": str(tmp_path),
                    },
                    "outputs": {
                        "count": {"type": "int", "path": "$SCRATCH/count.txt"}
                    },
                },
                {
                    "id": "use_count",
                    "type": "BashCommand",
                    "inputs": {
                        "command": 'echo "Count is: ${generate_count.outputs.count}"',
                        "working_dir": str(tmp_path),
                    },
                    "depends_on": ["generate_count"],
                },
            ],
        )

        executor = WorkflowExecutor()
        executor.load_workflow(workflow_def)
        result = await executor.execute_workflow("test-workflow", {})

        assert result.is_success

        # Verify the second block received resolved variable
        use_count_output = result.value["blocks"]["use_count"]
        assert "Count is: 42" in use_count_output["stdout"]

    @pytest.mark.asyncio
    async def test_reference_multiple_custom_outputs(self, tmp_path: Path) -> None:
        """Test referencing multiple custom outputs from previous blocks."""
        workflow_def = WorkflowDefinition(
            name="test-workflow",
            description="Test multiple output references",
            blocks=[
                {
                    "id": "step1",
                    "type": "BashCommand",
                    "inputs": {
                        "command": 'echo "10" > $SCRATCH/count.txt',
                        "working_dir": str(tmp_path),
                    },
                    "outputs": {
                        "count": {"type": "int", "path": "$SCRATCH/count.txt"}
                    },
                },
                {
                    "id": "step2",
                    "type": "BashCommand",
                    "inputs": {
                        "command": 'echo "success" > $SCRATCH/status.txt',
                        "working_dir": str(tmp_path),
                    },
                    "outputs": {
                        "status": {"type": "string", "path": "$SCRATCH/status.txt"}
                    },
                },
                {
                    "id": "step3",
                    "type": "BashCommand",
                    "inputs": {
                        "command": (
                            'echo "Count: ${step1.outputs.count}, '
                            'Status: ${step2.outputs.status}"'
                        ),
                        "working_dir": str(tmp_path),
                    },
                    "depends_on": ["step1", "step2"],
                },
            ],
        )

        executor = WorkflowExecutor()
        executor.load_workflow(workflow_def)
        result = await executor.execute_workflow("test-workflow", {})

        assert result.is_success

        # Verify the third block received both resolved variables
        step3_output = result.value["blocks"]["step3"]
        assert "Count: 10" in step3_output["stdout"]
        assert "Status: success" in step3_output["stdout"]

    @pytest.mark.asyncio
    async def test_reference_json_output_field(self, tmp_path: Path) -> None:
        """Test referencing specific field from JSON output."""
        workflow_def = WorkflowDefinition(
            name="test-workflow",
            description="Test JSON output field reference",
            blocks=[
                {
                    "id": "generate_json",
                    "type": "BashCommand",
                    "inputs": {
                        "command": (
                            'echo \'{"name": "test", "count": 42, "success": true}\' '
                            "> $SCRATCH/data.json"
                        ),
                        "working_dir": str(tmp_path),
                    },
                    "outputs": {
                        "data": {"type": "json", "path": "$SCRATCH/data.json"}
                    },
                },
                {
                    "id": "use_json",
                    "type": "BashCommand",
                    "inputs": {
                        "command": 'echo "JSON data: ${generate_json.outputs.data}"',
                        "working_dir": str(tmp_path),
                    },
                    "depends_on": ["generate_json"],
                },
            ],
        )

        executor = WorkflowExecutor()
        executor.load_workflow(workflow_def)
        result = await executor.execute_workflow("test-workflow", {})

        assert result.is_success

        # Verify JSON was resolved correctly
        use_json_output = result.value["blocks"]["use_json"]
        assert "JSON data:" in use_json_output["stdout"]


class TestMultiLevelPathResolution:
    """Test multi-level path resolution for custom outputs."""

    def test_resolve_three_level_path(self) -> None:
        """Test resolving block.outputs.field (3 levels)."""
        context = {
            "block1.outputs.count": 42,
            "block1.outputs.status": "success",
        }

        resolver = VariableResolver(context)

        # Resolve 3-level path
        result = resolver.resolve("Value: ${block1.outputs.count}")
        assert result == "Value: 42"

        result2 = resolver.resolve("Status: ${block1.outputs.status}")
        assert result2 == "Status: success"

    def test_resolve_four_level_path(self) -> None:
        """Test resolving deeper nested paths (4+ levels)."""
        context = {
            "block1.outputs.nested.field": "deep_value",
        }

        resolver = VariableResolver(context)

        # Resolve 4-level path
        result = resolver.resolve("Value: ${block1.outputs.nested.field}")
        assert result == "Value: deep_value"

    def test_resolve_multiple_levels_in_same_string(self) -> None:
        """Test resolving multiple multi-level paths in one string."""
        context = {
            "block1.outputs.count": 10,
            "block2.outputs.status": "done",
            "block3.outputs.result": "pass",
        }

        resolver = VariableResolver(context)

        result = resolver.resolve(
            "Count: ${block1.outputs.count}, "
            "Status: ${block2.outputs.status}, "
            "Result: ${block3.outputs.result}"
        )

        assert result == "Count: 10, Status: done, Result: pass"

    def test_missing_output_variable_error(self) -> None:
        """Test clear error when referencing missing output."""
        context = {
            "block1.outputs.count": 42,
        }

        resolver = VariableResolver(context)

        # Reference non-existent output
        with pytest.raises(VariableNotFoundError) as exc_info:
            resolver.resolve("Value: ${block1.outputs.missing}")

        error_msg = str(exc_info.value)
        assert "block1.outputs.missing" in error_msg
        assert "not found" in error_msg


class TestOutputComposition:
    """Test output composition patterns between blocks."""

    @pytest.mark.asyncio
    async def test_chain_outputs_through_multiple_blocks(self, tmp_path: Path) -> None:
        """Test chaining outputs through multiple sequential blocks."""
        workflow_def = WorkflowDefinition(
            name="test-workflow",
            description="Test output chaining",
            blocks=[
                {
                    "id": "step1",
                    "type": "BashCommand",
                    "inputs": {
                        "command": 'echo "5" > $SCRATCH/value.txt',
                        "working_dir": str(tmp_path),
                    },
                    "outputs": {
                        "value": {"type": "int", "path": "$SCRATCH/value.txt"}
                    },
                },
                {
                    "id": "step2",
                    "type": "BashCommand",
                    "inputs": {
                        "command": (
                            'expr ${step1.outputs.value} \\* 2 > $SCRATCH/doubled.txt'
                        ),
                        "working_dir": str(tmp_path),
                    },
                    "outputs": {
                        "doubled": {"type": "int", "path": "$SCRATCH/doubled.txt"}
                    },
                    "depends_on": ["step1"],
                },
                {
                    "id": "step3",
                    "type": "BashCommand",
                    "inputs": {
                        "command": (
                            'expr ${step2.outputs.doubled} + 3 '
                            "> $SCRATCH/final.txt"
                        ),
                        "working_dir": str(tmp_path),
                    },
                    "outputs": {
                        "final": {"type": "int", "path": "$SCRATCH/final.txt"}
                    },
                    "depends_on": ["step2"],
                },
            ],
        )

        executor = WorkflowExecutor()
        executor.load_workflow(workflow_def)
        result = await executor.execute_workflow("test-workflow", {})

        assert result.is_success

        # Verify chain: 5 -> 10 -> 13
        assert result.value["blocks"]["step1"]["outputs.value"] == 5
        assert result.value["blocks"]["step2"]["outputs.doubled"] == 10
        assert result.value["blocks"]["step3"]["outputs.final"] == 13

    @pytest.mark.asyncio
    async def test_parallel_blocks_with_outputs_merged(self, tmp_path: Path) -> None:
        """Test parallel blocks producing outputs that are merged in final block."""
        workflow_def = WorkflowDefinition(
            name="test-workflow",
            description="Test parallel output merging",
            blocks=[
                {
                    "id": "parallel_a",
                    "type": "BashCommand",
                    "inputs": {
                        "command": 'echo "10" > $SCRATCH/value_a.txt',
                        "working_dir": str(tmp_path),
                    },
                    "outputs": {
                        "value": {"type": "int", "path": "$SCRATCH/value_a.txt"}
                    },
                },
                {
                    "id": "parallel_b",
                    "type": "BashCommand",
                    "inputs": {
                        "command": 'echo "20" > $SCRATCH/value_b.txt',
                        "working_dir": str(tmp_path),
                    },
                    "outputs": {
                        "value": {"type": "int", "path": "$SCRATCH/value_b.txt"}
                    },
                },
                {
                    "id": "merge",
                    "type": "BashCommand",
                    "inputs": {
                        "command": (
                            'expr ${parallel_a.outputs.value} + ${parallel_b.outputs.value} '
                            "> $SCRATCH/sum.txt"
                        ),
                        "working_dir": str(tmp_path),
                    },
                    "outputs": {
                        "sum": {"type": "int", "path": "$SCRATCH/sum.txt"}
                    },
                    "depends_on": ["parallel_a", "parallel_b"],
                },
            ],
        )

        executor = WorkflowExecutor()
        executor.load_workflow(workflow_def)
        result = await executor.execute_workflow("test-workflow", {})

        assert result.is_success

        # Verify parallel outputs merged: 10 + 20 = 30
        assert result.value["blocks"]["parallel_a"]["outputs.value"] == 10
        assert result.value["blocks"]["parallel_b"]["outputs.value"] == 20
        assert result.value["blocks"]["merge"]["outputs.sum"] == 30

    @pytest.mark.asyncio
    async def test_conditional_execution_with_custom_outputs(self, tmp_path: Path) -> None:
        """Test conditional execution based on custom output values."""
        workflow_def = WorkflowDefinition(
            name="test-workflow",
            description="Test conditional with custom outputs",
            blocks=[
                {
                    "id": "check_value",
                    "type": "BashCommand",
                    "inputs": {
                        "command": 'echo "15" > $SCRATCH/value.txt',
                        "working_dir": str(tmp_path),
                    },
                    "outputs": {
                        "value": {"type": "int", "path": "$SCRATCH/value.txt"}
                    },
                },
                {
                    "id": "run_if_high",
                    "type": "BashCommand",
                    "inputs": {
                        "command": 'echo "value is high"',
                        "working_dir": str(tmp_path),
                    },
                    "condition": "${check_value.outputs.value} > 10",
                    "depends_on": ["check_value"],
                },
                {
                    "id": "run_if_low",
                    "type": "BashCommand",
                    "inputs": {
                        "command": 'echo "value is low"',
                        "working_dir": str(tmp_path),
                    },
                    "condition": "${check_value.outputs.value} <= 10",
                    "depends_on": ["check_value"],
                },
            ],
        )

        executor = WorkflowExecutor()
        executor.load_workflow(workflow_def)
        result = await executor.execute_workflow("test-workflow", {})

        assert result.is_success

        # Verify conditional execution: high should run, low should skip
        assert "run_if_high" in result.value["blocks"]
        assert "value is high" in result.value["blocks"]["run_if_high"]["stdout"]

        # Low condition should be skipped (not in blocks output)
        assert "run_if_low" not in result.value["blocks"]


class TestWorkflowLevelOutputs:
    """Test workflow-level outputs using custom block outputs."""

    @pytest.mark.asyncio
    async def test_workflow_output_from_custom_output(self, tmp_path: Path) -> None:
        """Test exposing custom block output as workflow output."""
        workflow_def = WorkflowDefinition(
            name="test-workflow",
            description="Test workflow-level outputs",
            blocks=[
                {
                    "id": "generate_result",
                    "type": "BashCommand",
                    "inputs": {
                        "command": (
                            'echo \'{"status": "success", "count": 42}\' '
                            "> $SCRATCH/result.json"
                        ),
                        "working_dir": str(tmp_path),
                    },
                    "outputs": {
                        "result": {"type": "json", "path": "$SCRATCH/result.json"}
                    },
                }
            ],
        )

        executor = WorkflowExecutor()
        executor.load_workflow(workflow_def)
        result = await executor.execute_workflow("test-workflow", {})

        assert result.is_success

        # Verify custom output is accessible
        block_output = result.value["blocks"]["generate_result"]
        assert "outputs.result" in block_output
        assert block_output["outputs.result"]["status"] == "success"
        assert block_output["outputs.result"]["count"] == 42


class TestEdgeCasesAndErrorHandling:
    """Test edge cases and error handling for custom outputs."""

    @pytest.mark.asyncio
    async def test_optional_output_with_conditional_block(self, tmp_path: Path) -> None:
        """Test optional output from conditionally executed block."""
        workflow_def = WorkflowDefinition(
            name="test-workflow",
            description="Test optional output with condition",
            blocks=[
                {
                    "id": "conditional_output",
                    "type": "BashCommand",
                    "inputs": {
                        "command": 'echo "data" > $SCRATCH/optional.txt',
                        "working_dir": str(tmp_path),
                    },
                    "outputs": {
                        "data": {
                            "type": "string",
                            "path": "$SCRATCH/optional.txt",
                            "required": False,
                        }
                    },
                    "condition": "False",  # Block won't execute
                },
            ],
        )

        executor = WorkflowExecutor()
        executor.load_workflow(workflow_def)
        result = await executor.execute_workflow("test-workflow", {})

        # Workflow should succeed even though block was skipped
        assert result.is_success

        # Block should not be in output (because it was skipped)
        assert "conditional_output" not in result.value["blocks"]

    @pytest.mark.asyncio
    async def test_empty_custom_outputs_dict(self, tmp_path: Path) -> None:
        """Test block with no custom outputs defined."""
        workflow_def = WorkflowDefinition(
            name="test-workflow",
            description="Test empty outputs",
            blocks=[
                {
                    "id": "no_outputs",
                    "type": "BashCommand",
                    "inputs": {
                        "command": 'echo "no custom outputs"',
                        "working_dir": str(tmp_path),
                    },
                    # No outputs defined
                }
            ],
        )

        executor = WorkflowExecutor()
        executor.load_workflow(workflow_def)
        result = await executor.execute_workflow("test-workflow", {})

        assert result.is_success

        # Standard outputs should exist
        block_output = result.value["blocks"]["no_outputs"]
        assert "exit_code" in block_output
        assert "stdout" in block_output

    @pytest.mark.asyncio
    async def test_mix_standard_and_custom_outputs_in_expression(
        self, tmp_path: Path
    ) -> None:
        """Test expression referencing both standard and custom outputs."""
        workflow_def = WorkflowDefinition(
            name="test-workflow",
            description="Test mixed output references",
            blocks=[
                {
                    "id": "step1",
                    "type": "BashCommand",
                    "inputs": {
                        "command": 'echo "42" > $SCRATCH/value.txt',
                        "working_dir": str(tmp_path),
                    },
                    "outputs": {
                        "custom_value": {
                            "type": "int",
                            "path": "$SCRATCH/value.txt",
                        }
                    },
                },
                {
                    "id": "step2",
                    "type": "BashCommand",
                    "inputs": {
                        "command": (
                            'echo "Exit: ${step1.exit_code}, '
                            'Value: ${step1.outputs.custom_value}"'
                        ),
                        "working_dir": str(tmp_path),
                    },
                    "depends_on": ["step1"],
                },
            ],
        )

        executor = WorkflowExecutor()
        executor.load_workflow(workflow_def)
        result = await executor.execute_workflow("test-workflow", {})

        assert result.is_success

        # Verify both standard and custom outputs resolved
        step2_output = result.value["blocks"]["step2"]
        assert "Exit: 0" in step2_output["stdout"]
        assert "Value: 42" in step2_output["stdout"]
