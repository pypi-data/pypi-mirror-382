"""
Async WorkflowBlock base class for DAG-based workflow execution.

This module provides the foundational async block abstraction, adapting
the proven patterns from the legacy synchronous implementation to work
with MCP's async-first architecture.

Design Decisions:
- Async execution: Blocks perform I/O operations (git, files, APIs)
- Pydantic v2 validation: Type-safe inputs/outputs with modern syntax
- Result monad: Explicit error handling without exceptions
- Context injection: Access to shared workflow state
- Dependency tracking: Explicit depends_on declarations
"""

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, ValidationError

from .result import Result


class BlockInput(BaseModel):
    """Base class for block input validation using Pydantic v2."""

    model_config = {"extra": "forbid"}  # Pydantic v2 config - reject unknown fields


class BlockOutput(BaseModel):
    """Base class for block output validation using Pydantic v2."""

    model_config = {"extra": "forbid"}


class WorkflowBlock(ABC):
    """
    Abstract base class for async workflow blocks.

    Workflow blocks are the atomic units of execution in DAG-based workflows.
    Each block:
    - Validates inputs using Pydantic models
    - Executes asynchronously (I/O operations)
    - Returns type-safe results using Result monad
    - Supports dependency declarations via depends_on

    Example:
        class MyBlock(WorkflowBlock):
            def input_model(self) -> type[BlockInput]:
                return MyBlockInput

            def output_model(self) -> type[BlockOutput]:
                return MyBlockOutput

            async def execute(self, context: dict[str, Any]) -> Result[BlockOutput]:
                inputs = self._validated_inputs
                # Async I/O operations
                result = await some_async_operation(inputs.param)
                return Result.success(MyBlockOutput(result=result))
    """

    # Instance attributes
    id: str
    depends_on: list[str]
    _raw_inputs: dict[str, Any]
    _validated_inputs: BlockInput | None

    def __init__(
        self,
        id: str,
        inputs: dict[str, Any],
        depends_on: list[str] | None = None,
        outputs: dict[str, Any] | None = None,
    ):
        """
        Initialize a workflow block.

        Args:
            id: Unique block identifier
            inputs: Runtime input parameters
            depends_on: List of block IDs this block depends on
            outputs: Optional output schema (used by some blocks like BashCommand)
        """
        self.id = id
        self.depends_on = depends_on or []
        self._raw_inputs = inputs
        self._validated_inputs = None
        self._validate_inputs()

    @abstractmethod
    def input_model(self) -> type[BlockInput]:
        """
        Return the Pydantic model class for input validation.

        Returns:
            Pydantic BaseModel class defining expected inputs
        """
        pass

    @abstractmethod
    def output_model(self) -> type[BlockOutput]:
        """
        Return the Pydantic model class for output validation.

        Returns:
            Pydantic BaseModel class defining expected outputs
        """
        pass

    @abstractmethod
    async def execute(self, context: dict[str, Any]) -> Result[BlockOutput]:
        """
        Execute the block's async logic.

        This is the core method that implements block behavior. It:
        - Has access to validated inputs via self._validated_inputs
        - Can read from context (outputs from previous blocks)
        - Performs async I/O operations (git, files, APIs)
        - Returns Result[BlockOutput] for type-safe error handling

        Args:
            context: Shared workflow context with outputs from previous blocks

        Returns:
            Result.success(output) on success, Result.failure(error) on failure
        """
        pass

    def _validate_inputs(self) -> None:
        """
        Validate inputs against the input model schema.

        Raises:
            ValueError: If inputs don't match schema
        """
        try:
            input_model = self.input_model()
            self._validated_inputs = input_model(**self._raw_inputs)
        except ValidationError as e:
            raise ValueError(f"Block '{self.id}' input validation failed: {e}")

    def validate_output(self, output_data: dict[str, Any]) -> Result[BlockOutput]:
        """
        Validate output data against the output model schema.

        Args:
            output_data: Raw output dictionary to validate

        Returns:
            Result.success(validated_output) or Result.failure(error_message)
        """
        try:
            output_model = self.output_model()
            validated = output_model(**output_data)
            return Result.success(validated)
        except ValidationError as e:
            return Result.failure(f"Block '{self.id}' output validation failed: {e}")


class BlockRegistry:
    """
    Registry for workflow block types.

    Maps block type names (strings) to WorkflowBlock classes for dynamic
    instantiation from YAML workflow definitions.

    Usage:
        registry = BlockRegistry()
        registry.register("MyBlock", MyBlock)
        block_class = registry.get("MyBlock")
        block = block_class(id="block1", inputs={...})
    """

    def __init__(self) -> None:
        self._blocks: dict[str, type[WorkflowBlock]] = {}

    def register(self, name: str, block_class: type[WorkflowBlock]) -> None:
        """Register a block type."""
        self._blocks[name] = block_class

    def get(self, name: str) -> type[WorkflowBlock]:
        """Get a block type by name."""
        if name not in self._blocks:
            raise ValueError(f"Unknown block type: '{name}'")
        return self._blocks[name]

    def list_types(self) -> list[str]:
        """List all registered block types."""
        return list(self._blocks.keys())


# Global block registry instance
BLOCK_REGISTRY = BlockRegistry()
