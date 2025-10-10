# Checkpoint & Pause/Resume Architecture

## Overview

This document describes the comprehensive architecture for workflow pause/resume with automatic checkpointing in the MCP workflows system. The design enables:

1. **Automatic Checkpointing**: Save workflow state after every block execution
2. **Crash Recovery**: Resume workflows from last successful checkpoint
3. **Interactive Blocks**: Pause execution to request LLM input, then resume
4. **Nested Workflow Support**: Handle pauses in child workflows with propagation

## Design Principles

- **TDD (Test-Driven Development)**: Write tests FIRST, then implementation for every component
- **YAGNI**: Implement only what's needed now, design for future extensibility
- **KISS**: Start with in-memory storage, enable database migration later
- **Backward Compatibility**: Existing workflows work unchanged, checkpointing is transparent
- **Minimal Disruption**: Extend existing components rather than rewriting

## Test-Driven Development Approach

**Every phase follows strict TDD methodology**:

1. **RED**: Write failing tests that specify desired behavior
2. **GREEN**: Write minimal code to make tests pass
3. **REFACTOR**: Improve code while keeping tests green

**TDD Benefits for This Project**:
- ✅ Checkpoint serialization correctness guaranteed
- ✅ Resume logic verified before implementation complexity
- ✅ Edge cases caught early (corruption, expiration, nested pauses)
- ✅ Refactoring safety as system evolves
- ✅ Living documentation through test examples

**Test Coverage Requirements**:
- **Minimum**: 90% coverage for checkpoint code
- **Target**: 95%+ coverage
- **Edge cases**: Must have explicit tests
- **Integration**: End-to-end workflow tests required

## Core Components

### 1. Checkpoint Data Model

#### CheckpointState

Complete workflow state snapshot for persistence:

```python
from dataclasses import dataclass
from typing import Any

@dataclass
class CheckpointState:
    """Complete workflow state for checkpoint/restore."""

    # Identification
    checkpoint_id: str  # Format: "chk_<uuid>" or "pause_<uuid>"
    workflow_name: str
    created_at: float  # Unix timestamp
    schema_version: int = 1  # For future migrations

    # Execution state
    runtime_inputs: dict[str, Any]  # Original inputs to execute_workflow()
    context: dict[str, Any]  # Serializable context (filtered)
    completed_blocks: list[str]  # Block IDs completed so far
    current_wave_index: int  # Current wave in execution (0-indexed)
    execution_waves: list[list[str]]  # All waves from DAG resolution
    block_definitions: dict[str, dict[str, Any]]  # Block configs for reconstruction

    # Nested workflow support
    workflow_stack: list[str]  # For circular dependency detection
    parent_checkpoint_id: str | None = None  # Link to parent if nested

    # Pause-specific (optional)
    paused_block_id: str | None = None  # Block that triggered pause
    pause_prompt: str | None = None  # Prompt for LLM
    pause_metadata: dict[str, Any] | None = None  # Block-specific pause data
    child_checkpoint_id: str | None = None  # Child checkpoint if paused in ExecuteWorkflow

@dataclass
class CheckpointMetadata:
    """Lightweight checkpoint info for listing."""
    checkpoint_id: str
    workflow_name: str
    created_at: float
    is_paused: bool
    pause_prompt: str | None = None
```

#### PauseData

Data associated with paused execution:

```python
@dataclass
class PauseData:
    """Data for paused execution state."""
    checkpoint_id: str  # Token for resuming
    prompt: str  # Message to LLM requesting input
    expected_response_schema: dict[str, Any] | None = None  # Optional JSON schema
    pause_metadata: dict[str, Any] = field(default_factory=dict)  # Block-specific context
```

### 2. Extended Result Type

Extend the existing `Result[T]` monad with pause capability:

```python
@dataclass
class Result(Generic[T]):
    """Result type with pause support."""

    # Existing fields
    is_success: bool
    value: T | None = None
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    # NEW: Pause support
    is_paused: bool = False
    pause_data: PauseData | None = None

    @staticmethod
    def pause(
        prompt: str,
        checkpoint_id: str = "",
        expected_schema: dict[str, Any] | None = None,
        **metadata: Any
    ) -> "Result[T]":
        """Create a paused result that halts workflow execution."""
        return Result(
            is_success=False,  # Not a success (execution halts)
            is_paused=True,
            pause_data=PauseData(
                checkpoint_id=checkpoint_id,  # Filled by executor
                prompt=prompt,
                expected_response_schema=expected_schema,
                pause_metadata=metadata
            )
        )
```

**Three-State Model**:
- `is_success=True`: Block completed successfully
- `is_success=False, is_paused=False`: Block failed (error)
- `is_success=False, is_paused=True`: Block paused (waiting for LLM input)

### 3. CheckpointStore Interface

Abstract interface for checkpoint persistence with pluggable backends:

```python
from abc import ABC, abstractmethod
from typing import Protocol

class CheckpointStore(ABC):
    """Abstract interface for checkpoint persistence.

    Enables seamless migration from in-memory to database storage.
    """

    @abstractmethod
    async def save_checkpoint(self, state: CheckpointState) -> str:
        """Save checkpoint and return checkpoint_id.

        Args:
            state: Complete checkpoint state

        Returns:
            checkpoint_id for later retrieval
        """
        pass

    @abstractmethod
    async def load_checkpoint(self, checkpoint_id: str) -> CheckpointState | None:
        """Load checkpoint by ID.

        Args:
            checkpoint_id: Token from save_checkpoint()

        Returns:
            CheckpointState if found, None otherwise
        """
        pass

    @abstractmethod
    async def list_checkpoints(
        self,
        workflow_name: str | None = None
    ) -> list[CheckpointMetadata]:
        """List all checkpoints, optionally filtered by workflow.

        Args:
            workflow_name: Filter by workflow (None = all workflows)

        Returns:
            List of checkpoint metadata sorted by created_at descending
        """
        pass

    @abstractmethod
    async def delete_checkpoint(self, checkpoint_id: str) -> bool:
        """Delete checkpoint.

        Args:
            checkpoint_id: Token to delete

        Returns:
            True if checkpoint existed and was deleted, False otherwise
        """
        pass

    @abstractmethod
    async def cleanup_expired(self, max_age_seconds: int) -> int:
        """Remove checkpoints older than max_age_seconds.

        Args:
            max_age_seconds: Age threshold in seconds

        Returns:
            Number of checkpoints deleted
        """
        pass
```

#### InMemoryCheckpointStore

Initial implementation using in-memory dict:

```python
import asyncio
from collections import defaultdict
from typing import DefaultDict

class InMemoryCheckpointStore(CheckpointStore):
    """In-memory checkpoint storage for Phase 1.

    Thread-safe using asyncio.Lock.
    Suitable for single-process deployments and development.
    """

    def __init__(self):
        self._checkpoints: dict[str, CheckpointState] = {}
        self._lock = asyncio.Lock()

    async def save_checkpoint(self, state: CheckpointState) -> str:
        async with self._lock:
            self._checkpoints[state.checkpoint_id] = state
            return state.checkpoint_id

    async def load_checkpoint(self, checkpoint_id: str) -> CheckpointState | None:
        async with self._lock:
            return self._checkpoints.get(checkpoint_id)

    async def list_checkpoints(
        self,
        workflow_name: str | None = None
    ) -> list[CheckpointMetadata]:
        async with self._lock:
            checkpoints = self._checkpoints.values()

            if workflow_name:
                checkpoints = [c for c in checkpoints if c.workflow_name == workflow_name]

            # Convert to metadata and sort by created_at descending
            metadata_list = [
                CheckpointMetadata(
                    checkpoint_id=c.checkpoint_id,
                    workflow_name=c.workflow_name,
                    created_at=c.created_at,
                    is_paused=c.paused_block_id is not None,
                    pause_prompt=c.pause_prompt
                )
                for c in checkpoints
            ]

            metadata_list.sort(key=lambda m: m.created_at, reverse=True)
            return metadata_list

    async def delete_checkpoint(self, checkpoint_id: str) -> bool:
        async with self._lock:
            if checkpoint_id in self._checkpoints:
                del self._checkpoints[checkpoint_id]
                return True
            return False

    async def cleanup_expired(self, max_age_seconds: int) -> int:
        """Remove old checkpoints, but preserve paused checkpoints."""
        async with self._lock:
            now = time.time()
            expired = [
                cid for cid, state in self._checkpoints.items()
                if (now - state.created_at) > max_age_seconds
                and state.paused_block_id is None  # Don't expire paused checkpoints
            ]

            for cid in expired:
                del self._checkpoints[cid]

            return len(expired)

    async def trim_per_workflow(self, max_per_workflow: int) -> int:
        """Keep only last N checkpoints per workflow."""
        async with self._lock:
            by_workflow: DefaultDict[str, list[tuple[float, str]]] = defaultdict(list)

            for cid, state in self._checkpoints.items():
                by_workflow[state.workflow_name].append((state.created_at, cid))

            deleted_count = 0
            for workflow_name, checkpoints in by_workflow.items():
                # Sort by created_at descending
                checkpoints.sort(reverse=True)

                # Delete excess non-paused checkpoints
                for _, cid in checkpoints[max_per_workflow:]:
                    if self._checkpoints[cid].paused_block_id is None:
                        del self._checkpoints[cid]
                        deleted_count += 1

            return deleted_count
```

### 4. InteractiveBlock Base Class

New base class for blocks that can pause execution:

```python
from abc import abstractmethod
from typing import Any

class InteractiveBlock(WorkflowBlock):
    """Base class for blocks that can pause workflow execution.

    Interactive blocks extend WorkflowBlock with the ability to:
    1. Pause workflow execution mid-block
    2. Request input from the LLM with a prompt
    3. Resume execution with the LLM's response

    Subclasses must implement both execute() and resume() methods.

    Example use cases:
    - User confirmation dialogs
    - Parameter selection from options
    - Human-in-the-loop decision points
    - External approval workflows
    """

    @abstractmethod
    async def execute(self, context: dict[str, Any]) -> Result[BlockOutput]:
        """Initial execution - may return Result.pause().

        If this block needs LLM input, return Result.pause(prompt="...").
        Otherwise, return Result.success() or Result.failure() as normal.

        Args:
            context: Shared workflow context

        Returns:
            Result.success(), Result.failure(), or Result.pause()
        """
        pass

    @abstractmethod
    async def resume(
        self,
        context: dict[str, Any],
        llm_response: str,
        pause_metadata: dict[str, Any]
    ) -> Result[BlockOutput]:
        """Resume execution with LLM response.

        Called when workflow is resumed after a pause. The block should
        process the LLM's response and either:
        - Complete successfully (Result.success())
        - Fail (Result.failure())
        - Pause again (Result.pause()) for multi-step interactions

        Args:
            context: Restored workflow context
            llm_response: The LLM's response to the pause prompt
            pause_metadata: Metadata stored when block paused

        Returns:
            Result.success(), Result.failure(), or Result.pause()
        """
        pass
```

#### Example Interactive Blocks

```python
from pydantic import Field

# 1. Confirmation Block
class ConfirmOperationInput(BlockInput):
    message: str = Field(description="Confirmation message to display")
    operation: str = Field(description="Operation being confirmed")
    details: dict[str, Any] = Field(default_factory=dict, description="Additional context")

class ConfirmOperationOutput(BlockOutput):
    confirmed: bool = Field(description="Whether user confirmed")
    response: str = Field(description="Full LLM response")

class ConfirmOperation(InteractiveBlock):
    """Pause workflow and ask LLM to confirm an operation."""

    def input_model(self) -> type[BlockInput]:
        return ConfirmOperationInput

    def output_model(self) -> type[BlockOutput]:
        return ConfirmOperationOutput

    async def execute(self, context: dict[str, Any]) -> Result[BlockOutput]:
        inputs = cast(ConfirmOperationInput, self._validated_inputs)

        # Pause and ask for confirmation
        return Result.pause(
            prompt=f"Confirm operation: {inputs.message}\n\nRespond with 'yes' or 'no'",
            operation=inputs.operation,
            details=inputs.details
        )

    async def resume(
        self,
        context: dict[str, Any],
        llm_response: str,
        pause_metadata: dict[str, Any]
    ) -> Result[BlockOutput]:
        # Parse LLM response
        response_lower = llm_response.strip().lower()
        confirmed = response_lower in ["yes", "y", "true", "confirm", "approved"]

        return Result.success(ConfirmOperationOutput(
            confirmed=confirmed,
            response=llm_response
        ))

# 2. Choice Selection Block
class AskChoiceInput(BlockInput):
    question: str = Field(description="Question to ask")
    choices: list[str] = Field(description="Available choices")

class AskChoiceOutput(BlockOutput):
    choice: str = Field(description="Selected choice")
    choice_index: int = Field(description="Index of selected choice")

class AskChoice(InteractiveBlock):
    """Pause workflow and ask LLM to select from options."""

    def input_model(self) -> type[BlockInput]:
        return AskChoiceInput

    def output_model(self) -> type[BlockOutput]:
        return AskChoiceOutput

    async def execute(self, context: dict[str, Any]) -> Result[BlockOutput]:
        inputs = cast(AskChoiceInput, self._validated_inputs)

        choices_str = "\n".join(f"{i+1}. {c}" for i, c in enumerate(inputs.choices))
        prompt = f"{inputs.question}\n\nChoices:\n{choices_str}\n\nRespond with the number of your choice."

        return Result.pause(
            prompt=prompt,
            choices=inputs.choices
        )

    async def resume(
        self,
        context: dict[str, Any],
        llm_response: str,
        pause_metadata: dict[str, Any]
    ) -> Result[BlockOutput]:
        choices = pause_metadata["choices"]

        # Parse response (try as number first, then text match)
        try:
            choice_num = int(llm_response.strip())
            if 1 <= choice_num <= len(choices):
                choice = choices[choice_num - 1]
                return Result.success(AskChoiceOutput(
                    choice=choice,
                    choice_index=choice_num - 1
                ))
        except ValueError:
            # Try text match
            response_lower = llm_response.strip().lower()
            for i, choice in enumerate(choices):
                if choice.lower() in response_lower:
                    return Result.success(AskChoiceOutput(
                        choice=choice,
                        choice_index=i
                    ))

        return Result.failure(f"Invalid choice: {llm_response}")

# 3. Free-form Input Block
class GetInputInput(BlockInput):
    prompt: str = Field(description="Prompt for LLM")
    validation_pattern: str | None = Field(default=None, description="Regex pattern for validation")

class GetInputOutput(BlockOutput):
    input_value: str = Field(description="Input provided by LLM")

class GetInput(InteractiveBlock):
    """Pause workflow and get free-form input from LLM."""

    def input_model(self) -> type[BlockInput]:
        return GetInputInput

    def output_model(self) -> type[BlockOutput]:
        return GetInputOutput

    async def execute(self, context: dict[str, Any]) -> Result[BlockOutput]:
        inputs = cast(GetInputInput, self._validated_inputs)

        return Result.pause(
            prompt=inputs.prompt,
            validation_pattern=inputs.validation_pattern
        )

    async def resume(
        self,
        context: dict[str, Any],
        llm_response: str,
        pause_metadata: dict[str, Any]
    ) -> Result[BlockOutput]:
        validation_pattern = pause_metadata.get("validation_pattern")

        if validation_pattern:
            import re
            if not re.match(validation_pattern, llm_response):
                return Result.failure(
                    f"Input doesn't match pattern {validation_pattern}: {llm_response}"
                )

        return Result.success(GetInputOutput(input_value=llm_response))
```

### 5. Context Serialization

Utility functions for converting context to/from JSON:

```python
import json
from pathlib import Path
from datetime import datetime
from typing import Any
import logging

logger = logging.getLogger(__name__)

def serialize_context(context: dict[str, Any]) -> dict[str, Any]:
    """
    Extract JSON-serializable data from workflow context.

    Filtering rules:
    1. Skip __executor__ (transient, reconstructed on resume)
    2. Include __workflow_stack__ (needed for circular detection)
    3. Convert Path objects to strings
    4. Convert datetime to ISO format strings
    5. Skip any non-serializable values with warning

    Args:
        context: Full workflow context

    Returns:
        JSON-serializable context dictionary
    """
    serializable = {}

    for key, value in context.items():
        # Skip executor reference
        if key == "__executor__":
            continue

        # Try direct serialization first
        try:
            json.dumps(value)
            serializable[key] = value
            continue
        except (TypeError, ValueError):
            pass

        # Attempt type-specific conversions
        try:
            if isinstance(value, Path):
                serializable[key] = str(value)
            elif hasattr(value, 'isoformat'):  # datetime/date/time
                serializable[key] = value.isoformat()
            elif hasattr(value, '__dict__'):  # Custom objects
                # Try to serialize as dict
                serializable[key] = value.__dict__
            else:
                logger.warning(
                    f"Skipping non-serializable context key '{key}' of type {type(value).__name__}"
                )
        except Exception as e:
            logger.warning(f"Failed to serialize context key '{key}': {e}")

    return serializable

def deserialize_context(
    serialized: dict[str, Any],
    executor: "WorkflowExecutor"
) -> dict[str, Any]:
    """
    Reconstruct workflow context from serialized data.

    Adds back transient fields like __executor__.

    Args:
        serialized: JSON-deserialized context
        executor: Current executor instance

    Returns:
        Restored workflow context
    """
    context = serialized.copy()
    context["__executor__"] = executor
    return context

def validate_checkpoint_size(state: CheckpointState, max_size_mb: float = 10.0) -> bool:
    """
    Validate checkpoint size doesn't exceed limit.

    Args:
        state: Checkpoint state to validate
        max_size_mb: Maximum size in megabytes

    Returns:
        True if size is acceptable, False if too large
    """
    try:
        serialized = json.dumps(state.__dict__)
        size_mb = len(serialized.encode('utf-8')) / (1024 * 1024)

        if size_mb > max_size_mb:
            logger.warning(
                f"Checkpoint {state.checkpoint_id} size ({size_mb:.2f} MB) "
                f"exceeds limit ({max_size_mb} MB)"
            )
            return False

        return True
    except Exception as e:
        logger.error(f"Failed to validate checkpoint size: {e}")
        return False
```

## Executor Integration

### Modified WorkflowExecutor

Key changes to `src/workflows_mcp/engine/executor.py`:

```python
import uuid
import time
from typing import Any

class WorkflowExecutor:
    """Executes DAG-based workflows with automatic checkpointing."""

    def __init__(
        self,
        checkpoint_store: CheckpointStore | None = None,
        checkpoint_config: CheckpointConfig | None = None
    ):
        """Initialize executor with checkpoint support.

        Args:
            checkpoint_store: Checkpoint persistence backend (default: in-memory)
            checkpoint_config: Checkpoint behavior configuration
        """
        self.workflows: dict[str, WorkflowDefinition] = {}

        # Checkpoint support (NEW)
        self.checkpoint_store = checkpoint_store or InMemoryCheckpointStore()
        self.checkpoint_config = checkpoint_config or CheckpointConfig()

    async def execute_workflow(
        self,
        workflow_name: str,
        runtime_inputs: dict[str, Any] | None = None
    ) -> Result[dict[str, Any]]:
        """Execute a workflow by name with automatic checkpointing.

        This method now creates checkpoints after each block execution.
        If a block pauses, execution halts and returns pause information.

        Args:
            workflow_name: Name of workflow to execute
            runtime_inputs: Runtime input overrides

        Returns:
            Result.success(outputs) - Normal completion
            Result.failure(error) - Execution failure
            Result.pause(prompt, checkpoint_id) - Paused for LLM input
        """
        start_time = time.time()

        # ... (existing workflow loading and context setup) ...

        # Store original runtime inputs for checkpointing
        original_inputs = runtime_inputs.copy() if runtime_inputs else {}

        # ... (existing block instantiation and DAG resolution) ...

        # Execute blocks wave-by-wave with checkpointing
        completed_blocks: list[str] = []

        for wave_idx, wave in enumerate(execution_waves):
            # ... (existing wave execution logic) ...

            # Process wave results
            for block_id, result in zip(block_id_mapping, results):
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
                        pause_data=result.pause_data
                    )

                    # Update pause_data with checkpoint_id
                    result.pause_data.checkpoint_id = checkpoint_id

                    # Return pause result to halt execution
                    return result

                # ... (existing success/failure handling) ...

                # Store block output in context
                # ... (existing context update logic) ...

                # Track completed block
                completed_blocks.append(block_id)

            # Checkpoint after wave completion (if enabled)
            if self.checkpoint_config.enabled:
                await self._checkpoint_after_wave(
                    workflow_name=workflow_name,
                    runtime_inputs=original_inputs,
                    context=context,
                    completed_blocks=completed_blocks,
                    current_wave_index=wave_idx,
                    execution_waves=execution_waves,
                    block_defs=block_defs
                )

        # ... (existing output collection and return) ...

    async def resume_workflow(
        self,
        checkpoint_id: str,
        llm_response: str | None = None
    ) -> Result[dict[str, Any]]:
        """Resume workflow from checkpoint.

        Args:
            checkpoint_id: Checkpoint token to resume from
            llm_response: LLM response if resuming from pause

        Returns:
            Result with workflow outputs or error
        """
        # 1. Load checkpoint
        state = await self.checkpoint_store.load_checkpoint(checkpoint_id)
        if state is None:
            return Result.failure(
                f"Checkpoint not found: {checkpoint_id}. It may have expired."
            )

        # 2. Validate workflow is loaded
        if state.workflow_name not in self.workflows:
            return Result.failure(
                f"Workflow '{state.workflow_name}' from checkpoint not loaded in executor"
            )

        # 3. Restore context
        context = deserialize_context(state.context, self)
        context["__workflow_stack__"] = state.workflow_stack

        # 4. Handle paused block resume
        if state.paused_block_id:
            if not llm_response:
                return Result.failure(
                    f"Checkpoint {checkpoint_id} is paused - llm_response required"
                )

            # Resume paused block
            result = await self._resume_paused_block(
                state=state,
                context=context,
                llm_response=llm_response
            )

            if result.is_paused:
                # Block paused again - handled in _resume_paused_block
                return result
            elif not result.is_success:
                return result

            # Block completed - store output and continue
            output_dict = result.value.model_dump()
            for field_name, field_value in output_dict.items():
                if field_name == "custom_outputs" and isinstance(field_value, dict):
                    for output_name, output_value in field_value.items():
                        context[f"{state.paused_block_id}.outputs.{output_name}"] = output_value
                else:
                    context[f"{state.paused_block_id}.{field_name}"] = field_value

            # Add to completed blocks
            state.completed_blocks.append(state.paused_block_id)

        # 5. Continue execution from next wave
        return await self._continue_execution_from_wave(
            workflow_name=state.workflow_name,
            runtime_inputs=state.runtime_inputs,
            execution_waves=state.execution_waves,
            start_wave_index=state.current_wave_index + 1,
            context=context,
            block_defs=state.block_definitions,
            completed_blocks=state.completed_blocks
        )

    async def _checkpoint_after_wave(
        self,
        workflow_name: str,
        runtime_inputs: dict[str, Any],
        context: dict[str, Any],
        completed_blocks: list[str],
        current_wave_index: int,
        execution_waves: list[list[str]],
        block_defs: dict[str, dict[str, Any]]
    ) -> str:
        """Create checkpoint after wave completion."""

        checkpoint_id = f"chk_{uuid.uuid4().hex}"

        state = CheckpointState(
            checkpoint_id=checkpoint_id,
            workflow_name=workflow_name,
            runtime_inputs=runtime_inputs,
            context=serialize_context(context),
            completed_blocks=completed_blocks.copy(),
            current_wave_index=current_wave_index,
            execution_waves=execution_waves,
            block_definitions=block_defs,
            workflow_stack=context.get("__workflow_stack__", []),
            created_at=time.time()
        )

        # Validate size before saving
        if not validate_checkpoint_size(state):
            logger.warning(f"Skipping checkpoint - size exceeds limit")
            return ""

        await self.checkpoint_store.save_checkpoint(state)

        # Cleanup old checkpoints
        if self.checkpoint_config.auto_cleanup:
            await self.checkpoint_store.trim_per_workflow(
                self.checkpoint_config.max_per_workflow
            )

        return checkpoint_id

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
        pause_data: PauseData
    ) -> str:
        """Create checkpoint for paused execution."""

        checkpoint_id = f"pause_{uuid.uuid4().hex}"

        state = CheckpointState(
            checkpoint_id=checkpoint_id,
            workflow_name=workflow_name,
            runtime_inputs=runtime_inputs,
            context=serialize_context(context),
            completed_blocks=completed_blocks.copy(),
            current_wave_index=current_wave_index,
            execution_waves=execution_waves,
            block_definitions=block_defs,
            workflow_stack=context.get("__workflow_stack__", []),
            created_at=time.time(),
            paused_block_id=paused_block_id,
            pause_prompt=pause_data.prompt,
            pause_metadata=pause_data.pause_metadata
        )

        await self.checkpoint_store.save_checkpoint(state)
        return checkpoint_id

    async def _resume_paused_block(
        self,
        state: CheckpointState,
        context: dict[str, Any],
        llm_response: str
    ) -> Result[BlockOutput]:
        """Resume execution of a paused interactive block."""

        block_def = state.block_definitions[state.paused_block_id]
        block_id = state.paused_block_id

        # Instantiate block
        block = self._instantiate_block(block_def, block_id, context)

        # Check if it's an interactive block
        if not isinstance(block, InteractiveBlock):
            return Result.failure(
                f"Block {block_id} is not an InteractiveBlock - cannot resume"
            )

        # Resume block execution
        result = await block.resume(
            context=context,
            llm_response=llm_response,
            pause_metadata=state.pause_metadata or {}
        )

        # Check if block paused again
        if result.is_paused:
            # Create new pause checkpoint
            checkpoint_id = await self._create_pause_checkpoint(
                workflow_name=state.workflow_name,
                runtime_inputs=state.runtime_inputs,
                context=context,
                completed_blocks=state.completed_blocks,
                current_wave_index=state.current_wave_index,
                execution_waves=state.execution_waves,
                block_defs=state.block_definitions,
                paused_block_id=block_id,
                pause_data=result.pause_data
            )

            # Update pause_data with new checkpoint_id
            result.pause_data.checkpoint_id = checkpoint_id

        return result

    async def _continue_execution_from_wave(
        self,
        workflow_name: str,
        runtime_inputs: dict[str, Any],
        execution_waves: list[list[str]],
        start_wave_index: int,
        context: dict[str, Any],
        block_defs: dict[str, dict[str, Any]],
        completed_blocks: list[str]
    ) -> Result[dict[str, Any]]:
        """Continue workflow execution from a specific wave.

        This is the refactored wave execution logic extracted from execute_workflow
        to enable resumption from checkpoints.
        """

        for wave_idx in range(start_wave_index, len(execution_waves)):
            wave = execution_waves[wave_idx]

            # ... (same wave execution logic as execute_workflow) ...
            # Process blocks in wave, handle pauses, checkpoint after wave

            pass  # Implementation details same as execute_workflow

        # Collect outputs and return
        # ... (same as execute_workflow) ...

    def _instantiate_block(
        self,
        block_def: dict[str, Any],
        block_id: str,
        context: dict[str, Any]
    ) -> WorkflowBlock:
        """Instantiate a block from its definition with variable resolution."""

        block_type = block_def["type"]
        block_inputs = block_def.get("inputs", {})
        block_depends_on = block_def.get("depends_on", [])
        block_outputs = block_def.get("outputs")

        # Resolve variables in inputs
        variable_resolver = VariableResolver(context)
        resolved_inputs = variable_resolver.resolve(block_inputs)

        # Get block class and instantiate
        block_class = BLOCK_REGISTRY.get(block_type)

        if block_outputs is not None:
            block = block_class(
                id=block_id,
                inputs=resolved_inputs,
                depends_on=block_depends_on,
                outputs=block_outputs
            )
        else:
            block = block_class(
                id=block_id,
                inputs=resolved_inputs,
                depends_on=block_depends_on
            )

        return block
```

### CheckpointConfig

Configuration for checkpoint behavior:

```python
@dataclass
class CheckpointConfig:
    """Checkpoint behavior configuration."""

    # Feature toggle
    enabled: bool = True

    # Retention policy
    max_per_workflow: int = 10  # Keep last N checkpoints per workflow
    ttl_seconds: int = 86400  # 24 hours
    keep_paused: bool = True  # Don't auto-expire paused checkpoints

    # Cleanup
    auto_cleanup: bool = True  # Trim old checkpoints after each save
    cleanup_interval_seconds: int = 3600  # Background cleanup every hour

    # Size limits
    max_checkpoint_size_mb: float = 10.0
```

## MCP Tools

New MCP tools for checkpoint management in `src/workflows_mcp/server.py`:

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("workflows")

@mcp.tool()
async def resume_workflow(
    checkpoint_id: str,
    llm_response: str = ""
) -> dict:
    """
    Resume a paused or checkpointed workflow.

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
    executor = get_global_executor()

    result = await executor.resume_workflow(checkpoint_id, llm_response)

    if result.is_paused:
        # Paused again
        return {
            "status": "paused",
            "checkpoint_id": result.pause_data.checkpoint_id,
            "prompt": result.pause_data.prompt,
            "message": "Workflow paused again - use resume_workflow to continue"
        }
    elif result.is_success:
        return {
            "status": "success",
            "outputs": result.value,
            "message": "Workflow completed successfully"
        }
    else:
        return {
            "status": "failure",
            "error": result.error,
            "message": "Workflow execution failed"
        }

@mcp.tool()
async def list_checkpoints(workflow_name: str = "") -> dict:
    """
    List available workflow checkpoints.

    Shows all checkpoints, including both automatic checkpoints (for crash recovery)
    and pause checkpoints (for interactive workflows).

    Args:
        workflow_name: Filter by workflow name (empty = all workflows)

    Returns:
        List of checkpoint metadata with creation time, pause status, etc.

    Example:
        list_checkpoints(workflow_name="python-ci-pipeline")
    """
    executor = get_global_executor()

    checkpoints = await executor.checkpoint_store.list_checkpoints(
        workflow_name if workflow_name else None
    )

    return {
        "checkpoints": [
            {
                "checkpoint_id": c.checkpoint_id,
                "workflow": c.workflow_name,
                "created_at": c.created_at,
                "created_at_iso": datetime.fromtimestamp(c.created_at).isoformat(),
                "is_paused": c.is_paused,
                "pause_prompt": c.pause_prompt,
                "type": "pause" if c.is_paused else "automatic"
            }
            for c in checkpoints
        ],
        "total": len(checkpoints)
    }

@mcp.tool()
async def get_checkpoint_info(checkpoint_id: str) -> dict:
    """
    Get detailed information about a specific checkpoint.

    Useful for inspecting checkpoint state before resuming.

    Args:
        checkpoint_id: Checkpoint token

    Returns:
        Detailed checkpoint information
    """
    executor = get_global_executor()

    state = await executor.checkpoint_store.load_checkpoint(checkpoint_id)
    if state is None:
        return {
            "found": False,
            "error": f"Checkpoint {checkpoint_id} not found or expired"
        }

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
        "progress_percentage": (
            len(state.completed_blocks) /
            sum(len(wave) for wave in state.execution_waves) * 100
        )
    }

@mcp.tool()
async def delete_checkpoint(checkpoint_id: str) -> dict:
    """
    Delete a checkpoint.

    Useful for cleaning up paused workflows that are no longer needed.

    Args:
        checkpoint_id: Checkpoint token to delete

    Returns:
        Deletion status
    """
    executor = get_global_executor()

    deleted = await executor.checkpoint_store.delete_checkpoint(checkpoint_id)

    return {
        "deleted": deleted,
        "checkpoint_id": checkpoint_id,
        "message": (
            "Checkpoint deleted successfully" if deleted
            else "Checkpoint not found"
        )
    }
```

## Nested Workflow Support

### ExecuteWorkflow Pause Propagation

Modify `src/workflows_mcp/engine/blocks_workflow.py` to detect and propagate child pauses:

```python
class ExecuteWorkflow(WorkflowBlock):
    async def execute(self, context: dict[str, Any]) -> Result[BlockOutput]:
        # ... existing setup ...

        # Execute child workflow
        child_result = await executor.execute_workflow(workflow_name, child_context)

        # NEW: Detect child pause and propagate to parent
        if child_result.is_paused:
            return Result.pause(
                prompt=f"[Child workflow '{workflow_name}'] {child_result.pause_data.prompt}",
                child_checkpoint_id=child_result.pause_data.checkpoint_id,
                child_workflow=workflow_name,
                original_prompt=child_result.pause_data.prompt
            )

        # ... existing success/failure handling ...
```

### Resume Strategy for Nested Workflows

When resuming a pause in ExecuteWorkflow:

1. Detect `child_checkpoint_id` in pause_metadata
2. Resume child workflow first with llm_response
3. If child completes successfully, use child outputs and continue parent
4. If child pauses again, propagate new pause to parent
5. If child fails, propagate failure to parent

Implementation in `WorkflowExecutor._resume_paused_block()`:

```python
async def _resume_paused_block(
    self,
    state: CheckpointState,
    context: dict[str, Any],
    llm_response: str
) -> Result[BlockOutput]:
    """Resume paused block with special handling for ExecuteWorkflow."""

    block_def = state.block_definitions[state.paused_block_id]
    block_type = block_def["type"]

    # Special handling for ExecuteWorkflow pause
    if block_type == "ExecuteWorkflow" and "child_checkpoint_id" in state.pause_metadata:
        child_checkpoint_id = state.pause_metadata["child_checkpoint_id"]

        # Resume child workflow first
        child_result = await self.resume_workflow(child_checkpoint_id, llm_response)

        if child_result.is_paused:
            # Child paused again - propagate to parent
            return Result.pause(
                prompt=f"[Child workflow] {child_result.pause_data.prompt}",
                child_checkpoint_id=child_result.pause_data.checkpoint_id,
                child_workflow=state.pause_metadata["child_workflow"]
            )
        elif child_result.is_success:
            # Child completed - create ExecuteWorkflow output
            child_outputs = child_result.value

            output = ExecuteWorkflowOutput(
                success=True,
                workflow=state.pause_metadata["child_workflow"],
                outputs=child_outputs,
                execution_time_ms=child_outputs.get("execution_time_seconds", 0) * 1000,
                total_blocks=child_outputs.get("total_blocks", 0),
                execution_waves=child_outputs.get("execution_waves", 0)
            )

            return Result.success(output)
        else:
            # Child failed
            return Result.failure(
                f"Child workflow failed on resume: {child_result.error}"
            )

    # Standard interactive block resume
    block = self._instantiate_block(block_def, state.paused_block_id, context)

    if not isinstance(block, InteractiveBlock):
        return Result.failure(f"Block {state.paused_block_id} is not interactive")

    return await block.resume(context, llm_response, state.pause_metadata or {})
```

## Implementation Phases

### Phase 1: Core Checkpoint Infrastructure (Foundation)

**Goal**: Build checkpoint data model and storage without modifying executor

**TDD Workflow**:

#### Step 1: Write Tests FIRST (RED Phase)

Create test files with failing tests:

```python
# tests/test_checkpoint_serialization.py
import pytest
from workflows_mcp.engine.serialization import serialize_context, deserialize_context
from pathlib import Path
from datetime import datetime

def test_serialize_basic_types():
    """Ensure basic types serialize correctly."""
    context = {"str": "value", "int": 42, "bool": True, "list": [1, 2]}
    result = serialize_context(context)
    assert result == context

def test_serialize_path_objects():
    """Path objects must convert to strings."""
    context = {"path": Path("/tmp/test")}
    result = serialize_context(context)
    assert result["path"] == "/tmp/test"
    assert isinstance(result["path"], str)

def test_serialize_datetime_objects():
    """Datetime objects must convert to ISO format."""
    now = datetime.now()
    context = {"timestamp": now}
    result = serialize_context(context)
    assert result["timestamp"] == now.isoformat()

def test_skip_executor_reference():
    """Executor reference must be filtered out."""
    executor = object()
    context = {"__executor__": executor, "data": "value"}
    result = serialize_context(context)
    assert "__executor__" not in result
    assert result["data"] == "value"

def test_checkpoint_size_validation():
    """Large checkpoints must be rejected."""
    from workflows_mcp.engine.serialization import validate_checkpoint_size
    from workflows_mcp.engine.checkpoint import CheckpointState

    # Create oversized checkpoint
    large_context = {"data": "x" * 20_000_000}  # ~20MB
    state = CheckpointState(
        checkpoint_id="test",
        workflow_name="test",
        created_at=0.0,
        runtime_inputs={},
        context=large_context,
        completed_blocks=[],
        current_wave_index=0,
        execution_waves=[],
        block_definitions={},
        workflow_stack=[]
    )

    assert validate_checkpoint_size(state, max_size_mb=10.0) is False

# tests/test_checkpoint_store.py
import pytest
from workflows_mcp.engine.checkpoint_store import InMemoryCheckpointStore
from workflows_mcp.engine.checkpoint import CheckpointState

@pytest.mark.asyncio
async def test_save_and_load_checkpoint():
    """Checkpoint must be retrievable after save."""
    store = InMemoryCheckpointStore()
    state = CheckpointState(
        checkpoint_id="chk_123",
        workflow_name="test",
        created_at=1000.0,
        runtime_inputs={},
        context={},
        completed_blocks=[],
        current_wave_index=0,
        execution_waves=[],
        block_definitions={},
        workflow_stack=[]
    )

    checkpoint_id = await store.save_checkpoint(state)
    assert checkpoint_id == "chk_123"

    loaded = await store.load_checkpoint("chk_123")
    assert loaded is not None
    assert loaded.checkpoint_id == "chk_123"
    assert loaded.workflow_name == "test"

@pytest.mark.asyncio
async def test_list_checkpoints_filter_by_workflow():
    """List must filter by workflow name."""
    store = InMemoryCheckpointStore()

    # Save checkpoints for two workflows
    await store.save_checkpoint(create_test_checkpoint("chk_1", "workflow_a"))
    await store.save_checkpoint(create_test_checkpoint("chk_2", "workflow_a"))
    await store.save_checkpoint(create_test_checkpoint("chk_3", "workflow_b"))

    all_checkpoints = await store.list_checkpoints()
    assert len(all_checkpoints) == 3

    workflow_a = await store.list_checkpoints(workflow_name="workflow_a")
    assert len(workflow_a) == 2

@pytest.mark.asyncio
async def test_concurrent_access():
    """Store must handle concurrent save/load safely."""
    import asyncio
    store = InMemoryCheckpointStore()

    async def save_many(prefix: str, count: int):
        for i in range(count):
            state = create_test_checkpoint(f"{prefix}_{i}", "test")
            await store.save_checkpoint(state)

    # Run 3 concurrent tasks saving checkpoints
    await asyncio.gather(
        save_many("a", 10),
        save_many("b", 10),
        save_many("c", 10)
    )

    checkpoints = await store.list_checkpoints()
    assert len(checkpoints) == 30  # All saves successful
```

**Run tests**: `pytest tests/test_checkpoint_*.py` → All tests FAIL (expected)

#### Step 2: Implement MINIMAL Code (GREEN Phase)

Now create implementation files to make tests pass:

**Files to Create**:
- `src/workflows_mcp/engine/checkpoint.py` - Data models
- `src/workflows_mcp/engine/checkpoint_store.py` - Storage
- `src/workflows_mcp/engine/serialization.py` - Serialization

**Files to Modify**:
- `src/workflows_mcp/engine/result.py` - Add pause support

**Run tests**: `pytest tests/test_checkpoint_*.py` → All tests PASS

#### Step 3: Refactor (REFACTOR Phase)

- Extract common test fixtures
- Improve error messages
- Add type hints
- Document edge cases

**Run tests**: `pytest tests/test_checkpoint_*.py` → All tests still PASS

**Success Criteria**:
- ✅ All tests pass (100% success rate)
- ✅ Coverage ≥90% for checkpoint code
- ✅ Context round-trips correctly
- ✅ No changes to existing executor behavior

**Risk**: Minimal - isolated infrastructure

---

### Phase 2: Executor Integration (Automatic Checkpointing)

**Goal**: Make executor checkpoint after each wave, support restore

**TDD Workflow**:

#### Step 1: Write Tests FIRST (RED Phase)

```python
# tests/test_executor_checkpointing.py
import pytest
from workflows_mcp.engine.executor import WorkflowExecutor, WorkflowDefinition
from workflows_mcp.engine.checkpoint_store import InMemoryCheckpointStore

@pytest.mark.asyncio
async def test_automatic_checkpoint_after_each_wave():
    """Executor must create checkpoint after completing each wave."""
    store = InMemoryCheckpointStore()
    executor = WorkflowExecutor(checkpoint_store=store)

    # Load workflow with 3 blocks in 2 waves
    workflow_def = create_test_workflow_with_waves()
    executor.load_workflow(workflow_def)

    result = await executor.execute_workflow("test-workflow", {})
    assert result.is_success

    # Check checkpoints created
    checkpoints = await store.list_checkpoints()
    assert len(checkpoints) >= 2  # At least 2 checkpoints (one per wave)

@pytest.mark.asyncio
async def test_checkpoint_contains_correct_state():
    """Checkpoint must contain all necessary state for resume."""
    store = InMemoryCheckpointStore()
    executor = WorkflowExecutor(checkpoint_store=store)

    workflow_def = create_test_workflow()
    executor.load_workflow(workflow_def)

    await executor.execute_workflow("test-workflow", {"input": "value"})

    checkpoints = await store.list_checkpoints()
    assert len(checkpoints) > 0

    checkpoint = checkpoints[0]
    state = await store.load_checkpoint(checkpoint.checkpoint_id)

    # Verify state completeness
    assert state.workflow_name == "test-workflow"
    assert state.runtime_inputs == {"input": "value"}
    assert isinstance(state.context, dict)
    assert isinstance(state.completed_blocks, list)
    assert isinstance(state.execution_waves, list)

@pytest.mark.asyncio
async def test_resume_from_checkpoint_continues_execution():
    """Resume must continue from last completed wave."""
    store = InMemoryCheckpointStore()
    executor = WorkflowExecutor(checkpoint_store=store)

    # Workflow: block1 (wave 0) → block2 (wave 1) → block3 (wave 2)
    workflow_def = create_sequential_workflow()
    executor.load_workflow(workflow_def)

    # Execute first wave, then simulate crash
    # (Implementation will pause after wave 1)

    # For testing, manually create a checkpoint mid-execution
    checkpoint_id = "test_chk_123"
    # ... setup checkpoint state ...

    # Resume should complete remaining waves
    result = await executor.resume_workflow(checkpoint_id)
    assert result.is_success

@pytest.mark.asyncio
async def test_resume_restores_context_correctly():
    """Context must be fully restored including block outputs."""
    store = InMemoryCheckpointStore()
    executor = WorkflowExecutor(checkpoint_store=store)

    # Create checkpoint with specific context
    checkpoint_id = await create_test_checkpoint_with_context(
        store,
        context={"block1.output": "value1", "var": "data"}
    )

    # Resume and verify context
    # (Test implementation will verify context restoration)
    result = await executor.resume_workflow(checkpoint_id)
    assert result.is_success

@pytest.mark.asyncio
async def test_resume_with_missing_checkpoint():
    """Resume with invalid checkpoint must return clear error."""
    executor = WorkflowExecutor(checkpoint_store=InMemoryCheckpointStore())

    result = await executor.resume_workflow("nonexistent_checkpoint")
    assert not result.is_success
    assert "not found" in result.error.lower()
```

**Run tests**: `pytest tests/test_executor_checkpointing.py` → All tests FAIL (expected)

#### Step 2: Implement MINIMAL Code (GREEN Phase)

Modify `src/workflows_mcp/engine/executor.py`:

- Add `checkpoint_store` and `checkpoint_config` to `__init__`
- Add `_checkpoint_after_wave()` method
- Add `resume_workflow()` method
- Add `_continue_execution_from_wave()` method
- Modify `execute_workflow()` to checkpoint after waves

**Run tests**: `pytest tests/test_executor_checkpointing.py` → All tests PASS

#### Step 3: Refactor (REFACTOR Phase)

- Extract checkpoint creation logic
- Add comprehensive error handling
- Optimize checkpoint storage
- Add logging

**Run tests**: `pytest tests/test_executor_checkpointing.py` → All tests still PASS

**Success Criteria**:
- ✅ All tests pass
- ✅ Checkpoints created automatically
- ✅ Resume works correctly
- ✅ Context restored properly
- ✅ Existing workflows unchanged
- ✅ Performance regression <5%

**Risk**: Medium - modifies core executor, but changes are additive

---

### Phase 3: Interactive Block Support (Pause/Resume)

**Goal**: Enable blocks to pause and resume with LLM input

**Files to Create**:
- `src/workflows_mcp/engine/interactive.py`
  - InteractiveBlock abstract base class
  - Documentation and examples

- `src/workflows_mcp/engine/blocks_interactive.py`
  - ConfirmOperation block
  - AskChoice block
  - GetInput block
  - Register blocks in BLOCK_REGISTRY

**Files to Modify**:
- `src/workflows_mcp/engine/executor.py`
  - Modify wave execution to detect `result.is_paused`
  - Call `_create_pause_checkpoint()` on pause
  - Return pause result immediately (halt execution)
  - Enhance `_resume_paused_block()` to handle InteractiveBlock

- `src/workflows_mcp/engine/blocks_workflow.py`
  - Modify `ExecuteWorkflow.execute()` to detect child pauses
  - Propagate pause to parent with metadata

**Testing**:
```python
# tests/test_interactive_blocks.py
def test_confirm_operation_pause_and_resume()
def test_ask_choice_valid_selection()
def test_ask_choice_invalid_selection()
def test_get_input_with_validation()
def test_interactive_block_multi_pause()

# tests/test_pause_resume_integration.py
def test_workflow_pause_and_resume_end_to_end()
def test_nested_workflow_pause_propagation()
def test_pause_checkpoint_persists_until_resume()
def test_resume_with_incorrect_response()
def test_multi_level_nested_pause()
```

**Success Criteria**:
- Interactive blocks can pause execution
- LLM can resume with response
- Nested workflow pauses propagate correctly
- Multi-pause scenarios work
- Pause checkpoints persist until deleted

**Risk**: Medium - new execution path, but well-isolated

---

### Phase 4: MCP Tools (LLM Interface) ✅ COMPLETE

**Goal**: Expose checkpoint management to Claude via MCP tools

**Status**: ✅ Implemented and tested (all 482 tests pass)

**Files Modified**:
- ✅ `src/workflows_mcp/server.py`
  - Added `@mcp.tool() resume_workflow(checkpoint_id, llm_response)` - Resume paused/checkpointed workflows
  - Added `@mcp.tool() list_checkpoints(workflow_name?)` - List all checkpoints with pause status
  - Added `@mcp.tool() get_checkpoint_info(checkpoint_id)` - Get detailed checkpoint information with progress %
  - Added `@mcp.tool() delete_checkpoint(checkpoint_id)` - Delete checkpoints for cleanup

**Testing**: ✅ Comprehensive test suite added
```python
# tests/test_mcp_checkpoint_tools.py - 12 tests, all passing
test_resume_workflow_tool_with_checkpoint()       # Resume from automatic checkpoint
test_resume_workflow_tool_with_pause()            # Resume paused workflow with response
test_resume_workflow_tool_missing_checkpoint()    # Handle missing checkpoint gracefully
test_list_checkpoints_tool_all()                  # List all checkpoints
test_list_checkpoints_tool_filtered()             # Filter by workflow name
test_list_checkpoints_shows_pause_status()        # Show pause vs automatic checkpoints
test_get_checkpoint_info_tool()                   # Get detailed checkpoint info
test_get_checkpoint_info_not_found()              # Handle missing checkpoint
test_get_checkpoint_info_shows_progress()         # Calculate execution progress %
test_delete_checkpoint_tool()                     # Delete checkpoint successfully
test_delete_checkpoint_not_found()                # Handle missing checkpoint deletion
test_tools_handle_no_executor_gracefully()        # Graceful degradation
```

**Implementation Highlights**:
- No Pydantic models needed - FastMCP auto-generates schemas from type hints
- Tools return dicts (JSON-serializable) for direct MCP protocol compatibility
- Comprehensive error handling with clear status messages
- ISO timestamps for JSON-friendly date handling
- Progress percentage calculation for execution monitoring
- Graceful handling of missing executor (defensive programming)

**Success Criteria**: ✅ All met
- ✅ All tools callable via MCP protocol
- ✅ Type-safe with mypy validation
- ✅ Claude can successfully resume workflows
- ✅ Checkpoint listing shows correct metadata (pause status, timestamps, progress)
- ✅ No regressions - all 482 tests pass
- ✅ 86% code coverage maintained

**Risk Assessment**: Low - new tools are additive and don't modify existing functionality

---

### Phase 5: Testing & Documentation

**Goal**: Comprehensive testing and migration guide

**Files to Create**:
- `tests/test_checkpoint_edge_cases.py`
  - Test checkpoint corruption handling
  - Test invalid resume scenarios
  - Test checkpoint size limits
  - Test concurrent checkpoint access

- `tests/test_pause_resume_scenarios.py`
  - Test wave-level pause
  - Test block failure after resume
  - Test conditional skip after resume
  - Test nested pause timeout

- `docs/CHECKPOINT_ARCHITECTURE.md` (this file)

- `docs/DATABASE_MIGRATION.md`
  - SQLite schema
  - Migration steps
  - Example SQLiteCheckpointStore implementation

- `examples/workflows/interactive-approval.yaml`
  - Example workflow with confirmation blocks
  - Demonstrates pause/resume pattern

- `examples/workflows/multi-step-questionnaire.yaml`
  - Multiple interactive blocks in sequence
  - Shows progressive data collection

**Documentation Sections**:
1. How automatic checkpointing works
2. Creating custom interactive blocks
3. Using resume_workflow tool
4. Checkpoint cleanup and expiration
5. Database migration guide (SQLite)
6. Troubleshooting guide
7. Performance considerations

**Success Criteria**:
- 95%+ test coverage for checkpoint code
- All edge cases tested
- Documentation complete and accurate
- Example workflows demonstrate features
- Database migration path documented

**Risk**: None - documentation and comprehensive testing

---

## Database Migration Path

### Future: SQLiteCheckpointStore

For production deployments, migrate to SQLite:

```python
import sqlite3
import json
from typing import Any

class SQLiteCheckpointStore(CheckpointStore):
    """SQLite-backed checkpoint storage for production."""

    def __init__(self, db_path: str = "checkpoints.db"):
        self.db_path = db_path
        self._init_schema()

    def _init_schema(self):
        """Create checkpoints table."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS checkpoints (
                    checkpoint_id TEXT PRIMARY KEY,
                    workflow_name TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    is_paused BOOLEAN NOT NULL,
                    checkpoint_data TEXT NOT NULL,
                    INDEX idx_workflow_name (workflow_name),
                    INDEX idx_created_at (created_at),
                    INDEX idx_is_paused (is_paused)
                )
            """)

    async def save_checkpoint(self, state: CheckpointState) -> str:
        """Save checkpoint to SQLite."""
        checkpoint_data = json.dumps({
            "runtime_inputs": state.runtime_inputs,
            "context": state.context,
            "completed_blocks": state.completed_blocks,
            "current_wave_index": state.current_wave_index,
            "execution_waves": state.execution_waves,
            "block_definitions": state.block_definitions,
            "workflow_stack": state.workflow_stack,
            "parent_checkpoint_id": state.parent_checkpoint_id,
            "paused_block_id": state.paused_block_id,
            "pause_prompt": state.pause_prompt,
            "pause_metadata": state.pause_metadata,
            "child_checkpoint_id": state.child_checkpoint_id,
            "schema_version": state.schema_version
        })

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO checkpoints
                (checkpoint_id, workflow_name, created_at, is_paused, checkpoint_data)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    state.checkpoint_id,
                    state.workflow_name,
                    state.created_at,
                    state.paused_block_id is not None,
                    checkpoint_data
                )
            )

        return state.checkpoint_id

    async def load_checkpoint(self, checkpoint_id: str) -> CheckpointState | None:
        """Load checkpoint from SQLite."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM checkpoints WHERE checkpoint_id = ?",
                (checkpoint_id,)
            )
            row = cursor.fetchone()

        if row is None:
            return None

        data = json.loads(row["checkpoint_data"])

        return CheckpointState(
            checkpoint_id=row["checkpoint_id"],
            workflow_name=row["workflow_name"],
            created_at=row["created_at"],
            **data
        )

    # ... implement remaining CheckpointStore methods ...
```

### Migration Steps

1. Install SQLite support: `uv add aiosqlite`
2. Implement SQLiteCheckpointStore (above)
3. Add configuration option to choose backend:
   ```python
   checkpoint_store = (
       SQLiteCheckpointStore("checkpoints.db")
       if config.use_sqlite
       else InMemoryCheckpointStore()
   )
   ```
4. Optional: Migration tool to export in-memory checkpoints to SQLite

## Error Handling

### Error Messages

```python
CHECKPOINT_ERRORS = {
    "not_found": (
        "Checkpoint {checkpoint_id} not found. It may have expired or been deleted."
    ),
    "corrupted": (
        "Checkpoint {checkpoint_id} is corrupted or uses an incompatible schema version."
    ),
    "expired": (
        "Checkpoint {checkpoint_id} expired at {expired_at}. "
        "Automatic checkpoints expire after {ttl} seconds."
    ),
    "invalid_resume": (
        "Cannot resume checkpoint {checkpoint_id}: {reason}"
    ),
    "workflow_not_found": (
        "Workflow '{workflow}' from checkpoint is not loaded in executor. "
        "Available workflows: {available}"
    ),
    "missing_llm_response": (
        "Checkpoint {checkpoint_id} is paused - llm_response parameter required. "
        "Pause prompt: {prompt}"
    ),
    "not_interactive": (
        "Block {block_id} is not an InteractiveBlock - cannot resume with llm_response"
    ),
    "size_limit": (
        "Checkpoint size ({size_mb} MB) exceeds limit ({limit_mb} MB). "
        "Consider reducing context size or increasing limit."
    ),
    "schema_version": (
        "Checkpoint schema version {checkpoint_version} is incompatible with "
        "current version {current_version}. Migration required."
    )
}
```

### Edge Case Handling

1. **Checkpoint Corruption**: Catch JSON decode errors, return clear error
2. **Invalid Resume**: Validate checkpoint type matches resume operation
3. **Multiple Resume**: Option to delete checkpoint after successful resume
4. **Wave-Level Pause**: Only checkpoint completed blocks in wave
5. **Block Failure After Resume**: Normal failure handling, preserve checkpoints
6. **Large Context**: Warn when approaching size limit, fail gracefully if exceeded
7. **Schema Migration**: Version field enables gradual migration

## Performance Considerations

### Checkpoint Overhead

- **In-Memory**: Negligible (~1ms per checkpoint)
- **SQLite**: Moderate (~10-50ms per checkpoint)
- **Network DB**: Higher (100-500ms per checkpoint)

### Mitigation Strategies

1. **Batch Checkpoints**: Checkpoint per wave, not per block (default)
2. **Async I/O**: All checkpoint operations are async
3. **Background Cleanup**: Cleanup runs in separate asyncio task
4. **Size Limits**: Prevent unbounded checkpoint growth
5. **Selective Checkpointing**: Config option to disable for simple workflows

### Scalability

- **In-Memory**: Limited by server RAM (~10k checkpoints typical)
- **SQLite**: Limited by disk (~100k-1M checkpoints)
- **PostgreSQL**: Limited by database capacity (~millions of checkpoints)

## Security Considerations

### Checkpoint Data Privacy

- Checkpoints may contain sensitive data (credentials, API keys, user data)
- Recommendation: Encrypt checkpoint storage at rest
- Never log checkpoint contents in plain text
- Implement checkpoint access controls in multi-tenant scenarios

### Serialization Safety

- Only serialize JSON-compatible data (no code execution)
- Validate checkpoint schema version before deserialize
- Sanitize context before serialization (filter sensitive keys)

## Usage Examples

### Example 1: Interactive Approval Workflow

Complete workflow demonstrating human-in-the-loop approval:

**Workflow Definition** (`templates/examples/interactive-approval.yaml`):
```yaml
name: interactive-approval
description: Deployment workflow with human approval checkpoint

blocks:
  # Run tests automatically
  - id: run_tests
    type: BashCommand
    inputs:
      command: "pytest tests/ -v"
      check_returncode: false

  # Pause for approval if tests pass
  - id: confirm_deploy
    type: ConfirmOperation
    inputs:
      message: "Tests passed. Deploy ${project} to ${environment}?"
      operation: "deploy_${project}_to_${environment}"
    depends_on: [run_tests]
    condition: "${run_tests.exit_code} == 0"

  # Deploy only if approved
  - id: deploy
    type: BashCommand
    inputs:
      command: "kubectl apply -f k8s/"
    depends_on: [confirm_deploy]
    condition: "${confirm_deploy.confirmed} == true"

outputs:
  deployment_approved: "${confirm_deploy.confirmed}"
  deployment_success: "${deploy.success}"
```

**Usage Flow**:
```python
# Step 1: Execute workflow
result = await executor.execute_workflow("interactive-approval", {
    "project": "my-app",
    "environment": "production"
})

# Result:
# {
#   "status": "paused",
#   "checkpoint_id": "pause_abc123",
#   "prompt": "Confirm operation: Tests passed. Deploy my-app to production?\n\nRespond with 'yes' or 'no'"
# }

# Step 2: Resume with approval
result = await executor.resume_workflow("pause_abc123", "yes")

# Result:
# {
#   "status": "success",
#   "outputs": {
#     "deployment_approved": true,
#     "deployment_success": true
#   }
# }
```

---

### Example 2: Multi-Step Configuration Wizard

Multiple interactive questions in sequence:

**Workflow Definition** (`templates/examples/multi-step-questionnaire.yaml`):
```yaml
name: config-wizard
description: Interactive project setup wizard

blocks:
  # Question 1: Confirmation
  - id: confirm_start
    type: ConfirmOperation
    inputs:
      message: "Start interactive project setup wizard?"
      operation: "start_wizard"

  # Question 2: Select type
  - id: select_type
    type: AskChoice
    inputs:
      question: "What type of project?"
      choices: ["python-fastapi", "node-express", "react-app"]
    depends_on: [confirm_start]
    condition: "${confirm_start.confirmed} == true"

  # Question 3: Get name
  - id: get_name
    type: GetInput
    inputs:
      prompt: "Enter project name (lowercase, hyphens):"
      validation_pattern: "^[a-z0-9-]+$"
    depends_on: [select_type]

  # Question 4: Final confirmation
  - id: confirm_creation
    type: ConfirmOperation
    inputs:
      message: |
        Create project with these settings?
        - Name: ${get_name.input_value}
        - Type: ${select_type.choice}
      operation: "create_project"
    depends_on: [get_name]

  # Create project if confirmed
  - id: create_project
    type: BashCommand
    inputs:
      command: "mkdir -p ${get_name.input_value}"
    depends_on: [confirm_creation]
    condition: "${confirm_creation.confirmed} == true"

outputs:
  project_name: "${get_name.input_value}"
  project_type: "${select_type.choice}"
  project_created: "${create_project.success}"
```

**Usage Flow** (4 pause/resume cycles):
```python
# Pause 1: Confirm start
r1 = await execute_workflow("config-wizard")
# → checkpoint_id="pause_001", prompt="Start wizard?"

r2 = await resume_workflow("pause_001", "yes")
# → checkpoint_id="pause_002", prompt="What type of project?"

# Pause 2: Select type
r3 = await resume_workflow("pause_002", "1")  # python-fastapi
# → checkpoint_id="pause_003", prompt="Enter project name:"

# Pause 3: Get name
r4 = await resume_workflow("pause_003", "my-awesome-app")
# → checkpoint_id="pause_004", prompt="Create project...?"

# Pause 4: Final confirmation
r5 = await resume_workflow("pause_004", "yes")
# → status="success", outputs={...}
```

**Key Features Demonstrated**:
- Multiple pause/resume cycles in one workflow
- Context accumulation across pauses (can reference previous answers)
- Conditional execution based on responses
- Input validation (regex pattern for project name)
- Different interactive block types

---

### Example 3: Crash Recovery

Workflow with automatic checkpoints for crash recovery:

```python
# Execute long-running workflow
executor = WorkflowExecutor(
    checkpoint_store=SQLiteCheckpointStore("checkpoints.db"),
    checkpoint_config=CheckpointConfig(enabled=True)
)

# Start workflow
result = await executor.execute_workflow("long-pipeline", {})

# Simulate crash after wave 5 completes
# (checkpoint created automatically after each wave)

# Later: List available checkpoints
checkpoints = await executor.checkpoint_store.list_checkpoints("long-pipeline")
# → [
#     CheckpointMetadata(checkpoint_id="chk_wave5", created_at=..., is_paused=False),
#     CheckpointMetadata(checkpoint_id="chk_wave4", created_at=..., is_paused=False),
#     ...
# ]

# Resume from latest checkpoint
latest = checkpoints[0]
result = await executor.resume_workflow(latest.checkpoint_id)
# → Continues from wave 6
```

---

### Example 4: MCP Tool Integration

Using interactive workflows via MCP tools:

```javascript
// Start workflow via MCP
const result1 = await mcp.call("execute_workflow", {
  workflow: "interactive-approval",
  inputs: { project: "my-app", environment: "production" }
});

if (result1.status === "paused") {
  console.log("Workflow paused");
  console.log("Checkpoint:", result1.checkpoint_id);
  console.log("Prompt:", result1.prompt);

  // Later: Resume workflow
  const result2 = await mcp.call("resume_workflow", {
    checkpoint_id: result1.checkpoint_id,
    llm_response: "yes"
  });

  if (result2.status === "success") {
    console.log("Deployment approved and completed");
    console.log("Outputs:", result2.outputs);
  }
}

// List all paused workflows
const paused = await mcp.call("list_checkpoints", {});
paused.checkpoints
  .filter(c => c.is_paused)
  .forEach(c => {
    console.log(`${c.checkpoint_id}: ${c.pause_prompt}`);
  });

// Get detailed checkpoint info
const info = await mcp.call("get_checkpoint_info", {
  checkpoint_id: "pause_abc123"
});
console.log(`Progress: ${info.progress_percentage}%`);
console.log(`Paused at: ${info.paused_block_id}`);

// Clean up completed checkpoint
await mcp.call("delete_checkpoint", {
  checkpoint_id: "pause_abc123"
});
```

---

## Production Deployment

### Recommended Checkpoint Store: SQLite

For production deployments, use SQLite instead of in-memory storage:

**Why SQLite for Production?**
- ✅ Checkpoints survive server restarts
- ✅ Full crash recovery capability
- ✅ Persistent storage for long-running workflows
- ✅ Handles 100k-1M checkpoints
- ✅ File-based: no additional infrastructure
- ✅ ACID transactions for data safety
- ✅ Built into Python standard library

**Configuration**:
```python
from workflows_mcp.engine.checkpoint_store_sqlite import SQLiteCheckpointStore
from workflows_mcp.engine.checkpoint import CheckpointConfig

# Production checkpoint store
checkpoint_store = SQLiteCheckpointStore(
    db_path="/var/lib/workflows/checkpoints.db"
)

# Production checkpoint configuration
checkpoint_config = CheckpointConfig(
    enabled=True,
    max_per_workflow=50,        # Keep more checkpoints in production
    ttl_seconds=7 * 86400,       # 7 days retention
    keep_paused=True,            # Never auto-delete paused checkpoints
    auto_cleanup=True,
    cleanup_interval_seconds=3600,  # Cleanup every hour
    max_checkpoint_size_mb=10.0
)

executor = WorkflowExecutor(
    checkpoint_store=checkpoint_store,
    checkpoint_config=checkpoint_config
)
```

---

### Checkpoint Cleanup Strategies

#### 1. Automatic Cleanup (Recommended)

Enable automatic cleanup to prevent unbounded storage growth:

```python
checkpoint_config = CheckpointConfig(
    auto_cleanup=True,                   # Enable automatic cleanup
    max_per_workflow=50,                 # Keep last 50 checkpoints per workflow
    ttl_seconds=7 * 86400,               # Delete checkpoints older than 7 days
    keep_paused=True,                    # NEVER delete paused checkpoints
    cleanup_interval_seconds=3600        # Run cleanup every hour
)
```

**Cleanup Rules**:
- Automatic checkpoints (`chk_*`) expire after `ttl_seconds`
- Paused checkpoints (`pause_*`) never expire automatically
- Per-workflow limit enforced (oldest deleted first)
- Cleanup runs in background asyncio task

---

#### 2. Background Cleanup Task

Run periodic cleanup in background process:

```python
import asyncio
from workflows_mcp.engine.checkpoint_store_sqlite import SQLiteCheckpointStore

async def cleanup_task(store: SQLiteCheckpointStore, config: CheckpointConfig):
    """Background checkpoint cleanup task."""
    while True:
        await asyncio.sleep(config.cleanup_interval_seconds)

        # Cleanup expired automatic checkpoints
        expired_count = await store.cleanup_expired(config.ttl_seconds)
        print(f"Cleaned up {expired_count} expired checkpoints")

        # Trim excess per-workflow checkpoints
        trimmed_count = await store.trim_per_workflow(config.max_per_workflow)
        print(f"Trimmed {trimmed_count} excess checkpoints")

        # Vacuum database for performance
        await store.vacuum()
        print("Database vacuumed")

# Start cleanup task
asyncio.create_task(cleanup_task(checkpoint_store, checkpoint_config))
```

---

#### 3. Manual Cleanup

Explicit cleanup via MCP tools or API:

```python
# Delete specific checkpoint
await executor.checkpoint_store.delete_checkpoint("pause_abc123")

# Cleanup old checkpoints (older than 24 hours)
deleted = await executor.checkpoint_store.cleanup_expired(86400)

# Trim to last 20 per workflow
trimmed = await executor.checkpoint_store.trim_per_workflow(20)

# Vacuum database (reclaim space)
if isinstance(executor.checkpoint_store, SQLiteCheckpointStore):
    await executor.checkpoint_store.vacuum()
```

---

### Monitoring and Observability

#### Checkpoint Storage Metrics

Track checkpoint storage health:

```python
async def get_checkpoint_metrics(store: CheckpointStore) -> dict:
    """Collect checkpoint storage metrics."""
    checkpoints = await store.list_checkpoints()

    total = len(checkpoints)
    paused = sum(1 for c in checkpoints if c.is_paused)
    automatic = total - paused

    # Workflow distribution
    by_workflow = {}
    for c in checkpoints:
        by_workflow[c.workflow_name] = by_workflow.get(c.workflow_name, 0) + 1

    # Age distribution
    import time
    now = time.time()
    age_buckets = {
        "< 1 hour": 0,
        "1-24 hours": 0,
        "1-7 days": 0,
        "> 7 days": 0
    }

    for c in checkpoints:
        age_seconds = now - c.created_at
        if age_seconds < 3600:
            age_buckets["< 1 hour"] += 1
        elif age_seconds < 86400:
            age_buckets["1-24 hours"] += 1
        elif age_seconds < 7 * 86400:
            age_buckets["1-7 days"] += 1
        else:
            age_buckets["> 7 days"] += 1

    return {
        "total_checkpoints": total,
        "paused_checkpoints": paused,
        "automatic_checkpoints": automatic,
        "workflows": by_workflow,
        "age_distribution": age_buckets,
        "oldest_checkpoint_age_seconds": now - min(c.created_at for c in checkpoints) if checkpoints else 0,
        "newest_checkpoint_age_seconds": now - max(c.created_at for c in checkpoints) if checkpoints else 0,
    }
```

---

#### Database Size Monitoring (SQLite)

Monitor database file size and growth:

```python
import os

def get_db_metrics(db_path: str) -> dict:
    """Get database file metrics."""
    stat = os.stat(db_path)

    return {
        "size_bytes": stat.st_size,
        "size_mb": stat.st_size / (1024 * 1024),
        "last_modified": stat.st_mtime,
    }

# Monitor database size
metrics = get_db_metrics("/var/lib/workflows/checkpoints.db")
if metrics["size_mb"] > 1000:  # > 1GB
    print("WARNING: Database size exceeds 1GB - consider cleanup")
```

---

#### Performance Monitoring

Track checkpoint operation latency:

```python
import time

async def monitored_checkpoint_save(
    store: CheckpointStore,
    state: CheckpointState
) -> tuple[str, float]:
    """Save checkpoint with latency monitoring."""
    start = time.time()
    checkpoint_id = await store.save_checkpoint(state)
    latency = time.time() - start

    # Log slow operations
    if latency > 0.1:  # > 100ms
        print(f"SLOW CHECKPOINT SAVE: {latency*1000:.2f}ms for {checkpoint_id}")

    return checkpoint_id, latency

async def monitored_checkpoint_load(
    store: CheckpointStore,
    checkpoint_id: str
) -> tuple[CheckpointState | None, float]:
    """Load checkpoint with latency monitoring."""
    start = time.time()
    state = await store.load_checkpoint(checkpoint_id)
    latency = time.time() - start

    if latency > 0.1:  # > 100ms
        print(f"SLOW CHECKPOINT LOAD: {latency*1000:.2f}ms for {checkpoint_id}")

    return state, latency
```

---

### Best Practices for Production

#### 1. Database Location

Choose appropriate storage location:

**Good**:
```python
# Persistent storage with backup
checkpoint_store = SQLiteCheckpointStore("/var/lib/workflows/checkpoints.db")

# Or use application data directory
import platformdirs
app_dir = platformdirs.user_data_dir("workflows-mcp", "MCP")
checkpoint_store = SQLiteCheckpointStore(f"{app_dir}/checkpoints.db")
```

**Bad**:
```python
# Temporary directory (may be cleaned)
checkpoint_store = SQLiteCheckpointStore("/tmp/checkpoints.db")

# Working directory (may not be persistent)
checkpoint_store = SQLiteCheckpointStore("./checkpoints.db")
```

---

#### 2. Backup Strategy

Regular checkpoint database backups:

```bash
#!/bin/bash
# Backup checkpoint database daily

DB_PATH="/var/lib/workflows/checkpoints.db"
BACKUP_DIR="/var/backups/workflows"
DATE=$(date +%Y%m%d)

# Create backup
sqlite3 "$DB_PATH" ".backup '$BACKUP_DIR/checkpoints-$DATE.db'"

# Keep last 7 days
find "$BACKUP_DIR" -name "checkpoints-*.db" -mtime +7 -delete
```

---

#### 3. Resource Limits

Set appropriate resource limits:

```python
checkpoint_config = CheckpointConfig(
    enabled=True,
    max_per_workflow=50,                 # Limit per-workflow storage
    ttl_seconds=7 * 86400,               # 7 days retention
    max_checkpoint_size_mb=10.0,         # Prevent huge checkpoints
    auto_cleanup=True,
    cleanup_interval_seconds=3600
)
```

---

#### 4. Error Handling

Handle checkpoint failures gracefully:

```python
try:
    checkpoint_id = await executor.checkpoint_store.save_checkpoint(state)
except Exception as e:
    # Log error but don't fail workflow
    print(f"WARNING: Failed to save checkpoint: {e}")
    # Workflow continues without checkpoint

try:
    state = await executor.checkpoint_store.load_checkpoint(checkpoint_id)
    if state is None:
        print(f"ERROR: Checkpoint {checkpoint_id} not found")
        # Handle missing checkpoint
except Exception as e:
    print(f"ERROR: Failed to load checkpoint: {e}")
    # Handle load failure
```

---

#### 5. Security Considerations

Protect sensitive checkpoint data:

```python
# 1. File permissions (SQLite)
import os
os.chmod("/var/lib/workflows/checkpoints.db", 0o600)  # Owner read/write only

# 2. Encrypt at rest (optional)
from cryptography.fernet import Fernet

class EncryptedCheckpointStore(SQLiteCheckpointStore):
    def __init__(self, db_path: str, encryption_key: bytes):
        super().__init__(db_path)
        self.cipher = Fernet(encryption_key)

    async def save_checkpoint(self, state: CheckpointState) -> str:
        # Encrypt checkpoint data before saving
        checkpoint_data = json.dumps(state.__dict__)
        encrypted = self.cipher.encrypt(checkpoint_data.encode())
        # Save encrypted data
        # ...

    async def load_checkpoint(self, checkpoint_id: str) -> CheckpointState | None:
        # Load and decrypt checkpoint data
        encrypted = # ... load from DB
        decrypted = self.cipher.decrypt(encrypted)
        checkpoint_data = json.loads(decrypted)
        return CheckpointState(**checkpoint_data)

# 3. Sanitize sensitive data in context
def serialize_context(context: dict) -> dict:
    """Serialize context with sensitive data filtering."""
    sensitive_keys = ["password", "api_key", "secret", "token", "credential"]

    serializable = {}
    for key, value in context.items():
        # Skip sensitive keys
        if any(sensitive in key.lower() for sensitive in sensitive_keys):
            continue

        # ... rest of serialization logic

    return serializable
```

---

### Migration from InMemory to SQLite

See detailed migration guide in `docs/DATABASE_MIGRATION.md`:

**Quick Migration Steps**:
1. Install `aiosqlite` dependency
2. Implement `SQLiteCheckpointStore` class
3. Update configuration to use SQLite store
4. Export existing in-memory checkpoints (if any)
5. Deploy with SQLite configuration
6. Monitor checkpoint storage health
7. Configure background cleanup task

**Zero-Downtime Migration**:
```python
# Gradual rollout with feature flag
USE_SQLITE = os.getenv("USE_SQLITE_CHECKPOINTS", "false") == "true"

if USE_SQLITE:
    checkpoint_store = SQLiteCheckpointStore("/var/lib/workflows/checkpoints.db")
else:
    checkpoint_store = InMemoryCheckpointStore()

# Enable for 10% of workflows first, then ramp up
```

---

## Summary

This architecture provides:

✅ **Automatic Checkpointing**: Transparent workflow state snapshots
✅ **Crash Recovery**: Resume from last successful checkpoint
✅ **Interactive Blocks**: Pause for LLM input with resume capability
✅ **Nested Workflow Support**: Pause propagation through workflow hierarchy
✅ **Storage Flexibility**: In-memory → database migration path
✅ **Backward Compatibility**: Existing workflows work unchanged
✅ **YAGNI/KISS Compliance**: Start simple, enable complexity as needed
✅ **Production Ready**: SQLite storage, automatic cleanup, monitoring tools
✅ **Comprehensive Examples**: Tutorial workflows and documentation

**Implementation Status**:
- ✅ **Phase 1-4**: Core infrastructure, executor integration, interactive blocks, MCP tools - COMPLETE
- 🔄 **Phase 5**: Documentation and examples - IN PROGRESS
  - ✅ Example workflows: `interactive-approval.yaml`, `multi-step-questionnaire.yaml`
  - ✅ Tutorial documentation: `INTERACTIVE_BLOCKS_TUTORIAL.md`
  - ✅ Migration guide: `DATABASE_MIGRATION.md`
  - ✅ Architecture documentation: This document

**Next Steps for Users**:
1. Read `docs/INTERACTIVE_BLOCKS_TUTORIAL.md` for usage guide
2. Try example workflows in `templates/examples/`
3. For production: Read `docs/DATABASE_MIGRATION.md`
4. For implementation details: Read `CHECKPOINT_QUICKSTART.md`

The phased implementation ensures incremental delivery with clear testing gates at each stage.
