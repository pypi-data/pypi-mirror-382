#!/usr/bin/env python3
"""Test script to validate all example workflows."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from workflows_mcp.engine.loader import load_workflow_from_file, validate_workflow_file


def test_workflow(workflow_path: Path) -> bool:
    """Test a single workflow file."""
    print(f"\n{'='*60}")
    print(f"Testing: {workflow_path.name}")
    print(f"{'='*60}")

    # Validate workflow
    print("\n1. Validating workflow schema...")
    result = validate_workflow_file(str(workflow_path))
    if not result.is_success:
        print(f"   ❌ FAILED: {result.error}")
        return False
    print("   ✅ Valid schema")

    schema = result.value
    print(f"   - Name: {schema.name}")
    print(f"   - Description: {schema.description}")
    print(f"   - Tags: {', '.join(schema.tags)}")
    print(f"   - Blocks: {len(schema.blocks)}")
    print(f"   - Inputs: {len(schema.inputs)}")
    print(f"   - Outputs: {len(schema.outputs)}")

    # Load workflow
    print("\n2. Loading workflow definition...")
    result = load_workflow_from_file(str(workflow_path))
    if not result.is_success:
        print(f"   ❌ FAILED: {result.error}")
        return False
    print("   ✅ Loaded successfully")

    workflow_def = result.value
    print(f"   - Workflow name: {workflow_def.name}")
    print(f"   - Blocks loaded: {len(workflow_def.blocks)}")

    # Show block details
    print("\n3. Block details:")
    for block in workflow_def.blocks:
        block_id = block.get("id", "unknown")
        block_type = block.get("type", "unknown")
        deps = block.get("depends_on", [])
        deps_str = f" (depends on: {', '.join(deps)})" if deps else ""
        print(f"   - {block_id}: {block_type}{deps_str}")

    # Show inputs
    if schema.inputs:
        print("\n4. Inputs:")
        for name, input_def in schema.inputs.items():
            default = f" (default: {input_def.default})" if input_def.default is not None else ""
            print(f"   - {name}: {input_def.type}{default}")

    # Show outputs
    if schema.outputs:
        print("\n5. Outputs:")
        for name, value in schema.outputs.items():
            print(f"   - {name}: {value}")

    print(f"\n✅ All tests passed for {workflow_path.name}")
    return True


def main():
    """Test all example workflows."""
    examples_dir = Path(__file__).parent.parent / "templates" / "examples"

    print("="*60)
    print("EXAMPLE WORKFLOWS VALIDATION TEST")
    print("="*60)

    # Find all YAML files in examples directory
    workflow_files = sorted(examples_dir.glob("*.yaml"))

    if not workflow_files:
        print(f"\n❌ No workflow files found in {examples_dir}")
        sys.exit(1)

    print(f"\nFound {len(workflow_files)} workflow(s) to test:")
    for wf in workflow_files:
        print(f"  - {wf.name}")

    # Test each workflow
    results = []
    for workflow_path in workflow_files:
        success = test_workflow(workflow_path)
        results.append((workflow_path.name, success))

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"  {status}: {name}")

    print(f"\nTotal: {passed}/{total} workflows passed")

    if passed == total:
        print("\n🎉 All workflows validated successfully!")
        sys.exit(0)
    else:
        print(f"\n❌ {total - passed} workflow(s) failed validation")
        sys.exit(1)


if __name__ == "__main__":
    main()
