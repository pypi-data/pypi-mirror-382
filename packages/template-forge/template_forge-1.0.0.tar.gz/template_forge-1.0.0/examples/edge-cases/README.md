# Edge Cases Testing Example

This example demonstrates and tests various edge cases in Template Forge based on the requirements documentation. It's designed to validate proper handling of unusual inputs, boundary conditions, and error scenarios.

## Edge Cases Covered

### 1. Configuration Edge Cases (REQ-CFG)
- ✅ Token collision between static and namespaced tokens
- ✅ Conditional template generation with complex expressions
- ✅ Empty arrays and missing data handling
- ✅ Template-specific token overrides

### 2. Data Extraction Edge Cases (REQ-EXT)
- ✅ Wildcard extraction on empty arrays (`items[*]` where items is empty)
- ✅ Deep nesting with dot notation (5+ levels)
- ✅ Transform operations on unexpected types (e.g., `upper` on numbers)
- ✅ Regex filtering that doesn't match
- ✅ XML attributes vs text content extraction
- ✅ Array indexing beyond bounds

### 3. Template Engine Edge Cases (REQ-TPL)
- ✅ **Conditional template generation** - Templates that are only generated when conditions are met (REQ-TPL-130-138)
  - `conditionally-generated.txt.j2` - Only generated when `enable_feature == true` (currently false, so NOT generated)
  - `production-only.txt.j2` - Only generated when `environment == 'production'` (currently 'development', so NOT generated)
- ✅ Whitespace control in complex scenarios
- ✅ Filters on potentially undefined variables
- ✅ Loop over empty collections

### 4. Code Preservation Edge Cases (REQ-PRV)
- ✅ Preservation blocks in conditionally generated templates
- ✅ Preservation block identifiers with special characters
- ✅ Preserved content when template structure changes
- ✅ Multiple preservation blocks in single file

### 5. Automation Edge Cases (REQ-AUT)
- ✅ Conditional hooks that may not execute
- ✅ Hooks with different error handling modes
- ✅ Commands that reference generated files

## Test Files

### Input Data Files

1. **`edge-data.json`**: JSON with edge cases
   - Empty arrays
   - Deeply nested objects (5 levels)
   - Null values
   - Mixed type arrays
   - Special characters in keys

2. **`edge-config.xml`**: XML with edge cases
   - Elements with both attributes and text content
   - Empty elements
   - Multiple children with same tag name
   - Special characters in content

3. **`edge-tokens.yaml`**: YAML with edge cases
   - Boolean values (true/false, yes/no, on/off)
   - Numbers in scientific notation
   - Multi-line strings
   - Anchors and aliases

### Configuration

**`config.yaml`**: Tests multiple edge cases:
- Token collision warnings (static token vs namespaced input)
- Conditional templates (some won't generate)
- Template-specific token overrides
- Transformation on edge values
- Conditional hooks

### Templates

1. **`always-generated.txt.j2`**: Always generated
   - Tests loops over empty arrays
   - Tests filters with default values
   - Tests undefined variable handling with defaults

2. **`conditionally-generated.txt.j2`**: Only generated if condition is true
   - Tests REQ-TPL-130-138 (conditional template generation)

3. **`with-preservation.py.j2`**: Tests code preservation
   - Multiple preservation blocks
   - Preservation blocks with descriptive identifiers

4. **`edge-whitespace.txt.j2`**: Tests whitespace control
   - Aggressive whitespace stripping
   - Mix of `-` controls

## Running the Example

### Basic Generation
```bash
cd examples/edge-cases
template-forge
```

### Dry Run (Preview without writing)
```bash
template-forge --dry-run
```

### Show Variables (Debug token resolution)
```bash
template-forge --show-variables
```

### Validate Configuration
```bash
template-forge --validate
```

### With Verbose Output
```bash
template-forge --verbose
```

## Expected Behavior

### Success Cases
- ✅ Handles empty arrays gracefully (no errors)
- ✅ Logs warnings for token collisions
- ✅ Skips conditional templates when condition is false
- ✅ Preserves custom code in regeneration
- ✅ Applies transformations safely (returns original on failure)
- ✅ Executes only applicable conditional hooks

### Warning Cases
- ⚠️ Token collision: `version` defined in both static and namespace
- ⚠️ Conditional template skipped: `conditionally-generated.txt.j2`
- ⚠️ Regex filter no match: uses original value
- ⚠️ Transform failed: uses original value

### Error Cases (should NOT fail, but handle gracefully)
- Array index out of bounds → returns None or logs warning
- Missing nested key → returns None with warning
- Undefined variable in template → caught by Jinja2

## Test Scenarios

### Scenario 1: Token Collision Detection
Run with `--verbose` to see collision warnings:
```bash
template-forge --verbose
```

Expected output:
```
WARNING: Token collision detected
  Token: 'version'
  Original: '1.0.0' (from static_tokens)
  Override: '2.0.0' (from json.version)
  Result: Using '2.0.0' for templates
```

### Scenario 2: Conditional Template Generation (REQ-TPL-130-138)

This example demonstrates the new conditional template generation feature.

**Configuration:**
```yaml
static_tokens:
  enable_feature: false
  environment: "development"

templates:
  - template: conditionally-generated.txt.j2
    output: output/conditionally-generated.txt
    when: "enable_feature == true"
  
  - template: production-only.txt.j2
    output: output/production-only.txt
    when: "environment == 'production'"
```

**Test it:**
```bash
# Run with default settings (enable_feature: false, environment: development)
template-forge --verbose

# Check what was generated
ls -la output/
```

**Expected Behavior:**
- ✅ `conditionally-generated.txt` is NOT generated (enable_feature is false)
- ✅ `production-only.txt` is NOT generated (environment is 'development')
- ✅ Log shows: `DEBUG - Skipping template 'conditionally-generated.txt.j2' (condition 'enable_feature == true' not met)`

**To Generate Conditional Files:**
1. Edit `config.yaml` and set `enable_feature: true`
2. Run `template-forge`
3. Now `conditionally-generated.txt` will be created!

Or for production template:
1. Edit `config.yaml` and set `environment: "production"`
2. Run `template-forge`
3. Now `production-only.txt` will be created!

### Scenario 3: Empty Array Handling
Check `always-generated.txt`:
```bash
template-forge
cat output/always-generated.txt
```

Expected: No errors, empty arrays handled with "No items found" messages.

### Scenario 4: Code Preservation
1. Generate files:
   ```bash
   template-forge
   ```

2. Add custom code to `output/with-preservation.py`

3. Regenerate:
   ```bash
   template-forge
   ```

Expected: Custom code preserved between `@PRESERVE_START` and `@PRESERVE_END`.

### Scenario 5: Transformation Edge Cases
Check that transforms handle unexpected types:
- `upper` on number → returns original
- `len` on non-collection → returns original
- Regex on non-string → logs warning, uses original

### Scenario 6: Conditional Hooks
Modify `enable_docker` in config and regenerate:
```bash
# Edit config.yaml, set enable_docker: true
template-forge
```

Expected: Docker-related hook should execute only when condition is true.

## Validation

Run the test suite to validate all edge cases:
```bash
# From repository root
pytest tests/test_edge_cases.py -v
```

## Lessons Learned

This example demonstrates:
1. **Defensive Programming**: Handle missing data gracefully
2. **Clear Warnings**: Token collisions are warned, not errors
3. **Conditional Logic**: Templates and hooks can be conditional
4. **Preservation Robustness**: Code preservation works even with structural changes
5. **Transform Safety**: Transformations fail gracefully without breaking generation
6. **Array Safety**: Empty arrays and out-of-bounds access handled gracefully

## Requirements Coverage

| Requirement | Test Coverage |
|-------------|---------------|
| REQ-CFG-074-077 | Token collision detection and warnings |
| REQ-EXT-052-054 | Array/object wildcard extraction |
| REQ-EXT-060-063 | Data transformations with edge types |
| REQ-EXT-070-074 | Regex filtering edge cases |
| REQ-TPL-130-138 | Conditional template generation |
| REQ-TPL-045 | Undefined variable handling |
| REQ-PRV-042-043 | Preservation block lifecycle |
| REQ-AUT-030-033 | Conditional hook execution |

## Contributing

When adding new edge cases:
1. Document the edge case in this README
2. Add test data to appropriate input file
3. Create or modify template to test the case
4. Add expected behavior to this documentation
5. Update the test suite if needed
