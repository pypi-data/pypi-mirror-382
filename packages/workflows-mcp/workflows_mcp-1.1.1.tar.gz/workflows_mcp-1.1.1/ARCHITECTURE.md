# Workflows MCP Server Architecture

Comprehensive system architecture for the DAG-based workflow orchestration MCP server.

## Table of Contents

- [System Overview](#system-overview)
- [Design Principles](#design-principles)
- [Core Components](#core-components)
- [Workflow Execution Model](#workflow-execution-model)
- [Variable Resolution System](#variable-resolution-system)
- [Conditional Execution](#conditional-execution)
- [Workflow Composition](#workflow-composition)
- [Block System](#block-system)
- [MCP Integration](#mcp-integration)
- [Security Model](#security-model)
- [Error Handling](#error-handling)

## System Overview

The Workflows MCP Server is a Model Context Protocol server that provides DAG-based workflow orchestration for LLM Agents. The system enables complex multi-step automation through YAML-defined workflows with dependency resolution, variable substitution, conditional execution, and workflow composition.

### Key Characteristics

- **Declarative**: Workflows defined in YAML with clear semantics
- **Async-First**: Non-blocking I/O operations throughout
- **Type-Safe**: Pydantic v2 validation for all data structures
- **Composable**: Workflows can call other workflows as blocks
- **Extensible**: Custom blocks and user-defined workflows
- **MCP-Native**: Exposes workflows as MCP tools to LLM Agent

## Design Principles

### 1. Simplicity Over Complexity

Follow YAGNI (You Aren't Gonna Need It) and KISS (Keep It Simple, Stupid) principles:

- Minimal abstractions: only DAGResolver, WorkflowBlock, WorkflowExecutor
- No over-engineering: single workflow type (no template/workflow distinction)
- Clear execution model: DAG resolution → variable resolution → execution
- Straightforward composition: ExecuteWorkflow block for calling workflows

### 2. Separation of Concerns

**Synchronous vs Async**:

- DAGResolver: Synchronous pure graph algorithms (no I/O)
- WorkflowExecutor: Async orchestration with block execution
- WorkflowBlock: Async execution units with I/O operations

**Validation vs Execution**:

- Schema validation at load time (Pydantic models)
- Input validation before execution (type checking)
- Output validation after execution (result verification)

**Planning vs Execution**:

- Planning phase: DAG resolution, topological sort, wave detection (synchronous)
- Execution phase: Block execution, variable resolution, output collection (async)

### 3. Explicit Over Implicit

- Dependencies declared via `depends_on` (no implicit ordering)
- Variable resolution via explicit `${var}` syntax
- Context isolation in workflow composition (no implicit parent context)
- Type annotations throughout (Pydantic v2, Python type hints)

### 4. Fail-Fast Validation

- YAML schema validation at load time
- Cyclic dependency detection before execution
- Variable reference validation during resolution
- Type validation for all inputs and outputs
- Circular workflow dependency detection

## Core Components

### DAGResolver (`engine/dag.py`)

**Purpose**: Dependency resolution and execution order determination

**Characteristics**:

- **Synchronous**: Pure in-memory graph algorithms, no I/O
- **Algorithm**: Kahn's algorithm for topological sort (O(V + E))
- **Wave Detection**: Parallel execution opportunity identification
- **Validation**: Cyclic dependency detection with clear error messages

**API**:

```python
class DAGResolver:
    def topological_sort(self) -> Result[list[str]]:
        """
        Perform topological sort to determine execution order.

        Returns:
            Result containing ordered list of block names or error if cyclic dependency
        """

    def get_execution_waves(self) -> Result[list[list[str]]]:
        """
        Group blocks into waves that can be executed in parallel.

        Returns:
            Result containing list of waves (each wave is a list of blocks that can run in parallel)
        """
```

**Execution Waves**: Groups of blocks that can execute in parallel:

```python
# Each wave is a list of block IDs that have no dependencies on each other
waves: list[list[str]] = [["block1"], ["block2", "block3"], ["block4"]]
```

### WorkflowExecutor (`engine/executor.py`)

**Purpose**: Async workflow orchestration and execution

**Characteristics**:

- **Async**: Non-blocking I/O operations
- **Wave-Based Execution**: Parallel execution within waves via `asyncio.gather`
- **Context Management**: Shared context for cross-block data flow
- **Variable Resolution**: Resolves `${var}` syntax before block execution
- **Conditional Execution**: Evaluates conditions before executing blocks

**Execution Flow**:

```text
1. Load workflow definition (YAML → Pydantic model)
2. Resolve DAG (synchronous planning phase)
3. For each execution wave:
   a. Resolve variables for all blocks in wave
   b. Evaluate conditions for all blocks in wave
   c. Execute blocks in parallel (asyncio.gather)
   d. Collect outputs into shared context
4. Return final outputs
```

**API**:

```python
class WorkflowExecutor:
    async def execute_workflow(
        self,
        workflow_name: str,
        inputs: dict[str, Any]
    ) -> Result[dict[str, Any]]:
        """Execute workflow with given inputs."""
```

### WorkflowBlock (`engine/block.py`)

**Purpose**: Base class for all workflow execution units

**Characteristics**:

- **Async**: Supports I/O operations (files, network, subprocesses)
- **Type-Safe**: Pydantic v2 validation for inputs and outputs
- **Result Monad**: Explicit success/failure handling without exceptions
- **Registry**: Dynamic block instantiation from YAML type names

**Block Lifecycle**:

```text
1. Instantiation from YAML block definition
2. Input validation (Pydantic model)
3. Async execution (user-defined logic)
4. Output validation (Pydantic model)
5. Result wrapping (success or failure)
```

**API**:

```python
class WorkflowBlock(ABC):
    @abstractmethod
    def input_model(self) -> type[BlockInput]:
        """Return Pydantic model for inputs."""

    @abstractmethod
    def output_model(self) -> type[BlockOutput]:
        """Return Pydantic model for outputs."""

    @abstractmethod
    async def execute(self, context: dict[str, Any]) -> Result[BlockOutput]:
        """Execute block logic asynchronously."""
```

### WorkflowRegistry (`engine/registry.py`)

**Purpose**: In-memory workflow storage and discovery

**Characteristics**:

- **Multi-Directory Loading**: Built-in + user-defined templates
- **Priority System**: User templates override built-in templates by name
- **Tag-Based Filtering**: Discover workflows by tags (AND semantics)
- **Metadata Extraction**: Name, description, blocks, inputs, tags
- **Source Tracking**: Know where each workflow came from

**API**:

```python
class WorkflowRegistry:
    def register(self, workflow: WorkflowDefinition) -> None:
        """Register workflow in registry."""

    def get(self, name: str) -> WorkflowDefinition | None:
        """Retrieve workflow by name."""

    def filter_by_tags(self, tags: list[str]) -> list[WorkflowDefinition]:
        """Filter workflows by tags (AND semantics)."""

    def load_from_directories(
        self,
        directories: list[Path],
        on_duplicate: Literal["skip", "overwrite", "error"] = "skip"
    ) -> Result[dict[str, int]]:
        """Load workflows from multiple directories with priority."""
```

### WorkflowSchema (`engine/schema.py`)

**Purpose**: Pydantic model defining YAML workflow structure with comprehensive validation

**Characteristics**:

- **Type-Safe Validation**: Validates workflow YAML files with detailed error messages
- **Schema Definition**: Defines required fields (name, description, blocks) and optional fields (inputs, outputs, tags)
- **Dependency Validation**: Validates block dependencies form a valid DAG with no cycles
- **Variable Reference Validation**: Validates `${var}` and `${block.field}` syntax against available inputs and blocks
- **Block Type Validation**: Ensures all block types exist in BLOCK_REGISTRY
- **Input Type Validation**: Validates input declarations with type checking for defaults
- **Conversion**: Transforms validated schema to WorkflowDefinition for executor

**Schema Structure**:

```python
class WorkflowSchema(BaseModel):
    # Metadata fields
    name: str                                           # Unique workflow identifier (kebab-case)
    description: str                                    # Human-readable description
    version: str = "1.0"                               # Semantic version
    author: str | None = None                          # Optional author
    tags: list[str] = []                               # Searchable tags

    # Workflow structure
    inputs: dict[str, WorkflowInputDeclaration] = {}   # Input parameter declarations
    blocks: list[BlockDefinition]                      # Block definitions (required)
    outputs: dict[str, str | WorkflowOutputSchema] = {}  # Output mappings

    def to_workflow_definition(self) -> WorkflowDefinition:
        """Convert to executor-compatible WorkflowDefinition."""

    @staticmethod
    def validate_yaml_dict(data: dict[str, Any]) -> Result[WorkflowSchema]:
        """Validate YAML dictionary with detailed error messages."""
```

**Validation Example**:

```python
import yaml
from workflows_mcp.engine.schema import WorkflowSchema

# Load and validate YAML
with open("workflow.yaml") as f:
    data = yaml.safe_load(f)

result = WorkflowSchema.validate_yaml_dict(data)
if result.is_success:
    schema = result.value
    workflow_def = schema.to_workflow_definition()
    # Ready for execution
else:
    print(f"Validation failed: {result.error}")
```

**YAML Example**:

```yaml
name: example-workflow
description: Example workflow with inputs and outputs
version: "1.0"
tags: [python, testing]

inputs:
  project_path:
    type: string
    description: Path to project directory
    default: "."

  branch_name:
    type: string
    description: Git branch name
    required: true

blocks:
  - id: setup
    type: CreateWorktree
    inputs:
      branch: "${branch_name}"
      path: ".worktrees/${branch_name}"

  - id: run_tests
    type: BashCommand
    inputs:
      command: "pytest ${project_path}"
    depends_on:
      - setup

  - id: deploy
    type: BashCommand
    inputs:
      command: "echo 'Deploying...'"
    condition: "${run_tests.exit_code} == 0"
    depends_on:
      - run_tests

outputs:
  test_result:
    value: "${run_tests.exit_code}"
    type: int
    description: Test execution result
```

### WorkflowDefinition (`engine/executor.py`)

**Purpose**: Validated, executor-compatible representation of a loaded workflow

**Characteristics**:

- **Executor Format**: Simplified data structure optimized for execution
- **Immutable After Load**: Represents validated workflow ready for execution
- **Context Integration**: Blocks contain raw inputs for variable resolution at runtime
- **No Validation Logic**: Assumes data is already validated by WorkflowSchema
- **Factory Method**: Can be created from dictionary for programmatic workflows

**API**:

```python
class WorkflowDefinition:
    def __init__(
        self,
        name: str,
        description: str,
        blocks: list[dict[str, Any]],
        inputs: dict[str, dict[str, Any]] | None = None,
    ):
        """Create workflow definition with validated data."""

    @staticmethod
    def from_dict(data: dict[str, Any]) -> WorkflowDefinition:
        """Create from dictionary (for programmatic workflows)."""
```

**Programmatic Example**:

```python
from workflows_mcp.engine.executor import WorkflowDefinition, WorkflowExecutor

# Create workflow programmatically
workflow_def = WorkflowDefinition(
    name="simple-workflow",
    description="Programmatic workflow example",
    blocks=[
        {
            "id": "echo_hello",
            "type": "EchoBlock",
            "inputs": {"message": "Hello ${name}"},
            "depends_on": []
        },
        {
            "id": "echo_goodbye",
            "type": "EchoBlock",
            "inputs": {"message": "Goodbye ${name}"},
            "depends_on": ["echo_hello"]
        }
    ],
    inputs={
        "name": {
            "type": "string",
            "description": "User name",
            "default": "World",
            "required": False
        }
    }
)

# Execute workflow
executor = WorkflowExecutor()
executor.load_workflow(workflow_def)
result = await executor.execute_workflow("simple-workflow", {"name": "Claude"})
```

**YAML Loading Pattern**:

```python
# Load from YAML (via WorkflowSchema)
from workflows_mcp.engine.loader import load_workflow_from_file

result = load_workflow_from_file("workflow.yaml")
if result.is_success:
    workflow_def = result.value  # WorkflowDefinition instance
    executor.load_workflow(workflow_def)
```

### WorkflowLoader (`engine/loader.py`)

**Purpose**: YAML workflow file loading with validation and discovery

**Characteristics**:

- **File Loading**: Reads YAML files and converts to WorkflowDefinition
- **Validation Integration**: Uses WorkflowSchema for comprehensive validation
- **Discovery**: Finds and loads all workflows in a directory
- **Error Handling**: Clear error messages for file I/O, YAML parsing, and validation failures
- **Batch Loading**: Discover workflows with partial failure tolerance (skip invalid, load valid)

**API**:

```python
def load_workflow_from_file(file_path: str | Path) -> Result[WorkflowDefinition]:
    """Load and validate a workflow from YAML file."""

def load_workflow_from_yaml(
    yaml_content: str,
    source: str = "<string>"
) -> Result[WorkflowDefinition]:
    """Load and validate a workflow from YAML string."""

def discover_workflows(directory: str | Path) -> Result[list[WorkflowDefinition]]:
    """Discover and load all YAML workflows in a directory."""

def validate_workflow_file(file_path: str | Path) -> Result[WorkflowSchema]:
    """Validate a workflow file without converting to WorkflowDefinition."""
```

**File Loading Example**:

```python
from workflows_mcp.engine.loader import load_workflow_from_file
from workflows_mcp.engine.executor import WorkflowExecutor

# Load single workflow
result = load_workflow_from_file("workflows/python-ci.yaml")
if result.is_success:
    workflow_def = result.value

    # Execute workflow
    executor = WorkflowExecutor()
    executor.load_workflow(workflow_def)
    exec_result = await executor.execute_workflow("python-ci", {"project_path": "."})
else:
    print(f"Failed to load: {result.error}")
```

**Directory Discovery Example**:

```python
from workflows_mcp.engine.loader import discover_workflows
from workflows_mcp.engine.registry import WorkflowRegistry

# Discover all workflows in directory
result = discover_workflows("templates/python")
if result.is_success:
    # Register all discovered workflows
    registry = WorkflowRegistry()
    for workflow_def in result.value:
        registry.register(workflow_def)

    print(f"Loaded {len(result.value)} workflows")
```

**YAML String Loading Example**:

```python
from workflows_mcp.engine.loader import load_workflow_from_yaml

yaml_content = """
name: inline-workflow
description: Workflow defined as string
blocks:
  - id: echo
    type: EchoBlock
    inputs:
      message: "Hello from inline workflow"
"""

result = load_workflow_from_yaml(yaml_content, source="inline-definition")
if result.is_success:
    executor.load_workflow(result.value)
```

**Validation-Only Example** (for linting tools):

```python
from workflows_mcp.engine.loader import validate_workflow_file

# Validate without executing
result = validate_workflow_file("workflow.yaml")
if result.is_success:
    schema = result.value
    print(f"✓ Valid workflow: {schema.name}")
    print(f"  Version: {schema.version}")
    print(f"  Blocks: {len(schema.blocks)}")
    print(f"  Tags: {', '.join(schema.tags)}")
else:
    print(f"✗ Validation failed: {result.error}")
```

### Result Monad (`engine/result.py`)

**Purpose**: Type-safe error handling without exceptions

**Characteristics**:

- **Success/Failure Pattern**: Explicit result states
- **Metadata Support**: Additional context for debugging
- **Unwrap Methods**: Extract values with clear error handling
- **Composability**: Chain operations with error propagation

**API**:

```python
@dataclass
class Result[T]:
    value: T | None
    error: str | None
    metadata: dict[str, Any]

    @staticmethod
    def success(value: T, metadata: dict = None) -> Result[T]:
        """Create success result."""

    @staticmethod
    def failure(error: str, metadata: dict = None) -> Result[T]:
        """Create failure result."""

    def is_success(self) -> bool:
        """Check if result is successful."""

    def unwrap(self) -> T:
        """Extract value or raise exception."""
```

## Workflow Execution Model

### 1. DAG Resolution Phase (Synchronous)

**Input**: List of block definitions from YAML
**Output**: List of execution waves (groups of parallel blocks)

**Algorithm** (Kahn's Topological Sort):

```text
1. Identify blocks with no dependencies (in-degree = 0) → Wave 1
2. Remove Wave 1 blocks from graph
3. Identify newly independent blocks → Wave 2
4. Repeat until all blocks assigned to waves
5. If any blocks remain, cyclic dependency exists → error
```

**Parallel Execution Opportunities**:

```yaml
# Example: Diamond DAG pattern
blocks:
  - id: start
    type: BashCommand

  - id: parallel_a
    type: BashCommand
    depends_on: [start]

  - id: parallel_b
    type: BashCommand
    depends_on: [start]

  - id: merge
    type: BashCommand
    depends_on: [parallel_a, parallel_b]
```

**Execution Waves**:

- Wave 1: `[start]`
- Wave 2: `[parallel_a, parallel_b]` (execute in parallel)
- Wave 3: `[merge]`

### 2. Variable Resolution Phase

**Purpose**: Replace `${var}` syntax with actual values from context

**Resolution Rules**:

1. Workflow inputs: `${inputs.name}` → from runtime inputs
2. Block outputs: `${block_id.field}` → from previous block results
3. Nested references: `${create_file.${input_var}}` → recursive resolution

**Resolution Order**:

```text
1. Resolve workflow inputs (from runtime inputs dict)
2. Resolve block outputs (from shared context)
3. Recursive resolution for nested references
4. Validation: fail if reference not found
```

**Example**:

```yaml
blocks:
  - id: create_dir
    type: BashCommand
    inputs:
      command: mkdir -p ${inputs.workspace}/output

  - id: write_file
    type: CreateFile
    inputs:
      path: "${create_dir.stdout}/data.txt"  # Depends on create_dir output
    depends_on: [create_dir]
```

### 3. Conditional Execution Phase

**Purpose**: Evaluate conditions to determine if blocks should execute

**Condition Evaluation**:

- **Safe AST Evaluation**: No arbitrary code execution
- **Boolean Expressions**: Comparisons, logical operators (and, or, not)
- **Access to Context**: Can reference inputs and previous block outputs

**Supported Operators**:

- Comparison: `==`, `!=`, `<`, `>`, `<=`, `>=`
- Logical: `and`, `or`, `not`
- Membership: `in`, `not in`

**Example**:

```yaml
blocks:
  - id: run_tests
    type: BashCommand
    inputs:
      command: pytest tests/

  - id: deploy
    type: ExecuteWorkflow
    inputs:
      workflow: "deploy-production"
    condition: "${run_tests.exit_code} == 0"
    depends_on: [run_tests]
```

### 4. Async Execution Phase

**Purpose**: Execute blocks in parallel waves with async I/O

**Execution Strategy**:

```python
for wave in execution_waves:
    # Resolve variables for all blocks in wave
    resolved_blocks = [resolve_variables(block, context) for block in wave]

    # Filter blocks based on conditions
    blocks_to_execute = [
        block for block in resolved_blocks
        if evaluate_condition(block.condition, context)
    ]

    # Execute blocks in parallel within wave
    results = await asyncio.gather(*[
        block.execute(context)
        for block in blocks_to_execute
    ])

    # Collect outputs into shared context
    for block, result in zip(blocks_to_execute, results):
        if result.is_success:
            context[block.id] = result.value
        else:
            return Result.failure(f"Block {block.id} failed: {result.error}")
```

## Variable Resolution System

### VariableResolver (`engine/variables.py`)

**Purpose**: Resolve `${var}` syntax in block inputs

**Resolution Patterns**:

1. **Workflow Inputs**: `${inputs.name}`

   ```yaml
   inputs:
     - name: username
       type: string

   blocks:
     - id: greet
       type: BashCommand
       inputs:
         command: echo "Hello, ${inputs.username}!"
   ```

2. **Block Outputs**: `${block_id.field}`

   ```yaml
   blocks:
     - id: setup
       type: ExecuteWorkflow
       inputs:
         workflow: "setup-python-env"

     - id: test
       type: BashCommand
       inputs:
         command: "${setup.python_path} -m pytest"
       depends_on: [setup]
   ```

3. **Nested References**: `${block.${input_var}}`

   ```yaml
   inputs:
     - name: field_name
       type: string
       default: "python_path"

   blocks:
     - id: use_field
       type: BashCommand
       inputs:
         command: "${setup.${inputs.field_name}} --version"
   ```

**Recursive Resolution**:

```python
def resolve(value: str, context: dict[str, Any]) -> str:
    """
    Recursively resolve variables in value.

    Example:
        value = "${create_file.${input_name}}"
        context = {"input_name": "path", "create_file": {"path": "/tmp/file.txt"}}
        result = "/tmp/file.txt"
    """
    while "${" in value:
        # Extract variable reference
        var_ref = extract_variable(value)  # e.g., "create_file.path"

        # Resolve reference from context
        resolved = lookup_in_context(var_ref, context)

        # Replace in value
        value = value.replace(f"${{{var_ref}}}", resolved)

    return value
```

## Conditional Execution

### ConditionEvaluator (`engine/variables.py`)

**Purpose**: Safe evaluation of boolean expressions for conditional execution

**Safety Model**:

- **AST-Based Parsing**: Python's `ast` module for safe expression parsing
- **No Arbitrary Code**: Only allowed operations (comparisons, logical operators)
- **Sandboxed Execution**: Limited variable access (only context)

**Supported Expressions**:

```python
# Comparisons
"${block.exit_code} == 0"
"${block.count} > 10"
"${block.enabled} != False"

# Logical operators
"${test.success} and ${lint.success}"
"${error_count} > 0 or ${warning_count} > 100"
"not ${skip_deployment}"

# Membership
"'error' in ${block.stdout}"
"${status} not in ['failed', 'cancelled']"
```

**Evaluation Algorithm**:

```python
def evaluate(condition: str, context: dict[str, Any]) -> bool:
    """
    Safely evaluate boolean condition.

    1. Resolve variables in condition string
    2. Parse expression into AST
    3. Validate AST (only allowed operations)
    4. Evaluate AST with context
    5. Return boolean result
    """
    # Resolve variables
    resolved_condition = resolve_variables(condition, context)

    # Parse AST
    tree = ast.parse(resolved_condition, mode='eval')

    # Validate (no function calls, no attribute access except allowed)
    validate_ast(tree)

    # Evaluate
    result = eval(compile(tree, '<string>', 'eval'), {"__builtins__": {}}, context)

    return bool(result)
```

## Workflow Composition

### ExecuteWorkflow Block (`engine/blocks_workflow.py`)

**Purpose**: Call workflows as blocks for composition

**Design Principles**:

- **Clean Isolation**: Child workflows receive ONLY explicitly passed inputs
- **No Parent Context**: Child workflows don't inherit parent's full context
- **Automatic Namespacing**: Child outputs stored under `parent_context[block_id]`
- **Circular Detection**: Prevent infinite recursion via execution stack tracking

**Context Management**:

```python
# Parent workflow execution
parent_context = {
    "inputs": {"username": "alice"},
    "setup": {"python_path": "/path/to/python"},
}

# ExecuteWorkflow block
block = ExecuteWorkflowBlock(
    id="run_tests",
    workflow="pytest-workflow",
    inputs={
        "python_path": "${setup.python_path}",  # Resolved before passing
        "test_dir": "tests/"
    }
)

# Child workflow receives ONLY:
child_context = {
    "inputs": {
        "python_path": "/path/to/python",  # Resolved value
        "test_dir": "tests/"
    }
}

# Child outputs stored in parent as:
parent_context["run_tests"] = {
    "exit_code": 0,
    "coverage": 85.5,
    "passed": 42
}
```

**Circular Dependency Prevention**:

```python
class WorkflowExecutionStack:
    """Track workflow execution to prevent circular calls."""

    def __init__(self):
        self.stack: list[str] = []

    def enter(self, workflow_name: str):
        """Enter workflow execution."""
        if workflow_name in self.stack:
            raise CircularDependencyError(
                f"Circular workflow call: {' → '.join(self.stack + [workflow_name])}"
            )
        self.stack.append(workflow_name)

    def exit(self, workflow_name: str):
        """Exit workflow execution."""
        self.stack.pop()
```

## Block System

### Built-In Blocks

#### BashCommand (`blocks_bash.py`)

Execute shell commands with timeout and environment control.

**Inputs**:

- `command`: Shell command to execute
- `working_dir`: Working directory (optional)
- `timeout`: Timeout in seconds (default: 120)
- `env`: Environment variables (dict)

**Outputs**:

- `exit_code`: Command exit code
- `stdout`: Standard output
- `stderr`: Standard error
- `success`: Boolean (exit_code == 0)

#### CreateFile (`blocks_file.py`)

Create files with permissions and encoding control.

**Inputs**:

- `path`: File path
- `content`: File content
- `permissions`: Unix permissions (default: 0o644)
- `encoding`: Text encoding (default: utf-8)
- `overwrite`: Allow overwrite (default: false)

**Outputs**:

- `file_path`: Created file path
- `success`: Boolean

#### ReadFile (`blocks_file.py`)

Read text or binary files with size limits.

**Inputs**:

- `path`: File path
- `mode`: 'text' or 'binary' (default: text)
- `encoding`: Text encoding (default: utf-8)
- `max_size_mb`: Maximum file size (default: 10)

**Outputs**:

- `content`: File content
- `size_bytes`: File size
- `success`: Boolean

#### PopulateTemplate (`blocks_file.py`)

Render Jinja2 templates with variables.

**Inputs**:

- `template`: Jinja2 template string
- `variables`: Template variables (dict)
- `strict`: Strict mode (undefined variables are errors)

**Outputs**:

- `rendered`: Rendered template
- `success`: Boolean

#### ExecuteWorkflow (`blocks_workflow.py`)

Call another workflow as a block.

**Inputs**:

- `workflow`: Workflow name
- `inputs`: Workflow inputs (dict)
- `timeout`: Execution timeout (default: 600)

**Outputs**:

- All outputs from child workflow
- `workflow_name`: Executed workflow name
- `success`: Boolean
- `execution_time`: Time in seconds

### Custom Block Development

**Create Input/Output Models**:

```python
from workflows_mcp.engine.block import BlockInput, BlockOutput
from pydantic import Field

class MyBlockInput(BlockInput):
    param: str = Field(description="Parameter description")

class MyBlockOutput(BlockOutput):
    result: str
    success: bool
```

**Implement Block**:

```python
from workflows_mcp.engine.block import WorkflowBlock
from workflows_mcp.engine.result import Result

class MyBlock(WorkflowBlock):
    def input_model(self) -> type[BlockInput]:
        return MyBlockInput

    def output_model(self) -> type[BlockOutput]:
        return MyBlockOutput

    async def execute(self, context: dict[str, Any]) -> Result[BlockOutput]:
        inputs = self._validated_inputs

        # Implement block logic
        result = await some_async_operation(inputs.param)

        return Result.success(MyBlockOutput(
            result=result,
            success=True
        ))
```

**Register Block**:

```python
from workflows_mcp.engine.block import BLOCK_REGISTRY

BLOCK_REGISTRY["MyBlock"] = MyBlock
```

## MCP Integration

### Server Architecture (`server.py`, `tools.py`)

**FastMCP Integration**:

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("workflows")

@mcp.tool()
async def execute_workflow(workflow: str, inputs: dict = None) -> dict:
    """Execute a DAG-based workflow with inputs."""
    executor = WorkflowExecutor()
    result = await executor.execute_workflow(workflow, inputs or {})

    return {
        "status": "success" if result.is_success else "failure",
        "outputs": result.value if result.is_success else {},
        "error": result.error if not result.is_success else None
    }

@mcp.tool()
async def list_workflows(tags: list[str] | None = None) -> list[dict]:
    """List available workflows by tags."""
    workflows = workflow_registry.filter_by_tags(tags) if tags else workflow_registry.all()
    return [workflow.metadata() for workflow in workflows]

@mcp.tool()
async def get_workflow_info(workflow: str) -> dict:
    """Get detailed workflow metadata."""
    workflow_def = workflow_registry.get(workflow)
    if not workflow_def:
        return {"error": f"Workflow '{workflow}' not found"}

    return workflow_def.full_metadata()
```

### Workflow Discovery Flow

```text
User: "Run Python tests"
  ↓
LLM discovers tools: list_workflows, get_workflow_info, execute_workflow
  ↓
LLM: list_workflows(tags=["python", "testing"])
  ↓
MCP Server returns: [{"name": "run-pytest", ...}, ...]
  ↓
LLM: get_workflow_info("run-pytest")
  ↓
MCP Server returns: {"inputs": [...], "blocks": [...]}
  ↓
LLM: execute_workflow("run-pytest", {"test_dir": "tests/"})
  ↓
MCP Server executes workflow and returns results
  ↓
LLM presents results to user
```

## Security Model

### File Operations Security

**Safe Mode (Default)**:

- Only relative paths allowed
- No path traversal (`../`)
- No symlinks
- Size limits (10MB default)
- Must be within working directory

**Unsafe Mode (Opt-In)**:

- Absolute paths allowed
- Still blocks symlinks
- Still enforces size limits
- Requires explicit `unsafe: true` flag

### Custom File-Based Outputs

**Path Validation**:

```python
def validate_output_path(path: str, unsafe: bool = False) -> Result[Path]:
    """Validate output file path for security."""
    resolved = Path(path).resolve()

    if not unsafe:
        # Safe mode checks
        if resolved.is_absolute():
            return Result.failure("Absolute paths not allowed in safe mode")

        if ".." in path:
            return Result.failure("Path traversal not allowed")

        if not resolved.is_relative_to(Path.cwd()):
            return Result.failure("Path must be within working directory")

    if resolved.is_symlink():
        return Result.failure("Symlinks not allowed")

    if resolved.stat().st_size > MAX_FILE_SIZE:
        return Result.failure(f"File exceeds size limit: {MAX_FILE_SIZE}")

    return Result.success(resolved)
```

### Command Execution Security

**BashCommand Safety**:

- Timeout enforcement (prevents infinite loops)
- Environment variable isolation
- No shell injection (command passed as list when possible)
- Working directory validation

## Error Handling

### Result Monad Pattern

All workflow operations return `Result[T]`:

```python
# Success case
result = await block.execute(context)
if result.is_success:
    outputs = result.value
else:
    handle_error(result.error)

# Chaining operations
result = (
    await load_workflow(name)
    .and_then(lambda w: resolve_dag(w))
    .and_then(lambda waves: execute_waves(waves))
)
```

### Error Categories

**Load-Time Errors**:

- Invalid YAML syntax
- Schema validation failures
- Circular dependencies in DAG
- Invalid variable references

**Runtime Errors**:

- Block execution failures
- Timeout errors
- Variable resolution failures
- Condition evaluation errors

**Error Propagation**:

```text
Block fails → Wave fails → Workflow fails → MCP tool returns error
```

## Summary

The Workflows MCP Server provides a clean, composable architecture for DAG-based workflow orchestration:

- **Simple Abstractions**: DAGResolver, WorkflowBlock, WorkflowExecutor
- **Type-Safe**: Pydantic v2 validation throughout
- **Async-First**: Non-blocking I/O with parallel execution
- **Composable**: Workflows call workflows via ExecuteWorkflow
- **MCP-Native**: Natural LLM Agents integration
- **Secure**: Safe defaults with opt-in unsafe modes

This architecture enables complex automation while maintaining clarity, type safety, and extensibility.
