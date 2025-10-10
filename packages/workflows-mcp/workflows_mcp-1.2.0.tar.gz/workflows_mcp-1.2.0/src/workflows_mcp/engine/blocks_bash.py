"""BashCommand block for executing shell commands in workflows."""

import asyncio
import json
import os
import shlex
import time
from pathlib import Path
from typing import Any, cast

from pydantic import Field

from .block import BLOCK_REGISTRY, BlockInput, BlockOutput, WorkflowBlock
from .result import Result


class OutputSecurityError(Exception):
    """Raised when output path violates security constraints."""

    pass


class OutputNotFoundError(Exception):
    """Raised when output file not found."""

    pass


def validate_output_path(
    output_name: str, path: str, working_dir: Path, unsafe: bool = False
) -> Path:
    """
    Validate output file path with security checks.

    Security rules:
    - Safe mode (default): Relative paths only, within working_dir
    - Unsafe mode (opt-in): Allows absolute paths
    - Always: No symlinks, size limit (10MB), no path traversal

    Args:
        output_name: Name of the output (for error messages)
        path: File path to validate (can contain env vars)
        working_dir: Working directory for relative paths
        unsafe: Allow absolute paths (default: False)

    Returns:
        Validated absolute Path

    Raises:
        OutputSecurityError: If path violates security constraints
        OutputNotFoundError: If file doesn't exist
    """
    # Expand environment variables
    expanded_path = os.path.expandvars(path)

    # Convert to Path object
    file_path = Path(expanded_path)

    # Security check: reject absolute paths in safe mode
    if file_path.is_absolute() and not unsafe:
        raise OutputSecurityError(
            f"Output '{output_name}': Absolute paths not allowed in safe mode. "
            f"Path: {path}. Set 'unsafe: true' to allow absolute paths."
        )

    # Build absolute path (without resolving symlinks yet)
    if file_path.is_absolute():
        absolute_path = file_path
    else:
        absolute_path = working_dir / file_path

    # Check file exists
    if not absolute_path.exists():
        raise OutputNotFoundError(
            f"Output '{output_name}': File not found at {absolute_path}"
        )

    # Security check: no symlinks (check before resolving)
    if absolute_path.is_symlink():
        raise OutputSecurityError(
            f"Output '{output_name}': Symlinks not allowed for security. Path: {absolute_path}"
        )

    # Now resolve the path (follow any remaining symlinks in parent directories)
    resolved_path = absolute_path.resolve()

    # Security check: no path traversal outside working_dir in safe mode
    if not unsafe:
        try:
            resolved_path.relative_to(working_dir.resolve())
        except ValueError:
            raise OutputSecurityError(
                f"Output '{output_name}': Path escapes working directory. "
                f"Path: {path}, Resolved: {resolved_path}, Working dir: {working_dir}"
            )

    # Security check: must be a file
    if not resolved_path.is_file():
        raise OutputSecurityError(
            f"Output '{output_name}': Path is not a file. Path: {resolved_path}"
        )

    # Security check: size limit (10MB)
    max_size = 10 * 1024 * 1024  # 10MB
    file_size = resolved_path.stat().st_size
    if file_size > max_size:
        raise OutputSecurityError(
            f"Output '{output_name}': File too large ({file_size} bytes, max {max_size} bytes). "
            f"Path: {resolved_path}"
        )

    return resolved_path


def parse_output_value(content: str, output_type: str) -> Any:
    """
    Parse file content according to declared type.

    Args:
        content: Raw file content
        output_type: One of: string, int, float, bool, json

    Returns:
        Parsed value with correct Python type

    Raises:
        ValueError: If content doesn't match declared type
    """
    content = content.strip()

    if output_type == "string":
        return content
    elif output_type == "int":
        try:
            return int(content)
        except ValueError:
            raise ValueError(f"Cannot parse as int: {content}")
    elif output_type == "float":
        try:
            return float(content)
        except ValueError:
            raise ValueError(f"Cannot parse as float: {content}")
    elif output_type == "bool":
        # Accept: true/false, 1/0, yes/no (case-insensitive)
        lower = content.lower()
        if lower in ["true", "1", "yes"]:
            return True
        elif lower in ["false", "0", "no"]:
            return False
        else:
            raise ValueError(
                f"Cannot parse as bool: {content}. "
                f"Accepted values: true/false, 1/0, yes/no (case-insensitive)"
            )
    elif output_type == "json":
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Cannot parse as JSON: {e}")
    else:
        raise ValueError(f"Unknown output type: {output_type}")


class BashCommandInput(BlockInput):
    """Input for BashCommand block."""

    command: str = Field(description="Bash command to execute")
    working_dir: str = Field(default="", description="Working directory (empty = current dir)")
    timeout: int = Field(default=120, description="Timeout in seconds")
    env: dict[str, str] = Field(default_factory=dict, description="Environment variables")
    capture_output: bool = Field(default=True, description="Capture stdout/stderr")
    shell: bool = Field(default=True, description="Execute via shell")
    check_returncode: bool = Field(
        default=True, description="Treat non-zero exit codes as failures"
    )


class BashCommandOutput(BlockOutput):
    """Output for BashCommand block."""

    exit_code: int = Field(description="Process exit code")
    stdout: str = Field(description="Standard output")
    stderr: str = Field(description="Standard error")
    success: bool = Field(description="Whether command succeeded")
    command_executed: str = Field(description="The command that was executed")
    execution_time_ms: float = Field(description="Execution time in milliseconds")
    custom_outputs: dict[str, Any] = Field(
        default_factory=dict, description="Custom file-based outputs"
    )


class BashCommand(WorkflowBlock):
    """
    Execute bash command with timeout and output capture.

    Features:
    - Async subprocess execution
    - Timeout support
    - Environment variable injection
    - Working directory control
    - Output capture (stdout/stderr)
    - Shell/direct execution modes
    - Exit code validation
    - Custom file-based outputs
    - Scratch directory management

    Example YAML usage:
        - id: run_tests
          type: BashCommand
          inputs:
            command: "pytest tests/ -v --cov=src"
            working_dir: "/path/to/project"
            timeout: 300
            env:
              PYTHONPATH: "/path/to/project/src"
              CI: "true"
          outputs:
            test_results:
              type: json
              path: "$SCRATCH/results.json"
              description: "Test execution results"
    """

    # Instance attribute for custom outputs
    outputs: dict[str, Any] | None

    def __init__(
        self,
        id: str,
        inputs: dict[str, Any],
        depends_on: list[str] | None = None,
        outputs: dict[str, Any] | None = None,
    ):
        """Initialize BashCommand with optional outputs."""
        super().__init__(id, inputs, depends_on)
        self.outputs = outputs

    def input_model(self) -> type[BlockInput]:
        return BashCommandInput

    def output_model(self) -> type[BlockOutput]:
        return BashCommandOutput

    async def execute(self, context: dict[str, Any]) -> Result[BlockOutput]:
        """Execute bash command asynchronously."""
        inputs = cast(BashCommandInput, self._validated_inputs)
        if inputs is None:
            return Result.failure("Inputs not validated")

        start = time.time()

        try:
            # Prepare working directory
            cwd = Path(inputs.working_dir) if inputs.working_dir else Path.cwd()
            if not cwd.exists():
                return Result.failure(f"Working directory does not exist: {cwd}")

            # Setup scratch directory
            scratch_dir = cwd / ".scratch"
            scratch_dir.mkdir(exist_ok=True, mode=0o700)

            # Update .gitignore if it exists
            gitignore = cwd / ".gitignore"
            if gitignore.exists():
                content = gitignore.read_text()
                if ".scratch/" not in content:
                    with gitignore.open("a") as f:
                        f.write("\n.scratch/\n")

            # Prepare environment with SCRATCH
            env = dict(os.environ)
            if inputs.env:
                env.update(inputs.env)
            env["SCRATCH"] = ".scratch"

            # Execute command
            if inputs.shell:
                # Execute via shell (supports pipes, redirects, etc.)
                process = await asyncio.create_subprocess_shell(
                    inputs.command,
                    stdout=asyncio.subprocess.PIPE if inputs.capture_output else None,
                    stderr=asyncio.subprocess.PIPE if inputs.capture_output else None,
                    cwd=cwd,
                    env=env,
                )
            else:
                # Execute directly (safer, but no shell features)
                args = shlex.split(inputs.command)
                process = await asyncio.create_subprocess_exec(
                    *args,
                    stdout=asyncio.subprocess.PIPE if inputs.capture_output else None,
                    stderr=asyncio.subprocess.PIPE if inputs.capture_output else None,
                    cwd=cwd,
                    env=env,
                )

            # Wait for completion with timeout
            try:
                stdout_bytes, stderr_bytes = await asyncio.wait_for(
                    process.communicate(), timeout=inputs.timeout
                )
            except TimeoutError:
                process.kill()
                await process.wait()
                return Result.failure(
                    f"Command timed out after {inputs.timeout} seconds: {inputs.command}"
                )

            # Decode output
            stdout = stdout_bytes.decode("utf-8") if stdout_bytes else ""
            stderr = stderr_bytes.decode("utf-8") if stderr_bytes else ""
            exit_code = process.returncode or 0

            execution_time = (time.time() - start) * 1000  # Convert to ms

            # Determine success
            success = exit_code == 0 if inputs.check_returncode else True

            # Read custom outputs (if declared)
            custom_outputs: dict[str, Any] = {}
            if self.outputs:
                # Set SCRATCH for path expansion
                original_env = os.environ.get("SCRATCH")
                os.environ["SCRATCH"] = ".scratch"

                try:
                    for output_name, output_schema in self.outputs.items():
                        try:
                            # Validate path
                            file_path = validate_output_path(
                                output_name,
                                output_schema["path"],
                                cwd,
                                output_schema.get("unsafe", False),
                            )

                            # Read file
                            content = file_path.read_text()

                            # Parse type
                            value = parse_output_value(content, output_schema["type"])

                            # TODO: Validate with expression if provided
                            # if output_schema.get("validation"):
                            #     # Use ConditionEvaluator to validate
                            #     pass

                            custom_outputs[output_name] = value

                        except (OutputSecurityError, OutputNotFoundError, ValueError) as e:
                            if output_schema.get("required", True):
                                return Result.failure(f"Output '{output_name}' error: {e}")
                            # Optional output, continue without it
                finally:
                    # Restore original environment
                    if original_env is not None:
                        os.environ["SCRATCH"] = original_env
                    elif "SCRATCH" in os.environ:
                        del os.environ["SCRATCH"]

            output = BashCommandOutput(
                exit_code=exit_code,
                stdout=stdout,
                stderr=stderr,
                success=success,
                command_executed=inputs.command,
                execution_time_ms=execution_time,
                custom_outputs=custom_outputs,
            )

            # Return failure if exit code is non-zero and check_returncode is True
            if not success:
                return Result.failure(
                    f"Command failed with exit code {exit_code}: {inputs.command}\n"
                    f"stderr: {stderr[:500]}"
                )

            return Result.success(output)

        except Exception as e:
            execution_time = (time.time() - start) * 1000
            return Result.failure(f"Failed to execute command: {inputs.command}\nError: {str(e)}")


# Register BashCommand block
BLOCK_REGISTRY.register("BashCommand", BashCommand)
