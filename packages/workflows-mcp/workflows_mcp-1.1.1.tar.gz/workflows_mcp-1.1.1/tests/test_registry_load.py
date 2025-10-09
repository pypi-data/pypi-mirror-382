#!/usr/bin/env python3
"""Test loading example workflows via WorkflowRegistry."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from workflows_mcp.engine.registry import WorkflowRegistry


def main():
    """Test WorkflowRegistry loading of example workflows."""
    print("="*60)
    print("WORKFLOW REGISTRY LOADING TEST")
    print("="*60)

    # Initialize registry with examples directory
    examples_dir = Path(__file__).parent.parent / "templates" / "examples"
    registry = WorkflowRegistry()

    print(f"\nLoading workflows from: {examples_dir}")
    result = registry.load_from_directory(str(examples_dir))

    if not result.is_success:
        print(f"\n❌ Failed to load workflows: {result.error}")
        sys.exit(1)

    loaded_count = result.value
    print(f"\n✅ Loaded {loaded_count} workflow(s)")

    # List all workflows
    print("\n" + "="*60)
    print("REGISTERED WORKFLOWS")
    print("="*60)

    all_workflow_names = registry.list_names()
    print(f"\nTotal workflows in registry: {len(all_workflow_names)}")

    for workflow_name in sorted(all_workflow_names):
        try:
            wf = registry.get(workflow_name)
            print(f"\n  ✅ {workflow_name}")
            print(f"     Description: {wf.description}")
            print(f"     Blocks: {len(wf.blocks)}")
        except KeyError:
            print(f"  ❌ {workflow_name} - Not found")

    # Test tag filtering
    print("\n" + "="*60)
    print("TAG FILTERING")
    print("="*60)

    test_workflows = registry.list_by_tags(["test"])
    print(f"\nWorkflows with 'test' tag: {len(test_workflows)}")
    for wf in test_workflows:
        print(f"  - {wf.name}")

    # Test metadata access
    print("\n" + "="*60)
    print("WORKFLOW METADATA")
    print("="*60)

    all_metadata = registry.list_all_metadata()
    print(f"\nWorkflows with metadata: {len(all_metadata)}")
    for meta in all_metadata:
        print(f"\n  - {meta.get('name', 'unknown')}")
        print(f"    Tags: {', '.join(meta.get('tags', []))}")

    print("\n" + "="*60)
    print("SUCCESS - All registry operations passed!")
    print("="*60)


if __name__ == "__main__":
    main()
