"""Validation script for Phase 0 - Task 2: MCP Tool Skeleton.

This script validates:
1. Pydantic models are correctly defined
2. MCP tools are registered with FastMCP server
3. Tool invocation works (even with stub implementations)
4. Type schemas are generated correctly from type hints

Run with: uv run python test_tools.py
"""

import asyncio
import sys


def print_section(title: str) -> None:
    """Print a formatted section header."""
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}\n")


def print_success(message: str) -> None:
    """Print a success message."""
    print(f"✅ {message}")


def print_error(message: str) -> None:
    """Print an error message."""
    print(f"❌ {message}")


def print_info(message: str) -> None:
    """Print an info message."""
    print(f"ℹ️  {message}")


async def validate_pydantic_models() -> bool:
    """Validate Pydantic model definitions."""
    print_section("Task 1: Validate Pydantic Models")

    try:
        from workflows_mcp.tools import (
            ExecuteWorkflowInput,
            ExecuteWorkflowOutput,
            WorkflowDetailedInfo,
            WorkflowInfo,
        )

        print_success("All Pydantic models imported successfully")

        # Test ExecuteWorkflowInput
        input_model = ExecuteWorkflowInput(
            workflow="test-workflow", inputs={"key": "value"}, async_execution=False
        )
        print_success(
            f"ExecuteWorkflowInput validation: {input_model.workflow}, {len(input_model.inputs)} inputs"
        )

        # Test ExecuteWorkflowOutput
        output_model = ExecuteWorkflowOutput(
            status="success",
            outputs={"result": "test"},
            execution_time=1.23,
            error=None,
        )
        print_success(
            f"ExecuteWorkflowOutput validation: {output_model.status}, {output_model.execution_time}s"
        )

        # Test WorkflowInfo
        info_model = WorkflowInfo(name="test", description="Test workflow", category="test")
        print_success(f"WorkflowInfo validation: {info_model.name} ({info_model.category})")

        # Test WorkflowDetailedInfo
        detailed_model = WorkflowDetailedInfo(
            name="test",
            description="Test workflow",
            inputs={"param": "string"},
            outputs={"result": "string"},
            blocks=["block1", "block2"],
            dependencies={"block1": [], "block2": ["block1"]},
        )
        print_success(
            f"WorkflowDetailedInfo validation: {detailed_model.name}, {len(detailed_model.blocks)} blocks"
        )

        print_info("All Pydantic models validated successfully")
        return True

    except Exception as e:
        print_error(f"Pydantic model validation failed: {e}")
        return False


async def validate_tool_registration() -> bool:
    """Validate MCP tool registration."""
    print_section("Task 2: Validate MCP Tool Registration")

    try:
        from workflows_mcp.server import mcp

        print_success("FastMCP server imported successfully")

        # Check that tools are registered
        # In FastMCP, list_tools() is async and returns a list directly
        tools = await mcp.list_tools()
        tool_names = [tool.name for tool in tools]

        print_info(f"Registered tools: {tool_names}")

        expected_tools = ["execute_workflow", "list_workflows", "get_workflow_info"]
        for tool_name in expected_tools:
            if tool_name in tool_names:
                print_success(f"Tool '{tool_name}' is registered")
            else:
                print_error(f"Tool '{tool_name}' is NOT registered")
                return False

        print_info(f"All {len(expected_tools)} expected tools are registered")
        return True

    except Exception as e:
        print_error(f"Tool registration validation failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def validate_tool_invocation() -> bool:
    """Validate tool invocation with stub implementations."""
    print_section("Task 3: Validate Tool Invocation")

    try:
        # Import the tool functions directly from server module
        from workflows_mcp.server import execute_workflow, get_workflow_info, list_workflows

        print_success("All tool functions imported successfully")

        # Test execute_workflow with real workflow
        print_info("Testing execute_workflow...")
        result1 = await execute_workflow(
            workflow="hello-world", inputs={"message": "test"}, async_execution=False
        )
        assert isinstance(result1, dict), "execute_workflow should return dict"
        assert "status" in result1, "execute_workflow should have 'status' field"
        assert result1["status"] == "success", "execute_workflow should return 'success' status"
        print_success(
            f"execute_workflow returned: {result1['status']} with {len(result1.get('outputs', {}))} outputs"
        )

        # Test list_workflows stub
        print_info("Testing list_workflows...")
        result2 = await list_workflows(category="all")
        assert isinstance(result2, list), "list_workflows should return list"
        assert len(result2) > 0, "list_workflows should return non-empty list"
        print_success(f"list_workflows returned {len(result2)} workflows")

        # Test list_workflows with category filter
        print_info("Testing list_workflows with category filter...")
        result3 = await list_workflows(category="test")
        assert isinstance(result3, list), "list_workflows should return list"
        print_success(f"list_workflows(category='test') returned {len(result3)} workflows")

        # Test get_workflow_info with real workflow
        print_info("Testing get_workflow_info...")
        result4 = await get_workflow_info(workflow="hello-world")
        assert isinstance(result4, dict), "get_workflow_info should return dict"
        assert "name" in result4, "get_workflow_info should have 'name' field"
        assert "blocks" in result4, "get_workflow_info should have 'blocks' field"
        print_success(
            f"get_workflow_info returned info for '{result4['name']}' with {len(result4.get('blocks', []))} blocks"
        )

        print_info("All tool stubs validated successfully")
        return True

    except Exception as e:
        print_error(f"Tool invocation validation failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def validate_type_schemas() -> bool:
    """Validate that type hints generate correct schemas."""
    print_section("Task 4: Validate Type Schema Generation")

    try:
        from workflows_mcp.server import mcp

        print_success("FastMCP server imported for schema validation")

        # Check tool schemas - list_tools() is async and returns a list directly
        tools = await mcp.list_tools()

        for tool in tools:
            print_info(f"Tool: {tool.name}")
            print_info(
                f"  Description: {tool.description[:80]}..."
                if len(tool.description) > 80
                else f"  Description: {tool.description}"
            )

            # Validate inputSchema exists
            if hasattr(tool, "inputSchema") and tool.inputSchema:
                schema = tool.inputSchema
                print_success(f"  Input schema generated: {schema.get('type', 'unknown')} type")

                # Check for properties
                if "properties" in schema:
                    props = schema["properties"]
                    print_info(f"    Properties: {list(props.keys())}")
            else:
                print_error(f"  No input schema found for {tool.name}")

        print_info("Type schema validation completed")
        return True

    except Exception as e:
        print_error(f"Type schema validation failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main() -> int:
    """Main validation function."""
    print("\n" + "=" * 70)
    print("  Phase 0 - Task 2: MCP Tool Skeleton Validation")
    print("=" * 70)

    results = []

    # Run all validation tasks
    results.append(await validate_pydantic_models())
    results.append(await validate_tool_registration())
    results.append(await validate_tool_invocation())
    results.append(await validate_type_schemas())

    # Print summary
    print_section("Validation Summary")

    total = len(results)
    passed = sum(results)

    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")

    if all(results):
        print_success("\n🎉 All validation tests passed!")
        print_info("Phase 0 - Task 2 is complete")
        return 0
    else:
        print_error("\n❌ Some validation tests failed")
        print_info("Please review the errors above")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
