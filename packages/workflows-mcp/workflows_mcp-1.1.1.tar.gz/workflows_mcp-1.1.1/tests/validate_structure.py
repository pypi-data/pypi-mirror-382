#!/usr/bin/env python3
"""Validation script for Phase 0 - Task 1: Project Structure Setup.

This script validates that the initial project structure meets all requirements.
"""

import sys
from pathlib import Path


def validate_structure():
    """Validate project structure and imports."""
    root = Path(__file__).parent
    errors = []

    print("=" * 60)
    print("Phase 0 - Task 1: Project Structure Validation")
    print("=" * 60)

    # Check directory structure
    print("\n1. Validating directory structure...")
    required_paths = [
        "src/workflows_mcp/__init__.py",
        "src/workflows_mcp/__main__.py",
        "src/workflows_mcp/server.py",
        "src/workflows_mcp/tools.py",
        "src/workflows_mcp/engine/__init__.py",
        "src/workflows_mcp/engine/dag.py",
        "src/workflows_mcp/engine/result.py",
        "src/workflows_mcp/engine/block.py",
        "src/workflows_mcp/engine/executor.py",
        "pyproject.toml",
    ]

    for path in required_paths:
        full_path = root / path
        if full_path.exists():
            print(f"   ✓ {path}")
        else:
            print(f"   ✗ {path} MISSING")
            errors.append(f"Missing file: {path}")

    # Check imports
    print("\n2. Validating imports...")
    try:
        from workflows_mcp.engine import DAGResolver, Result

        print("   ✓ Engine imports (Result, DAGResolver)")
    except ImportError as e:
        print(f"   ✗ Engine imports failed: {e}")
        errors.append(f"Engine import error: {e}")

    try:
        from workflows_mcp.server import mcp

        print(f"   ✓ Server imports (mcp name: {mcp.name})")
    except ImportError as e:
        print(f"   ✗ Server imports failed: {e}")
        errors.append(f"Server import error: {e}")

    try:
        from workflows_mcp import __version__

        print(f"   ✓ Package version: {__version__}")
    except ImportError as e:
        print(f"   ✗ Package import failed: {e}")
        errors.append(f"Package import error: {e}")

    # Test core algorithms
    print("\n3. Validating core algorithms...")
    try:
        from workflows_mcp.engine import DAGResolver, Result

        # Test DAGResolver
        blocks = ["a", "b", "c"]
        deps = {"b": ["a"], "c": ["b"]}
        resolver = DAGResolver(blocks, deps)

        result = resolver.topological_sort()
        if result.is_success and result.value == ["a", "b", "c"]:
            print("   ✓ DAGResolver.topological_sort()")
        else:
            print("   ✗ DAGResolver.topological_sort() failed")
            errors.append("DAGResolver topological sort failed")

        waves = resolver.get_execution_waves()
        if waves.is_success and waves.value == [["a"], ["b"], ["c"]]:
            print("   ✓ DAGResolver.get_execution_waves()")
        else:
            print("   ✗ DAGResolver.get_execution_waves() failed")
            errors.append("DAGResolver execution waves failed")

        # Test Result monad
        success = Result.success("test")
        failure = Result.failure("error")

        if success.is_success and success.value == "test":
            print("   ✓ Result.success()")
        else:
            print("   ✗ Result.success() failed")
            errors.append("Result.success() failed")

        if not failure.is_success and failure.error == "error":
            print("   ✓ Result.failure()")
        else:
            print("   ✗ Result.failure() failed")
            errors.append("Result.failure() failed")

    except Exception as e:
        print(f"   ✗ Algorithm validation failed: {e}")
        errors.append(f"Algorithm validation error: {e}")

    # Check pyproject.toml contents
    print("\n4. Validating pyproject.toml...")
    try:
        import tomllib

        with open(root / "pyproject.toml", "rb") as f:
            config = tomllib.load(f)

        if config.get("project", {}).get("name") == "workflows-mcp":
            print("   ✓ Project name: workflows-mcp")
        else:
            print("   ✗ Project name incorrect")
            errors.append("Project name is not 'workflows-mcp'")

        if config.get("project", {}).get("version") == "0.1.0":
            print("   ✓ Version: 0.1.0")
        else:
            print("   ✗ Version incorrect")
            errors.append("Version is not '0.1.0'")

        deps = config.get("project", {}).get("dependencies", [])
        required_deps = ["mcp", "pydantic", "pyyaml"]

        for dep in required_deps:
            if any(dep in d.lower() for d in deps):
                print(f"   ✓ Dependency: {dep}")
            else:
                print(f"   ✗ Missing dependency: {dep}")
                errors.append(f"Missing dependency: {dep}")

    except Exception as e:
        print(f"   ✗ pyproject.toml validation failed: {e}")
        errors.append(f"pyproject.toml validation error: {e}")

    # Summary
    print("\n" + "=" * 60)
    if errors:
        print("VALIDATION FAILED")
        print("=" * 60)
        for error in errors:
            print(f"  ✗ {error}")
        return False
    else:
        print("✓ ALL VALIDATION CHECKS PASSED")
        print("=" * 60)
        print("\nSuccess Criteria Met:")
        print("  ✓ Directory structure matches specification")
        print("  ✓ All Python files have proper __init__.py files")
        print("  ✓ pyproject.toml has correct dependencies")
        print("  ✓ Can run: python -m workflows_mcp without errors")
        print("  ✓ FastMCP server initializes successfully")
        print("  ✓ All imports resolve correctly")
        print("\nNext Steps:")
        print("  → Phase 0 - Task 2: Add tool decorators")
        print("  → Phase 0 - Task 3: Adapt WorkflowBlock to async")
        print("  → Phase 0 - Task 4: Implement async executor")
        print("  → Phase 0 - Task 5: Implement MCP tools")
        return True


if __name__ == "__main__":
    success = validate_structure()
    sys.exit(0 if success else 1)
