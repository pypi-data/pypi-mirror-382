"""
Unit tests for WorkflowRegistry.

Tests cover:
- Registration (success and duplicate detection)
- Retrieval (success and not found)
- Tag filtering
- Directory loading (with example YAML files)
- Metadata extraction for MCP tools
- Clear() for test isolation
"""

from pathlib import Path

import pytest

from workflows_mcp.engine.executor import WorkflowDefinition
from workflows_mcp.engine.registry import WorkflowRegistry
from workflows_mcp.engine.schema import WorkflowSchema


@pytest.fixture
def registry() -> WorkflowRegistry:
    """Create a fresh registry for each test."""
    return WorkflowRegistry()


@pytest.fixture
def sample_workflow_def() -> WorkflowDefinition:
    """Create a sample WorkflowDefinition for testing."""
    return WorkflowDefinition(
        name="test-workflow",
        description="Test workflow description",
        blocks=[
            {
                "id": "block1",
                "type": "EchoBlock",
                "inputs": {"message": "Hello"},
                "depends_on": [],
            }
        ],
    )


@pytest.fixture
def sample_workflow_schema() -> WorkflowSchema:
    """Create a sample WorkflowSchema for testing."""
    return WorkflowSchema(
        name="test-workflow",
        description="Test workflow description",
        version="1.0",
        author="Test Author",
        tags=["test", "sample"],
        blocks=[
            {
                "id": "block1",
                "type": "EchoBlock",
                "inputs": {"message": "Hello"},
                "depends_on": [],
            }
        ],
    )


@pytest.fixture
def temp_workflow_dir(tmp_path: Path) -> Path:
    """Create a temporary directory with sample workflow YAML files."""
    # Create test workflow 1
    workflow1 = """
name: workflow-one
description: First test workflow
version: "1.0"
author: Test Author

blocks:
  - id: block1
    type: EchoBlock
    inputs:
      message: "Test 1"
      delay_ms: 0
"""
    (tmp_path / "workflow1.yaml").write_text(workflow1)

    # Create test workflow 2 (different category)
    workflow2 = """
name: workflow-two
description: Second test workflow
version: "1.0"

blocks:
  - id: block1
    type: EchoBlock
    inputs:
      message: "Test 2"
      delay_ms: 0
"""
    (tmp_path / "workflow2.yaml").write_text(workflow2)

    # Create subdirectory with workflow 3
    subdir = tmp_path / "subdir"
    subdir.mkdir()

    workflow3 = """
name: workflow-three
description: Third test workflow (in subdirectory)
version: "2.0"

blocks:
  - id: block1
    type: EchoBlock
    inputs:
      message: "Test 3"
      delay_ms: 0
"""
    (subdir / "workflow3.yaml").write_text(workflow3)

    # Create invalid workflow (should be skipped)
    invalid_workflow = """
name: invalid-workflow
# Missing required field: description
blocks: []  # Invalid: blocks list cannot be empty
"""
    (tmp_path / "invalid.yaml").write_text(invalid_workflow)

    return tmp_path


class TestRegistration:
    """Test workflow registration functionality."""

    def test_register_workflow_success(
        self, registry: WorkflowRegistry, sample_workflow_def: WorkflowDefinition
    ) -> None:
        """Test successful workflow registration."""
        registry.register(sample_workflow_def)

        assert len(registry) == 1

        assert registry.exists("test-workflow")
        assert "test-workflow" in registry

    def test_register_workflow_with_schema(
        self,
        registry: WorkflowRegistry,
        sample_workflow_def: WorkflowDefinition,
        sample_workflow_schema: WorkflowSchema,
    ) -> None:
        """Test registration with schema metadata."""
        registry.register(sample_workflow_def, sample_workflow_schema)

        assert registry.exists("test-workflow")
        schema = registry.get_schema("test-workflow")
        assert schema is not None

        assert schema.version == "1.0"

    def test_register_duplicate_raises_error(
        self, registry: WorkflowRegistry, sample_workflow_def: WorkflowDefinition
    ) -> None:
        """Test that registering duplicate workflow raises ValueError."""
        registry.register(sample_workflow_def)

        with pytest.raises(ValueError, match="already registered"):
            registry.register(sample_workflow_def)

    def test_unregister_workflow(
        self, registry: WorkflowRegistry, sample_workflow_def: WorkflowDefinition
    ) -> None:
        """Test workflow unregistration."""
        registry.register(sample_workflow_def)
        assert registry.exists("test-workflow")

        registry.unregister("test-workflow")
        assert not registry.exists("test-workflow")

        assert len(registry) == 0

    def test_unregister_nonexistent_raises_error(self, registry: WorkflowRegistry) -> None:
        """Test that unregistering non-existent workflow raises KeyError."""
        with pytest.raises(KeyError, match="not found"):
            registry.unregister("nonexistent")


class TestRetrieval:
    """Test workflow retrieval functionality."""

    def test_get_workflow_success(
        self, registry: WorkflowRegistry, sample_workflow_def: WorkflowDefinition
    ) -> None:
        """Test successful workflow retrieval."""
        registry.register(sample_workflow_def)

        workflow = registry.get("test-workflow")
        assert workflow.name == "test-workflow"

        assert workflow.description == "Test workflow description"

    def test_get_workflow_not_found(self, registry: WorkflowRegistry) -> None:
        """Test that retrieving non-existent workflow raises KeyError."""
        with pytest.raises(KeyError, match="not found"):
            registry.get("nonexistent")

    def test_get_workflow_not_found_lists_available(
        self, registry: WorkflowRegistry, sample_workflow_def: WorkflowDefinition
    ) -> None:
        """Test that KeyError includes list of available workflows."""
        registry.register(sample_workflow_def)

        with pytest.raises(KeyError, match="Available workflows"):
            registry.get("nonexistent")

    def test_exists(
        self, registry: WorkflowRegistry, sample_workflow_def: WorkflowDefinition
    ) -> None:
        """Test exists() method."""
        assert not registry.exists("test-workflow")

        registry.register(sample_workflow_def)
        assert registry.exists("test-workflow")

    def test_contains_operator(
        self, registry: WorkflowRegistry, sample_workflow_def: WorkflowDefinition
    ) -> None:
        """Test 'in' operator support."""
        assert "test-workflow" not in registry

        registry.register(sample_workflow_def)
        assert "test-workflow" in registry


class TestListing:
    """Test workflow listing functionality."""

    def test_list_all_empty(self, registry: WorkflowRegistry) -> None:
        """Test listing when registry is empty."""
        workflows = registry.list_all()
        assert workflows == []

    def test_list_all_multiple_workflows(self, registry: WorkflowRegistry) -> None:
        """Test listing multiple workflows."""
        wf1 = WorkflowDefinition("workflow-1", "First", [])
        wf2 = WorkflowDefinition("workflow-2", "Second", [])

        registry.register(wf1)
        registry.register(wf2)

        workflows = registry.list_all()
        assert len(workflows) == 2

        names = {w.name for w in workflows}
        assert names == {"workflow-1", "workflow-2"}

    def test_list_names(self, registry: WorkflowRegistry) -> None:
        """Test listing workflow names."""
        wf1 = WorkflowDefinition("workflow-1", "First", [])
        wf2 = WorkflowDefinition("workflow-2", "Second", [])

        registry.register(wf1)
        registry.register(wf2)

        names = registry.list_names()
        assert names == ["workflow-1", "workflow-2"]  # Should be sorted


class TestMetadata:
    """Test metadata extraction for MCP tools."""

    def test_get_workflow_metadata_basic(
        self, registry: WorkflowRegistry, sample_workflow_def: WorkflowDefinition
    ) -> None:
        """Test metadata extraction without schema."""
        registry.register(sample_workflow_def)

        metadata = registry.get_workflow_metadata("test-workflow")
        assert metadata["name"] == "test-workflow"

        assert metadata["description"] == "Test workflow description"
    def test_get_workflow_metadata_with_schema(
        self,
        registry: WorkflowRegistry,
        sample_workflow_def: WorkflowDefinition,
        sample_workflow_schema: WorkflowSchema,
    ) -> None:
        """Test metadata extraction with schema."""
        registry.register(sample_workflow_def, sample_workflow_schema)

        metadata = registry.get_workflow_metadata("test-workflow")
        assert metadata["name"] == "test-workflow"
        assert metadata["description"] == "Test workflow description"
        assert metadata["version"] == "1.0"
        assert metadata["author"] == "Test Author"
        assert metadata["tags"] == ["test", "sample"]

    def test_list_all_metadata(self, registry: WorkflowRegistry) -> None:
        """Test listing metadata for all workflows."""
        wf1 = WorkflowDefinition("workflow-1", "First", [])
        wf2 = WorkflowDefinition("workflow-2", "Second", [])

        registry.register(wf1)
        registry.register(wf2)

        metadata_list = registry.list_all_metadata()
        assert len(metadata_list) == 2

        assert metadata_list[0]["name"] == "workflow-1"  # Sorted
        assert metadata_list[1]["name"] == "workflow-2"


class TestDirectoryLoading:
    """Test loading workflows from directories."""

    def test_load_from_directory_success(
        self, registry: WorkflowRegistry, temp_workflow_dir: Path
    ) -> None:
        """Test successful directory loading."""
        result = registry.load_from_directory(temp_workflow_dir)

        assert result.is_success

        assert result.value == 3  # 3 valid workflows (invalid one skipped)

        assert registry.exists("workflow-one")

        assert registry.exists("workflow-two")
        assert registry.exists("workflow-three")

        assert not registry.exists("invalid-workflow")

    def test_load_from_directory_nonexistent(self, registry: WorkflowRegistry) -> None:
        """Test loading from non-existent directory."""
        result = registry.load_from_directory("/nonexistent/path")

        assert not result.is_success

        assert "not found" in result.error.lower()

    def test_load_from_directory_recursive(
        self, registry: WorkflowRegistry, temp_workflow_dir: Path
    ) -> None:
        """Test that directory loading is recursive."""
        result = registry.load_from_directory(temp_workflow_dir)

        assert result.is_success
        # workflow-three is in subdirectory - should still be loaded
        assert registry.exists("workflow-three")

    def test_load_from_directory_duplicate_handling(
        self, registry: WorkflowRegistry, temp_workflow_dir: Path
    ) -> None:
        """Test that duplicate workflows are skipped with warning."""
        # Load once
        result1 = registry.load_from_directory(temp_workflow_dir)
        assert result1.is_success

        assert result1.value == 3

        # Load again - duplicates should be skipped
        result2 = registry.load_from_directory(temp_workflow_dir)
        assert result2.is_success

        assert result2.value == 0  # No new workflows loaded

        # Still only 3 workflows
        assert len(registry) == 3


class TestClear:
    """Test registry clearing functionality."""

    def test_clear_empty_registry(self, registry: WorkflowRegistry) -> None:
        """Test clearing empty registry."""
        registry.clear()
        assert len(registry) == 0

    def test_clear_with_workflows(
        self, registry: WorkflowRegistry, sample_workflow_def: WorkflowDefinition
    ) -> None:
        """Test clearing registry with workflows."""
        registry.register(sample_workflow_def)
        assert len(registry) == 1

        registry.clear()
        assert len(registry) == 0

        assert not registry.exists("test-workflow")

    def test_clear_with_schemas(
        self,
        registry: WorkflowRegistry,
        sample_workflow_def: WorkflowDefinition,
        sample_workflow_schema: WorkflowSchema,
    ) -> None:
        """Test that clear removes both workflows and schemas."""
        registry.register(sample_workflow_def, sample_workflow_schema)
        assert registry.get_schema("test-workflow") is not None

        registry.clear()
        assert registry.get_schema("test-workflow") is None


class TestMagicMethods:
    """Test magic methods (__len__, __contains__, __repr__)."""

    def test_len(self, registry: WorkflowRegistry) -> None:
        """Test __len__ method."""
        assert len(registry) == 0

        wf1 = WorkflowDefinition("workflow-1", "First", [])
        registry.register(wf1)
        assert len(registry) == 1

        wf2 = WorkflowDefinition("workflow-2", "Second", [])
        registry.register(wf2)
        assert len(registry) == 2

    def test_repr(self, registry: WorkflowRegistry) -> None:
        """Test __repr__ method."""
        repr_str = repr(registry)
        assert "WorkflowRegistry" in repr_str

        assert "0 workflows" in repr_str

        wf = WorkflowDefinition("test", "Test", [])
        registry.register(wf)

        repr_str = repr(registry)
        assert "1 workflows" in repr_str


class TestSourceTracking:
    """Test workflow source tracking functionality."""

    def test_register_with_source_dir(self, registry: WorkflowRegistry) -> None:
        """Test registering workflow with source directory."""
        wf = WorkflowDefinition("test-wf", "Test", [])
        source = Path("/tmp/templates")

        registry.register(wf, source_dir=source)

        assert registry.exists("test-wf")

        assert registry.get_workflow_source("test-wf") == source

    def test_register_without_source_dir(self, registry: WorkflowRegistry) -> None:
        """Test registering workflow without source directory."""
        wf = WorkflowDefinition("test-wf", "Test", [])

        registry.register(wf)

        assert registry.exists("test-wf")

        assert registry.get_workflow_source("test-wf") is None

    def test_get_workflow_source_nonexistent(self, registry: WorkflowRegistry) -> None:
        """Test getting source for non-existent workflow."""
        assert registry.get_workflow_source("nonexistent") is None

    def test_list_by_source_empty(self, registry: WorkflowRegistry) -> None:
        """Test listing workflows by source with empty registry."""
        workflows = registry.list_by_source(Path("/tmp/templates"))
        assert workflows == []

    def test_list_by_source_with_workflows(self, registry: WorkflowRegistry) -> None:
        """Test listing workflows filtered by source directory."""
        source1 = Path("/tmp/templates")
        source2 = Path("/tmp/library")

        wf1 = WorkflowDefinition("wf-1", "First", [])
        wf2 = WorkflowDefinition("wf-2", "Second", [])
        wf3 = WorkflowDefinition("wf-3", "Third", [])

        registry.register(wf1, source_dir=source1)
        registry.register(wf2, source_dir=source1)
        registry.register(wf3, source_dir=source2)

        # List workflows from source1
        source1_workflows = registry.list_by_source(source1)
        assert len(source1_workflows) == 2

        assert set(source1_workflows) == {"wf-1", "wf-2"}

        # List workflows from source2
        source2_workflows = registry.list_by_source(source2)
        assert len(source2_workflows) == 1

        assert source2_workflows == ["wf-3"]

        # List workflows from unused source
        unused_workflows = registry.list_by_source(Path("/tmp/unused"))
        assert unused_workflows == []

    def test_unregister_removes_source(self, registry: WorkflowRegistry) -> None:
        """Test that unregister removes source tracking."""
        wf = WorkflowDefinition("test-wf", "Test", [])
        source = Path("/tmp/templates")

        registry.register(wf, source_dir=source)
        assert registry.get_workflow_source("test-wf") == source

        registry.unregister("test-wf")
        assert registry.get_workflow_source("test-wf") is None

    def test_clear_removes_all_sources(self, registry: WorkflowRegistry) -> None:
        """Test that clear removes all source tracking."""
        wf1 = WorkflowDefinition("wf-1", "First", [])
        wf2 = WorkflowDefinition("wf-2", "Second", [])
        source = Path("/tmp/templates")

        registry.register(wf1, source_dir=source)
        registry.register(wf2, source_dir=source)

        assert len(registry.list_by_source(source)) == 2

        registry.clear()

        assert len(registry.list_by_source(source)) == 0


@pytest.fixture
def multi_workflow_dirs(tmp_path: Path) -> tuple[Path, Path, Path]:
    """Create multiple temporary directories with workflow YAML files."""
    # Directory 1: templates (priority 1)
    dir1 = tmp_path / "templates"
    dir1.mkdir()

    workflow1 = """
name: workflow-alpha
description: Alpha workflow from templates
version: "1.0"

blocks:
  - id: block1
    type: EchoBlock
    inputs:
      message: "Alpha from templates"
      delay_ms: 0
"""
    (dir1 / "alpha.yaml").write_text(workflow1)

    workflow2 = """
name: workflow-beta
description: Beta workflow from templates
version: "1.0"

blocks:
  - id: block1
    type: EchoBlock
    inputs:
      message: "Beta from templates"
      delay_ms: 0
"""
    (dir1 / "beta.yaml").write_text(workflow2)

    # Directory 2: library (priority 2)
    dir2 = tmp_path / "library"
    dir2.mkdir()

    workflow3 = """
name: workflow-gamma
description: Gamma workflow from library
version: "2.0"

blocks:
  - id: block1
    type: EchoBlock
    inputs:
      message: "Gamma from library"
      delay_ms: 0
"""
    (dir2 / "gamma.yaml").write_text(workflow3)

    # Duplicate workflow in library (should be skipped with default policy)
    workflow4 = """
name: workflow-alpha
description: Alpha workflow from library (duplicate)
version: "2.0"

blocks:
  - id: block1
    type: EchoBlock
    inputs:
      message: "Alpha from library"
      delay_ms: 0
"""
    (dir2 / "alpha_duplicate.yaml").write_text(workflow4)

    # Directory 3: user (priority 3)
    dir3 = tmp_path / "user"
    dir3.mkdir()

    workflow5 = """
name: workflow-delta
description: Delta workflow from user
version: "1.0"

blocks:
  - id: block1
    type: EchoBlock
    inputs:
      message: "Delta from user"
      delay_ms: 0
"""
    (dir3 / "delta.yaml").write_text(workflow5)

    return dir1, dir2, dir3


class TestMultiDirectoryLoading:
    """Test loading workflows from multiple directories."""

    def test_load_from_directories_success(
        self, registry: WorkflowRegistry, multi_workflow_dirs: tuple[Path, Path, Path]
    ) -> None:
        """Test successful multi-directory loading."""
        dir1, dir2, dir3 = multi_workflow_dirs

        result = registry.load_from_directories([dir1, dir2, dir3])

        assert result.is_success

        assert isinstance(result.value, dict)

        # Check counts per directory
        assert result.value[str(dir1.resolve())] == 2  # alpha, beta

        assert result.value[str(dir2.resolve())] == 1  # gamma (alpha duplicate skipped)
        assert result.value[str(dir3.resolve())] == 1  # delta

        # Check all workflows loaded
        assert registry.exists("workflow-alpha")

        assert registry.exists("workflow-beta")
        assert registry.exists("workflow-gamma")

        assert registry.exists("workflow-delta")

        # Total count
        assert len(registry) == 4

    def test_load_from_directories_empty_list(self, registry: WorkflowRegistry) -> None:
        """Test loading with empty directory list."""
        result = registry.load_from_directories([])

        assert not result.is_success

        assert "No directories provided" in result.error

    def test_load_from_directories_priority_ordering(
        self, registry: WorkflowRegistry, multi_workflow_dirs: tuple[Path, Path, Path]
    ) -> None:
        """Test that first directory takes precedence (skip mode)."""
        dir1, dir2, dir3 = multi_workflow_dirs

        result = registry.load_from_directories([dir1, dir2, dir3], on_duplicate="skip")

        assert result.is_success

        # workflow-alpha from dir1 should be kept (first loaded)
        workflow = registry.get("workflow-alpha")
        assert "templates" in workflow.description

        assert registry.get_workflow_source("workflow-alpha") == dir1.resolve()

    def test_load_from_directories_skip_mode(
        self, registry: WorkflowRegistry, multi_workflow_dirs: tuple[Path, Path, Path]
    ) -> None:
        """Test duplicate handling with skip mode."""
        dir1, dir2, dir3 = multi_workflow_dirs

        result = registry.load_from_directories([dir1, dir2, dir3], on_duplicate="skip")

        assert result.is_success

        assert len(registry) == 4  # 4 unique workflows

        # First version kept
        assert "templates" in registry.get("workflow-alpha").description

    def test_load_from_directories_overwrite_mode(
        self, registry: WorkflowRegistry, multi_workflow_dirs: tuple[Path, Path, Path]
    ) -> None:
        """Test duplicate handling with overwrite mode."""
        dir1, dir2, dir3 = multi_workflow_dirs

        result = registry.load_from_directories([dir1, dir2, dir3], on_duplicate="overwrite")

        assert result.is_success

        assert len(registry) == 4  # 4 unique workflows

        # Last version kept (from library)
        workflow = registry.get("workflow-alpha")
        assert "library" in workflow.description

        assert registry.get_workflow_source("workflow-alpha") == dir2.resolve()

    def test_load_from_directories_error_mode(
        self, registry: WorkflowRegistry, multi_workflow_dirs: tuple[Path, Path, Path]
    ) -> None:
        """Test duplicate handling with error mode."""
        dir1, dir2, dir3 = multi_workflow_dirs

        result = registry.load_from_directories([dir1, dir2, dir3], on_duplicate="error")

        assert not result.is_success

        assert "Duplicate workflow" in result.error
        assert "workflow-alpha" in result.error

    def test_load_from_directories_nonexistent_dir(
        self, registry: WorkflowRegistry, tmp_path: Path
    ) -> None:
        """Test loading with non-existent directory in list."""
        dir1 = tmp_path / "templates"
        dir1.mkdir()

        workflow = """
name: test-wf
description: Test
version: "1.0"

blocks:
  - id: block1
    type: EchoBlock
    inputs:
      message: "Test"
      delay_ms: 0
"""
        (dir1 / "test.yaml").write_text(workflow)

        nonexistent = tmp_path / "nonexistent"

        result = registry.load_from_directories([dir1, nonexistent])

        # Should succeed but skip nonexistent directory
        assert result.is_success

        assert result.value[str(dir1.resolve())] == 1
        assert result.value[str(nonexistent.resolve())] == 0

    def test_load_from_directories_source_tracking(
        self, registry: WorkflowRegistry, multi_workflow_dirs: tuple[Path, Path, Path]
    ) -> None:
        """Test that source directories are tracked correctly."""
        dir1, dir2, dir3 = multi_workflow_dirs

        result = registry.load_from_directories([dir1, dir2, dir3])

        assert result.is_success

        # Check source tracking
        assert registry.get_workflow_source("workflow-alpha") == dir1.resolve()

        assert registry.get_workflow_source("workflow-beta") == dir1.resolve()
        assert registry.get_workflow_source("workflow-gamma") == dir2.resolve()

        assert registry.get_workflow_source("workflow-delta") == dir3.resolve()

        # List workflows by source
        dir1_workflows = registry.list_by_source(dir1.resolve())
        assert len(dir1_workflows) == 2

        assert set(dir1_workflows) == {"workflow-alpha", "workflow-beta"}

        dir2_workflows = registry.list_by_source(dir2.resolve())
        assert len(dir2_workflows) == 1

        assert dir2_workflows == ["workflow-gamma"]

        dir3_workflows = registry.list_by_source(dir3.resolve())
        assert len(dir3_workflows) == 1

        assert dir3_workflows == ["workflow-delta"]

    def test_load_from_directories_mixed_valid_invalid(
        self, registry: WorkflowRegistry, tmp_path: Path
    ) -> None:
        """Test loading from mix of valid and invalid directories."""
        dir1 = tmp_path / "valid"
        dir1.mkdir()

        workflow = """
name: valid-wf
description: Valid workflow
version: "1.0"

blocks:
  - id: block1
    type: EchoBlock
    inputs:
      message: "Valid"
      delay_ms: 0
"""
        (dir1 / "valid.yaml").write_text(workflow)

        # Create a file instead of directory
        file_path = tmp_path / "not_a_dir.txt"
        file_path.write_text("This is a file, not a directory")

        result = registry.load_from_directories([dir1, file_path])

        assert result.is_success

        assert result.value[str(dir1.resolve())] == 1
        assert result.value[str(file_path.resolve())] == 0

        assert len(registry) == 1

    def test_load_from_directories_backward_compatibility(
        self, registry: WorkflowRegistry, temp_workflow_dir: Path
    ) -> None:
        """Test that single directory loading still works."""
        # Load using old method
        result1 = registry.load_from_directory(temp_workflow_dir)
        assert result1.is_success

        assert result1.value == 3

        registry.clear()

        # Load using new method with single directory
        result2 = registry.load_from_directories([temp_workflow_dir])
        assert result2.is_success

        assert isinstance(result2.value, dict)
        assert result2.value[str(temp_workflow_dir.resolve())] == 3


class TestTagFiltering:
    """Test tag-based workflow filtering functionality."""

    def test_list_metadata_by_tags_empty_registry(
        self, registry: WorkflowRegistry
    ) -> None:
        """Test tag filtering with empty registry."""
        result = registry.list_metadata_by_tags(["python"])
        assert result == []

    def test_list_metadata_by_tags_empty_tag_list(
        self, registry: WorkflowRegistry
    ) -> None:
        """Test that empty tag list returns empty result."""
        wf = WorkflowDefinition("test-wf", "Test", [])
        schema = WorkflowSchema(
            name="test-wf",
            description="Test",
            tags=["python", "linting"],
            blocks=[{"id": "b1", "type": "EchoBlock", "inputs": {}, "depends_on": []}],
        )
        registry.register(wf, schema)

        result = registry.list_metadata_by_tags([])
        assert result == []

    def test_list_metadata_by_tags_single_tag_match(
        self, registry: WorkflowRegistry
    ) -> None:
        """Test filtering with single tag."""
        # Create workflow with tags
        wf1 = WorkflowDefinition("python-wf", "Python workflow", [])
        schema1 = WorkflowSchema(
            name="python-wf",
            description="Python workflow",
            tags=["python", "linting", "ruff"],
            blocks=[{"id": "b1", "type": "EchoBlock", "inputs": {}, "depends_on": []}],
        )

        # Create workflow without matching tag
        wf2 = WorkflowDefinition("git-wf", "Git workflow", [])
        schema2 = WorkflowSchema(
            name="git-wf",
            description="Git workflow",
            tags=["git", "version-control"],
            blocks=[{"id": "b1", "type": "EchoBlock", "inputs": {}, "depends_on": []}],
        )

        registry.register(wf1, schema1)
        registry.register(wf2, schema2)

        # Filter by "python" tag
        result = registry.list_metadata_by_tags(["python"])
        assert len(result) == 1

        assert result[0]["name"] == "python-wf"
        assert "python" in result[0]["tags"]

    def test_list_metadata_by_tags_multiple_tags_and_semantics(
        self, registry: WorkflowRegistry
    ) -> None:
        """Test filtering with multiple tags using AND semantics."""
        # Workflow with both tags
        wf1 = WorkflowDefinition("lint-python", "Python linting", [])
        schema1 = WorkflowSchema(
            name="lint-python",
            description="Python linting",
            tags=["python", "linting", "ruff", "mypy"],
            blocks=[{"id": "b1", "type": "EchoBlock", "inputs": {}, "depends_on": []}],
        )

        # Workflow with only one tag
        wf2 = WorkflowDefinition("run-pytest", "Run Python tests", [])
        schema2 = WorkflowSchema(
            name="run-pytest",
            description="Run Python tests",
            tags=["python", "testing", "pytest"],
            blocks=[{"id": "b1", "type": "EchoBlock", "inputs": {}, "depends_on": []}],
        )

        # Workflow with different tags
        wf3 = WorkflowDefinition("lint-node", "Node linting", [])
        schema3 = WorkflowSchema(
            name="lint-node",
            description="Node linting",
            tags=["node", "linting", "eslint"],
            blocks=[{"id": "b1", "type": "EchoBlock", "inputs": {}, "depends_on": []}],
        )

        registry.register(wf1, schema1)
        registry.register(wf2, schema2)
        registry.register(wf3, schema3)

        # Filter by both "python" AND "linting"
        result = registry.list_metadata_by_tags(["python", "linting"])
        assert len(result) == 1

        assert result[0]["name"] == "lint-python"

    def test_list_metadata_by_tags_match_all_false(
        self, registry: WorkflowRegistry
    ) -> None:
        """Test filtering with OR semantics (match_all=False)."""
        wf1 = WorkflowDefinition("python-ci", "Python CI", [])
        schema1 = WorkflowSchema(
            name="python-ci",
            description="Python CI",
            tags=["python", "ci", "testing"],
            blocks=[{"id": "b1", "type": "EchoBlock", "inputs": {}, "depends_on": []}],
        )

        wf2 = WorkflowDefinition("node-ci", "Node CI", [])
        schema2 = WorkflowSchema(
            name="node-ci",
            description="Node CI",
            tags=["node", "ci", "testing"],
            blocks=[{"id": "b1", "type": "EchoBlock", "inputs": {}, "depends_on": []}],
        )

        wf3 = WorkflowDefinition("deploy", "Deploy", [])
        schema3 = WorkflowSchema(
            name="deploy",
            description="Deploy",
            tags=["deployment", "production"],
            blocks=[{"id": "b1", "type": "EchoBlock", "inputs": {}, "depends_on": []}],
        )

        registry.register(wf1, schema1)
        registry.register(wf2, schema2)
        registry.register(wf3, schema3)

        # Filter with OR semantics: workflows with "python" OR "node"
        result = registry.list_metadata_by_tags(["python", "node"], match_all=False)
        assert len(result) == 2
        names = {wf["name"] for wf in result}
        assert names == {"python-ci", "node-ci"}

    def test_list_metadata_by_tags_no_schema(
        self, registry: WorkflowRegistry
    ) -> None:
        """Test that workflows without schemas are not included."""
        # Workflow without schema
        wf1 = WorkflowDefinition("no-schema-wf", "No schema", [])
        registry.register(wf1)

        # Workflow with schema and tags
        wf2 = WorkflowDefinition("with-schema-wf", "With schema", [])
        schema2 = WorkflowSchema(
            name="with-schema-wf",
            description="With schema",
            tags=["python", "testing"],
            blocks=[{"id": "b1", "type": "EchoBlock", "inputs": {}, "depends_on": []}],
        )
        registry.register(wf2, schema2)

        result = registry.list_metadata_by_tags(["python"])
        assert len(result) == 1

        assert result[0]["name"] == "with-schema-wf"

    def test_list_metadata_by_tags_workflow_with_empty_tags(
        self, registry: WorkflowRegistry
    ) -> None:
        """Test that workflows with empty tag list are not included."""
        wf = WorkflowDefinition("empty-tags-wf", "Empty tags", [])
        schema = WorkflowSchema(
            name="empty-tags-wf",
            description="Empty tags",
            tags=[],  # Empty tags list
            blocks=[{"id": "b1", "type": "EchoBlock", "inputs": {}, "depends_on": []}],
        )
        registry.register(wf, schema)

        result = registry.list_metadata_by_tags(["python"])
        assert result == []

    def test_list_metadata_by_tags_case_sensitive(
        self, registry: WorkflowRegistry
    ) -> None:
        """Test that tag matching is case-sensitive."""
        wf = WorkflowDefinition("test-wf", "Test", [])
        schema = WorkflowSchema(
            name="test-wf",
            description="Test",
            tags=["Python", "Testing"],  # Capitalized tags
            blocks=[{"id": "b1", "type": "EchoBlock", "inputs": {}, "depends_on": []}],
        )
        registry.register(wf, schema)

        # Lowercase search should not match
        result = registry.list_metadata_by_tags(["python"])
        assert result == []

        # Exact case should match
        result = registry.list_metadata_by_tags(["Python"])
        assert len(result) == 1

        assert result[0]["name"] == "test-wf"
