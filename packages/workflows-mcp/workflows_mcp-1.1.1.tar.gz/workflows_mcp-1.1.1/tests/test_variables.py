"""
Tests for variable resolution system.

Tests cover:
- String variable resolution (${var} syntax)
- Block output resolution (${block_id.field})
- Recursive resolution in dicts and lists
- Missing variable error handling
- Complex nested structures
"""

import pytest

from workflows_mcp.engine.variables import VariableNotFoundError, VariableResolver


class TestVariableResolver:
    """Test cases for VariableResolver."""

    def test_resolve_simple_string_input(self):
        """Test resolving workflow input in string."""
        context = {"branch": "main"}
        resolver = VariableResolver(context)

        result = resolver.resolve("Branch: ${branch}")
        assert result == "Branch: main"

    def test_resolve_block_output_field(self):
        """Test resolving block output field."""
        context = {"create_worktree.worktree_path": "/tmp/worktree"}
        resolver = VariableResolver(context)

        result = resolver.resolve("Path: ${create_worktree.worktree_path}")
        assert result == "Path: /tmp/worktree"

    def test_resolve_multiple_variables(self):
        """Test resolving multiple variables in one string."""
        context = {
            "project": "my-project",
            "version": "1.0",
        }
        resolver = VariableResolver(context)

        result = resolver.resolve("${project}-v${version}")
        assert result == "my-project-v1.0"

    def test_resolve_integer_value(self):
        """Test resolving integer variable."""
        context = {"run_tests.exit_code": 0}
        resolver = VariableResolver(context)

        result = resolver.resolve("Exit code: ${run_tests.exit_code}")
        assert result == "Exit code: 0"

    def test_resolve_boolean_value(self):
        """Test resolving boolean variable."""
        context = {"run_tests.success": True}
        resolver = VariableResolver(context)

        result = resolver.resolve("Success: ${run_tests.success}")
        assert result == "Success: True"

    def test_resolve_none_value(self):
        """Test resolving None variable."""
        context = {"optional_field": None}
        resolver = VariableResolver(context)

        result = resolver.resolve("Value: ${optional_field}")
        assert result == "Value: "

    def test_resolve_dict_values(self):
        """Test recursive resolution in dictionaries."""
        context = {
            "base_path": "/project",
            "create_worktree.name": "feature-123",
        }
        resolver = VariableResolver(context)

        input_dict = {
            "path": "${base_path}/${create_worktree.name}",
            "config": {"name": "${create_worktree.name}"},
        }

        result = resolver.resolve(input_dict)
        assert result == {
            "path": "/project/feature-123",
            "config": {"name": "feature-123"},
        }

    def test_resolve_list_values(self):
        """Test recursive resolution in lists."""
        context = {"repo": "my-repo", "branch": "main"}
        resolver = VariableResolver(context)

        input_list = ["${repo}", "${branch}", "fixed-value"]

        result = resolver.resolve(input_list)
        assert result == ["my-repo", "main", "fixed-value"]

    def test_resolve_nested_structures(self):
        """Test resolution in deeply nested structures."""
        context = {
            "project": "workflows",
            "version": "1.0",
            "create_worktree.path": "/tmp/worktree",
        }
        resolver = VariableResolver(context)

        input_data = {
            "metadata": {
                "name": "${project}",
                "version": "${version}",
                "paths": ["${create_worktree.path}/src", "${create_worktree.path}/tests"],
            },
            "config": {"base": "${create_worktree.path}"},
        }

        result = resolver.resolve(input_data)
        assert result == {
            "metadata": {
                "name": "workflows",
                "version": "1.0",
                "paths": ["/tmp/worktree/src", "/tmp/worktree/tests"],
            },
            "config": {"base": "/tmp/worktree"},
        }

    def test_resolve_primitive_types_passthrough(self):
        """Test that primitive types pass through unchanged."""
        resolver = VariableResolver({})

        assert resolver.resolve(42) == 42
        assert resolver.resolve(3.14) == 3.14
        assert resolver.resolve(True) is True
        assert resolver.resolve(None) is None

    def test_resolve_no_variables(self):
        """Test string without variables passes through."""
        resolver = VariableResolver({})

        result = resolver.resolve("No variables here")
        assert result == "No variables here"

    def test_missing_variable_error(self):
        """Test error when variable not found in context."""
        context = {"existing": "value"}
        resolver = VariableResolver(context)

        with pytest.raises(VariableNotFoundError) as exc_info:
            resolver.resolve("Missing: ${missing_var}")

        assert "missing_var" in str(exc_info.value)
        assert "existing" in str(exc_info.value)

    def test_missing_block_output_error(self):
        """Test error when block output field not found."""
        context = {"other_block.field": "value"}
        resolver = VariableResolver(context)

        with pytest.raises(VariableNotFoundError) as exc_info:
            resolver.resolve("${missing_block.field}")

        assert "missing_block.field" in str(exc_info.value)

    def test_complex_variable_names(self):
        """Test variables with underscores and numbers."""
        context = {
            "input_var_1": "value1",
            "block_2.output_field_3": "value2",
        }
        resolver = VariableResolver(context)

        result = resolver.resolve("${input_var_1} and ${block_2.output_field_3}")
        assert result == "value1 and value2"

    def test_partial_variable_syntax(self):
        """Test that incomplete variable syntax is left unchanged."""
        resolver = VariableResolver({"var": "value"})

        # Missing closing brace
        result = resolver.resolve("${var")
        assert result == "${var"

        # Missing opening brace
        result = resolver.resolve("var}")
        assert result == "var}"

    def test_empty_context(self):
        """Test resolver with empty context."""
        resolver = VariableResolver({})

        # Should work for non-variable strings
        assert resolver.resolve("plain text") == "plain text"
        assert resolver.resolve(42) == 42

        # Should fail for variables
        with pytest.raises(VariableNotFoundError):
            resolver.resolve("${nonexistent}")

    def test_resolve_with_mixed_content(self):
        """Test resolution with both variables and literals."""
        context = {
            "user": "alice",
            "action": "commit",
            "repo.name": "my-repo",
        }
        resolver = VariableResolver(context)

        result = resolver.resolve("User ${user} performed ${action} on ${repo.name}")
        assert result == "User alice performed commit on my-repo"

    def test_resolve_empty_string_value(self):
        """Test resolving variable with empty string value."""
        context = {"empty": ""}
        resolver = VariableResolver(context)

        result = resolver.resolve("Value: [${empty}]")
        assert result == "Value: []"

    def test_resolve_list_and_dict_in_string(self):
        """Test resolving complex types in string context."""
        context = {"my_list": [1, 2, 3], "my_dict": {"key": "value"}}
        resolver = VariableResolver(context)

        result = resolver.resolve("List: ${my_list}, Dict: ${my_dict}")
        assert "List: [1, 2, 3]" in result
        assert "Dict: {'key': 'value'}" in result
