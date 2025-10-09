#!/usr/bin/env bash
#
# Comprehensive Phase 1 Test Suite Runner
#
# This script runs all Phase 1 tests and generates a comprehensive report.
#

set -e  # Exit on error

echo "================================================================================"
echo "  PHASE 1 COMPREHENSIVE TEST SUITE"
echo "================================================================================"
echo ""
echo "Running all automated tests, quality checks, and validations..."
echo ""

# Track test results
TESTS_PASSED=0
TESTS_FAILED=0
TOTAL_TESTS=0

# Function to run test and track results
run_test() {
    local test_name="$1"
    local test_command="$2"

    TOTAL_TESTS=$((TOTAL_TESTS + 1))

    echo "--------------------------------------------------------------------------------"
    echo "Test $TOTAL_TESTS: $test_name"
    echo "--------------------------------------------------------------------------------"

    if eval "$test_command" 2>&1; then
        echo "✅ PASSED: $test_name"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo "❌ FAILED: $test_name"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi

    echo ""
}

# 1. Unit Tests
run_test "MCP Tool Validation" "uv run python tests/test_tools.py"
run_test "Registry Unit Tests" "uv run python tests/test_registry.py"
run_test "Registry Integration Tests" "uv run python tests/test_registry_integration.py"
run_test "Async Block Tests" "uv run python tests/test_async_block.py"
run_test "DAG Async Compatibility" "uv run python tests/test_dag_async.py"

# 2. Schema and Loader Tests
run_test "YAML Schema Integration Tests" "uv run python tests/test_schema_integration.py"
run_test "Workflow Loader Tests" "uv run python tests/test_loader.py"
run_test "Example Workflows Validation" "uv run python tests/test_example_workflows.py"
run_test "Registry Loading Tests" "uv run python tests/test_registry_load.py"

# 3. Integration Tests
run_test "MCP Integration Test" "uv run python tests/test_mcp_integration.py"
run_test "Phase 1 Comprehensive Integration" "uv run python tests/test_phase1_integration.py"

# 4. Manual Validation
run_test "Manual MCP Tool Validation" "uv run python tests/manual_mcp_validation.py"

# 5. Code Quality Checks
echo "================================================================================"
echo "  CODE QUALITY CHECKS"
echo "================================================================================"
echo ""

run_test "Type Checking (mypy --strict)" "uv run mypy src/workflows_mcp/ --strict"
run_test "Linting (ruff check)" "uv run ruff check src/workflows_mcp/"
run_test "Code Formatting (ruff format --check)" "uv run ruff format --check src/workflows_mcp/"

# Summary
echo "================================================================================"
echo "  TEST SUITE SUMMARY"
echo "================================================================================"
echo ""
echo "Total Tests:   $TOTAL_TESTS"
echo "Passed:        $TESTS_PASSED"
echo "Failed:        $TESTS_FAILED"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo "🎉 ALL TESTS PASSED!"
    echo ""
    echo "✅ Phase 1 Components Validated:"
    echo "   ✅ YAML workflow schema (schema.py)"
    echo "   ✅ WorkflowLoader (loader.py)"
    echo "   ✅ WorkflowRegistry (registry.py)"
    echo "   ✅ Templates directory structure"
    echo "   ✅ MCP tools integration (server.py, tools.py)"
    echo "   ✅ 5 example YAML workflows"
    echo "   ✅ Variable substitution (inputs + block outputs)"
    echo "   ✅ Parallel execution (DAG-based)"
    echo "   ✅ Error handling"
    echo "   ✅ Code quality (mypy, ruff)"
    echo ""
    echo "🚀 Phase 1 Complete! Ready for Phase 2 (Advanced Blocks)"
    exit 0
else
    echo "❌ $TESTS_FAILED test(s) failed"
    exit 1
fi
