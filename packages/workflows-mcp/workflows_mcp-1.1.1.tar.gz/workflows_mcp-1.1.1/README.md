# Workflows MCP Server

MCP (Model Context Protocol) server exposing DAG-based workflow execution as tools for LLM Agents.

## Overview

The Workflows MCP Server provides a comprehensive workflow orchestration system integrated with the Model Context Protocol. It enables LLM Agents to discover and execute complex multi-step workflows through natural language interactions.

### Core Capabilities

**DAG-Based Execution**:

- Dependency resolution via Kahn's algorithm
- Parallel wave detection and concurrent execution
- Branch/converge patterns (diamond DAGs)
- Topological sort for optimal execution order
- Cyclic dependency detection

**Variable Resolution System**:

- `${var}` syntax for workflow inputs
- `${block_id.field}` syntax for cross-block references
- Recursive resolution with nested references
- Integration throughout workflow definitions

**Conditional Execution**:

- Boolean expression evaluation with safe AST parsing
- Conditional block execution based on previous results
- Adaptive workflow behavior

**Workflow Composition**:

- Call workflows as blocks via ExecuteWorkflow
- Multi-level composition support
- Circular dependency detection
- Clean context isolation with automatic output namespacing

**File Operations**:

- **CreateFile**: Create files with permissions, encoding, overwrite protection
- **ReadFile**: Read text/binary files with size limits and line-by-line mode
- **PopulateTemplate**: Jinja2 template rendering with full language support

**Shell Integration**:

- **BashCommand**: Execute shell commands with timeout, environment variables, working directory control

## Installation

This project uses `uv` for package management:

```bash
# Install dependencies
uv sync

# Run validation
uv run python tests/validate_structure.py

# Run server (stdio transport)
uv run python -m workflows_mcp
```

## Quick Start

### Basic Workflow Example

```yaml
name: hello-world
description: Simple greeting workflow
version: 1.0.0

inputs:
  - name: username
    type: string
    description: Name to greet
    required: true

blocks:
  - id: greet
    type: BashCommand
    inputs:
      command: echo "Hello, ${inputs.username}!"
```

### Using Variable Resolution

```yaml
blocks:
  - id: create_file
    type: CreateFile
    inputs:
      path: "${workspace}/README.md"
      content: "# ${project_name}"

  - id: read_back
    type: ReadFile
    inputs:
      path: "${create_file.file_path}"
    depends_on: [create_file]
```

### Conditional Execution

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

### Workflow Composition

```yaml
blocks:
  - id: setup
    type: ExecuteWorkflow
    inputs:
      workflow: "setup-python-env"
      inputs:
        working_dir: "/path/to/project"
        python_version: "3.12"

  - id: test
    type: BashCommand
    inputs:
      command: "${setup.python_path} -m pytest"
      working_dir: "/path/to/project"
    depends_on: [setup]
```

## Configuration

### Custom Workflow Templates

By default, the MCP server loads workflows from the built-in `templates/` directory. You can add your own custom workflow directories using the `WORKFLOWS_TEMPLATE_PATHS` environment variable.

**Priority System**: User templates **override** built-in templates by name.

#### Environment Variable

Set `WORKFLOWS_TEMPLATE_PATHS` to a comma-separated list of directory paths:

```bash
export WORKFLOWS_TEMPLATE_PATHS="~/my-workflows,/opt/company-workflows"
```

Paths can use `~` for home directory expansion.

#### Claude Desktop Configuration

Add the environment variable to your `.mcp.json`:

```json
{
  "mcpServers": {
    "workflows": {
      "command": "uvx",
      "args": [
        "--from", "workflows-mcp",
        "workflows-mcp"
      ],
      "env": {
        "WORKFLOWS_LOG_LEVEL": "INFO",
        "WORKFLOWS_TEMPLATE_PATHS": "~/my-workflows,/opt/team-workflows"
      }
    }
  }
}
```

#### Use Cases

**Personal Customizations**:

```bash
WORKFLOWS_TEMPLATE_PATHS="~/.workflows"
```

**Team-Specific Workflows**:

```bash
WORKFLOWS_TEMPLATE_PATHS="/opt/company-workflows,~/my-experiments"
```

**Override Built-in Workflow**:
If you create `~/my-workflows/python-ci-pipeline.yaml`, it will replace the built-in `python-ci-pipeline` workflow.

#### Directory Structure Example

```bash
~/my-workflows/
├── custom-deploy.yaml          # New workflow
├── python-ci-pipeline.yaml     # Overrides built-in
└── team/
    ├── code-review.yaml        # Team-specific workflow
    └── release-process.yaml    # Team-specific workflow
```

## MCP Tools

The server exposes workflows as MCP tools for LLM Agents:

### execute_workflow

Execute a DAG-based workflow with inputs.

**Parameters**:

- `workflow` (str): Workflow name (e.g., 'python-ci-pipeline', 'setup-python-env')
- `inputs` (dict): Runtime inputs as key-value pairs for block variable substitution
- `async_execution` (bool): Run workflow in background and return immediately

**Returns**:

- `status`: Execution status (success/failure)
- `outputs`: Workflow output values
- `execution_time`: Total execution time in seconds
- `error`: Error message (if failed)

### list_workflows

List available workflows with optional tag filtering.

**Parameters**:

- `tags` (list[str], optional): Filter workflows by tags (uses AND semantics)

**Returns**:
List of workflow metadata dictionaries with name, description, tags, blocks, inputs.

**Examples**:

- `list_workflows()` - All workflows
- `list_workflows(tags=["python"])` - All Python-related workflows
- `list_workflows(tags=["python", "testing"])` - Workflows with both tags

### get_workflow_info

Get detailed information about a specific workflow.

**Parameters**:

- `workflow` (str): Workflow name/identifier

**Returns**:
Comprehensive workflow metadata including name, description, version, tags, blocks with dependencies, inputs, and outputs.

## Architecture

### Core Components

**DAGResolver** (`engine/dag.py`):

- Synchronous graph algorithms (pure in-memory operations)
- Kahn's algorithm for topological sort with O(V + E) complexity
- Execution wave detection for parallel execution opportunities
- Cyclic dependency detection with meaningful error messages

**Result Monad** (`engine/result.py`):

- Type-safe error handling without exceptions
- Success/failure pattern with metadata support
- Unwrap methods for value extraction

**WorkflowBlock** (`engine/block.py`):

- Async base class for workflow execution units
- Pydantic v2 validation for inputs and outputs
- Result monad integration for error handling
- Block registry for dynamic instantiation from YAML

**WorkflowSchema** (`engine/schema.py`):

- Pydantic models for YAML workflow definitions
- Comprehensive validation (blocks, inputs, dependencies)
- Type-safe workflow representation

**WorkflowLoader** (`engine/loader.py`):

- Directory scanning with recursive template discovery
- YAML parsing with error handling
- Validation against WorkflowSchema

**WorkflowRegistry** (`engine/registry.py`):

- In-memory workflow storage with tag-based filtering
- Metadata extraction (name, description, blocks, inputs, tags)
- Fast lookup by workflow name
- Multi-directory loading with priority-based override

**FastMCP Server** (`server.py`):

- Official Anthropic MCP Python SDK
- Stdio transport (default)
- Tool registration via decorators

### Design Principles

Following official Anthropic MCP SDK patterns:

- Minimal structure (not single file, not over-engineered)
- Type hints throughout (Pydantic v2 compatible)
- Async-first patterns for I/O operations
- Pure algorithms for graph operations (DAG, Result)

### Execution Model

The workflow engine follows a **declarative DAG-based execution model**:

1. **Workflow Definition** (YAML) → blocks with dependencies
2. **DAG Resolution** → topological sort determines execution order
3. **Variable Resolution** → cross-block references resolved from context
4. **Wave Execution** → blocks run in parallel waves based on dependencies
5. **Result Accumulation** → each block's output stored in shared context

## Development

### Requirements

- Python 3.12+
- uv package manager
- Dependencies: `mcp[cli]`, `pydantic>=2.0`, `pyyaml`

### Testing

Run the test suite:

```bash
# Run all tests
uv run pytest

# Run with coverage report
uv run pytest --cov=workflows_mcp --cov-report=term-missing

# Run specific test suites
uv run pytest tests/test_schema_integration.py    # YAML schema tests
uv run pytest tests/test_loader.py                # Workflow loader tests
uv run pytest tests/test_registry.py              # Registry tests
uv run pytest tests/test_bash_block.py            # BashCommand block tests
uv run pytest tests/test_file_blocks.py           # File blocks tests
uv run pytest tests/test_variables.py             # Variable resolution tests
uv run pytest tests/test_conditionals.py          # Conditional execution tests
uv run pytest tests/test_workflow_composition.py  # ExecuteWorkflow composition tests
uv run pytest tests/test_mcp_integration.py       # End-to-end MCP tests
```

All async tests are properly configured with pytest-asyncio auto mode.

### Validation

Run the comprehensive validation script:

```bash
uv run python tests/validate_structure.py
```

This validates:
- Directory structure
- All imports resolve correctly
- FastMCP server initializes
- DAGResolver algorithms work
- Result monad functions correctly
- WorkflowBlock async patterns work
- YAML workflow loading system
- pyproject.toml configuration

## Documentation

### Architecture & Guides

- [ARCHITECTURE.md](ARCHITECTURE.md) - Comprehensive system architecture and design
- [Workflow Templates](src/workflows_mcp/templates/README.md) - Built-in workflow catalog
- [Example Workflows](src/workflows_mcp/templates/examples/README.md) - Tutorial workflows

## Project Structure

```bash
workflows-mcp/
├── src/workflows_mcp/
│   ├── __init__.py              # Package initialization
│   ├── __main__.py              # Entry point for uv run
│   ├── server.py                # FastMCP initialization
│   ├── tools.py                 # MCP tool implementations
│   ├── templates/               # Workflow templates
│   │   ├── ci/                  # CI/CD pipeline workflows
│   │   ├── examples/            # Tutorial workflows
│   │   ├── files/               # File processing workflows
│   │   ├── git/                 # Git operation workflows
│   │   ├── node/                # Node.js project workflows
│   │   └── python/              # Python project workflows
│   └── engine/                  # Workflow engine
│       ├── __init__.py          # Engine exports
│       ├── dag.py               # DAG dependency resolution
│       ├── result.py            # Result monad
│       ├── block.py             # WorkflowBlock base class
│       ├── blocks_example.py    # Example async blocks (EchoBlock)
│       ├── blocks_bash.py       # BashCommand block
│       ├── blocks_file.py       # File blocks: CreateFile, ReadFile, PopulateTemplate
│       ├── blocks_workflow.py   # ExecuteWorkflow block
│       ├── variables.py         # Variable resolution & conditional execution
│       ├── executor.py          # Async workflow executor
│       ├── schema.py            # YAML workflow schema
│       ├── loader.py            # YAML workflow loader
│       └── registry.py          # Workflow registry
├── tests/                       # Test suite
├── pyproject.toml               # uv project configuration
├── ARCHITECTURE.md              # Architecture documentation
└── CLAUDE.md                    # Development guide
```

## References

- [MCP Official Docs](https://modelcontextprotocol.io/docs/develop/build-server)
- [Anthropic Python MCP SDK](https://github.com/modelcontextprotocol/python-sdk)
- [CLAUDE.md](CLAUDE.md) - Development guidelines
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture

## License

See LICENSE file for details
