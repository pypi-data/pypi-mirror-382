# Custom File-Based Outputs Test Suite

Comprehensive test coverage for the file-based outputs feature in the workflow engine.

## Test Files Overview

### 1. `test_custom_outputs.py` - Core Functionality Tests (14 tests)

Tests basic output reading, type conversion, and context storage.

**TestCustomOutputsBasics** (6 tests):
- `test_string_output_basic` - Read string output from file
- `test_int_output_conversion` - Int type conversion
- `test_float_output_conversion` - Float type conversion
- `test_bool_output_conversion` - Bool type conversion
- `test_json_output_parsing` - JSON output parsing
- `test_multiple_outputs` - Block with multiple custom outputs

**TestCustomOutputsEdgeCases** (5 tests):
- `test_empty_string_output` - Empty file as string output
- `test_whitespace_handling` - Whitespace trimming
- `test_invalid_int_conversion_fails` - Invalid int conversion error
- `test_invalid_json_fails` - Invalid JSON error
- `test_optional_output_with_invalid_type` - Optional output with invalid type

**TestCustomOutputsInContext** (3 tests):
- `test_outputs_stored_in_dot_outputs_namespace` - Verify `.outputs.` prefix storage
- `test_multiple_blocks_with_custom_outputs` - Multiple blocks with outputs
- `test_custom_outputs_coexist_with_standard_outputs` - Mix of standard and custom outputs

### 2. `test_output_security.py` - Security Validation Tests (30 tests)

Tests path security, validation, and error handling.

**TestPathTraversalPrevention** (5 tests):
- `test_reject_relative_path_traversal` - Reject `../` paths
- `test_reject_nested_path_traversal` - Reject multiple `../` levels
- `test_reject_hidden_traversal_in_path` - Reject hidden traversal in middle of path
- `test_accept_safe_relative_paths` - Accept safe relative paths
- `test_reject_traversal_then_return` - Reject going up then back down

**TestAbsolutePathRestrictions** (4 tests):
- `test_reject_absolute_path_in_safe_mode` - Reject absolute paths by default
- `test_allow_absolute_path_in_unsafe_mode` - Allow with `unsafe: true`
- `test_reject_absolute_path_outside_working_dir_in_safe_mode` - Reject outside paths in safe mode
- `test_allow_absolute_path_outside_in_unsafe_mode` - Allow outside paths in unsafe mode

**TestSymlinkBlocking** (3 tests):
- `test_reject_direct_symlink` - Block direct symlink references
- `test_reject_symlink_in_unsafe_mode` - Block symlinks even in unsafe mode
- `test_reject_symlink_to_outside_directory` - Block symlinks pointing outside

**TestFileSizeLimits** (5 tests):
- `test_accept_file_at_size_limit` - Accept file exactly at 10MB limit
- `test_reject_file_over_size_limit` - Reject files over 10MB
- `test_reject_large_file_in_unsafe_mode` - Size limit enforced in unsafe mode
- `test_accept_small_file` - Accept small files
- `test_accept_empty_file` - Accept empty files

**TestDirectoryAndFileTypeValidation** (3 tests):
- `test_reject_directory` - Directories not allowed
- `test_reject_directory_in_unsafe_mode` - Directories rejected in unsafe mode
- `test_accept_regular_file` - Regular files accepted

**TestMissingFileHandling** (3 tests):
- `test_reject_missing_file` - Missing files raise error
- `test_reject_missing_file_in_unsafe_mode` - Missing files rejected in unsafe mode
- `test_reject_missing_nested_file` - Missing nested files raise error

**TestEnvironmentVariableExpansion** (3 tests):
- `test_expand_SCRATCH_env_var` - Expand `$SCRATCH`
- `test_expand_custom_env_var` - Expand custom env vars
- `test_env_var_expansion_with_path_traversal_blocked` - Env var expansion doesn't bypass security

**TestPathValidationErrorMessages** (4 tests):
- `test_absolute_path_error_message` - Clear error for absolute paths
- `test_path_traversal_error_message` - Clear error for path traversal
- `test_file_not_found_error_message` - Clear error for missing files
- `test_size_limit_error_message` - Clear error for large files

### 3. `test_output_integration.py` - Integration Tests (14 tests)

Tests variable resolution, workflow composition, and end-to-end scenarios.

**TestOutputVariableResolution** (3 tests):
- `test_reference_custom_output_in_next_block` - Reference output in subsequent block
- `test_reference_multiple_custom_outputs` - Reference multiple outputs
- `test_reference_json_output_field` - Reference JSON output fields

**TestMultiLevelPathResolution** (4 tests):
- `test_resolve_three_level_path` - Resolve `block.outputs.field` (3 levels)
- `test_resolve_four_level_path` - Resolve 4+ level paths
- `test_resolve_multiple_levels_in_same_string` - Multiple multi-level paths
- `test_missing_output_variable_error` - Clear error for missing outputs

**TestOutputComposition** (3 tests):
- `test_chain_outputs_through_multiple_blocks` - Chain outputs through sequence
- `test_parallel_blocks_with_outputs_merged` - Merge parallel outputs
- `test_conditional_execution_with_custom_outputs` - Conditionals based on custom outputs

**TestWorkflowLevelOutputs** (1 test):
- `test_workflow_output_from_custom_output` - Expose custom outputs at workflow level

**TestEdgeCasesAndErrorHandling** (3 tests):
- `test_optional_output_with_conditional_block` - Optional output from skipped block
- `test_empty_custom_outputs_dict` - Block with no custom outputs
- `test_mix_standard_and_custom_outputs_in_expression` - Mix standard and custom outputs

## Test Coverage Summary

**Total Tests**: 58 comprehensive tests across 3 test files

**Coverage Areas**:
1. ✅ **Basic Output Reading** - String, int, float, bool, json types
2. ✅ **Type Conversion** - Parsing and validation for all types
3. ✅ **Path Security** - Traversal prevention, absolute path restrictions
4. ✅ **Symlink Blocking** - Security against symlink attacks
5. ✅ **File Size Limits** - 10MB limit enforcement
6. ✅ **Environment Variables** - `$SCRATCH` and custom vars
7. ✅ **Variable Resolution** - `${block.outputs.field}` syntax
8. ✅ **Multi-Level Paths** - 3+ level path resolution
9. ✅ **Workflow Composition** - Output chaining and merging
10. ✅ **Conditional Execution** - Conditionals based on custom outputs
11. ✅ **Error Handling** - Clear error messages for all failure scenarios
12. ✅ **Edge Cases** - Empty files, optional outputs, mixed outputs

## Key Features Validated

### Security Features
- Path traversal prevention (`../` blocked)
- Absolute path restrictions (safe mode by default)
- Symlink blocking (always enforced)
- File size limits (10MB maximum)
- Working directory confinement

### Functional Features
- Multiple output types: string, int, float, bool, json
- Environment variable expansion in paths
- Variable resolution with `.outputs.` namespace
- Multi-level path resolution (3+ levels)
- Integration with workflow context
- Conditional execution based on outputs
- Coexistence with standard BashCommand outputs

### Error Handling
- Clear error messages for all validation failures
- Optional vs required output handling
- Type conversion error handling
- Missing file error handling

## Running the Tests

```bash
# Run all custom output tests
pytest tests/test_custom_outputs.py tests/test_output_security.py tests/test_output_integration.py -v

# Run specific test class
pytest tests/test_output_security.py::TestPathTraversalPrevention -v

# Run with coverage
pytest tests/test_custom_outputs.py tests/test_output_security.py tests/test_output_integration.py --cov=src/workflows_mcp/engine --cov-report=html
```

## Implementation Notes

### Modified Files
1. **`src/workflows_mcp/engine/blocks_bash.py`**:
   - Added `SCRATCH` env var handling
   - Integrated output validation and reading
   - Fixed symlink check to occur before path resolution

2. **`src/workflows_mcp/engine/executor.py`**:
   - Added support for passing `outputs` parameter to blocks
   - Stores custom outputs in `.outputs.` namespace in context

### Test Patterns Used
- **pytest fixtures**: `tmp_path` for temporary directories
- **Async tests**: `@pytest.mark.asyncio` decorator
- **Error assertions**: `pytest.raises()` with message matching
- **Monkeypatch**: For environment variable testing

## Future Enhancements

Potential areas for additional testing:
- Validation expressions (currently TODO in implementation)
- Binary file handling
- Concurrent output file access
- Performance testing with large outputs
- Integration with workflow composition (ExecuteWorkflow blocks)
