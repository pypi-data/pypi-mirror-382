"""
Workflow composition block for Phase 2.2 - ExecuteWorkflow.

This module implements the ExecuteWorkflow block, enabling workflows to call
other workflows as reusable components. This is a critical feature for building
complex workflows from simpler, composable pieces.

Key Features:
- Execute child workflows by name (from registry)
- Pass inputs to child workflow with variable resolution
- Receive outputs from child workflow (namespaced under block_id)
- Circular dependency detection (prevent infinite recursion)
- Clean context isolation (child only sees passed inputs)
- Error propagation from child to parent
- Execution time tracking
"""

import time
from typing import Any, cast

from pydantic import Field

from .block import BLOCK_REGISTRY, BlockInput, BlockOutput, WorkflowBlock
from .result import Result


class ExecuteWorkflowInput(BlockInput):
    """Input for ExecuteWorkflow block."""

    workflow: str = Field(description="Workflow name to execute (supports ${variables})")
    inputs: dict[str, Any] = Field(
        default_factory=dict,
        description="Inputs to pass to child workflow (supports ${variables})",
    )
    timeout_ms: int | None = Field(
        default=None, description="Optional timeout for child execution in milliseconds"
    )


class ExecuteWorkflowOutput(BlockOutput):
    """Output for ExecuteWorkflow block."""

    success: bool = Field(description="Whether child workflow executed successfully")
    workflow: str = Field(description="Child workflow name executed")
    outputs: dict[str, Any] = Field(description="Child workflow outputs (entire outputs dict)")
    execution_time_ms: float = Field(description="Child workflow execution time in milliseconds")
    total_blocks: int = Field(description="Number of blocks executed in child workflow")
    execution_waves: int = Field(description="Number of execution waves in child workflow")


class ExecuteWorkflow(WorkflowBlock):
    """
    Execute another workflow as a block within a parent workflow.

    This block enables workflow composition by allowing one workflow to call
    another workflow. The child workflow executes in a clean, isolated context
    with only the inputs explicitly passed to it.

    Features:
    - Circular dependency detection: Prevents A -> B -> A recursion
    - Context isolation: Child sees only passed inputs, not parent context
    - Output namespacing: Child outputs stored under block_id in parent context
    - Error propagation: Child workflow failures become parent block failures
    - Execution tracking: Time and statistics from child execution

    Example YAML:
        blocks:
          - id: run_tests
            type: ExecuteWorkflow
            inputs:
              workflow: "pytest-runner"
              inputs:
                test_path: "${workspace_path}/tests"
                verbose: true

          - id: deploy
            type: ExecuteWorkflow
            inputs:
              workflow: "deploy-to-staging"
              inputs:
                version: "${app_version}"
                test_results: "${run_tests.outputs.passed}"
            depends_on: [run_tests]

    Circular Dependency Detection:
        - Direct: A calls A (detected immediately)
        - Indirect: A -> B -> A (detected via workflow stack)
        - Deep: A -> B -> C -> A (detected via workflow stack)
        - Diamond (allowed): A calls B and C, both call D (not circular)
    """

    def input_model(self) -> type[BlockInput]:
        return ExecuteWorkflowInput

    def output_model(self) -> type[BlockOutput]:
        return ExecuteWorkflowOutput

    async def execute(self, context: dict[str, Any]) -> Result[BlockOutput]:
        """
        Execute a child workflow with clean context isolation.

        Process:
        1. Retrieve executor from context
        2. Check for circular dependencies
        3. Create clean child context with only passed inputs
        4. Execute child workflow
        5. Collect child outputs and statistics
        6. Return outputs namespaced under block_id

        Args:
            context: Parent workflow context (includes __executor__ and __workflow_stack__)

        Returns:
            Result.success(ExecuteWorkflowOutput) with child outputs and statistics
            Result.failure(error_message) if workflow not found, circular dependency,
            or child failure
        """
        inputs = cast(ExecuteWorkflowInput, self._validated_inputs)
        if inputs is None:
            return Result.failure("Inputs not validated")

        start_time = time.time()

        # 1. Get executor from context
        executor = context.get("__executor__")
        if executor is None:
            return Result.failure(
                "Executor not found in context - workflow composition not supported in this context"
            )

        # 2. Circular dependency detection
        workflow_stack = context.get("__workflow_stack__", [])
        workflow_name = inputs.workflow

        if workflow_name in workflow_stack:
            # Circular dependency detected
            cycle_path = " → ".join(workflow_stack) + f" → {workflow_name}"
            return Result.failure(f"Circular dependency detected: {cycle_path}")

        # 3. Check if workflow exists in registry
        if workflow_name not in executor.workflows:
            available = ", ".join(executor.workflows.keys())
            return Result.failure(
                f"Workflow '{workflow_name}' not found in registry. Available: {available}"
            )

        # 4. Create clean child context with only passed inputs (context isolation)
        # Child workflow should NOT see parent context - only explicitly passed inputs
        child_context = dict(inputs.inputs)  # Copy inputs to avoid mutation

        # Pass workflow stack for circular dependency detection
        child_context["__workflow_stack__"] = workflow_stack.copy()

        # 5. Execute child workflow
        try:
            child_result = await executor.execute_workflow(workflow_name, child_context)

            if not child_result.is_success:
                return Result.failure(
                    f"Child workflow '{workflow_name}' failed: {child_result.error}"
                )

            if child_result.value is None:
                return Result.failure(f"Child workflow '{workflow_name}' returned None value")

            child_outputs = child_result.value

        except Exception as e:
            return Result.failure(f"Child workflow '{workflow_name}' raised exception: {e}")

        # 6. Collect statistics and create output
        execution_time_ms = (time.time() - start_time) * 1000

        output = ExecuteWorkflowOutput(
            success=True,
            workflow=workflow_name,
            outputs=child_outputs,
            execution_time_ms=execution_time_ms,
            total_blocks=child_outputs.get("total_blocks", 0),
            execution_waves=child_outputs.get("execution_waves", 0),
        )

        return Result.success(output)


# Register block
BLOCK_REGISTRY.register("ExecuteWorkflow", ExecuteWorkflow)
