"""Workflow engine core components.

This package contains the core workflow execution engine components adapted from the legacy
workflow system. Key components:

- Result: Type-safe Result monad for error handling
- DAGResolver: Dependency resolution via Kahn's algorithm (synchronous)
- WorkflowBlock: Async base class for workflow blocks
- BlockInput/BlockOutput: Pydantic v2 base classes for validation
- BLOCK_REGISTRY: Global registry for workflow block types
- WorkflowExecutor: Async workflow executor
- WorkflowDefinition: Workflow definition container
- WorkflowRegistry: Central registry for managing loaded workflow definitions
- WorkflowSchema: Pydantic v2 schema for YAML workflow validation
"""

# Import blocks to register in BLOCK_REGISTRY
from . import (
    blocks_bash,  # noqa: F401 - Register BashCommand
    blocks_example,  # noqa: F401 - Register EchoBlock
    blocks_file,  # noqa: F401 - Register CreateFile, ReadFile
    blocks_workflow,  # noqa: F401 - Register ExecuteWorkflow (Phase 2.2)
)
from .block import BLOCK_REGISTRY, BlockInput, BlockOutput, BlockRegistry, WorkflowBlock
from .dag import DAGResolver
from .executor import WorkflowDefinition, WorkflowExecutor
from .registry import WorkflowRegistry
from .result import Result
from .schema import WorkflowSchema

__all__ = [
    "Result",
    "DAGResolver",
    "WorkflowBlock",
    "BlockInput",
    "BlockOutput",
    "BLOCK_REGISTRY",
    "BlockRegistry",
    "WorkflowExecutor",
    "WorkflowDefinition",
    "WorkflowRegistry",
    "WorkflowSchema",
    "blocks_example",
]
