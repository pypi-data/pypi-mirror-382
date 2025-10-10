# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an **MCP (Model Context Protocol) server** that exposes DAG-based workflow execution as tools for LLM Agents. The server enables:

- **Workflow-as-Tools**: Complex multi-step workflows exposed as MCP tools
- **Adaptive Orchestration**: Claude can discover and execute workflows dynamically
- **Template-First Architecture**: Reusable workflow patterns for composition
- **Git Integration**: Worktree-based isolation for parallel development

### Current Capabilities

The workflow engine provides comprehensive workflow orchestration:

**Variable Resolution**:

- Use `${var}` syntax anywhere in block inputs
- Reference block outputs: `${block_id.field}`
- Recursive resolution with nested references
- Example:

  ```yaml
  - id: create_file
    type: CreateFile
    inputs:
      path: "${workspace}/README.md"
      content: "# ${project_name}"
  ```

**Conditional Execution**:

- Add conditions to any block with boolean expressions
- Safe AST evaluation (no arbitrary code execution)
- Example:

  ```yaml
  - id: deploy
    type: ExecuteWorkflow
    inputs:
      workflow: "deploy-production"
    condition: "${run_tests.exit_code} == 0"
    depends_on: [run_tests]
  ```

**File Operations**:

- **CreateFile**: Create files with content, permissions, encoding
- **ReadFile**: Read text/binary files into workflow context
- **PopulateTemplate**: Render Jinja2 templates with variables
- Example:

  ```yaml
  - id: populate_readme
    type: PopulateTemplate
    inputs:
      template: |
        # {{ project_name }}
        Version: {{ version }}
      variables:
        project_name: "MyApp"
        version: "1.0.0"
  ```

**Workflow Composition**:

- Call workflows as blocks via ExecuteWorkflow
- Multi-level composition support
- Circular dependency detection
- Example:

  ```yaml
  - id: ci_pipeline
    type: ExecuteWorkflow
    inputs:
      workflow: "python-ci-pipeline"
      inputs:
        project_path: "${workspace}"
  ```

**Reusable Workflow Library**:

- Python development workflows (setup-python-env, run-pytest, lint-python)
- Git operation workflows (create-feature-branch, commit-and-push)
- CI/CD workflows (python-ci-pipeline, conditional-deploy)
- File processing and example workflows

### Code Organization

The workflow engine implementation is in `src/workflows_mcp/engine/` with the MCP server in `src/workflows_mcp/server.py`. All workflow blocks, DAG resolution, variable resolution, and execution logic are part of the main package.

## MCP Development Principles

### Critical: Always Use Context7 for Library Research

**Before writing any code**, use the Context7 MCP tool to verify:

- Correct library versions and APIs
- Best practices and patterns
- Breaking changes and deprecations
- Official examples and documentation

Example usage:

```text
Use Context7 to research: "mcp python-sdk server implementation patterns"
Use Context7 to research: "pydantic v2 field validation latest"
```

This ensures you're always using current, correct library implementations.

### Official Anthropic Python MCP SDK

**Always use the official Anthropic SDK for MCP development:**

- **Repository**: <https://github.com/modelcontextprotocol/python-sdk>
- **Documentation**: <https://modelcontextprotocol.io/docs/develop/build-server>
- **Project Generator**: `modelcontextprotocol/create-python-server`
- **Contains**: Examples, guides, and best practices for Python MCP servers

**Installation (verified pattern)**:

 ```bash
# Create new project with uv (recommended)
uv init workflows-mcp
cd workflows-mcp
uv add "mcp[cli]"

# Or use the official generator
npx @modelcontextprotocol/create-server workflows-mcp
```python

**Basic Server Pattern (verified from official docs)**:

```python
from mcp.server.fastmcp import FastMCP

# Initialize server
mcp = FastMCP("workflows")

# Define a tool with decorator
@mcp.tool()
async def execute_workflow(workflow_name: str, inputs: dict) -> dict:
    """Execute a workflow with given inputs."""
    # Implementation
    return {"status": "success", "outputs": {}}

# Define a resource
@mcp.resource("workflow://list")
async def list_workflows() -> str:
    """List available workflows."""
    return '["workflow1", "workflow2"]'

# Define a prompt
@mcp.prompt()
def workflow_help(workflow_name: str) -> str:
    """Get help for a workflow."""
    return f"Help for {workflow_name}"

# Entry point for direct execution
def main():
    """Run the server."""
    mcp.run()  # Defaults to stdio transport

if __name__ == "__main__":
    main()
```

**When implementing MCP features:**

1. Use FastMCP built into the official SDK (not standalone FastMCP 2.0)
2. Leverage decorators: `@mcp.tool()`, `@mcp.resource()`, `@mcp.prompt()`
3. Use async functions for all handlers
4. Rely on type hints for automatic schema generation
5. Never write to stdout (use stderr for logging)

### MCP Server Best Practices (Official Guidelines)

**From Official Documentation**:

1. **Logging Rules** (Critical):
   - ⛔ **NEVER write to stdout** - MCP uses stdout for protocol communication
   - ✅ Use logging libraries that write to stderr: `logging`, `loguru`
   - ✅ Configure loggers to use stderr explicitly
   - ⛔ Avoid `print()` statements in production code

2. **Server Structure**:
   - Start simple: single `server.py` file
   - Organize into modules as complexity grows
   - Use decorators for all handlers
   - Keep server initialization minimal

3. **Tool Definitions**:
   - Use type hints for automatic schema generation
   - Write clear docstrings (become tool descriptions)
   - Prefer async functions for I/O operations
   - Return structured data (dicts, dataclasses, Pydantic models)

4. **Error Handling**:
   - Implement robust error handling in tools
   - Provide meaningful error messages
   - Use try-except for external API calls
   - Return error information in tool responses

5. **Development Workflow**:

   ```bash
   # Test during development with MCP Inspector
   uv run mcp dev server.py

   # Add dependencies for development
   uv run mcp dev server.py --with pandas --with numpy

   # Mount local code for live reloading
   uv run mcp dev server.py --with-editable .

   # Install in Claude Desktop
   uv run mcp install server.py

   # Install with custom name
   uv run mcp install server.py --name "My Workflow Server"

   # Install with environment variables
   uv run mcp install server.py -v API_KEY=abc123 -v DB_URL=postgres://...
   uv run mcp install server.py -f .env

   # Run directly
   uv run server.py
   python server.py
   ```

### Official MCP Project Structure

**Verified from**: `modelcontextprotocol/create-python-server` (official project generator)

**Philosophy from Official SDK**: "No configuration or complicated folder structures, only the files you need to run your server"

The official MCP Python SDK recommends a **minimal, simple structure**:

#### Start Simple: Single File Server

For most cases, start with a single `server.py` file:

```text
workflows-mcp/
├── server.py                  # All your tools, resources, prompts in one file
├── pyproject.toml             # uv project config (optional)
└── README.md                  # Documentation (optional)
```

#### Minimal Structure (Official Template)

When you need more organization, use the minimal structure from `create-python-server`:

```text
workflows-mcp/                  # MCP server project root
├── README.md
├── pyproject.toml             # uv-based project config
└── src/
    └── workflows_mcp/
        ├── __init__.py
        ├── __main__.py        # Entry point for uv run
        └── server.py          # Main server implementation
```

**Key principles from official SDK**:

- Start with single file, grow as needed
- Use `uv` for dependency management
- FastMCP is built into the SDK: `from mcp.server.fastmcp import FastMCP`
- Add structure only when complexity demands it

#### For Larger Projects

When your server grows complex, organize within `src/workflows_mcp/`:

```text
src/workflows_mcp/
├── __init__.py
├── __main__.py
├── server.py              # FastMCP initialization
├── tools.py               # Tool definitions (@mcp.tool())
├── resources.py           # Resource handlers (@mcp.resource())
├── prompts.py             # Prompt templates (@mcp.prompt())
└── workflows/             # Workflow engine logic
    ├── executor.py
    ├── dag.py
    └── templates.py
```

**Templates and configuration** (if needed):

```text
workflows-mcp/
├── templates/             # Optional: pre-packaged workflow templates
│   ├── python/
│   ├── node/
│   └── git/
└── tests/                 # Test suite
```

## Core Architecture

### Execution Model

The workflow engine follows a **declarative DAG-based execution model**:

1. **Workflow Definition** (YAML) → blocks with dependencies
2. **DAG Resolution** → topological sort determines execution order
3. **Variable Resolution** → cross-block references resolved from context
4. **Wave Execution** → blocks run in parallel waves based on dependencies
5. **Result Accumulation** → each block's output stored in shared context

### Key Components

**Core Engine** (`src/workflows_mcp/engine/`):

- `executor.py`: Workflow execution orchestrator, variable resolution, context management
- `dag.py`: Dependency resolution via Kahn's algorithm, parallel wave detection
- `block.py`: Abstract base class for workflow blocks with Pydantic validation
- `result.py`: Type-safe Result monad for error handling
- `variables.py`: Variable resolution and condition evaluation
- `schema.py`: YAML workflow schema definitions
- `loader.py`: Workflow loading from YAML files
- `registry.py`: Workflow registration and discovery

**Block System** (`src/workflows_mcp/engine/`):

- `blocks_bash.py`: BashCommand block for shell execution
- `blocks_file.py`: File operations (CreateFile, ReadFile, PopulateTemplate)
- `blocks_workflow.py`: ExecuteWorkflow block for workflow composition
- `blocks_example.py`: Example blocks (EchoBlock for testing)

**Entry Points**:

- `__main__.py`: CLI entry point for running the MCP server
- `server.py`: FastMCP server initialization
- `tools.py`: MCP tool implementations (execute_workflow, list_workflows, get_workflow_info)

### Variable Substitution System

Cross-block references use `${block_id.field}` syntax:

```yaml
blocks:
  - id: create_worktree
    type: CreateWorktree
    inputs:
      branch: "feature/new-feature"

  - id: create_file
    type: CreateFile
    inputs:
      path: "${create_worktree.worktree_path}/README.md"  # References previous block
    depends_on:
      - create_worktree
```

The engine resolves variables during execution by traversing the shared context dictionary.

## Development Commands

### Testing

Run the comprehensive test suite:

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=workflows_mcp --cov-report=term-missing

# Run specific test files
uv run pytest tests/test_schema_integration.py
uv run pytest tests/test_executor.py
uv run pytest tests/test_variables.py
```

### Code Quality

The project uses standard Python development tools:

```bash
# Type checking
uv run mypy src/workflows_mcp/

# Linting
uv run ruff check src/workflows_mcp/

# Formatting
uv run ruff format src/workflows_mcp/
```

## Adding New Blocks

Pattern for creating workflow blocks:

1. **Create Input/Output models** using Pydantic:

```python
class MyBlockInput(BlockInput):
    param: str = Field(description="Parameter description")

class MyBlockOutput(BlockOutput):
    result: str
    success: bool
```

2. **Implement WorkflowBlock**:

```python
class MyBlock(WorkflowBlock):
    def input_model(self) -> type[BlockInput]:
        return MyBlockInput

    def output_model(self) -> type[BlockOutput]:
        return MyBlockOutput

    def execute(self, context: Dict[str, Any]) -> Result[BlockOutput]:
        inputs = self._validated_inputs
        # Implement block logic
        return Result.success(MyBlockOutput(result="...", success=True))
```

3. **Register in BLOCK_REGISTRY** (`src/workflows_mcp/engine/block.py`):

```python
BLOCK_REGISTRY = {
    "MyBlock": MyBlock,
    # ... existing blocks
}
```

## Critical Design Patterns

### Result Type for Error Handling

All blocks return `Result[T]` instead of raising exceptions:

```python
from workflows_mcp.engine.result import Result

# Success case
return Result.success(output_object)

# Failure case
return Result.failure("Error description")

# With metadata
return Result.success(value, metadata={"execution_time": 1.23})
```

### Dependency Declaration

Blocks explicitly declare dependencies via `depends_on`:

```yaml
blocks:
  - id: step1
    type: SomeBlock

  - id: step2
    type: AnotherBlock
    depends_on:
      - step1  # step2 waits for step1
```

The DAGResolver validates and orders execution automatically.

### Git Worktree Pattern

The system extensively uses git worktrees for isolation:

```yaml
- id: create_worktree
  type: CreateWorktree
  inputs:
    path: ".worktrees/feature/my-feature"
    branch: "feature/my-feature"
    base_branch: "main"

# Use worktree path in subsequent blocks
- id: create_file
  type: CreateFile
  inputs:
    path: "${create_worktree.worktree_path}/new-file.txt"
    content: "File content"
  depends_on:
    - create_worktree
```

## System Architecture

See `ARCHITECTURE.md` for comprehensive system architecture documentation including:

- Core component design (DAGResolver, WorkflowExecutor, WorkflowBlock)
- Workflow execution model and parallel wave execution
- Variable resolution system
- Conditional execution
- Workflow composition patterns
- Block system architecture
- MCP integration
- Security model
- Error handling patterns

## Project Conventions

### MCP Development Standards

- **Python 3.12+** minimum version
- **uv for package management** - Fast, reliable Python package installer
- **Official Anthropic MCP SDK** - From <https://github.com/modelcontextprotocol/python-sdk>
- **Context7 for research** - Always verify library versions and APIs before coding
- **Pydantic v2** for all input/output validation
- **Type hints required** for all functions
- **Async/await patterns** - Follow SDK async examples

### General Standards

- **Git conventional commits** for semantic versioning
- **Worktree-based development** for isolated feature work
- **YAGNI principle** - Don't build features until needed
- **Templates over custom code** - Favor reusable workflow templates
- **MCP protocol compliance** - All tools must follow MCP specifications

### Custom Workflow Templates

Users can extend the workflow library with custom templates:

**Configuration**:

```bash
export WORKFLOWS_TEMPLATE_PATHS="~/my-workflows,/opt/team-workflows"
```

Or in `.mcp.json`:

```json
{
  "mcpServers": {
    "workflows": {
      "command": "uvx",
      "args": ["--from", "workflows-mcp", "workflows-mcp"],
      "env": {
        "WORKFLOWS_TEMPLATE_PATHS": "~/my-workflows,/opt/team-workflows"
      }
    }
  }
}
```

**Priority System**:

- Built-in templates load first
- User templates override built-in templates by name
- Later directories override earlier directories

**Use Cases**:

- **Personal customizations**: `~/my-workflows/`
- **Team-specific workflows**: `/opt/company-workflows/`
- **Override built-in**: Create `~/my-workflows/python-ci-pipeline.yaml` to replace built-in

**Source Tracking**: Use `WorkflowRegistry.get_workflow_source(name)` to see where each workflow came from

## File Organization

Current project structure:

```text
src/workflows_mcp/
├── __init__.py              # Package initialization
├── __main__.py              # Entry point (uv run workflows-mcp)
├── server.py                # FastMCP server initialization
├── tools.py                 # MCP tool implementations
├── templates/               # Built-in workflow templates
│   ├── ci/                  # CI/CD workflows
│   ├── examples/            # Tutorial workflows
│   ├── files/               # File processing
│   ├── git/                 # Git operations
│   ├── node/                # Node.js workflows
│   └── python/              # Python workflows
└── engine/                  # Workflow engine
    ├── __init__.py          # Engine exports
    ├── dag.py               # DAG dependency resolution
    ├── result.py            # Result monad
    ├── block.py             # WorkflowBlock base class
    ├── blocks_bash.py       # BashCommand block
    ├── blocks_file.py       # File operation blocks
    ├── blocks_workflow.py   # ExecuteWorkflow block
    ├── blocks_example.py    # Example blocks (EchoBlock)
    ├── variables.py         # Variable resolution & conditionals
    ├── executor.py          # Workflow executor
    ├── schema.py            # YAML workflow schema
    ├── loader.py            # YAML workflow loader
    └── registry.py          # Workflow registry
```

## Important Implementation Notes

- **Context is mutable**: Each block can read from and write to the shared context
- **Blocks are stateless**: No shared state between block instances
- **Validation happens twice**: Input validation before execution, output validation after
- **Variable resolution is lazy**: Variables resolved at execution time, not load time
- **Cyclic dependencies fail fast**: DAG resolver detects cycles before execution starts
- **Wave execution**: Blocks in the same dependency wave execute in parallel

## When Working on This Project

### MCP Development (Primary Focus)

1. **Use Context7 FIRST** - Before any code, research libraries and patterns via Context7 MCP tool
2. **Follow Anthropic Python MCP SDK** - Use official SDK from <https://github.com/modelcontextprotocol/python-sdk>
3. **Read ARCHITECTURE.md** for strategic context and MCP roadmap
4. **MCP-compliant implementations** - Tools, resources, and prompts must follow MCP specifications
5. **Type safety** - Pydantic models for all MCP tool inputs/outputs
6. **Async-first** - Use async/await patterns from SDK examples
7. **Templates over custom code** - Favor reusable workflow templates
