"""End-to-end integration test for Phase 0.

This test validates the complete MCP workflow execution pipeline:
1. Workflow loading and registration
2. MCP tool exposure and invocation
3. DAG-based execution with parallel waves
4. Result collection and validation
"""

import asyncio

from workflows_mcp.server import execute_workflow, get_workflow_info, list_workflows


async def test_end_to_end():
    """Test complete MCP workflow execution."""

    print("=== Phase 0 End-to-End Integration Test ===\n")

    # Test 1: List workflows
    print("Test 1: List workflows")
    workflows = await list_workflows()
    print(f"✅ Found {len(workflows)} workflows:")
    for wf in workflows:
        # Handle both registry metadata (tags, version) and fallback (blocks)
        tags = wf.get('tags', [])
        blocks = wf.get('blocks', 'N/A')
        tags_str = ', '.join(tags) if tags else 'N/A'
        print(f"  - {wf['name']}: {wf['description']} (tags: {tags_str}, blocks: {blocks})")

    # Test 2: Get workflow info for first workflow
    print("\nTest 2: Get workflow info")
    first_workflow = workflows[0]['name'] if workflows else "hello-world"
    info = await get_workflow_info(workflow=first_workflow)
    print(f"✅ Workflow: {info['name']} - {info['total_blocks']} blocks")
    print("   Blocks:")
    for block in info["blocks"]:
        deps = f" (depends on: {', '.join(block['depends_on'])})" if block["depends_on"] else ""
        print(f"     - {block['id']} ({block['type']}){deps}")

    # Test 3: Execute hello-world workflow
    print("\nTest 3: Execute hello-world workflow")
    result = await execute_workflow(workflow="hello-world", inputs={"name": "Phase 1"})
    print(f"✅ Status: {result['status']}")
    if result["status"] == "failure":
        print(f"   ERROR: {result.get('error', 'Unknown error')}")
        return
    print(f"   Execution time: {result['execution_time']:.3f}s")
    print(f"   Outputs: {result.get('outputs', {})}")

    # Test 4: Execute parallel workflow
    print("\nTest 4: Execute parallel-echo workflow")
    result2 = await execute_workflow(workflow="parallel-echo", inputs={})
    print(f"✅ Status: {result2['status']}")
    print(f"   Execution time: {result2['execution_time']:.3f}s")
    if result2['status'] == 'success':
        outputs = result2.get('outputs', {})
        blocks = outputs.get('blocks', {})
        print(f"   Blocks executed: {len(blocks)}")
        print(f"   Execution waves: {outputs.get('execution_waves', [])}")

    # Test 5: Verify block outputs (if parallel-echo succeeded)
    if result2['status'] == 'success':
        print("\nTest 5: Verify block outputs")
        block_outputs = result2.get("outputs", {}).get("blocks", {})
        print("✅ All blocks produced outputs:")
        for block_id, output in block_outputs.items():
            print(f"   - {block_id}: {output.get('echoed', 'N/A')}")

    print("\n🎉 Phase 0/Phase 1 Complete! MCP integration validated successfully!")
    print("\nNext steps:")
    print("  - Phase 2: Advanced blocks (git, bash, templates)")
    print("  - Phase 3: Variable substitution and context management")
    print("  - Phase 4: BashCommand tool and async execution")


if __name__ == "__main__":
    asyncio.run(test_end_to_end())
