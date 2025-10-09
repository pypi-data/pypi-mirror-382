"""
Test suite for tool provider workflows and catalog files.

Tests Phase 2 (Provider workflows) and Phase 3 (Tool catalog) of tool management architecture.
"""

from pathlib import Path

import pytest
import yaml

from workflows_mcp.engine.loader import load_workflow_from_file

# Tool management paths
TOOLS_DIR = Path(__file__).parent.parent / "src" / "workflows_mcp" / "templates" / "tools"
PROVIDERS_DIR = TOOLS_DIR / "providers"
CATALOG_DIR = TOOLS_DIR / "catalog"

PROVIDER_WORKFLOWS = [
    "providers/pip-install.yaml",
    "providers/uv-install.yaml",
    "providers/brew-install.yaml",
]

CATALOG_FILES = [
    "catalog/catalog-pytest.yaml",
    "catalog/catalog-ruff.yaml",
    "catalog/catalog-mypy.yaml",
]


def load_workflow(workflow_path: str):
    """Helper to load a workflow and handle Result."""
    result = load_workflow_from_file(str(TOOLS_DIR / workflow_path))
    assert result.is_success, f"Failed to load {workflow_path}: {result.error}"
    return result.value


def load_workflow_yaml(workflow_path: str) -> dict:
    """Helper to load raw YAML data from workflow file."""
    full_path = TOOLS_DIR / workflow_path
    with open(full_path) as f:
        return yaml.safe_load(f)


def load_catalog(catalog_path: str):
    """Helper to load a catalog file and handle Result."""
    result = load_workflow_from_file(str(TOOLS_DIR / catalog_path))
    assert result.is_success, f"Failed to load {catalog_path}: {result.error}"
    return result.value


class TestProviderWorkflowsExist:
    """Test that all provider workflow files exist."""

    @pytest.mark.parametrize("workflow_path", PROVIDER_WORKFLOWS)
    def test_provider_workflow_exists(self, workflow_path):
        """Test provider workflow file exists."""
        full_path = TOOLS_DIR / workflow_path
        assert full_path.exists(), f"Provider workflow not found: {full_path}"

    def test_all_providers_exist(self):
        """Verify all 3 provider workflows exist."""
        for workflow_path in PROVIDER_WORKFLOWS:
            full_path = TOOLS_DIR / workflow_path
            assert full_path.exists(), f"Provider workflow not found: {full_path}"


class TestCatalogFilesExist:
    """Test that all catalog metadata files exist."""

    @pytest.mark.parametrize("catalog_path", CATALOG_FILES)
    def test_catalog_file_exists(self, catalog_path):
        """Test catalog file exists."""
        full_path = TOOLS_DIR / catalog_path
        assert full_path.exists(), f"Catalog file not found: {full_path}"

    def test_all_catalogs_exist(self):
        """Verify all 3 catalog files exist."""
        for catalog_path in CATALOG_FILES:
            full_path = TOOLS_DIR / catalog_path
            assert full_path.exists(), f"Catalog file not found: {full_path}"


class TestProviderWorkflowsLoad:
    """Test that provider workflows load and validate successfully."""

    @pytest.mark.parametrize("workflow_path", PROVIDER_WORKFLOWS)
    def test_load_provider_workflow(self, workflow_path):
        """Test loading individual provider workflow."""
        workflow = load_workflow(workflow_path)
        yaml_data = load_workflow_yaml(workflow_path)

        # Validate structure
        assert workflow.name is not None
        assert workflow.description is not None
        assert len(workflow.blocks) > 0
        assert "tools" in yaml_data["tags"]

    def test_pip_install_workflow(self):
        """Test pip-install provider workflow structure."""
        workflow = load_workflow("providers/pip-install.yaml")
        yaml_data = load_workflow_yaml("providers/pip-install.yaml")

        assert workflow.name == "pip-install"

        # Check required inputs
        assert "package_name" in workflow.inputs
        assert workflow.inputs["package_name"]["required"] is True

        # Check optional inputs
        assert "version" in workflow.inputs
        assert "venv_path" in workflow.inputs
        assert "extra_args" in workflow.inputs
        assert "extras" in workflow.inputs

        # Check outputs (from YAML)
        assert "success" in yaml_data["outputs"]
        assert "installed_version" in yaml_data["outputs"]
        assert "install_location" in yaml_data["outputs"]
        assert "exit_code" in yaml_data["outputs"]

    def test_uv_install_workflow(self):
        """Test uv-install provider workflow structure."""
        workflow = load_workflow("providers/uv-install.yaml")
        yaml_data = load_workflow_yaml("providers/uv-install.yaml")

        assert workflow.name == "uv-install"

        # Check required inputs
        assert "package_name" in workflow.inputs
        assert workflow.inputs["package_name"]["required"] is True

        # Check optional inputs
        assert "version" in workflow.inputs
        assert "venv_path" in workflow.inputs
        assert "extras" in workflow.inputs

        # Check outputs (from YAML)
        assert "success" in yaml_data["outputs"]
        assert "installed_version" in yaml_data["outputs"]
        assert "install_location" in yaml_data["outputs"]
        assert "exit_code" in yaml_data["outputs"]
        assert "uv_available" in yaml_data["outputs"]

    def test_brew_install_workflow(self):
        """Test brew-install provider workflow structure."""
        workflow = load_workflow("providers/brew-install.yaml")
        yaml_data = load_workflow_yaml("providers/brew-install.yaml")

        assert workflow.name == "brew-install"

        # Check required inputs
        assert "package_name" in workflow.inputs
        assert workflow.inputs["package_name"]["required"] is True

        # Check optional inputs
        assert "cask" in workflow.inputs
        assert "upgrade" in workflow.inputs

        # Check outputs (from YAML)
        assert "success" in yaml_data["outputs"]
        assert "installed_version" in yaml_data["outputs"]
        assert "exit_code" in yaml_data["outputs"]
        assert "brew_available" in yaml_data["outputs"]
        assert "already_installed" in yaml_data["outputs"]


class TestCatalogFilesLoad:
    """Test that catalog files load and have correct structure."""

    @pytest.mark.parametrize("catalog_path", CATALOG_FILES)
    def test_load_catalog_file(self, catalog_path):
        """Test loading individual catalog file."""
        catalog = load_catalog(catalog_path)
        yaml_data = load_workflow_yaml(catalog_path)

        # Validate structure
        assert catalog.name is not None
        assert catalog.description is not None
        # Catalog files should have tool_catalog_type="catalog" marker
        assert yaml_data["inputs"]["tool_catalog_type"]["default"] == "catalog"
        assert "tools" in yaml_data["tags"]

    def test_catalog_pytest(self):
        """Test catalog-pytest metadata structure."""
        catalog = load_catalog("catalog/catalog-pytest.yaml")
        yaml_data = load_workflow_yaml("catalog/catalog-pytest.yaml")
        assert catalog.name == "catalog-pytest"

        # Check metadata in inputs.metadata.default
        assert "inputs" in yaml_data
        assert "metadata" in yaml_data["inputs"]
        assert "default" in yaml_data["inputs"]["metadata"]
        metadata = yaml_data["inputs"]["metadata"]["default"]

        assert "tool_name" in metadata
        assert metadata["tool_name"] == "pytest"
        assert "tool_type" in metadata
        assert metadata["tool_type"] == "python_package"
        assert "command_name" in metadata
        assert metadata["command_name"] == "pytest"

        # Check version_check
        assert "version_check" in metadata
        version_check = metadata["version_check"]
        assert "command" in version_check
        assert "pattern" in version_check
        assert "import_name" in version_check

        # Check installation options
        assert "installation" in metadata
        installation = metadata["installation"]
        assert "uv" in installation or "pip" in installation

        # Check constraints
        assert "constraints" in metadata
        constraints = metadata["constraints"]
        assert "python_version" in constraints
        assert "recommended_version" in constraints

    def test_catalog_ruff(self):
        """Test catalog-ruff metadata structure."""
        catalog = load_catalog("catalog/catalog-ruff.yaml")
        yaml_data = load_workflow_yaml("catalog/catalog-ruff.yaml")
        assert catalog.name == "catalog-ruff"

        # Check metadata in inputs.metadata.default
        assert "inputs" in yaml_data
        assert "metadata" in yaml_data["inputs"]
        assert "default" in yaml_data["inputs"]["metadata"]
        metadata = yaml_data["inputs"]["metadata"]["default"]

        assert metadata["tool_name"] == "ruff"
        assert metadata["tool_type"] == "python_package"
        assert metadata["command_name"] == "ruff"

        # Check version_check
        assert "version_check" in metadata
        assert "command" in metadata["version_check"]
        assert "pattern" in metadata["version_check"]

        # Check installation options
        assert "installation" in metadata

        # Check constraints
        assert "constraints" in metadata

    def test_catalog_mypy(self):
        """Test catalog-mypy metadata structure."""
        catalog = load_catalog("catalog/catalog-mypy.yaml")
        yaml_data = load_workflow_yaml("catalog/catalog-mypy.yaml")
        assert catalog.name == "catalog-mypy"

        # Check metadata in inputs.metadata.default
        assert "inputs" in yaml_data
        assert "metadata" in yaml_data["inputs"]
        assert "default" in yaml_data["inputs"]["metadata"]
        metadata = yaml_data["inputs"]["metadata"]["default"]

        assert metadata["tool_name"] == "mypy"
        assert metadata["tool_type"] == "python_package"
        assert metadata["command_name"] == "mypy"

        # Check version_check
        assert "version_check" in metadata
        assert "command" in metadata["version_check"]
        assert "pattern" in metadata["version_check"]

        # Check installation options
        assert "installation" in metadata

        # Check constraints
        assert "constraints" in metadata


class TestProviderBlockStructure:
    """Test that provider workflows use correct block types."""

    def test_providers_use_bash_commands(self):
        """Verify provider workflows use BashCommand blocks."""
        for workflow_path in PROVIDER_WORKFLOWS:
            workflow = load_workflow(workflow_path)

            # Check for BashCommand blocks
            bash_blocks = [block for block in workflow.blocks if block.get("type") == "BashCommand"]
            assert len(bash_blocks) > 0, f"{workflow_path} should use BashCommand blocks"

    def test_providers_have_verification_blocks(self):
        """Verify provider workflows have verification blocks."""
        for workflow_path in PROVIDER_WORKFLOWS:
            workflow = load_workflow(workflow_path)

            # Look for blocks that verify installation
            block_ids = [block.get("id") for block in workflow.blocks]
            has_verification = any(
                "verify" in block_id or "check" in block_id for block_id in block_ids
            )
            assert has_verification, f"{workflow_path} should have verification blocks"


class TestCatalogMetadataStructure:
    """Test that catalog files have NO blocks section (metadata only)."""

    @pytest.mark.parametrize("catalog_path", CATALOG_FILES)
    def test_catalog_has_minimal_blocks(self, catalog_path):
        """Verify catalog files have minimal blocks (only marker)."""
        catalog = load_catalog(catalog_path)

        # Catalog files should have only 1 block (the catalog_marker EchoBlock)
        assert len(catalog.blocks) == 1, f"{catalog_path} should have only 1 marker block"
        assert catalog.blocks[0]["id"] == "catalog_marker"
        assert catalog.blocks[0]["type"] == "EchoBlock"

    @pytest.mark.parametrize("catalog_path", CATALOG_FILES)
    def test_catalog_type_is_catalog(self, catalog_path):
        """Verify catalog files use tool_catalog_type: catalog."""
        yaml_data = load_workflow_yaml(catalog_path)
        assert (
            yaml_data["inputs"]["tool_catalog_type"]["default"] == "catalog"
        ), f"{catalog_path} should have tool_catalog_type: catalog"


class TestProviderOutputContracts:
    """Test that provider workflows have expected output contracts."""

    def test_all_providers_have_success_output(self):
        """Verify all providers have 'success' output."""
        for workflow_path in PROVIDER_WORKFLOWS:
            yaml_data = load_workflow_yaml(workflow_path)
            assert "success" in yaml_data["outputs"], f"{workflow_path} must have 'success' output"

    def test_all_providers_have_exit_code_output(self):
        """Verify all providers have 'exit_code' output."""
        for workflow_path in PROVIDER_WORKFLOWS:
            yaml_data = load_workflow_yaml(workflow_path)
            assert (
                "exit_code" in yaml_data["outputs"]
            ), f"{workflow_path} must have 'exit_code' output"

    def test_all_providers_have_version_output(self):
        """Verify all providers have 'installed_version' output."""
        for workflow_path in PROVIDER_WORKFLOWS:
            yaml_data = load_workflow_yaml(workflow_path)
            assert (
                "installed_version" in yaml_data["outputs"]
            ), f"{workflow_path} must have 'installed_version' output"


class TestIntegrationWithEnsureTool:
    """Test that providers integrate with ensure-tool workflow."""

    def test_ensure_tool_workflow_exists(self):
        """Verify ensure-tool core workflow exists."""
        ensure_tool_path = TOOLS_DIR / "core" / "ensure-tool.yaml"
        assert ensure_tool_path.exists(), "ensure-tool.yaml must exist"

    def test_provider_outputs_match_ensure_tool_expectations(self):
        """Verify provider outputs are compatible with ensure-tool."""
        # ensure-tool expects these outputs from providers
        required_outputs = ["success", "installed_version", "exit_code"]

        for workflow_path in PROVIDER_WORKFLOWS:
            yaml_data = load_workflow_yaml(workflow_path)

            for output_key in required_outputs:
                assert (
                    output_key in yaml_data["outputs"]
                ), f"{workflow_path} must have '{output_key}' output for ensure-tool compatibility"


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
