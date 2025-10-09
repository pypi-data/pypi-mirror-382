"""
Phase 4 Tests: Tool Management Integration

Tests for ensuring workflow integration with ensure-tool functionality.
Verifies backward compatibility and new auto-install features.
"""

from pathlib import Path

import pytest

from workflows_mcp.engine.loader import load_workflow_from_file

# Templates directory
TEMPLATES_DIR = Path(__file__).parent.parent / "src" / "workflows_mcp" / "templates"


def load_workflow(workflow_path: str):
    """Helper to load a workflow and handle Result."""
    file_path = TEMPLATES_DIR / workflow_path
    result = load_workflow_from_file(file_path)
    if not result.is_success:
        pytest.fail(f"Failed to load workflow {workflow_path}: {result.error}")
    return result.value


class TestBackwardCompatibility:
    """Test that existing behavior is preserved when auto_install is not used."""

    def test_run_pytest_without_auto_install(self):
        """run-pytest works as before when auto_install is not specified."""
        workflow_def = load_workflow("python/run-pytest.yaml")
        assert workflow_def is not None

        # Verify auto_install has default value of true
        assert "auto_install" in workflow_def.inputs
        assert workflow_def.inputs["auto_install"]["default"] is True

        # Verify ensure_pytest block exists and has condition
        ensure_block = next(
            (b for b in workflow_def.blocks if b["id"] == "ensure_pytest"), None
        )
        assert ensure_block is not None
        assert ensure_block["condition"] == "${auto_install}"

    def test_lint_python_without_auto_install(self):
        """lint-python works as before when auto_install is not specified."""
        workflow_def = load_workflow("python/lint-python.yaml")
        assert workflow_def is not None

        # Verify auto_install has default value of true
        assert "auto_install" in workflow_def.inputs
        assert workflow_def.inputs["auto_install"]["default"] is True

        # Verify ensure blocks exist with proper conditions
        ensure_ruff = next(
            (b for b in workflow_def.blocks if b["id"] == "ensure_ruff"), None
        )
        assert ensure_ruff is not None
        assert ensure_ruff["condition"] == "${auto_install}"

        ensure_mypy = next(
            (b for b in workflow_def.blocks if b["id"] == "ensure_mypy"), None
        )
        assert ensure_mypy is not None
        assert ensure_mypy["condition"] == "${auto_install} and not ${skip_mypy}"

    def test_conditional_deploy_without_auto_install(self):
        """conditional-deploy works as before when auto_install is not specified."""
        workflow_def = load_workflow("ci/conditional-deploy.yaml")
        assert workflow_def is not None

        # Verify auto_install has default value of false
        assert "auto_install" in workflow_def.inputs
        assert workflow_def.inputs["auto_install"]["default"] is False

        # Verify run_tests block passes through auto_install
        run_tests = next(
            (b for b in workflow_def.blocks if b["id"] == "run_tests"), None
        )
        assert run_tests is not None
        assert run_tests["type"] == "ExecuteWorkflow"
        assert "auto_install" in run_tests["inputs"]["inputs"]


class TestAutoInstallParameter:
    """Test that auto_install parameter is properly defined and validated."""

    def test_run_pytest_auto_install_parameter(self):
        """run-pytest accepts auto_install parameter."""
        workflow_def = load_workflow("python/run-pytest.yaml")

        # Verify parameter exists and has correct type
        auto_install_input = workflow_def.inputs["auto_install"]
        assert auto_install_input["type"] == "boolean"
        assert auto_install_input["default"] is True
        assert "auto" in auto_install_input["description"].lower()

    def test_lint_python_auto_install_parameter(self):
        """lint-python accepts auto_install parameter."""
        workflow_def = load_workflow("python/lint-python.yaml")

        # Verify parameter exists and has correct type
        auto_install_input = workflow_def.inputs["auto_install"]
        assert auto_install_input["type"] == "boolean"
        assert auto_install_input["default"] is True
        assert "auto" in auto_install_input["description"].lower()

    def test_conditional_deploy_auto_install_parameter(self):
        """conditional-deploy accepts auto_install parameter."""
        workflow_def = load_workflow("ci/conditional-deploy.yaml")

        # Verify parameter exists and has correct type
        auto_install_input = workflow_def.inputs["auto_install"]
        assert auto_install_input["type"] == "boolean"
        assert auto_install_input["default"] is False
        assert "auto" in auto_install_input["description"].lower()


class TestEnsureToolIntegration:
    """Test ensure-tool workflow integration."""

    def test_run_pytest_ensure_block_configuration(self):
        """run-pytest ensure_pytest block is properly configured."""
        workflow_def = load_workflow("python/run-pytest.yaml")

        ensure_block = next(
            (b for b in workflow_def.blocks if b["id"] == "ensure_pytest"), None
        )
        assert ensure_block is not None
        assert ensure_block["type"] == "ExecuteWorkflow"

        # Verify it calls the correct workflow
        assert ensure_block["inputs"]["workflow"] == "ensure-tool"

        # Verify inputs are properly configured
        inputs = ensure_block["inputs"]["inputs"]
        assert inputs["tool_name"] == "pytest"
        assert inputs["tool_type"] == "python_package"
        assert inputs["version"] == ">=7.0.0"
        assert inputs["venv_path"] == "${venv_path}"
        assert inputs["auto_install"] is True

    def test_lint_python_ensure_blocks_configuration(self):
        """lint-python ensure blocks are properly configured."""
        workflow_def = load_workflow("python/lint-python.yaml")

        # Check ensure_ruff
        ensure_ruff = next(
            (b for b in workflow_def.blocks if b["id"] == "ensure_ruff"), None
        )
        assert ensure_ruff is not None
        assert ensure_ruff["inputs"]["workflow"] == "ensure-tool"
        ruff_inputs = ensure_ruff["inputs"]["inputs"]
        assert ruff_inputs["tool_name"] == "ruff"
        assert ruff_inputs["tool_type"] == "python_package"

        # Check ensure_mypy
        ensure_mypy = next(
            (b for b in workflow_def.blocks if b["id"] == "ensure_mypy"), None
        )
        assert ensure_mypy is not None
        assert ensure_mypy["inputs"]["workflow"] == "ensure-tool"
        mypy_inputs = ensure_mypy["inputs"]["inputs"]
        assert mypy_inputs["tool_name"] == "mypy"
        assert mypy_inputs["tool_type"] == "python_package"


class TestConditionalExecution:
    """Test that ensure-tool blocks only run when conditions are met."""

    def test_ensure_blocks_have_proper_conditions(self):
        """Ensure blocks should only run when auto_install=true."""
        workflow_def = load_workflow("python/run-pytest.yaml")

        ensure_block = next(
            (b for b in workflow_def.blocks if b["id"] == "ensure_pytest"), None
        )
        assert ensure_block["condition"] == "${auto_install}"

    def test_mypy_ensure_respects_skip_flag(self):
        """ensure_mypy should respect both auto_install and skip_mypy."""
        workflow_def = load_workflow("python/lint-python.yaml")

        ensure_mypy = next(
            (b for b in workflow_def.blocks if b["id"] == "ensure_mypy"), None
        )
        # Should only run if auto_install=true AND skip_mypy=false
        assert ensure_mypy["condition"] == "${auto_install} and not ${skip_mypy}"


class TestDocumentation:
    """Test that workflows are properly documented with auto-install capability."""

    def test_run_pytest_mentions_auto_install(self):
        """run-pytest description mentions auto-install support."""
        workflow_def = load_workflow("python/run-pytest.yaml")
        assert "auto-install" in workflow_def.description.lower()

    def test_lint_python_mentions_auto_install(self):
        """lint-python description mentions auto-install support."""
        workflow_def = load_workflow("python/lint-python.yaml")
        assert "auto-install" in workflow_def.description.lower()
