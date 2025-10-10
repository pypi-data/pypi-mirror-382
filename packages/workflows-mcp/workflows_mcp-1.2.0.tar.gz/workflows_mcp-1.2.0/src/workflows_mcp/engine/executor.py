"""
Async workflow executor for DAG-based workflows.

This module implements the two-phase execution model:
1. Planning Phase (sync): DAGResolver computes execution order and waves
2. Execution Phase (async): Execute blocks concurrently within waves

The executor orchestrates the complete workflow lifecycle from definition loading
through execution to result collection, integrating all core engine components.

Phase 2.0 enhancements:
- Variable resolution: ${var} and ${block_id.field} syntax
- Conditional execution: Skip blocks based on boolean expressions
- Context accumulation: Block outputs stored in dot notation
"""

import asyncio
import logging
import time
import uuid
from typing import Any

from .block import BLOCK_REGISTRY, BlockOutput, WorkflowBlock
from .checkpoint import CheckpointConfig, CheckpointState
from .checkpoint_store import CheckpointStore, InMemoryCheckpointStore
from .dag import DAGResolver
from .result import Result
from .serialization import deserialize_context, serialize_context
from .variables import ConditionEvaluator, InvalidConditionError, VariableResolver

logger = logging.getLogger(__name__)


class WorkflowDefinition:
    """
    Workflow definition loaded from YAML.

    Attributes:
        name: Workflow name
        description: Workflow description
        blocks: List of block definitions
        inputs: Input parameter declarations with defaults
    """

    def __init__(
        self,
        name: str,
        description: str,
        blocks: list[dict[str, Any]],
        inputs: dict[str, dict[str, Any]] | None = None,
    ):
        self.name = name
        self.description = description
        self.blocks = blocks
        self.inputs = inputs or {}

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "WorkflowDefinition":
        """Create workflow definition from dictionary."""
        return WorkflowDefinition(
            name=data["name"],
            description=data.get("description", ""),
            blocks=data.get("blocks", []),
            inputs=data.get("inputs", {}),
        )


class WorkflowExecutor:
    """
    Executes DAG-based workflows with async block execution.

    Execution Flow:
    1. Load workflow definition
    2. Instantiate blocks and validate
    3. Build dependency graph (Planning Phase - sync)
    4. Compute execution order and waves via DAGResolver
    5. Execute blocks wave-by-wave (Execution Phase - async)
    6. Collect and validate outputs

    Example:
        executor = WorkflowExecutor()
        result = await executor.execute_workflow("my-workflow", {"input": "value"})
    """

    def __init__(
        self,
        checkpoint_store: CheckpointStore | None = None,
        checkpoint_config: CheckpointConfig | None = None,
    ) -> None:
        """Initialize the workflow executor.

        Args:
            checkpoint_store: Optional checkpoint store for pause/resume functionality
            checkpoint_config: Optional checkpoint configuration
        """
        self.workflows: dict[str, WorkflowDefinition] = {}
        self.checkpoint_store = checkpoint_store or InMemoryCheckpointStore()
        self.checkpoint_config = checkpoint_config or CheckpointConfig()

    def load_workflow(self, workflow_def: WorkflowDefinition) -> None:
        """
        Load a workflow definition.

        Args:
            workflow_def: Workflow definition to load
        """
        self.workflows[workflow_def.name] = workflow_def

    async def execute_workflow(
        self, workflow_name: str, runtime_inputs: dict[str, Any] | None = None
    ) -> Result[dict[str, Any]]:
        """
        Execute a workflow by name.

        Args:
            workflow_name: Name of workflow to execute
            runtime_inputs: Runtime input overrides (merged into context)

        Returns:
            Result.success(outputs) with all block outputs
            Result.failure(error_message) on failure
        """
        start_time = time.time()

        # 1. Get workflow definition
        if workflow_name not in self.workflows:
            return Result.failure(f"Workflow not found: {workflow_name}")

        workflow_def = self.workflows[workflow_name]

        # 2. Initialize context with input defaults, then apply runtime overrides
        context: dict[str, Any] = {}

        # Apply defaults from workflow input declarations
        for input_name, input_decl in workflow_def.inputs.items():
            if input_decl.get("default") is not None:
                context[input_name] = input_decl["default"]

        # Override with runtime inputs
        if runtime_inputs:
            context.update(runtime_inputs)

        # Store original inputs for checkpointing
        original_inputs = runtime_inputs or {}

        # Add workflow metadata
        context["__workflow_name__"] = workflow_name
        context["__start_time__"] = start_time

        # Add executor reference for ExecuteWorkflow block (Phase 2.2 workflow composition)
        context["__executor__"] = self

        # Initialize or extend workflow execution stack for circular dependency detection
        if "__workflow_stack__" not in context:
            context["__workflow_stack__"] = []
        context["__workflow_stack__"].append(workflow_name)

        # Track completed blocks for checkpointing
        completed_blocks: list[str] = []

        # 3. Instantiate blocks
        blocks: dict[str, WorkflowBlock] = {}
        dependencies: dict[str, list[str]] = {}

        # Store block definitions for later processing (conditions, variable resolution)
        block_defs: dict[str, dict[str, Any]] = {}

        for block_def in workflow_def.blocks:
            block_id = block_def["id"]
            block_type = block_def["type"]
            block_depends_on = block_def.get("depends_on", [])

            # Store block definition for later
            block_defs[block_id] = block_def

            try:
                # Get block class from registry (validation only)
                BLOCK_REGISTRY.get(block_type)

                # Store dependencies for DAG resolution
                dependencies[block_id] = block_depends_on

            except Exception as e:
                return Result.failure(f"Failed to validate block '{block_id}': {e}")

        # 4. Planning Phase (synchronous): Compute execution order
        try:
            block_ids = list(block_defs.keys())
            resolver = DAGResolver(block_ids, dependencies)
            waves_result = resolver.get_execution_waves()

            if not waves_result.is_success:
                return Result.failure(f"DAG resolution failed: {waves_result.error}")

            execution_waves = waves_result.value

            # Type guard: execution_waves should never be None if is_success is True
            if execution_waves is None:
                return Result.failure("DAG resolution returned None for execution waves")

        except Exception as e:
            return Result.failure(f"DAG resolution failed: {e}")

        # 5. Execution Phase (async): Execute blocks wave-by-wave
        for wave_idx, wave in enumerate(execution_waves):
            # Process blocks in this wave
            tasks = []
            block_id_mapping = []
            wave_executed_blocks: list[str] = []

            for block_id in wave:
                block_def = block_defs[block_id]
                block_type = block_def["type"]
                block_condition = block_def.get("condition")

                # Check condition
                if block_condition:
                    try:
                        evaluator = ConditionEvaluator()
                        should_execute = evaluator.evaluate(block_condition, context)

                        if not should_execute:
                            # Skip this block - populate full output schema with defaults
                            try:
                                block_output_schema = block_def.get("outputs")
                                skipped_outputs = self._create_skipped_block_outputs(
                                    block_type, block_id, block_output_schema
                                )
                                # Store all output fields in context
                                for field_name, field_value in skipped_outputs.items():
                                    context[f"{block_id}.{field_name}"] = field_value

                                # Handle custom outputs (e.g., BashCommand with outputs attribute)
                                if block_output_schema is not None:
                                    for output_name, output_spec in block_output_schema.items():
                                        # Get type-specific default value
                                        output_type = output_spec.get("type", "string")
                                        default_value = self._get_type_default(output_type)
                                        context[f"{block_id}.outputs.{output_name}"] = default_value
                            except Exception as e:
                                return Result.failure(
                                    f"Block '{block_id}' failed to create skipped outputs: {e}"
                                )
                            continue

                    except (InvalidConditionError, Exception) as e:
                        return Result.failure(
                            f"Block '{block_id}' condition evaluation failed: {e}"
                        )

                # Resolve variables in block inputs
                try:
                    block_inputs = block_def.get("inputs", {})
                    variable_resolver = VariableResolver(context)
                    resolved_inputs = variable_resolver.resolve(block_inputs)
                except Exception as e:
                    return Result.failure(f"Block '{block_id}' variable resolution failed: {e}")

                # Instantiate block with resolved inputs
                try:
                    block_class = BLOCK_REGISTRY.get(block_type)
                    block_depends_on = block_def.get("depends_on", [])
                    block_output_schema = block_def.get("outputs")

                    # Pass outputs parameter if block supports it (e.g., BashCommand)
                    if block_output_schema is not None:
                        block = block_class(
                            id=block_id,
                            inputs=resolved_inputs,
                            depends_on=block_depends_on,
                            outputs=block_output_schema,
                        )
                    else:
                        block = block_class(
                            id=block_id, inputs=resolved_inputs, depends_on=block_depends_on
                        )
                    blocks[block_id] = block
                except Exception as e:
                    return Result.failure(f"Failed to instantiate block '{block_id}': {e}")

                # Add to execution tasks
                tasks.append(self._execute_block(block, context))
                block_id_mapping.append(block_id)
                wave_executed_blocks.append(block_id)

            # Execute all blocks in this wave concurrently (if any)
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)

                # Process results
                for block_id, result in zip(block_id_mapping, results):
                    if isinstance(result, Exception):
                        return Result.failure(f"Block '{block_id}' raised exception: {result}")

                    # Type guard: result should be Result[BlockOutput]
                    if not isinstance(result, Result):
                        return Result.failure(f"Block '{block_id}' returned invalid result type")

                    # Check for pause
                    if result.is_paused:
                        # Create pause checkpoint
                        checkpoint_id = await self._create_pause_checkpoint(
                            workflow_name=workflow_name,
                            runtime_inputs=original_inputs,
                            context=context,
                            completed_blocks=completed_blocks,
                            current_wave_index=wave_idx,
                            execution_waves=execution_waves,
                            block_defs=block_defs,
                            paused_block_id=block_id,
                            pause_data=result.pause_data,
                        )

                        # Update pause_data with checkpoint_id
                        if result.pause_data:
                            result.pause_data.checkpoint_id = checkpoint_id

                        # Return pause result to halt execution
                        return result

                    if not result.is_success:
                        return Result.failure(f"Block '{block_id}' failed: {result.error}")

                    # Type guard: result.value should never be None if is_success is True
                    if result.value is None:
                        return Result.failure(f"Block '{block_id}' returned None value")

                    # Store block output in context (dot notation)
                    output_dict = result.value.model_dump()
                    for field_name, field_value in output_dict.items():
                        # Special handling for custom_outputs - store in .outputs. namespace
                        if field_name == "custom_outputs" and isinstance(field_value, dict):
                            for output_name, output_value in field_value.items():
                                context[f"{block_id}.outputs.{output_name}"] = output_value
                        else:
                            # Regular outputs (exit_code, stdout, etc.)
                            context[f"{block_id}.{field_name}"] = field_value

            # Track completed blocks from this wave
            completed_blocks.extend(wave_executed_blocks)

            # Create checkpoint after wave completes (if enabled)
            if self.checkpoint_config.enabled and self.checkpoint_config.checkpoint_every_wave:
                checkpoint_result = await self._checkpoint_after_wave(
                    workflow_name=workflow_name,
                    runtime_inputs=original_inputs,
                    context=context,
                    completed_blocks=completed_blocks,
                    current_wave_index=wave_idx,
                    execution_waves=execution_waves,
                    block_defs=block_defs,
                )
                if not checkpoint_result.is_success:
                    logger.warning(
                        f"Failed to create checkpoint after wave {wave_idx}: "
                        f"{checkpoint_result.error}"
                    )
                else:
                    logger.debug(
                        f"Created checkpoint {checkpoint_result.value} after wave {wave_idx}"
                    )

        # 6. Collect outputs
        execution_time = time.time() - start_time

        # Cleanup workflow stack (Phase 2.2 - prevent stack pollution)
        if "__workflow_stack__" in context and context["__workflow_stack__"]:
            context["__workflow_stack__"].pop()

        # Reconstruct block outputs from dot notation context
        block_outputs: dict[str, dict[str, Any]] = {}
        for block_id in blocks.keys():
            block_outputs[block_id] = {}
            # Collect all fields for this block from context
            prefix = f"{block_id}."
            for key, value in context.items():
                if key.startswith(prefix):
                    field_name = key[len(prefix) :]
                    block_outputs[block_id][field_name] = value

        outputs = {
            "blocks": block_outputs,
            "execution_time_seconds": execution_time,
            "total_blocks": len(blocks),
            "execution_waves": len(execution_waves),
        }

        return Result.success(outputs)

    def _get_type_default(self, output_type: str) -> Any:
        """
        Get type-specific default value for custom outputs.

        Args:
            output_type: One of: string, int, float, bool, json

        Returns:
            Type-appropriate default value
        """
        type_defaults = {
            "string": "",
            "int": 0,
            "float": 0.0,
            "bool": False,
            "json": {},
        }
        return type_defaults.get(output_type, "")

    def _create_skipped_block_outputs(
        self, block_type: str, block_id: str, block_output_schema: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Create default outputs for a skipped conditional block.

        When a block is skipped due to a failed condition, we still need to populate
        its output fields in the context so that downstream blocks can reference them
        without causing variable resolution failures.

        This method inspects the block's output model and creates a dictionary with
        type-appropriate default values for each field.

        Args:
            block_type: The type name of the block (e.g., "BashCommand", "EchoBlock")
            block_id: The block's ID (for error messages)
            block_output_schema: Optional custom output schema (for blocks with outputs attribute)

        Returns:
            Dictionary mapping output field names to default values

        Raises:
            ValueError: If block type is unknown or output model cannot be instantiated
        """
        try:
            # Get block class from registry
            block_class = BLOCK_REGISTRY.get(block_type)

            # Create a temporary instance to access the output model
            # We need to bypass input validation since we only need the output schema
            # Use a direct instantiation that skips __init__ to avoid validation errors
            temp_block = object.__new__(block_class)
            output_model_class = temp_block.output_model()

            # Get model fields and their types
            model_fields = output_model_class.model_fields

            # Create defaults for each field based on type
            defaults: dict[str, Any] = {}
            for field_name, field_info in model_fields.items():
                field_type = field_info.annotation

                # Handle standard output fields with sensible defaults for skipped blocks
                if field_name == "skipped":
                    defaults[field_name] = True
                elif field_name == "success":
                    defaults[field_name] = False
                elif field_name == "exit_code":
                    defaults[field_name] = -1
                elif field_name == "execution_time_ms":
                    defaults[field_name] = 0.0
                # Type-based defaults
                elif field_type is str or "str" in str(field_type):
                    defaults[field_name] = ""
                elif field_type is int or "int" in str(field_type):
                    defaults[field_name] = 0
                elif field_type is float or "float" in str(field_type):
                    defaults[field_name] = 0.0
                elif field_type is bool or "bool" in str(field_type):
                    defaults[field_name] = False
                elif "dict" in str(field_type) or "Dict" in str(field_type):
                    defaults[field_name] = {}
                elif "list" in str(field_type) or "List" in str(field_type):
                    defaults[field_name] = []
                else:
                    # For any other types, use None (field might be Optional)
                    defaults[field_name] = None

            # Always mark as skipped
            defaults["skipped"] = True
            defaults["success"] = False

            return defaults

        except Exception as e:
            raise ValueError(
                f"Failed to create skipped outputs for block '{block_id}' "
                f"of type '{block_type}': {e}"
            )

    async def _execute_block(
        self, block: WorkflowBlock, context: dict[str, Any]
    ) -> Result[BlockOutput]:
        """
        Execute a single block.

        Args:
            block: WorkflowBlock instance to execute
            context: Shared workflow context

        Returns:
            Result with block output
        """
        try:
            result = await block.execute(context)
            return result
        except Exception as e:
            return Result.failure(f"Block execution exception: {e}")

    async def _checkpoint_after_wave(
        self,
        workflow_name: str,
        runtime_inputs: dict[str, Any],
        context: dict[str, Any],
        completed_blocks: list[str],
        current_wave_index: int,
        execution_waves: list[list[str]],
        block_defs: dict[str, dict[str, Any]],
    ) -> Result[str]:
        """
        Create a checkpoint after wave completion.

        Args:
            workflow_name: Name of workflow being executed
            runtime_inputs: Original runtime inputs
            context: Current execution context
            completed_blocks: List of completed block IDs
            current_wave_index: Index of wave that just completed
            execution_waves: All execution waves
            block_defs: Block definitions

        Returns:
            Result with checkpoint ID on success
        """
        try:
            # Generate checkpoint ID
            checkpoint_id = (
                f"chk_{workflow_name}_{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}"
            )

            # Serialize context (exclude internal fields except workflow stack)
            context_to_save = {
                k: v
                for k, v in context.items()
                if not k.startswith("__") or k == "__workflow_stack__"
            }
            serialized_context = serialize_context(context_to_save)

            # Extract workflow stack
            workflow_stack = context.get("__workflow_stack__", [])

            # Create checkpoint state
            checkpoint_state = CheckpointState(
                checkpoint_id=checkpoint_id,
                workflow_name=workflow_name,
                created_at=time.time(),
                runtime_inputs=runtime_inputs,
                context=serialized_context,
                completed_blocks=completed_blocks.copy(),
                current_wave_index=current_wave_index,
                execution_waves=execution_waves,
                block_definitions=block_defs,
                workflow_stack=workflow_stack.copy() if isinstance(workflow_stack, list) else [],
            )

            # Save checkpoint
            await self.checkpoint_store.save_checkpoint(checkpoint_state)

            logger.info(
                f"Created checkpoint '{checkpoint_id}' for workflow '{workflow_name}' "
                f"after wave {current_wave_index} ({len(completed_blocks)} blocks completed)"
            )

            return Result.success(checkpoint_id)

        except Exception as e:
            logger.error(f"Failed to create checkpoint for workflow '{workflow_name}': {e}")
            return Result.failure(f"Failed to create checkpoint: {e}")

    async def _create_pause_checkpoint(
        self,
        workflow_name: str,
        runtime_inputs: dict[str, Any],
        context: dict[str, Any],
        completed_blocks: list[str],
        current_wave_index: int,
        execution_waves: list[list[str]],
        block_defs: dict[str, dict[str, Any]],
        paused_block_id: str,
        pause_data: Any,  # PauseData from result.py
    ) -> str:
        """
        Create a checkpoint for paused execution.

        Args:
            workflow_name: Name of workflow being executed
            runtime_inputs: Original runtime inputs
            context: Current execution context
            completed_blocks: List of completed block IDs
            current_wave_index: Index of wave where pause occurred
            execution_waves: All execution waves
            block_defs: Block definitions
            paused_block_id: ID of block that triggered pause
            pause_data: PauseData from interactive block

        Returns:
            Checkpoint ID for resumption
        """
        try:
            # Generate checkpoint ID with pause prefix
            checkpoint_id = (
                f"pause_{workflow_name}_{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}"
            )

            # Serialize context
            context_to_save = {
                k: v
                for k, v in context.items()
                if not k.startswith("__") or k == "__workflow_stack__"
            }
            serialized_context = serialize_context(context_to_save)

            # Extract workflow stack
            workflow_stack = context.get("__workflow_stack__", [])

            # Import CheckpointState here to avoid circular import at module level
            from .checkpoint import CheckpointState

            # Create pause checkpoint state
            checkpoint_state = CheckpointState(
                checkpoint_id=checkpoint_id,
                workflow_name=workflow_name,
                created_at=time.time(),
                runtime_inputs=runtime_inputs,
                context=serialized_context,
                completed_blocks=completed_blocks.copy(),
                current_wave_index=current_wave_index,
                execution_waves=execution_waves,
                block_definitions=block_defs,
                workflow_stack=workflow_stack.copy() if isinstance(workflow_stack, list) else [],
                paused_block_id=paused_block_id,
                pause_prompt=pause_data.prompt if pause_data else None,
                pause_metadata=pause_data.pause_metadata if pause_data else None,
            )

            # Save checkpoint
            await self.checkpoint_store.save_checkpoint(checkpoint_state)

            logger.info(
                f"Created pause checkpoint '{checkpoint_id}' for workflow '{workflow_name}' "
                f"at block '{paused_block_id}' in wave {current_wave_index}"
            )

            return checkpoint_id

        except Exception as e:
            logger.error(f"Failed to create pause checkpoint for workflow '{workflow_name}': {e}")
            # Return empty string on error (caller should handle)
            return ""

    async def _resume_paused_block(
        self,
        checkpoint_state: CheckpointState,
        context: dict[str, Any],
        llm_response: str,
    ) -> Result[BlockOutput]:
        """
        Resume execution of a paused interactive block.

        Args:
            checkpoint_state: Checkpoint state containing pause information
            context: Restored execution context
            llm_response: LLM's response to the pause prompt

        Returns:
            Result from block resume (success, failure, or pause again)
        """
        try:
            paused_block_id = checkpoint_state.paused_block_id
            if not paused_block_id:
                return Result.failure("No paused block in checkpoint")

            block_def = checkpoint_state.block_definitions.get(paused_block_id)
            if not block_def:
                return Result.failure(f"Block definition not found for '{paused_block_id}'")

            block_type = block_def["type"]

            # Resolve variables in block inputs
            block_inputs = block_def.get("inputs", {})
            variable_resolver = VariableResolver(context)
            resolved_inputs = variable_resolver.resolve(block_inputs)

            # Instantiate block
            block_class = BLOCK_REGISTRY.get(block_type)
            block_depends_on = block_def.get("depends_on", [])
            block_output_schema = block_def.get("outputs")

            if block_output_schema is not None:
                block = block_class(
                    id=paused_block_id,
                    inputs=resolved_inputs,
                    depends_on=block_depends_on,
                    outputs=block_output_schema,
                )
            else:
                block = block_class(
                    id=paused_block_id,
                    inputs=resolved_inputs,
                    depends_on=block_depends_on,
                )

            # Check if it's an interactive block
            from .interactive import InteractiveBlock

            if not isinstance(block, InteractiveBlock):
                return Result.failure(
                    f"Block {paused_block_id} is not an InteractiveBlock - cannot resume"
                )

            # Resume block execution
            pause_metadata = checkpoint_state.pause_metadata or {}
            result = await block.resume(
                context=context,
                llm_response=llm_response,
                pause_metadata=pause_metadata,
            )

            result_status = (
                "paused again"
                if result.is_paused
                else "success"
                if result.is_success
                else "failure"
            )
            logger.info(f"Resumed paused block '{paused_block_id}' with result: {result_status}")

            return result

        except Exception as e:
            logger.error(f"Failed to resume paused block: {e}")
            return Result.failure(f"Failed to resume paused block: {e}")

    async def resume_workflow(
        self, checkpoint_id: str, llm_response: dict[str, Any] | str | None = None
    ) -> Result[dict[str, Any]]:
        """
        Resume workflow execution from a checkpoint.

        Args:
            checkpoint_id: ID of checkpoint to resume from
            llm_response: Optional LLM response for paused workflows (unused for now)

        Returns:
            Result with workflow outputs on success
        """
        try:
            logger.info(f"Resuming workflow from checkpoint '{checkpoint_id}'")

            # Load checkpoint
            checkpoint_state = await self.checkpoint_store.load_checkpoint(checkpoint_id)
            if checkpoint_state is None:
                logger.error(f"Checkpoint not found: {checkpoint_id}")
                return Result.failure(f"Checkpoint not found: {checkpoint_id}")

            # Check if workflow is loaded
            workflow_name = checkpoint_state.workflow_name
            if workflow_name not in self.workflows:
                logger.error(
                    f"Workflow '{workflow_name}' not loaded in executor. "
                    "Cannot resume from checkpoint."
                )
                return Result.failure(
                    f"Workflow not found or not loaded: {workflow_name}. "
                    "Please load the workflow definition before resuming."
                )

            logger.debug(
                f"Resuming workflow '{workflow_name}' from wave "
                f"{checkpoint_state.current_wave_index + 1} "
                f"({len(checkpoint_state.completed_blocks)} blocks already completed)"
            )

            # Deserialize context (executor reference is restored automatically)
            context = deserialize_context(checkpoint_state.context, self)

            # Restore internal fields
            context["__workflow_name__"] = workflow_name
            context["__workflow_stack__"] = checkpoint_state.workflow_stack.copy()

            # Rebuild execution waves (same as original execution)
            execution_waves = checkpoint_state.execution_waves
            block_defs = checkpoint_state.block_definitions
            completed_blocks = checkpoint_state.completed_blocks.copy()
            current_wave_index = checkpoint_state.current_wave_index

            # Handle paused block resume
            if checkpoint_state.paused_block_id:
                if not llm_response:
                    return Result.failure(
                        f"Checkpoint {checkpoint_id} is paused - llm_response required"
                    )

                # Convert llm_response to string if it's a dict
                llm_response_str = (
                    llm_response if isinstance(llm_response, str) else str(llm_response)
                )

                # Resume the paused block
                paused_block_id = checkpoint_state.paused_block_id
                result = await self._resume_paused_block(
                    checkpoint_state=checkpoint_state,
                    context=context,
                    llm_response=llm_response_str,
                )

                # Check if block paused again
                if result.is_paused:
                    # Create new pause checkpoint
                    new_checkpoint_id = await self._create_pause_checkpoint(
                        workflow_name=workflow_name,
                        runtime_inputs=checkpoint_state.runtime_inputs,
                        context=context,
                        completed_blocks=completed_blocks,
                        current_wave_index=current_wave_index,
                        execution_waves=execution_waves,
                        block_defs=block_defs,
                        paused_block_id=paused_block_id,
                        pause_data=result.pause_data,
                    )
                    # Update pause_data with new checkpoint_id
                    if result.pause_data:
                        result.pause_data.checkpoint_id = new_checkpoint_id
                    return result
                elif not result.is_success:
                    return result

                # Block completed - store output and add to completed blocks
                if result.value:
                    output_dict = result.value.model_dump()
                    for field_name, field_value in output_dict.items():
                        if field_name == "custom_outputs" and isinstance(field_value, dict):
                            for output_name, output_value in field_value.items():
                                context[f"{paused_block_id}.outputs.{output_name}"] = output_value
                        else:
                            context[f"{paused_block_id}.{field_name}"] = field_value

                # Mark paused block as completed
                completed_blocks.append(paused_block_id)

            # Continue execution from next wave
            start_time = time.time()
            blocks: dict[str, WorkflowBlock] = {}

            for wave_idx in range(current_wave_index + 1, len(execution_waves)):
                wave = execution_waves[wave_idx]
                tasks = []
                block_id_mapping = []
                wave_executed_blocks: list[str] = []

                for block_id in wave:
                    block_def = block_defs[block_id]
                    block_type = block_def["type"]
                    block_condition = block_def.get("condition")

                    # Check condition
                    if block_condition:
                        try:
                            evaluator = ConditionEvaluator()
                            should_execute = evaluator.evaluate(block_condition, context)

                            if not should_execute:
                                # Skip this block
                                try:
                                    block_output_schema = block_def.get("outputs")
                                    skipped_outputs = self._create_skipped_block_outputs(
                                        block_type, block_id, block_output_schema
                                    )
                                    for field_name, field_value in skipped_outputs.items():
                                        context[f"{block_id}.{field_name}"] = field_value

                                    if block_output_schema is not None:
                                        for output_name, output_spec in block_output_schema.items():
                                            output_type = output_spec.get("type", "string")
                                            default_value = self._get_type_default(output_type)
                                            context[f"{block_id}.outputs.{output_name}"] = (
                                                default_value
                                            )
                                except Exception as e:
                                    return Result.failure(
                                        f"Block '{block_id}' failed to create skipped outputs: {e}"
                                    )
                                continue

                        except (InvalidConditionError, Exception) as e:
                            return Result.failure(
                                f"Block '{block_id}' condition evaluation failed: {e}"
                            )

                    # Resolve variables in block inputs
                    try:
                        block_inputs = block_def.get("inputs", {})
                        variable_resolver = VariableResolver(context)
                        resolved_inputs = variable_resolver.resolve(block_inputs)
                    except Exception as e:
                        return Result.failure(
                            f"Block '{block_id}' variable resolution failed: {e}"
                        )

                    # Instantiate block
                    try:
                        block = self._instantiate_block(
                            block_type, block_id, resolved_inputs, block_def
                        )
                        blocks[block_id] = block
                    except Exception as e:
                        return Result.failure(f"Failed to instantiate block '{block_id}': {e}")

                    # Add to execution tasks
                    tasks.append(self._execute_block(block, context))
                    block_id_mapping.append(block_id)
                    wave_executed_blocks.append(block_id)

                # Execute all blocks in this wave concurrently (if any)
                if tasks:
                    results = await asyncio.gather(*tasks, return_exceptions=True)

                    # Process results
                    for block_id, result in zip(block_id_mapping, results):
                        if isinstance(result, Exception):
                            return Result.failure(f"Block '{block_id}' raised exception: {result}")

                        if not isinstance(result, Result):
                            return Result.failure(
                                f"Block '{block_id}' returned invalid result type"
                            )

                        if not result.is_success:
                            return Result.failure(f"Block '{block_id}' failed: {result.error}")

                        if result.value is None:
                            return Result.failure(f"Block '{block_id}' returned None value")

                        # Store block output in context
                        output_dict = result.value.model_dump()
                        for field_name, field_value in output_dict.items():
                            if field_name == "custom_outputs" and isinstance(field_value, dict):
                                for output_name, output_value in field_value.items():
                                    context[f"{block_id}.outputs.{output_name}"] = output_value
                            else:
                                context[f"{block_id}.{field_name}"] = field_value

                # Track completed blocks
                completed_blocks.extend(wave_executed_blocks)

                # Create checkpoint after wave (if enabled)
                if self.checkpoint_config.enabled and self.checkpoint_config.checkpoint_every_wave:
                    checkpoint_result = await self._checkpoint_after_wave(
                        workflow_name=workflow_name,
                        runtime_inputs=checkpoint_state.runtime_inputs,
                        context=context,
                        completed_blocks=completed_blocks,
                        current_wave_index=wave_idx,
                        execution_waves=execution_waves,
                        block_defs=block_defs,
                    )
                    if not checkpoint_result.is_success:
                        pass

            # Collect outputs
            execution_time = time.time() - start_time

            # Cleanup workflow stack
            if "__workflow_stack__" in context and context["__workflow_stack__"]:
                context["__workflow_stack__"].pop()

            # Reconstruct block outputs
            block_outputs: dict[str, dict[str, Any]] = {}
            for block_id in blocks.keys():
                block_outputs[block_id] = {}
                prefix = f"{block_id}."
                for key, value in context.items():
                    if key.startswith(prefix):
                        field_name = key[len(prefix) :]
                        block_outputs[block_id][field_name] = value

            outputs = {
                "blocks": block_outputs,
                "execution_time_seconds": execution_time,
                "total_blocks": len(blocks),
                "execution_waves": len(execution_waves) - (current_wave_index + 1),
                "resumed_from_checkpoint": checkpoint_id,
            }

            logger.info(
                f"Successfully resumed workflow '{workflow_name}' from checkpoint "
                f"'{checkpoint_id}' (executed {len(blocks)} remaining blocks)"
            )

            return Result.success(outputs)

        except Exception as e:
            logger.error(f"Failed to resume workflow from checkpoint '{checkpoint_id}': {e}")
            return Result.failure(f"Failed to resume workflow: {e}")

    def _instantiate_block(
        self,
        block_type: str,
        block_id: str,
        resolved_inputs: dict[str, Any],
        block_def: dict[str, Any],
    ) -> WorkflowBlock:
        """
        Instantiate a block with resolved inputs.

        Args:
            block_type: Type of block to instantiate
            block_id: Block ID
            resolved_inputs: Resolved input values
            block_def: Block definition dict

        Returns:
            Instantiated WorkflowBlock

        Raises:
            Exception if block cannot be instantiated
        """
        block_class = BLOCK_REGISTRY.get(block_type)
        block_depends_on = block_def.get("depends_on", [])
        block_output_schema = block_def.get("outputs")

        # Pass outputs parameter if block supports it
        if block_output_schema is not None:
            return block_class(
                id=block_id,
                inputs=resolved_inputs,
                depends_on=block_depends_on,
                outputs=block_output_schema,
            )
        else:
            return block_class(id=block_id, inputs=resolved_inputs, depends_on=block_depends_on)
