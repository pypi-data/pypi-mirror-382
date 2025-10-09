"""
Integration tests for WorkflowRegistry with real workflow files.

These tests demonstrate how the registry integrates with:
- Real YAML workflow files in examples/
- WorkflowExecutor for end-to-end workflow execution
- MCP tool interfaces
"""

from pathlib import Path

import pytest

from workflows_mcp.engine import (
    WorkflowExecutor,
    WorkflowRegistry,
)


@pytest.fixture
def registry_with_examples() -> WorkflowRegistry:
    """Create registry loaded with example workflows."""
    registry = WorkflowRegistry()
    examples_dir = Path(__file__).parent.parent / "examples"

    if examples_dir.exists():
        result = registry.load_from_directory(examples_dir)
        if not result.is_success:
            pytest.skip(f"Could not load examples: {result.error}")

    return registry


class TestRegistryIntegration:
    """Test registry integration with real workflow files."""

    def test_load_example_workflow(self, registry_with_examples: WorkflowRegistry) -> None:
        """Test loading the example-workflow.yaml file."""
        if len(registry_with_examples) == 0:
            pytest.skip("No example workflows found")

        # Check that example-workflow was loaded
        assert registry_with_examples.exists("example-workflow")

        # Get workflow definition
        workflow = registry_with_examples.get("example-workflow")
        assert workflow.name == "example-workflow"
        assert workflow.description == "Example workflow demonstrating YAML schema features"

    def test_example_workflow_metadata(self, registry_with_examples: WorkflowRegistry) -> None:
        """Test metadata extraction for example workflow."""
        if not registry_with_examples.exists("example-workflow"):
            pytest.skip("example-workflow not found")

        metadata = registry_with_examples.get_workflow_metadata("example-workflow")

        assert metadata["name"] == "example-workflow"
        assert "test" in metadata["tags"]
        assert metadata["version"] == "1.0"
        assert metadata["author"] == "Workflows MCP Team"
        assert "example" in metadata["tags"]

    def test_registry_to_executor_integration(
        self, registry_with_examples: WorkflowRegistry
    ) -> None:
        """Test loading workflow from registry into executor."""
        if not registry_with_examples.exists("example-workflow"):
            pytest.skip("example-workflow not found")

        # Get workflow from registry
        workflow = registry_with_examples.get("example-workflow")

        # Load into executor
        executor = WorkflowExecutor()
        executor.load_workflow(workflow)

        # Verify executor has the workflow
        assert "example-workflow" in executor.workflows

    @pytest.mark.asyncio
    async def test_end_to_end_workflow_execution(
        self, registry_with_examples: WorkflowRegistry
    ) -> None:
        """Test complete workflow execution from registry to results."""
        if not registry_with_examples.exists("example-workflow"):
            pytest.skip("example-workflow not found")

        # Get workflow from registry
        workflow = registry_with_examples.get("example-workflow")

        # Load into executor
        executor = WorkflowExecutor()
        executor.load_workflow(workflow)

        # Execute workflow with inputs
        result = await executor.execute_workflow(
            "example-workflow",
            runtime_inputs={"user_name": "Test User", "verbose": True},
        )

        # Verify execution succeeded
        assert result.is_success, f"Workflow execution failed: {result.error}"

        # Verify output structure
        output = result.value
        assert output is not None
        assert "blocks" in output
        assert "execution_time_seconds" in output
        assert output["total_blocks"] > 0


class TestMCPToolInterface:
    """Test interfaces designed for MCP tools."""

    def test_list_all_metadata_for_mcp(self, registry_with_examples: WorkflowRegistry) -> None:
        """Test MCP-friendly metadata listing."""
        if len(registry_with_examples) == 0:
            pytest.skip("No example workflows found")

        metadata_list = registry_with_examples.list_all_metadata()

        # Should be a list of dicts
        assert isinstance(metadata_list, list)
        assert len(metadata_list) > 0

        # Each metadata entry should have required fields
        for metadata in metadata_list:
            assert "name" in metadata
            assert "description" in metadata
            assert isinstance(metadata["name"], str)
            assert isinstance(metadata["description"], str)

    def test_workflow_discovery_pattern(self, registry_with_examples: WorkflowRegistry) -> None:
        """Test typical MCP tool workflow discovery pattern."""
        if len(registry_with_examples) == 0:
            pytest.skip("No example workflows found")

        # 1. List all available workflows
        all_workflows = registry_with_examples.list_names()
        assert len(all_workflows) > 0

        # 2. Get metadata for first workflow
        first_workflow_name = all_workflows[0]
        metadata = registry_with_examples.get_workflow_metadata(first_workflow_name)

        # 3. Verify metadata structure suitable for MCP tool response
        assert "name" in metadata
        assert "description" in metadata

        # Optional fields may or may not be present
        if "tags" in metadata:
            assert isinstance(metadata["tags"], list)
