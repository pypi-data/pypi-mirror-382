# Interactive Blocks Tutorial

## Introduction

Interactive blocks enable workflows to pause execution and request input from the LLM (Large Language Model) before continuing. This creates human-in-the-loop workflows where critical decisions, confirmations, or data collection can be handled interactively.

**Key Capabilities**:
- ✅ Pause workflow execution at any block
- ✅ Request LLM input with custom prompts
- ✅ Automatic checkpoint creation at pause points
- ✅ Resume workflows with LLM responses
- ✅ Multiple pause/resume cycles in a single workflow
- ✅ Context preservation across pauses

**Common Use Cases**:
- Deployment approvals before production changes
- Configuration wizards with multiple questions
- Data validation and correction workflows
- Conditional branching based on user decisions
- Risk assessment and manual override points

## Available Interactive Blocks

The workflow engine provides three built-in interactive block types:

### 1. ConfirmOperation

**Purpose**: Yes/no confirmation dialogs for critical operations.

**Input Parameters**:
- `message` (string, required): Confirmation message to display
- `operation` (string, required): Name of operation being confirmed
- `details` (dict, optional): Additional context information

**Output Fields**:
- `confirmed` (boolean): `true` if LLM approved, `false` otherwise
- `response` (string): Full LLM response text

**Accepted Responses**:
- **Yes**: "yes", "y", "true", "confirm", "approved"
- **No**: Anything else (including "no", "n", "false", "cancel", "denied")

**Example**:
```yaml
- id: confirm_deploy
  type: ConfirmOperation
  inputs:
    message: "Deploy to production?"
    operation: "production_deployment"
    details:
      environment: "production"
      version: "v2.1.0"
```

**Workflow Behavior**:
1. Block executes and returns `Result.pause()` with prompt
2. Executor creates checkpoint and halts workflow
3. Returns pause information to MCP tool caller
4. LLM provides response via `resume_workflow()`
5. Block's `resume()` method processes response
6. Workflow continues with `confirmed` output in context

---

### 2. AskChoice

**Purpose**: Multiple choice selection from predefined options.

**Input Parameters**:
- `question` (string, required): Question to ask
- `choices` (list[string], required): List of available choices

**Output Fields**:
- `choice` (string): Selected choice text
- `choice_index` (int): Zero-based index of selected choice

**Accepted Response Formats**:
- **By number**: "1", "2", "3" (1-indexed, matches displayed list)
- **By text**: "production", "staging" (case-insensitive match)

**Example**:
```yaml
- id: select_environment
  type: AskChoice
  inputs:
    question: "Select deployment environment:"
    choices:
      - "development"
      - "staging"
      - "production"
```

**Prompt Display**:
```sql
Select deployment environment:

Choices:
1. development
2. staging
3. production

Respond with the number of your choice.
```

**Response Processing**:
- If LLM responds with "2" → choice="staging", choice_index=1
- If LLM responds with "production" → choice="production", choice_index=2
- Invalid responses return `Result.failure()`

---

### 3. GetInput

**Purpose**: Free-form text input with optional validation.

**Input Parameters**:
- `prompt` (string, required): Prompt text for LLM
- `validation_pattern` (string, optional): Regex pattern for validation

**Output Fields**:
- `input_value` (string): Input provided by LLM

**Example**:
```yaml
- id: get_project_name
  type: GetInput
  inputs:
    prompt: "Enter project name (lowercase, hyphens allowed):"
    validation_pattern: "^[a-z0-9-]+$"
```

**Validation Behavior**:
- If `validation_pattern` is set, input must match regex
- Failed validation returns `Result.failure()` with error message
- Workflow can be resumed again with corrected input

---

## How Pause/Resume Works

### Execution Flow

```sql
┌─────────────────────────────────────────────────────────────────────┐
│ Workflow Execution                                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Block 1 (Normal) ──✓──> Context Updated ──> Block 2 (Interactive) │
│                                                  │                  │
│                                                  ▼                  │
│                                         Result.pause() returned     │
│                                                  │                  │
│                                                  ▼                  │
│                                    Executor detects pause           │
│                                                  │                  │
│                                                  ▼                  │
│                              Create CheckpointState                 │
│                              ├─ workflow_name                      │
│                              ├─ completed_blocks: [block1]         │
│                              ├─ current_wave_index: 1              │
│                              ├─ paused_block_id: block2            │
│                              ├─ pause_prompt: "Confirm...?"        │
│                              └─ context: {serialized context}      │
│                                                  │                  │
│                                                  ▼                  │
│                              Save to CheckpointStore                │
│                              checkpoint_id = "pause_abc123"        │
│                                                  │                  │
│                                                  ▼                  │
│                              Return to MCP caller                   │
│                              {                                      │
│                                status: "paused",                    │
│                                checkpoint_id: "pause_abc123",      │
│                                prompt: "Confirm...?"                │
│                              }                                      │
│                                                                     │
│  ═══════════════════════ Workflow Paused ═══════════════════════   │
│                                                                     │
│  Later: resume_workflow("pause_abc123", "yes")                     │
│                                                  │                  │
│                                                  ▼                  │
│                              Load CheckpointState                   │
│                                                  │                  │
│                                                  ▼                  │
│                              Restore context                        │
│                              Restore workflow_stack                 │
│                                                  │                  │
│                                                  ▼                  │
│                              Call block2.resume(                    │
│                                context,                             │
│                                llm_response="yes",                  │
│                                pause_metadata                       │
│                              )                                      │
│                                                  │                  │
│                                                  ▼                  │
│                              Result.success() returned              │
│                              output: {confirmed: true}              │
│                                                  │                  │
│                                                  ▼                  │
│                              Update context with output             │
│                              completed_blocks.append(block2)        │
│                                                  │                  │
│                                                  ▼                  │
│  Block 3 (Normal) ──✓──> Continue execution...                     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Key Concepts

**1. Automatic Checkpointing**

When a block returns `Result.pause()`:
- Executor automatically creates a `CheckpointState` snapshot
- Saves: context, completed blocks, execution waves, paused block info
- Generates unique checkpoint_id (format: `pause_<uuid>`)
- Returns immediately without continuing execution

**2. Context Preservation**

All workflow state is serialized and saved:
- Variable values from previous blocks
- Block outputs (success/failure, exit codes, outputs)
- Workflow stack (for nested workflows)
- Runtime inputs

Non-serializable values are filtered:
- `__executor__` reference (reconstructed on resume)
- Custom objects converted to dicts
- Path objects converted to strings

**3. Resume Process**

When `resume_workflow(checkpoint_id, llm_response)` is called:
1. Load `CheckpointState` from store
2. Validate workflow is loaded in executor
3. Deserialize and restore context
4. Find paused block and instantiate it
5. Call `block.resume(context, llm_response, pause_metadata)`
6. Process result (success, failure, or pause again)
7. Continue execution from next wave

**4. Multiple Pauses**

A single workflow can pause multiple times:
- Each pause creates a new checkpoint
- Each resume continues from that specific pause point
- Previous checkpoints remain valid (can branch back)
- Final workflow completion returns all outputs

---

## Example Workflows

### Example 1: Deployment Approval

**Scenario**: Run tests, pause for approval, deploy if approved.

```yaml
name: deployment-approval
description: Deploy with human approval

inputs:
  environment:
    type: string
    default: "production"

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
      message: "Tests passed. Deploy to ${environment}?"
      operation: "deploy_to_${environment}"
      details:
        test_exit_code: "${run_tests.exit_code}"
    depends_on: [run_tests]
    condition: "${run_tests.exit_code} == 0"

  # Deploy only if approved
  - id: deploy
    type: BashCommand
    inputs:
      command: "kubectl apply -f k8s/"
    depends_on: [confirm_deploy]
    condition: "${confirm_deploy.confirmed} == true"

  # Notify result
  - id: notify
    type: BashCommand
    inputs:
      command: |
        if [ "${deploy.success}" == "true" ]; then
          echo "✅ Deployment successful"
        else
          echo "❌ Deployment cancelled"
        fi
    depends_on: [deploy]
```

**Usage**:
```python
# Execute workflow
result = execute_workflow("deployment-approval", {"environment": "production"})

# Result: {"status": "paused", "checkpoint_id": "pause_abc", "prompt": "..."}

# Approve deployment
result = resume_workflow("pause_abc", "yes")

# Result: {"status": "success", "outputs": {...}}
```

---

### Example 2: Configuration Wizard

**Scenario**: Collect multiple configuration values through questions.

```yaml
name: config-wizard
description: Interactive configuration setup

blocks:
  # Question 1: Select database
  - id: select_database
    type: AskChoice
    inputs:
      question: "Select database type:"
      choices: ["PostgreSQL", "MySQL", "MongoDB"]

  # Question 2: Get database name
  - id: get_db_name
    type: GetInput
    inputs:
      prompt: "Enter database name (alphanumeric only):"
      validation_pattern: "^[a-zA-Z0-9_]+$"
    depends_on: [select_database]

  # Question 3: Confirm setup
  - id: confirm_setup
    type: ConfirmOperation
    inputs:
      message: |
        Create database with these settings?
        - Type: ${select_database.choice}
        - Name: ${get_db_name.input_value}
      operation: "create_database"
    depends_on: [get_db_name]

  # Create configuration file
  - id: create_config
    type: CreateFile
    inputs:
      path: "./config.json"
      content: |
        {
          "database": {
            "type": "${select_database.choice}",
            "name": "${get_db_name.input_value}"
          }
        }
    depends_on: [confirm_setup]
    condition: "${confirm_setup.confirmed} == true"

outputs:
  database_type: "${select_database.choice}"
  database_name: "${get_db_name.input_value}"
  config_created: "${create_config.success}"
```

**Usage Flow**:
```python
# Step 1: Start workflow
result1 = execute_workflow("config-wizard")
# → Pauses at select_database
# → checkpoint_id="pause_001", prompt="Select database type..."

# Step 2: Select database
result2 = resume_workflow("pause_001", "1")  # PostgreSQL
# → Pauses at get_db_name
# → checkpoint_id="pause_002", prompt="Enter database name..."

# Step 3: Enter name
result3 = resume_workflow("pause_002", "my_app_db")
# → Pauses at confirm_setup
# → checkpoint_id="pause_003", prompt="Create database...?"

# Step 4: Confirm
result4 = resume_workflow("pause_003", "yes")
# → Completes workflow
# → status="success", outputs={...}
```

---

## Best Practices

### 1. Clear Prompts

**Good**:
```yaml
message: "Deploy v2.1.0 to production? This will affect 10,000 users."
```

**Bad**:
```yaml
message: "Deploy?"  # Too vague
```

**Tips**:
- Include context (what, where, impact)
- State expected responses clearly
- Add consequences/risks if relevant

---

### 2. Validate Input

Use `validation_pattern` for GetInput blocks:

```yaml
# Email validation
- id: get_email
  type: GetInput
  inputs:
    prompt: "Enter email address:"
    validation_pattern: "^[\\w\\.-]+@[\\w\\.-]+\\.\\w+$"

# Semantic version validation
- id: get_version
  type: GetInput
  inputs:
    prompt: "Enter version (e.g., 1.2.3):"
    validation_pattern: "^\\d+\\.\\d+\\.\\d+$"
```

---

### 3. Conditional Pauses

Only pause when necessary:

```yaml
# Pause for approval only if tests pass
- id: confirm_deploy
  type: ConfirmOperation
  inputs:
    message: "Deploy to production?"
    operation: "production_deploy"
  depends_on: [run_tests]
  condition: "${run_tests.exit_code} == 0"  # Skip if tests fail
```

---

### 4. Meaningful Details

Provide context in `details` field:

```yaml
- id: confirm_deploy
  type: ConfirmOperation
  inputs:
    message: "Deploy to production?"
    operation: "production_deploy"
    details:
      version: "v2.1.0"
      environment: "production"
      test_results: "${run_tests.stdout}"
      risk_level: "medium"
```

---

### 5. Handle Denial

Always handle negative responses:

```yaml
blocks:
  - id: confirm_action
    type: ConfirmOperation
    inputs:
      message: "Proceed with action?"
      operation: "risky_action"

  # Success path
  - id: do_action
    type: BashCommand
    inputs:
      command: "perform_action.sh"
    depends_on: [confirm_action]
    condition: "${confirm_action.confirmed} == true"

  # Denial path
  - id: log_cancellation
    type: BashCommand
    inputs:
      command: "echo 'Action cancelled by user'"
    depends_on: [confirm_action]
    condition: "${confirm_action.confirmed} == false"
```

---

### 6. Choice Ordering

Order choices from most to least common:

```yaml
# Good - most common first
choices: ["development", "staging", "production"]

# Bad - alphabetical but least common first
choices: ["production", "staging", "development"]
```

---

### 7. Checkpoint Cleanup

Clean up completed paused workflows:

```python
# After workflow completes successfully
if result.is_success:
    # Delete checkpoint to save space
    delete_checkpoint(checkpoint_id)
```

Or use automatic cleanup:
```python
executor = WorkflowExecutor(
    checkpoint_config=CheckpointConfig(
        auto_cleanup=True,
        max_per_workflow=10
    )
)
```

---

## Troubleshooting

### Issue: "Checkpoint not found"

**Cause**: Checkpoint expired or was deleted.

**Solutions**:
- Check checkpoint TTL setting (default: 24 hours)
- List checkpoints: `list_checkpoints()` to verify it exists
- Paused checkpoints don't expire by default

---

### Issue: "Invalid choice: XYZ"

**Cause**: LLM response doesn't match any choice.

**Solutions**:
- Ensure prompt clearly states expected format
- Use numbered responses (more reliable)
- Check for typos in choice text

Example fix:
```yaml
# Before (unclear)
prompt: "Pick one: dev, staging, prod"

# After (clear)
prompt: |
  Select deployment environment:
  1. development
  2. staging
  3. production

  Respond with the number (1-3)
```

---

### Issue: "Input doesn't match pattern"

**Cause**: LLM response failed regex validation.

**Solutions**:
- Provide example in prompt
- Simplify validation pattern
- Allow workflow to be resumed with corrected input

Example fix:
```yaml
# Before (no example)
prompt: "Enter project name:"
validation_pattern: "^[a-z0-9-]+$"

# After (with example)
prompt: |
  Enter project name (lowercase letters, numbers, hyphens only):
  Example: my-awesome-project
validation_pattern: "^[a-z0-9-]+$"
```

---

### Issue: Nested workflow pause not visible

**Cause**: Pause in child workflow not propagated to parent.

**Verification**:
```yaml
# Parent workflow
- id: run_child
  type: ExecuteWorkflow
  inputs:
    workflow: "child-with-pause"

# This SHOULD pause the parent workflow too
```

**Expected Behavior**:
- Child pause propagates to parent automatically
- Parent checkpoint contains `child_checkpoint_id`
- Resume parent → resumes child → continues parent

**If not working**: Check that child workflow block is actually interactive.

---

## Advanced Patterns

### Pattern 1: Multi-Stage Approval

Require multiple approvals for high-risk operations:

```yaml
blocks:
  - id: manager_approval
    type: ConfirmOperation
    inputs:
      message: "Manager: Approve production deploy?"
      operation: "manager_approval"

  - id: security_approval
    type: ConfirmOperation
    inputs:
      message: "Security: Approve production deploy?"
      operation: "security_approval"
    depends_on: [manager_approval]
    condition: "${manager_approval.confirmed} == true"

  - id: deploy
    type: BashCommand
    inputs:
      command: "deploy.sh production"
    depends_on: [security_approval]
    condition: "${security_approval.confirmed} == true"
```

Usage: Requires TWO resume calls, both with "yes".

---

### Pattern 2: Validation Loop

Re-prompt until valid input is provided:

```yaml
blocks:
  - id: get_input
    type: GetInput
    inputs:
      prompt: "Enter email:"
      validation_pattern: "^[\\w\\.-]+@[\\w\\.-]+\\.\\w+$"

  # If validation fails, workflow fails
  # User can call resume_workflow again with corrected input
```

The block's `resume()` method validates input and returns failure if invalid. The workflow can be resumed repeatedly until valid input is provided.

---

### Pattern 3: Conditional Questions

Ask follow-up questions based on previous answers:

```yaml
blocks:
  - id: select_deployment
    type: AskChoice
    inputs:
      question: "Deployment type?"
      choices: ["Cloud", "On-Premise"]

  # Only ask for cloud provider if Cloud was selected
  - id: select_cloud_provider
    type: AskChoice
    inputs:
      question: "Cloud provider?"
      choices: ["AWS", "GCP", "Azure"]
    depends_on: [select_deployment]
    condition: "${select_deployment.choice} == 'Cloud'"

  # Only ask for on-premise details if On-Premise was selected
  - id: get_datacenter
    type: GetInput
    inputs:
      prompt: "Enter datacenter location:"
    depends_on: [select_deployment]
    condition: "${select_deployment.choice} == 'On-Premise'"
```

---

### Pattern 4: Abort on Deny

Stop workflow if critical confirmation is denied:

```yaml
blocks:
  - id: confirm_destructive
    type: ConfirmOperation
    inputs:
      message: "⚠️  WARNING: This will delete all data. Continue?"
      operation: "delete_all_data"

  - id: delete_data
    type: BashCommand
    inputs:
      command: "rm -rf /data/*"
    depends_on: [confirm_destructive]
    condition: "${confirm_destructive.confirmed} == true"

  # No further blocks after denial
  # Workflow ends with confirm_destructive.confirmed = false
```

---

## MCP Tool Integration

Interactive blocks work seamlessly with MCP tools:

### Tool: execute_workflow

Starts a workflow, may return pause:

```javascript
const result = await execute_workflow({
  workflow: "deployment-approval",
  inputs: { environment: "production" }
});

if (result.status === "paused") {
  console.log("Workflow paused");
  console.log("Checkpoint ID:", result.checkpoint_id);
  console.log("Prompt:", result.prompt);
  // Save checkpoint_id for later resume
}
```

---

### Tool: resume_workflow

Continues a paused workflow:

```javascript
const result = await resume_workflow({
  checkpoint_id: "pause_abc123",
  llm_response: "yes"
});

if (result.status === "paused") {
  console.log("Paused again at different block");
  // Multiple pauses possible
} else if (result.status === "success") {
  console.log("Workflow completed");
  console.log("Outputs:", result.outputs);
}
```

---

### Tool: list_checkpoints

View all paused workflows:

```javascript
const result = await list_checkpoints({
  workflow_name: "deployment-approval"  // Optional filter
});

result.checkpoints.forEach(cp => {
  console.log(`${cp.checkpoint_id}: ${cp.workflow} - ${cp.pause_prompt}`);
  console.log(`  Created: ${cp.created_at_iso}`);
  console.log(`  Paused: ${cp.is_paused}`);
});
```

---

### Tool: get_checkpoint_info

Get detailed checkpoint information:

```javascript
const info = await get_checkpoint_info({
  checkpoint_id: "pause_abc123"
});

console.log("Workflow:", info.workflow_name);
console.log("Progress:", `${info.progress_percentage}%`);
console.log("Completed blocks:", info.completed_blocks);
console.log("Paused at block:", info.paused_block_id);
console.log("Prompt:", info.pause_prompt);
```

---

### Tool: delete_checkpoint

Clean up completed checkpoints:

```javascript
await delete_checkpoint({
  checkpoint_id: "pause_abc123"
});
```

---

## Creating Custom Interactive Blocks

You can create your own interactive blocks by extending `InteractiveBlock`:

### Step 1: Define Input/Output Models

```python
from pydantic import Field
from workflows_mcp.engine.block import BlockInput, BlockOutput

class MyInteractiveInput(BlockInput):
    prompt: str = Field(description="Custom prompt")
    options: dict[str, str] = Field(description="Custom options")

class MyInteractiveOutput(BlockOutput):
    selected_option: str = Field(description="User selection")
    metadata: dict[str, Any] = Field(default_factory=dict)
```

---

### Step 2: Implement InteractiveBlock

```python
from workflows_mcp.engine.interactive import InteractiveBlock
from workflows_mcp.engine.result import Result

class MyInteractiveBlock(InteractiveBlock):
    def input_model(self) -> type[BlockInput]:
        return MyInteractiveInput

    def output_model(self) -> type[BlockOutput]:
        return MyInteractiveOutput

    async def execute(self, context: dict[str, Any]) -> Result[BlockOutput]:
        """Initial execution - return Result.pause()"""
        inputs = self._validated_inputs

        # Create custom prompt
        prompt = f"{inputs.prompt}\n\nOptions:\n"
        for key, desc in inputs.options.items():
            prompt += f"  {key}: {desc}\n"

        # Pause workflow
        return Result.pause(
            prompt=prompt,
            checkpoint_id="",  # Filled by executor
            options=inputs.options  # Save for resume
        )

    async def resume(
        self,
        context: dict[str, Any],
        llm_response: str,
        pause_metadata: dict[str, Any]
    ) -> Result[BlockOutput]:
        """Resume execution with LLM response"""
        options = pause_metadata["options"]

        # Validate response
        response = llm_response.strip()
        if response not in options:
            return Result.failure(f"Invalid option: {response}")

        # Return success
        return Result.success(MyInteractiveOutput(
            selected_option=response,
            metadata={"original_options": options}
        ))
```

---

### Step 3: Register Block

```python
from workflows_mcp.engine.block import BLOCK_REGISTRY

BLOCK_REGISTRY.register("MyInteractiveBlock", MyInteractiveBlock)
```

---

### Step 4: Use in Workflows

```yaml
blocks:
  - id: custom_prompt
    type: MyInteractiveBlock
    inputs:
      prompt: "Select configuration mode:"
      options:
        simple: "Simple mode with defaults"
        advanced: "Advanced mode with customization"
        expert: "Expert mode with all options"
```

---

## Performance Considerations

### Checkpoint Storage

- **In-Memory**: Fast (< 1ms), limited by RAM
- **SQLite**: Moderate (10-50ms), disk-limited
- **PostgreSQL**: Network latency, highly scalable

For production: Use SQLite or PostgreSQL (see `DATABASE_MIGRATION.md`).

---

### Checkpoint Size

Checkpoints include full context. Large contexts impact:
- Storage space
- Serialization time
- Network transfer (if using remote DB)

**Optimization**:
```python
# Limit checkpoint size
checkpoint_config = CheckpointConfig(
    max_checkpoint_size_mb=10.0
)
```

---

### Cleanup Strategy

Configure automatic cleanup:
```python
checkpoint_config = CheckpointConfig(
    auto_cleanup=True,
    max_per_workflow=10,  # Keep last 10 per workflow
    ttl_seconds=86400,     # 24 hours for automatic checkpoints
    keep_paused=True       # Never auto-delete paused checkpoints
)
```

---

## Related Documentation

- **Architecture**: `CHECKPOINT_ARCHITECTURE.md` - Complete technical design
- **Database Migration**: `DATABASE_MIGRATION.md` - SQLite/PostgreSQL setup
- **Quick Start**: `CHECKPOINT_QUICKSTART.md` - TDD implementation guide
- **Example Workflows**:
  - `templates/examples/interactive-approval.yaml`
  - `templates/examples/multi-step-questionnaire.yaml`

---

## Questions?

- Architecture details → `CHECKPOINT_ARCHITECTURE.md`
- Implementation guide → `CHECKPOINT_QUICKSTART.md`
- Database setup → `DATABASE_MIGRATION.md`
- Project conventions → `CLAUDE.md`, `ARCHITECTURE.md`
