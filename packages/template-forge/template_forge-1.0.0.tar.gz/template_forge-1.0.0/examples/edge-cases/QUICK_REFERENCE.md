# Edge Cases Quick Reference

## Quick Test Commands

### Run All Tests
```bash
cd examples/edge-cases
template-forge
```

### Preview Without Writing (Dry Run)
```bash
template-forge --dry-run
```

### Show All Variables
```bash
template-forge --show-variables
```

### Validate Configuration
```bash
template-forge --validate
```

### Verbose Output (See Warnings)
```bash
template-forge --verbose
```

## Expected Warnings

When running with `--verbose`, you should see these warnings:

### Token Collision Warning
```
WARNING: Token collision detected
  Token: 'version'
  Original: '1.0.0' (from static_tokens)
  Override: '2.0.0' (from json.project.version)
```

### Conditional Template Skipped
```
DEBUG: Skipping template conditionally-generated.txt.j2 (condition: enable_feature == true)
```

### Regex No Match Warning
```
WARNING: Regex filter '\d+' did not match value 'only text here', using original value
```

## Edge Cases by Category

### 1. Empty Collections
- **File**: `edge-data.json`
- **Fields**: `modules: []`, `features.enabled: []`, `api.endpoints: []`
- **Test**: Loops should not error, should show "No items" messages

### 2. Deep Nesting (5+ Levels)
- **File**: `edge-data.json`
- **Path**: `project.metadata.author.profile.location.city.name`
- **Test**: Should extract "San Francisco" successfully

### 3. Null Values
- **File**: `edge-data.json`
- **Fields**: `features.experimental: null`, `database.credentials.password: null`
- **Test**: Should use defaults or show "(null)"

### 4. Array Index Out of Bounds
- **Config**: `components[999].name`
- **Test**: Should handle gracefully, show "Index out of bounds"

### 5. Regex No Match
- **Config**: Extract numbers from "only text here"
- **Test**: Regex `\d+` won't match, should warn and use original

### 6. Transform on Unexpected Types
- **Config**: Apply `upper` transform to number "12345"
- **Test**: Should handle gracefully, return original value

### 7. XML Attributes vs Text
- **File**: `edge-config.xml`
- **Element**: `<server host="localhost" port="8080">Production Server</server>`
- **Test**: Can extract both `@host` attribute and text content

### 8. Boolean Variations
- **File**: `edge-tokens.yaml`
- **Values**: `true`, `True`, `TRUE`, `yes`, `Yes`, `on`, etc.
- **Test**: All should parse correctly as boolean

### 9. Conditional Templates
- **Template**: `conditionally-generated.txt.j2`
- **Condition**: `enable_feature == true`
- **Test**: NOT generated when flag is false

### 10. Token Overrides
- **Template**: `with-overrides.txt.j2`
- **Override**: Template-specific `author` overrides static token
- **Test**: Should show "Template-Specific Author"

## Test Results

### Files That SHOULD Be Generated
✅ `output/always-generated.txt`
✅ `output/with-preservation.py`
✅ `output/edge-whitespace.txt`
✅ `output/with-overrides.txt`

### Files That SHOULD NOT Be Generated
❌ `output/conditionally-generated.txt` (enable_feature is false)
❌ `output/production-only.txt` (environment is development)

## Modifying for Different Tests

### Enable Conditional Template
Edit `config.yaml`:
```yaml
static_tokens:
  enable_feature: true  # Change from false to true
```

Then regenerate:
```bash
template-forge
```

Now `conditionally-generated.txt` should be created.

### Enable Production Template
Edit `config.yaml`:
```yaml
static_tokens:
  environment: "production"  # Change from "development"
```

Then regenerate:
```bash
template-forge
```

Now `production-only.txt` should be created.

### Test Code Preservation

1. Generate initially:
   ```bash
   template-forge
   ```

2. Edit `output/with-preservation.py` and add custom code:
   ```python
   # @PRESERVE_START custom_imports
   import json
   import datetime
   # @PRESERVE_END custom_imports
   ```

3. Regenerate:
   ```bash
   template-forge
   ```

4. Check that your custom imports are still there!

### Test Hook Conditions

Edit `config.yaml`:
```yaml
static_tokens:
  enable_docker: true  # Enable Docker hook
```

Regenerate and watch the hooks:
```bash
template-forge --verbose
```

## Troubleshooting

### No Warnings Shown
Use `--verbose` flag:
```bash
template-forge --verbose
```

### Template Errors
Validate first:
```bash
template-forge --validate
```

### Want to See What Would Change
Use dry-run:
```bash
template-forge --dry-run
```

### Undefined Variable Errors
Check available variables:
```bash
template-forge --show-variables
```

## Running Automated Tests

From repository root:
```bash
# Run edge cases tests only
pytest tests/test_edge_cases.py -v

# Run with coverage
pytest tests/test_edge_cases.py --cov=template_forge --cov-report=term-missing

# Run specific test
pytest tests/test_edge_cases.py::TestEdgeCasesGeneration::test_always_generated_template -v
```

## Success Criteria

All these should pass:
- ✅ Configuration validates successfully
- ✅ Generation completes without errors
- ✅ Token collision warnings appear (verbose mode)
- ✅ Conditional templates skip as expected
- ✅ Empty arrays handled gracefully
- ✅ Regex no-match handled gracefully
- ✅ Transform edge cases handled gracefully
- ✅ Code preservation works across regeneration
- ✅ Hooks execute (or skip) based on conditions
