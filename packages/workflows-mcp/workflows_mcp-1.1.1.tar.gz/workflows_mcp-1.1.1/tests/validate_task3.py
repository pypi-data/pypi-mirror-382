"""
Validate Phase 0 - Task 3: DAGResolver Async Compatibility

This script validates that all deliverables for Task 3 are complete.
"""

import sys
from pathlib import Path


def validate_task3():
    """Validate all Task 3 deliverables."""

    print("=== Phase 0 - Task 3 Validation ===\n")

    errors = []
    warnings = []

    # Check 1: dag.py has architectural decision documentation
    print("1. Checking dag.py documentation...")
    dag_path = Path("src/workflows_mcp/engine/dag.py")
    if not dag_path.exists():
        errors.append("dag.py not found")
    else:
        content = dag_path.read_text()
        if "ARCHITECTURAL DECISION" not in content:
            errors.append("dag.py missing architectural decision documentation")
        elif "intentionally SYNCHRONOUS" not in content:
            errors.append("dag.py missing synchronous design explanation")
        else:
            print("   ✅ dag.py has comprehensive documentation")

    # Check 2: test_dag_async.py exists and is comprehensive
    print("2. Checking test_dag_async.py...")
    test_path = Path("test_dag_async.py")
    if not test_path.exists():
        errors.append("test_dag_async.py not found")
    else:
        content = test_path.read_text()
        required_tests = [
            "test_dag_in_async_context",
            "test_performance",
            "Linear dependency chain",
            "Parallel execution",
            "Complex multi-level",
            "Cyclic dependency",
            "Missing dependency",
        ]
        missing = [t for t in required_tests if t not in content]
        if missing:
            warnings.append(f"test_dag_async.py missing tests: {missing}")
        else:
            print("   ✅ test_dag_async.py has comprehensive test coverage")

    # Check 3: DECISION_DAG_ASYNC.md exists
    print("3. Checking DECISION_DAG_ASYNC.md...")
    decision_path = Path("DECISION_DAG_ASYNC.md")
    if not decision_path.exists():
        errors.append("DECISION_DAG_ASYNC.md not found")
    else:
        content = decision_path.read_text()
        required_sections = [
            "Path A",
            "Rationale",
            "Performance Validation",
            "Design Pattern",
            "Alternative Considered",
        ]
        missing = [s for s in required_sections if s not in content]
        if missing:
            warnings.append(f"DECISION_DAG_ASYNC.md missing sections: {missing}")
        else:
            print("   ✅ DECISION_DAG_ASYNC.md is comprehensive")

    # Check 4: README.md updated
    print("4. Checking README.md updates...")
    readme_path = Path("README.md")
    if not readme_path.exists():
        errors.append("README.md not found")
    else:
        content = readme_path.read_text()
        required_updates = [
            "Task 3 Complete",
            "Architectural Decisions",
            "DAGResolver Remains Synchronous",
            "test_dag_async.py",
        ]
        missing = [u for u in required_updates if u not in content]
        if missing:
            warnings.append(f"README.md missing updates: {missing}")
        else:
            print("   ✅ README.md properly updated")

    # Check 5: Run actual test
    print("5. Running test_dag_async.py...")
    import subprocess

    try:
        result = subprocess.run(
            ["uv", "run", "python", "test_dag_async.py"], capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            errors.append(f"test_dag_async.py failed: {result.stderr}")
        elif "All Tests Passed" not in result.stdout:
            warnings.append("test_dag_async.py may not have completed all tests")
        else:
            print("   ✅ test_dag_async.py passes all tests")
    except Exception as e:
        errors.append(f"Failed to run test_dag_async.py: {e}")

    # Summary
    print("\n=== Validation Summary ===\n")

    if errors:
        print("❌ ERRORS:")
        for error in errors:
            print(f"   - {error}")

    if warnings:
        print("\n⚠️  WARNINGS:")
        for warning in warnings:
            print(f"   - {warning}")

    if not errors and not warnings:
        print("✅ All Task 3 deliverables validated successfully!")
        print("\nDeliverables:")
        print("  1. ✅ dag.py documentation")
        print("  2. ✅ test_dag_async.py comprehensive test suite")
        print("  3. ✅ DECISION_DAG_ASYNC.md architectural decision")
        print("  4. ✅ README.md updated")
        print("\nDecision: Path A - DAGResolver remains synchronous")
        print("\nNext: Phase 0 - Task 4: Adapt WorkflowBlock to async")
        return 0
    elif errors:
        print("\n❌ Task 3 validation FAILED")
        return 1
    else:
        print("\n⚠️  Task 3 validation PASSED with warnings")
        return 0


if __name__ == "__main__":
    sys.exit(validate_task3())
