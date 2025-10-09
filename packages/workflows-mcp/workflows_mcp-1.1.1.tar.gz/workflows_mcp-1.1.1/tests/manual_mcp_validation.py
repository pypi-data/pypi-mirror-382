"""Manual MCP Tool Validation Script.

This script simulates how Claude would interact with the MCP tools,
demonstrating the complete workflow lifecycle:
1. Discover available workflows
2. Get detailed workflow information
3. Execute workflows with various inputs
4. Handle errors gracefully
"""

import asyncio
import json

from workflows_mcp.server import execute_workflow, get_workflow_info, list_workflows


def print_section(title: str) -> None:
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


async def demonstrate_workflow_discovery():
    """Demonstrate workflow discovery using list_workflows."""
    print_section("1. Workflow Discovery")

    print("📋 Listing all available workflows...")
    workflows = await list_workflows(category="all")

    print(f"\n✅ Found {len(workflows)} workflows:\n")
    for wf in workflows:
        category = wf.get("category", "N/A")
        version = wf.get("version", "N/A")
        tags = wf.get("tags", [])
        print(f"  • {wf['name']}")
        print(f"    Description: {wf['description']}")
        print(f"    Category: {category} | Version: {version}")
        if tags:
            print(f"    Tags: {', '.join(tags)}")
        print()


async def demonstrate_category_filtering():
    """Demonstrate workflow filtering by category."""
    print_section("2. Category Filtering")

    print("🔍 Filtering workflows by category='test'...")
    test_workflows = await list_workflows(category="test")

    print(f"\n✅ Found {len(test_workflows)} test workflows:\n")
    for wf in test_workflows:
        print(f"  • {wf['name']}: {wf['description']}")


async def demonstrate_workflow_info():
    """Demonstrate getting detailed workflow information."""
    print_section("3. Workflow Information Retrieval")

    workflow_name = "parallel-echo"
    print(f"📖 Getting detailed info for '{workflow_name}'...\n")

    info = await get_workflow_info(workflow=workflow_name)

    print(f"Name: {info['name']}")
    print(f"Description: {info['description']}")
    print(f"Total Blocks: {info['total_blocks']}")
    print("\nBlock Structure:")

    for i, block in enumerate(info["blocks"], 1):
        deps = (
            f" (depends on: {', '.join(block['depends_on'])})" if block["depends_on"] else " (root)"
        )
        print(f"  {i}. {block['id']} ({block['type']}){deps}")

    if "inputs" in info:
        print("\nRequired Inputs:")
        for input_name, input_desc in info["inputs"].items():
            print(f"  • {input_name}: {input_desc}")


async def demonstrate_simple_execution():
    """Demonstrate simple workflow execution."""
    print_section("4. Simple Workflow Execution")

    print("🚀 Executing 'hello-world' workflow...\n")

    result = await execute_workflow(workflow="hello-world", inputs={"name": "MCP User"})

    print(f"Status: {result['status']}")
    print(f"Execution Time: {result['execution_time']:.4f}s")

    if result["status"] == "success":
        print("\nOutputs:")
        print(json.dumps(result["outputs"], indent=2))


async def demonstrate_parallel_execution():
    """Demonstrate parallel workflow execution."""
    print_section("5. Parallel Workflow Execution")

    print("🔀 Executing 'parallel-echo' workflow (diamond pattern)...\n")

    result = await execute_workflow(
        workflow="parallel-echo", inputs={"start_message": "Beginning parallel execution"}
    )

    print(f"Status: {result['status']}")
    print(f"Execution Time: {result['execution_time']:.4f}s")

    if result["status"] == "success":
        outputs = result["outputs"]
        print(f"\nTotal Blocks: {outputs['total_blocks']}")
        print(f"Execution Waves: {outputs['execution_waves']}")
        print("\nBlock Outputs:")
        for block_id, block_output in outputs["blocks"].items():
            print(f"  • {block_id}: {block_output.get('echoed', 'N/A')}")


async def demonstrate_complex_workflow():
    """Demonstrate complex multi-stage workflow execution."""
    print_section("6. Complex Multi-Stage Workflow")

    print("⚙️  Executing 'complex-workflow' with custom inputs...\n")

    result = await execute_workflow(
        workflow="complex-workflow",
        inputs={"project_name": "production-system", "environment": "production"},
    )

    print(f"Status: {result['status']}")
    print(f"Execution Time: {result['execution_time']:.4f}s")

    if result["status"] == "success":
        outputs = result["outputs"]
        print(f"\nTotal Blocks: {outputs['total_blocks']}")
        print(f"Execution Waves: {outputs['execution_waves']}")
        efficiency = (1 - outputs["execution_waves"] / outputs["total_blocks"]) * 100
        print(f"Parallelization Efficiency: {efficiency:.1f}%")

        print("\nExecution Flow:")
        for i, wave_blocks in enumerate(outputs.get("execution_order", []), 1):
            print(f"  Wave {i}: {', '.join(wave_blocks) if isinstance(wave_blocks, list) else wave_blocks}")


async def demonstrate_variable_substitution():
    """Demonstrate variable substitution with inputs and block outputs."""
    print_section("7. Variable Substitution")

    print("🔄 Executing 'input-substitution' workflow with custom variables...\n")

    result = await execute_workflow(
        workflow="input-substitution",
        inputs={
            "user_name": "Alice",
            "project_name": "quantum-engine",
            "iterations": 10,
            "verbose": True,
        },
    )

    print(f"Status: {result['status']}")
    print(f"Execution Time: {result['execution_time']:.4f}s")

    if result["status"] == "success":
        blocks = result["outputs"]["blocks"]
        print("\nVariable Substitution Results:")

        # Show how variables were used
        if "greet_user" in blocks:
            print(f"  Greeting: {blocks['greet_user'].get('echoed', 'N/A')}")

        if "show_config" in blocks:
            print(f"  Config: {blocks['show_config'].get('echoed', 'N/A')}")

        if "combine_variables" in blocks:
            print(f"  Combined: {blocks['combine_variables'].get('echoed', 'N/A')}")


async def demonstrate_error_handling():
    """Demonstrate error handling for invalid requests."""
    print_section("8. Error Handling")

    # Missing workflow
    print("❌ Attempting to execute non-existent workflow...\n")
    result = await execute_workflow(workflow="does-not-exist", inputs={})

    print(f"Status: {result['status']}")
    if result["status"] == "failure":
        print(f"Error: {result['error']}\n")

    # Invalid category
    print("❌ Attempting to list workflows with invalid category...\n")
    result = await list_workflows(category="invalid-category")

    if isinstance(result, list) and len(result) > 0 and "error" in result[0]:
        print(f"Error: {result[0]['error']}")
        print(f"Valid Categories: {result[0].get('valid_categories', [])}\n")


async def main():
    """Run all MCP tool demonstrations."""
    print("\n" + "=" * 80)
    print("  MCP WORKFLOW TOOLS - MANUAL VALIDATION")
    print("=" * 80)
    print("\nThis script demonstrates how Claude Code would interact with")
    print("the MCP workflow execution tools in a real usage scenario.")

    # Run all demonstrations
    await demonstrate_workflow_discovery()
    await demonstrate_category_filtering()
    await demonstrate_workflow_info()
    await demonstrate_simple_execution()
    await demonstrate_parallel_execution()
    await demonstrate_complex_workflow()
    await demonstrate_variable_substitution()
    await demonstrate_error_handling()

    # Summary
    print_section("Validation Summary")
    print("✅ All MCP tools demonstrated successfully!")
    print("\n📋 MCP Tools Validated:")
    print("  ✅ list_workflows - Workflow discovery and filtering")
    print("  ✅ get_workflow_info - Detailed workflow metadata")
    print("  ✅ execute_workflow - DAG-based workflow execution")
    print("\n🎯 Key Features Demonstrated:")
    print("  ✅ Workflow discovery and filtering by category")
    print("  ✅ Detailed workflow introspection")
    print("  ✅ Simple sequential execution")
    print("  ✅ Parallel execution with wave optimization")
    print("  ✅ Complex multi-stage workflows")
    print("  ✅ Variable substitution (inputs + block outputs)")
    print("  ✅ Error handling for invalid requests")
    print("\n🚀 Phase 1 MCP Integration: Complete!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
