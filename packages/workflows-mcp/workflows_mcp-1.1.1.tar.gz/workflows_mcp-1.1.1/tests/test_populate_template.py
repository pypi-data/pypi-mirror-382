"""
Comprehensive tests for PopulateTemplate workflow block.

Tests cover:
- Basic template rendering (inline)
- Template from file (template_path)
- Variable substitution (simple and nested)
- Conditional rendering ({% if %})
- Loop rendering ({% for %})
- Jinja2 filters (upper, lower, default, etc.)
- Strict mode (fail on undefined)
- Non-strict mode (silent undefined)
- Trim blocks and lstrip blocks
- Template syntax error handling
- Missing template file error
- Variables used extraction
- Complex templates with multiple variables
- Integration workflows (ReadFile → PopulateTemplate → CreateFile)
- Registry verification
"""

import tempfile
from pathlib import Path

import pytest

from workflows_mcp.engine import BLOCK_REGISTRY
from workflows_mcp.engine.blocks_file import (
    CreateFile,
    PopulateTemplate,
    PopulateTemplateOutput,
    ReadFile,
)
from workflows_mcp.engine.loader import load_workflow_from_yaml


@pytest.fixture
def temp_dir():
    """Create a temporary directory for file operations."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.mark.asyncio
class TestPopulateTemplateBlock:
    """Tests for PopulateTemplate workflow block."""

    async def test_basic_template_rendering(self, temp_dir):
        """Test basic inline template rendering."""
        template = "Hello, {{ name }}!"
        variables = {"name": "World"}

        block = PopulateTemplate(
            id="populate_basic",
            inputs={
                "template": template,
                "variables": variables,
            },
        )

        result = await block.execute({})

        assert result.is_success
        output = result.value
        assert isinstance(output, PopulateTemplateOutput)
        assert output.success is True
        assert output.rendered == "Hello, World!"
        assert output.template_source == "inline"
        assert "name" in output.variables_used
        assert output.size_bytes == len(b"Hello, World!")

    async def test_template_from_file(self, temp_dir):
        """Test loading template from file."""
        template_path = temp_dir / "template.j2"
        template_content = "Project: {{ project }}\nVersion: {{ version }}"
        template_path.write_text(template_content)

        variables = {"project": "MyProject", "version": "1.0.0"}

        block = PopulateTemplate(
            id="populate_from_file",
            inputs={
                "template": "",  # Ignored when template_path is set
                "template_path": str(template_path),
                "variables": variables,
            },
        )

        result = await block.execute({})

        assert result.is_success
        output = result.value
        assert output.success is True
        assert "Project: MyProject" in output.rendered
        assert "Version: 1.0.0" in output.rendered
        assert output.template_source == "file"
        assert "project" in output.variables_used
        assert "version" in output.variables_used

    async def test_variable_substitution_simple(self, temp_dir):
        """Test simple variable substitution."""
        template = "Name: {{ name }}, Age: {{ age }}, City: {{ city }}"
        variables = {"name": "Alice", "age": 30, "city": "New York"}

        block = PopulateTemplate(
            id="populate_vars",
            inputs={
                "template": template,
                "variables": variables,
            },
        )

        result = await block.execute({})

        assert result.is_success
        assert result.value.rendered == "Name: Alice, Age: 30, City: New York"

    async def test_variable_substitution_nested(self, temp_dir):
        """Test nested variable access in templates."""
        template = "User: {{ user.name }}, Email: {{ user.email }}"
        variables = {"user": {"name": "Bob", "email": "bob@example.com"}}

        block = PopulateTemplate(
            id="populate_nested",
            inputs={
                "template": template,
                "variables": variables,
            },
        )

        result = await block.execute({})

        assert result.is_success
        assert "User: Bob" in result.value.rendered
        assert "Email: bob@example.com" in result.value.rendered
        # Variables used should include the dotted path
        assert "user.name" in result.value.variables_used or "user" in result.value.variables_used

    async def test_conditional_rendering(self, temp_dir):
        """Test conditional rendering with {% if %}."""
        template = """
{% if debug %}
Debug mode enabled
{% else %}
Production mode
{% endif %}
"""
        # Test with debug=True
        block = PopulateTemplate(
            id="populate_if_true",
            inputs={
                "template": template,
                "variables": {"debug": True},
            },
        )

        result = await block.execute({})
        assert result.is_success
        assert "Debug mode enabled" in result.value.rendered
        assert "Production mode" not in result.value.rendered

        # Test with debug=False
        block2 = PopulateTemplate(
            id="populate_if_false",
            inputs={
                "template": template,
                "variables": {"debug": False},
            },
        )

        result2 = await block2.execute({})
        assert result2.is_success
        assert "Production mode" in result2.value.rendered
        assert "Debug mode enabled" not in result2.value.rendered

    async def test_loop_rendering(self, temp_dir):
        """Test loop rendering with {% for %}."""
        template = """
Features:
{% for feature in features %}
- {{ feature }}
{% endfor %}
"""
        variables = {"features": ["Fast", "Reliable", "Scalable"]}

        block = PopulateTemplate(
            id="populate_loop",
            inputs={
                "template": template,
                "variables": variables,
            },
        )

        result = await block.execute({})

        assert result.is_success
        rendered = result.value.rendered
        assert "- Fast" in rendered
        assert "- Reliable" in rendered
        assert "- Scalable" in rendered

    async def test_jinja2_filters(self, temp_dir):
        """Test Jinja2 built-in filters."""
        template = """
Upper: {{ name | upper }}
Lower: {{ name | lower }}
Title: {{ name | title }}
Default: {{ missing | default('N/A') }}
"""
        variables = {"name": "hello world"}

        block = PopulateTemplate(
            id="populate_filters",
            inputs={
                "template": template,
                "variables": variables,
            },
        )

        result = await block.execute({})

        assert result.is_success
        rendered = result.value.rendered
        assert "Upper: HELLO WORLD" in rendered
        assert "Lower: hello world" in rendered
        assert "Title: Hello World" in rendered
        assert "Default: N/A" in rendered

    async def test_strict_mode_undefined_variable(self, temp_dir):
        """Test strict mode fails on undefined variables."""
        template = "Hello, {{ name }}! Your role is {{ role }}."
        variables = {"name": "Alice"}  # Missing 'role'

        block = PopulateTemplate(
            id="populate_strict",
            inputs={
                "template": template,
                "variables": variables,
                "strict": True,
            },
        )

        result = await block.execute({})

        assert not result.is_success
        assert "Undefined variable" in result.error
        assert "strict mode" in result.error

    async def test_non_strict_mode_undefined_variable(self, temp_dir):
        """Test non-strict mode silently handles undefined variables."""
        template = "Hello, {{ name }}! Your role is {{ role }}."
        variables = {"name": "Alice"}  # Missing 'role'

        block = PopulateTemplate(
            id="populate_non_strict",
            inputs={
                "template": template,
                "variables": variables,
                "strict": False,  # Default
            },
        )

        result = await block.execute({})

        assert result.is_success
        # Jinja2 renders undefined as empty string by default
        assert "Hello, Alice!" in result.value.rendered

    async def test_trim_blocks(self, temp_dir):
        """Test trim_blocks option."""
        template = """
{% if true %}
Line 1
{% endif %}
Line 2
"""
        # Test with trim_blocks=True (default)
        block = PopulateTemplate(
            id="populate_trim_true",
            inputs={
                "template": template,
                "variables": {},
                "trim_blocks": True,
            },
        )

        result = await block.execute({})
        assert result.is_success
        # With trim_blocks, no extra newlines after blocks
        assert result.value.rendered.count("\n") <= 3

        # Test with trim_blocks=False
        block2 = PopulateTemplate(
            id="populate_trim_false",
            inputs={
                "template": template,
                "variables": {},
                "trim_blocks": False,
            },
        )

        result2 = await block2.execute({})
        assert result2.is_success
        # Without trim_blocks, extra newlines remain
        assert result2.value.rendered.count("\n") >= 3

    async def test_lstrip_blocks(self, temp_dir):
        """Test lstrip_blocks option."""
        template = "    {% if true %}Content{% endif %}"

        # Test with lstrip_blocks=True (default)
        block = PopulateTemplate(
            id="populate_lstrip_true",
            inputs={
                "template": template,
                "variables": {},
                "lstrip_blocks": True,
            },
        )

        result = await block.execute({})
        assert result.is_success
        # With lstrip_blocks, leading whitespace before block is stripped
        assert result.value.rendered == "Content"

        # Test with lstrip_blocks=False
        block2 = PopulateTemplate(
            id="populate_lstrip_false",
            inputs={
                "template": template,
                "variables": {},
                "lstrip_blocks": False,
            },
        )

        result2 = await block2.execute({})
        assert result2.is_success
        # Without lstrip_blocks, leading whitespace remains
        assert result2.value.rendered == "    Content"

    async def test_template_syntax_error(self, temp_dir):
        """Test template syntax error handling."""
        template = "Hello, {{ name"  # Missing closing braces

        block = PopulateTemplate(
            id="populate_syntax_error",
            inputs={
                "template": template,
                "variables": {"name": "Alice"},
            },
        )

        result = await block.execute({})

        assert not result.is_success
        assert "Template syntax error" in result.error

    async def test_missing_template_file(self, temp_dir):
        """Test error handling for missing template file."""
        template_path = temp_dir / "nonexistent.j2"

        block = PopulateTemplate(
            id="populate_missing",
            inputs={
                "template": "",
                "template_path": str(template_path),
                "variables": {},
            },
        )

        result = await block.execute({})

        assert not result.is_success
        assert "Template file not found" in result.error

    async def test_variables_used_extraction(self, temp_dir):
        """Test extraction of variables used in template."""
        template = """
{{ name }} {{ age }} {{ city }}
{% if debug %}{{ debug_info }}{% endif %}
{{ name }}  {# Duplicate reference #}
"""
        variables = {"name": "Alice", "age": 30, "city": "NYC", "debug": False}

        block = PopulateTemplate(
            id="populate_vars_extract",
            inputs={
                "template": template,
                "variables": variables,
            },
        )

        result = await block.execute({})

        assert result.is_success
        output = result.value
        # Should extract variable names from {{ variable }} patterns
        # Note: Our regex extracts {{ var }} patterns, not {% if var %} patterns
        assert "name" in output.variables_used
        assert "age" in output.variables_used
        assert "city" in output.variables_used
        assert "debug_info" in output.variables_used
        # Duplicates should be removed
        assert len(output.variables_used) == len(set(output.variables_used))
        # List should be sorted
        assert output.variables_used == sorted(output.variables_used)

    async def test_complex_template_multiple_variables(self, temp_dir):
        """Test complex template with multiple variables and features."""
        template = """
# {{ project_name }}

**Version**: {{ version }}
**Author**: {{ author }}

## Description
{{ description }}

## Features
{% for feature in features %}
- {{ feature }}
{% endfor %}

{% if license %}
## License
{{ license }}
{% endif %}

## Contact
Email: {{ contact.email | default('N/A') }}
Website: {{ contact.website | default('N/A') }}
"""
        variables = {
            "project_name": "Awesome Project",
            "version": "2.0.0",
            "author": "Jane Doe",
            "description": "A really awesome project",
            "features": ["Feature A", "Feature B", "Feature C"],
            "license": "MIT",
            "contact": {"email": "jane@example.com"},
        }

        block = PopulateTemplate(
            id="populate_complex",
            inputs={
                "template": template,
                "variables": variables,
            },
        )

        result = await block.execute({})

        assert result.is_success
        rendered = result.value.rendered
        assert "# Awesome Project" in rendered
        assert "**Version**: 2.0.0" in rendered
        assert "**Author**: Jane Doe" in rendered
        assert "- Feature A" in rendered
        assert "- Feature B" in rendered
        assert "- Feature C" in rendered
        assert "## License" in rendered
        assert "MIT" in rendered
        assert "Email: jane@example.com" in rendered
        assert "Website: N/A" in rendered  # Default filter applied

    async def test_registry_verification(self):
        """Test that PopulateTemplate is registered in BLOCK_REGISTRY."""
        assert "PopulateTemplate" in BLOCK_REGISTRY.list_types()
        block_class = BLOCK_REGISTRY.get("PopulateTemplate")
        assert block_class == PopulateTemplate

    async def test_execution_time_metadata(self, temp_dir):
        """Test execution time metadata is recorded."""
        template = "Simple template"

        block = PopulateTemplate(
            id="populate_metadata",
            inputs={
                "template": template,
                "variables": {},
            },
        )

        result = await block.execute({})

        assert result.is_success
        assert "execution_time_ms" in result.metadata
        assert result.metadata["execution_time_ms"] >= 0


@pytest.mark.asyncio
class TestPopulateTemplateIntegration:
    """Integration tests for PopulateTemplate with other blocks."""

    async def test_read_populate_create_workflow(self, temp_dir):
        """Test ReadFile → PopulateTemplate → CreateFile workflow."""
        # Create template file
        template_path = temp_dir / "readme.j2"
        template_content = """# {{ project_name }}

Author: {{ author }}
Version: {{ version }}

{{ description }}
"""
        template_path.write_text(template_content)

        # Step 1: Read template
        read_block = ReadFile(
            id="read_template",
            inputs={"path": str(template_path)},
        )

        read_result = await read_block.execute({})
        assert read_result.is_success

        # Step 2: Populate template with variables
        context = {"read_template": read_result.value}
        populate_block = PopulateTemplate(
            id="populate_readme",
            inputs={
                "template": read_result.value.content,
                "variables": {
                    "project_name": "MyProject",
                    "author": "John Doe",
                    "version": "1.0.0",
                    "description": "A sample project description",
                },
            },
        )

        populate_result = await populate_block.execute(context)
        assert populate_result.is_success

        # Step 3: Write rendered content to file
        output_path = temp_dir / "README.md"
        context["populate_readme"] = populate_result.value
        create_block = CreateFile(
            id="create_readme",
            inputs={
                "path": str(output_path),
                "content": populate_result.value.rendered,
            },
        )

        create_result = await create_block.execute(context)
        assert create_result.is_success

        # Verify final output
        assert output_path.exists()
        final_content = output_path.read_text()
        assert "# MyProject" in final_content
        assert "Author: John Doe" in final_content
        assert "Version: 1.0.0" in final_content
        assert "A sample project description" in final_content

    async def test_workflow_yaml_integration(self, temp_dir):
        """Test PopulateTemplate in a full YAML workflow."""
        # Create template file
        template_path = temp_dir / "config.j2"
        template_content = """
[app]
name = {{ app_name }}
port = {{ port }}
debug = {{ debug }}
"""
        template_path.write_text(template_content)

        workflow_yaml = f"""
name: test-populate-template
description: Test PopulateTemplate in workflow
tags: [test]

blocks:
  - id: read_template
    type: ReadFile
    inputs:
      path: "{template_path}"

  - id: populate_config
    type: PopulateTemplate
    inputs:
      template: "${{read_template.content}}"
      variables:
        app_name: "MyApp"
        port: 8080
        debug: true
    depends_on:
      - read_template

  - id: write_config
    type: CreateFile
    inputs:
      path: "{temp_dir}/config.ini"
      content: "${{populate_config.rendered}}"
    depends_on:
      - populate_config
"""

        # Load workflow from YAML
        load_result = load_workflow_from_yaml(workflow_yaml)
        assert load_result.is_success, f"Failed to load workflow: {load_result.error}"
        workflow = load_result.value

        # Execute workflow
        from workflows_mcp.engine import WorkflowExecutor

        executor = WorkflowExecutor()
        executor.load_workflow(workflow)
        result = await executor.execute_workflow("test-populate-template", {})

        assert result.is_success

        # Verify final output
        config_path = temp_dir / "config.ini"
        assert config_path.exists()
        config_content = config_path.read_text()
        assert "name = MyApp" in config_content
        assert "port = 8080" in config_content
        assert "debug = True" in config_content
