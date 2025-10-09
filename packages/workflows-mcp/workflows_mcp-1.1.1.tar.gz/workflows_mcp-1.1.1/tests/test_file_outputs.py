"""
Unit tests for file-based outputs infrastructure.

Tests path validation, type parsing, and BashCommand integration.
"""

import json
from pathlib import Path

import pytest

from workflows_mcp.engine.blocks_bash import (
    OutputNotFoundError,
    OutputSecurityError,
    parse_output_value,
    validate_output_path,
)


class TestValidateOutputPath:
    """Test path validation with security checks."""

    def test_valid_relative_path(self, tmp_path: Path) -> None:
        """Test valid relative path within working directory."""
        # Create test file
        test_file = tmp_path / "output.txt"
        test_file.write_text("test content")

        # Validate path
        validated = validate_output_path("test_output", "output.txt", tmp_path, unsafe=False)

        assert validated == test_file
        assert validated.exists()

    def test_valid_relative_path_in_subdirectory(self, tmp_path: Path) -> None:
        """Test valid relative path in subdirectory."""
        # Create subdirectory and file
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        test_file = subdir / "output.txt"
        test_file.write_text("test content")

        # Validate path
        validated = validate_output_path("test_output", "subdir/output.txt", tmp_path, unsafe=False)

        assert validated == test_file
        assert validated.exists()

    def test_env_var_expansion(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test environment variable expansion in paths."""
        # Set environment variable
        monkeypatch.setenv("TEST_DIR", "subdir")

        # Create subdirectory and file
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        test_file = subdir / "output.txt"
        test_file.write_text("test content")

        # Validate path with env var
        validated = validate_output_path(
            "test_output", "$TEST_DIR/output.txt", tmp_path, unsafe=False
        )

        assert validated == test_file

    def test_reject_absolute_path_in_safe_mode(self, tmp_path: Path) -> None:
        """Test that absolute paths are rejected in safe mode."""
        # Create test file
        test_file = tmp_path / "output.txt"
        test_file.write_text("test content")

        # Attempt to validate absolute path
        with pytest.raises(OutputSecurityError, match="Absolute paths not allowed in safe mode"):
            validate_output_path("test_output", str(test_file), tmp_path, unsafe=False)

    def test_allow_absolute_path_in_unsafe_mode(self, tmp_path: Path) -> None:
        """Test that absolute paths are allowed in unsafe mode."""
        # Create test file
        test_file = tmp_path / "output.txt"
        test_file.write_text("test content")

        # Validate absolute path in unsafe mode
        validated = validate_output_path("test_output", str(test_file), tmp_path, unsafe=True)

        assert validated == test_file

    def test_reject_path_traversal(self, tmp_path: Path) -> None:
        """Test that path traversal outside working directory is rejected."""
        # Create file outside working directory
        parent_dir = tmp_path.parent
        outside_file = parent_dir / "outside.txt"
        outside_file.write_text("test content")

        # Attempt to traverse outside working directory
        with pytest.raises(OutputSecurityError, match="Path escapes working directory"):
            validate_output_path("test_output", "../outside.txt", tmp_path, unsafe=False)

    def test_reject_path_traversal_with_dots(self, tmp_path: Path) -> None:
        """Test that path traversal attempts with .. are rejected."""
        # Create subdirectory
        subdir = tmp_path / "subdir"
        subdir.mkdir()

        # Create file outside working directory
        parent_dir = tmp_path.parent
        outside_file = parent_dir / "outside.txt"
        outside_file.write_text("test content")

        # Attempt to traverse with ../../
        with pytest.raises(OutputSecurityError, match="Path escapes working directory"):
            validate_output_path("test_output", "../../outside.txt", tmp_path, unsafe=False)

    def test_file_not_found(self, tmp_path: Path) -> None:
        """Test that missing files raise OutputNotFoundError."""
        with pytest.raises(OutputNotFoundError, match="File not found"):
            validate_output_path("test_output", "nonexistent.txt", tmp_path, unsafe=False)

    def test_reject_symlink(self, tmp_path: Path) -> None:
        """Test that symlinks are rejected."""
        # Create target file and symlink
        target_file = tmp_path / "target.txt"
        target_file.write_text("test content")

        symlink_file = tmp_path / "link.txt"
        symlink_file.symlink_to(target_file)

        # Attempt to validate symlink
        with pytest.raises(OutputSecurityError, match="Symlinks not allowed"):
            validate_output_path("test_output", "link.txt", tmp_path, unsafe=False)

    def test_reject_directory(self, tmp_path: Path) -> None:
        """Test that directories are rejected."""
        # Create directory
        test_dir = tmp_path / "testdir"
        test_dir.mkdir()

        # Attempt to validate directory
        with pytest.raises(OutputSecurityError, match="Path is not a file"):
            validate_output_path("test_output", "testdir", tmp_path, unsafe=False)

    def test_reject_large_file(self, tmp_path: Path) -> None:
        """Test that files larger than 10MB are rejected."""
        # Create large file (> 10MB)
        large_file = tmp_path / "large.txt"
        large_size = 11 * 1024 * 1024  # 11MB
        large_file.write_bytes(b"x" * large_size)

        # Attempt to validate large file
        with pytest.raises(OutputSecurityError, match="File too large"):
            validate_output_path("test_output", "large.txt", tmp_path, unsafe=False)

    def test_file_size_limit_edge_case(self, tmp_path: Path) -> None:
        """Test file exactly at size limit (10MB) is accepted."""
        # Create file exactly 10MB
        exact_file = tmp_path / "exact.txt"
        exact_size = 10 * 1024 * 1024  # Exactly 10MB
        exact_file.write_bytes(b"x" * exact_size)

        # Validate file
        validated = validate_output_path("test_output", "exact.txt", tmp_path, unsafe=False)

        assert validated == exact_file


class TestParseOutputValue:
    """Test type parsing for output values."""

    def test_parse_string(self) -> None:
        """Test parsing string type."""
        assert parse_output_value("hello world", "string") == "hello world"
        assert parse_output_value("  hello world  ", "string") == "hello world"
        assert parse_output_value("", "string") == ""

    def test_parse_int(self) -> None:
        """Test parsing int type."""
        assert parse_output_value("42", "int") == 42
        assert parse_output_value("-100", "int") == -100
        assert parse_output_value("  123  ", "int") == 123

    def test_parse_int_invalid(self) -> None:
        """Test parsing invalid int."""
        with pytest.raises(ValueError, match="Cannot parse as int"):
            parse_output_value("not a number", "int")

        with pytest.raises(ValueError, match="Cannot parse as int"):
            parse_output_value("3.14", "int")

    def test_parse_float(self) -> None:
        """Test parsing float type."""
        assert parse_output_value("3.14", "float") == 3.14
        assert parse_output_value("-0.5", "float") == -0.5
        assert parse_output_value("42", "float") == 42.0
        assert parse_output_value("  1.23  ", "float") == 1.23

    def test_parse_float_invalid(self) -> None:
        """Test parsing invalid float."""
        with pytest.raises(ValueError, match="Cannot parse as float"):
            parse_output_value("not a number", "float")

    def test_parse_bool_true(self) -> None:
        """Test parsing bool type (true values)."""
        assert parse_output_value("true", "bool") is True
        assert parse_output_value("True", "bool") is True
        assert parse_output_value("TRUE", "bool") is True
        assert parse_output_value("1", "bool") is True
        assert parse_output_value("yes", "bool") is True
        assert parse_output_value("Yes", "bool") is True

    def test_parse_bool_false(self) -> None:
        """Test parsing bool type (false values)."""
        assert parse_output_value("false", "bool") is False
        assert parse_output_value("False", "bool") is False
        assert parse_output_value("FALSE", "bool") is False
        assert parse_output_value("0", "bool") is False
        assert parse_output_value("no", "bool") is False
        assert parse_output_value("No", "bool") is False

    def test_parse_bool_invalid(self) -> None:
        """Test parsing invalid bool."""
        with pytest.raises(ValueError, match="Cannot parse as bool"):
            parse_output_value("not a bool", "bool")

        with pytest.raises(ValueError, match="Cannot parse as bool"):
            parse_output_value("2", "bool")

    def test_parse_json_object(self) -> None:
        """Test parsing JSON object."""
        json_str = '{"key": "value", "number": 42}'
        expected = {"key": "value", "number": 42}
        assert parse_output_value(json_str, "json") == expected

    def test_parse_json_array(self) -> None:
        """Test parsing JSON array."""
        json_str = '[1, 2, 3, "four"]'
        expected = [1, 2, 3, "four"]
        assert parse_output_value(json_str, "json") == expected

    def test_parse_json_nested(self) -> None:
        """Test parsing nested JSON."""
        json_str = '{"nested": {"key": "value"}, "array": [1, 2, 3]}'
        expected = {"nested": {"key": "value"}, "array": [1, 2, 3]}
        assert parse_output_value(json_str, "json") == expected

    def test_parse_json_invalid(self) -> None:
        """Test parsing invalid JSON."""
        with pytest.raises(ValueError, match="Cannot parse as JSON"):
            parse_output_value("not json", "json")

        with pytest.raises(ValueError, match="Cannot parse as JSON"):
            parse_output_value("{invalid}", "json")

    def test_unknown_type(self) -> None:
        """Test that unknown types raise ValueError."""
        with pytest.raises(ValueError, match="Unknown output type"):
            parse_output_value("value", "unknown_type")


class TestBashCommandWithOutputs:
    """Integration tests for BashCommand with file-based outputs."""

    @pytest.mark.asyncio
    async def test_bash_command_with_string_output(self, tmp_path: Path) -> None:
        """Test BashCommand with string output."""
        from workflows_mcp.engine.blocks_bash import BashCommand

        # Create scratch directory
        scratch_dir = tmp_path / ".scratch"
        scratch_dir.mkdir()

        # Create command that writes to file
        command = f'echo "test output" > {scratch_dir}/output.txt'

        # Create block with output declaration
        outputs = {
            "result": {
                "type": "string",
                "path": ".scratch/output.txt",
                "required": True,
            }
        }

        block = BashCommand(
            id="test_block",
            inputs={
                "command": command,
                "working_dir": str(tmp_path),
            },
            outputs=outputs,
        )

        # Execute block
        result = await block.execute({})

        # Verify result
        assert result.is_success
        assert result.value.custom_outputs["result"] == "test output"

    @pytest.mark.asyncio
    async def test_bash_command_with_json_output(self, tmp_path: Path) -> None:
        """Test BashCommand with JSON output."""
        from workflows_mcp.engine.blocks_bash import BashCommand

        # Create scratch directory
        scratch_dir = tmp_path / ".scratch"
        scratch_dir.mkdir()

        # Create command that writes JSON to file
        json_data = {"key": "value", "number": 42}
        json_str = json.dumps(json_data)
        command = f'echo \'{json_str}\' > {scratch_dir}/output.json'

        # Create block with output declaration
        outputs = {
            "result": {
                "type": "json",
                "path": ".scratch/output.json",
                "required": True,
            }
        }

        block = BashCommand(
            id="test_block",
            inputs={
                "command": command,
                "working_dir": str(tmp_path),
            },
            outputs=outputs,
        )

        # Execute block
        result = await block.execute({})

        # Verify result
        assert result.is_success
        assert result.value.custom_outputs["result"] == json_data

    @pytest.mark.asyncio
    async def test_bash_command_with_env_var_in_output_path(self, tmp_path: Path) -> None:
        """Test BashCommand with environment variable in output path."""
        from workflows_mcp.engine.blocks_bash import BashCommand

        # Create scratch directory
        scratch_dir = tmp_path / ".scratch"
        scratch_dir.mkdir()

        # Create command using $SCRATCH
        command = 'echo "42" > $SCRATCH/output.txt'

        # Create block with output declaration using env var
        outputs = {
            "result": {
                "type": "int",
                "path": "$SCRATCH/output.txt",
                "required": True,
            }
        }

        block = BashCommand(
            id="test_block",
            inputs={
                "command": command,
                "working_dir": str(tmp_path),
            },
            outputs=outputs,
        )

        # Execute block
        result = await block.execute({})

        # Verify result
        assert result.is_success
        assert result.value.custom_outputs["result"] == 42

    @pytest.mark.asyncio
    async def test_bash_command_missing_required_output(self, tmp_path: Path) -> None:
        """Test BashCommand fails when required output is missing."""
        from workflows_mcp.engine.blocks_bash import BashCommand

        # Create command that doesn't create output file
        command = "echo 'not creating file'"

        # Create block with required output
        outputs = {
            "result": {
                "type": "string",
                "path": ".scratch/missing.txt",
                "required": True,
            }
        }

        block = BashCommand(
            id="test_block",
            inputs={
                "command": command,
                "working_dir": str(tmp_path),
            },
            outputs=outputs,
        )

        # Execute block
        result = await block.execute({})

        # Verify failure
        assert not result.is_success
        assert "File not found" in result.error

    @pytest.mark.asyncio
    async def test_bash_command_optional_output_missing(self, tmp_path: Path) -> None:
        """Test BashCommand succeeds when optional output is missing."""
        from workflows_mcp.engine.blocks_bash import BashCommand

        # Create command that doesn't create output file
        command = "echo 'not creating file'"

        # Create block with optional output
        outputs = {
            "result": {
                "type": "string",
                "path": ".scratch/missing.txt",
                "required": False,
            }
        }

        block = BashCommand(
            id="test_block",
            inputs={
                "command": command,
                "working_dir": str(tmp_path),
            },
            outputs=outputs,
        )

        # Execute block
        result = await block.execute({})

        # Verify success (optional output missing is okay)
        assert result.is_success
        assert "result" not in result.value.custom_outputs

    @pytest.mark.asyncio
    async def test_scratch_directory_created_and_gitignored(self, tmp_path: Path) -> None:
        """Test that scratch directory is created and added to .gitignore."""
        from workflows_mcp.engine.blocks_bash import BashCommand

        # Create .gitignore
        gitignore = tmp_path / ".gitignore"
        gitignore.write_text("# Existing content\n*.pyc\n")

        # Create simple command
        command = "echo 'test'"

        block = BashCommand(
            id="test_block",
            inputs={
                "command": command,
                "working_dir": str(tmp_path),
            },
        )

        # Execute block
        await block.execute({})

        # Verify scratch directory exists
        scratch_dir = tmp_path / ".scratch"
        assert scratch_dir.exists()
        assert scratch_dir.is_dir()

        # Verify .gitignore updated
        gitignore_content = gitignore.read_text()
        assert ".scratch/" in gitignore_content
        assert "*.pyc" in gitignore_content  # Original content preserved
