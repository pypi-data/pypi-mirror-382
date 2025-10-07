# Edge Cases to Requirements Traceability

This document maps each edge case in the example to specific requirements from the documentation.

## Configuration Edge Cases

| Edge Case | Requirement | File | Description |
|-----------|-------------|------|-------------|
| Token collision detection | REQ-CFG-074-077 | `config.yaml` | Static token `version` collides with `json.project.version` |
| Template-specific overrides | REQ-CFG-041 | `config.yaml`, `with-overrides.txt.j2` | Template overrides static `author` token |
| Conditional template generation | REQ-CFG-032, REQ-TPL-130-138 | `config.yaml` | Templates generated based on conditions |
| Multiple namespaces | REQ-CFG-021 | `config.yaml` | Three inputs with unique namespaces (json, xml, yaml) |
| Static + namespaced coexistence | REQ-CFG-033-034 | `config.yaml` | Static tokens and namespaced inputs work together |

## Data Extraction Edge Cases

| Edge Case | Requirement | File | Description |
|-----------|-------------|------|-------------|
| Empty array extraction | REQ-EXT-080 | `edge-data.json` | Extract empty arrays: `modules: []` |
| Wildcard on empty array | REQ-EXT-053 | `edge-data.json` | `modules[*]` returns empty list |
| Deep nesting (5 levels) | REQ-EXT-052 | `edge-data.json` | Extract `project.metadata.author.profile.location.city.name` |
| Array index out of bounds | REQ-EXT-082 | `config.yaml` | `components[999].name` handled gracefully |
| Null value extraction | REQ-EXT-050-056 | `edge-data.json` | Extract null values: `features.experimental: null` |
| Transform on unexpected type | REQ-EXT-062 | `config.yaml` | Apply `upper` to number string "12345" |
| Regex no match | REQ-EXT-073 | `config.yaml` | Regex `\d+` on "only text here" logs warning |
| Regex with groups | REQ-EXT-071 | `config.yaml` | Extract email domain with `@(.+)$` |
| XML attribute extraction | REQ-EXT-033 | `edge-config.xml` | Extract `server.@host` attribute |
| XML text content | REQ-EXT-032 | `edge-config.xml` | Extract `server.name` text content |
| XML both attributes and text | REQ-EXT-036 | `edge-config.xml` | `<server host="..." port="...">Name</server>` |
| XML empty element | REQ-EXT-035 | `edge-config.xml` | `<empty_element/>` extraction |
| XML multiple same tags | REQ-EXT-037 | `edge-config.xml` | Multiple `<server>` elements as array |
| XML deep nesting | REQ-EXT-031 | `edge-config.xml` | 5-level nested XML elements |
| YAML boolean variations | REQ-EXT-023 | `edge-tokens.yaml` | true/True/TRUE/yes/on all parse as boolean |
| YAML anchors and aliases | REQ-EXT-024 | `edge-tokens.yaml` | `&default_template` and `<<: *default_template` |
| YAML multiline strings | REQ-EXT-023 | `edge-tokens.yaml` | Literal `|` and folded `>` strings |

## Template Engine Edge Cases

| Edge Case | Requirement | File | Description |
|-----------|-------------|------|-------------|
| Conditional template (false) | REQ-TPL-134 | `conditionally-generated.txt.j2` | Skipped when `enable_feature == false` |
| Conditional template (condition) | REQ-TPL-133 | `config.yaml` | Uses `when: "enable_feature == true"` |
| Loop over empty array | REQ-TPL-021 | `always-generated.txt.j2` | `{% for %} ... {% else %}` handles empty |
| Undefined variable with default | REQ-TPL-045, REQ-TPL-030 | `always-generated.txt.j2` | `{{ var \| default('N/A') }}` |
| Whitespace control | REQ-TPL-090 | `edge-whitespace.txt.j2` | Uses `{%-` and `-%}` extensively |
| Jinja2 environment options | REQ-TPL-060-062 | `config.yaml` | Sets `trim_blocks`, `lstrip_blocks` |
| Nested data access | REQ-TPL-044 | `always-generated.txt.j2` | Access deep nested: `{{ json.city_name }}` |

## Code Preservation Edge Cases

| Edge Case | Requirement | File | Description |
|-----------|-------------|------|-------------|
| Multiple preservation blocks | REQ-PRV-032 | `with-preservation.py.j2` | 4+ preservation blocks in single file |
| Descriptive identifiers | REQ-PRV-082 | `with-preservation.py.j2` | `custom_imports`, `custom_methods`, etc. |
| Conditional preservation | REQ-PRV-102-104 | N/A (future) | Preservation in conditional templates |
| Preservation validation | REQ-PRV-060-063 | N/A | Would catch nested or unmatched markers |
| Block matching by identifier | REQ-PRV-050-052 | `with-preservation.py.j2` | Identifiers match between generations |

## Automation Edge Cases

| Edge Case | Requirement | File | Description |
|-----------|-------------|------|-------------|
| Conditional hook execution | REQ-AUT-030-033 | `config.yaml` | Hook runs when `enable_docker == true` |
| Multiple hook error modes | REQ-AUT-020-023 | `config.yaml` | `on_error: ignore/warn/fail` |
| Hook with working directory | REQ-AUT-050-052 | N/A | Could add `working_dir` parameter |
| Hook after all templates | REQ-AUT-010-011 | `config.yaml` | Hooks run only after successful generation |
| Hook skipped by condition | REQ-AUT-032 | `config.yaml` | Docker hook skipped when flag is false |

## CLI Edge Cases

| Edge Case | Requirement | Test Method | Description |
|-----------|-------------|-------------|-------------|
| Dry run mode | REQ-CLI-030-036 | `--dry-run` | Preview without writing files |
| Variable preview | REQ-CLI-040-047 | `--show-variables` | Display all resolved tokens |
| Validation mode | REQ-CLI-100-105 | `--validate` | Check config without generation |
| Verbose warnings | REQ-CLI-090 | `--verbose` | Show collision and skip warnings |
| Configuration discovery | REQ-CFG-080-083 | No explicit path | Auto-find config.yaml |

## Error Handling Edge Cases

| Edge Case | Expected Behavior | How Tested |
|-----------|-------------------|------------|
| Empty array iteration | No error, uses `{% else %}` block | `always-generated.txt.j2` |
| Null value access | Returns None, uses default filter | `{{ null_value \| default('N/A') }}` |
| Missing nested key | Logs warning, returns None | Deep nesting with missing keys |
| Array out of bounds | Handles gracefully, returns None | `components[999].name` |
| Regex no match | Logs warning, uses original value | `\d+` on text without numbers |
| Transform failure | Returns original value | `upper` on non-string types |
| Undefined variable | Jinja2 undefined error (if no default) | Caught by template validation |
| Token collision | Logs warning, uses override value | `version` in both static and namespace |
| Conditional false | Template skipped silently (DEBUG log) | `enable_feature == false` |

## Data Type Edge Cases

| Data Type | Edge Cases Tested | File |
|-----------|------------------|------|
| String | Empty "", special chars, unicode, multiline | All input files |
| Number | Zero, negative, scientific notation, large | `edge-data.json`, `edge-tokens.yaml` |
| Boolean | true/false variations, yes/no, on/off | `edge-tokens.yaml` |
| Null | Direct null, null in nested objects | `edge-data.json` |
| Array | Empty [], single element, nested arrays | `edge-data.json` |
| Object | Empty {}, deeply nested, null values | `edge-data.json` |

## Special Characters Edge Cases

| Character Type | Example | File |
|----------------|---------|------|
| Punctuation | `!@#$%^&*()_+-=[]{}` | `edge-data.json` |
| Quotes | `"double"`, `'single'` | All input files |
| XML special | `<>&"'` (escaped) | `edge-config.xml` |
| Unicode | Chinese: 你好, Emoji: 🌍 | `edge-data.json`, `edge-tokens.yaml` |
| Whitespace | Tabs, newlines, extra spaces | `edge-config.xml`, `edge-tokens.yaml` |
| Path separators | `/`, `\`, `.` in keys | `edge-tokens.yaml` |

## Requirements Coverage Summary

### Configuration (REQ-CFG)
- ✅ REQ-CFG-021: Namespace organization
- ✅ REQ-CFG-033-034: Static/namespaced coexistence
- ✅ REQ-CFG-041: Template-specific overrides
- ✅ REQ-CFG-074-077: Token collision detection

### Data Extraction (REQ-EXT)
- ✅ REQ-EXT-032-038: XML extraction (attributes, text, deep nesting)
- ✅ REQ-EXT-052-054: Array/object wildcards
- ✅ REQ-EXT-062-063: Transform safety
- ✅ REQ-EXT-070-074: Regex filtering
- ✅ REQ-EXT-080-083: Array and object handling

### Template Engine (REQ-TPL)
- ✅ REQ-TPL-021: Control structures (if/for/else)
- ✅ REQ-TPL-030: Built-in filters
- ✅ REQ-TPL-045: Undefined variable handling
- ✅ REQ-TPL-060-062: Jinja2 options
- ✅ REQ-TPL-090: Whitespace control
- ✅ REQ-TPL-130-138: Conditional templates

### Code Preservation (REQ-PRV)
- ✅ REQ-PRV-010-014: Preservation markers
- ✅ REQ-PRV-032-033: Multiple blocks per file
- ✅ REQ-PRV-042-044: Content injection and matching
- ✅ REQ-PRV-050-052: Block matching by identifier
- ✅ REQ-PRV-082: Descriptive identifiers

### Automation (REQ-AUT)
- ✅ REQ-AUT-010-016: Hook execution
- ✅ REQ-AUT-020-023: Error handling
- ✅ REQ-AUT-030-033: Conditional hooks

### CLI (REQ-CLI)
- ✅ REQ-CLI-030-036: Dry run mode
- ✅ REQ-CLI-040-047: Variable preview
- ✅ REQ-CLI-090: Verbose mode
- ✅ REQ-CLI-100-105: Validation mode

## Testing Checklist

Use this checklist to verify all edge cases:

- [ ] Run generation without errors: `template-forge`
- [ ] See token collision warning: `template-forge --verbose`
- [ ] Verify conditional templates skipped: Check output directory
- [ ] Verify empty arrays handled: Check `always-generated.txt`
- [ ] Verify preservation markers: Check `with-preservation.py`
- [ ] Verify token overrides: Check `with-overrides.txt`
- [ ] Test dry run: `template-forge --dry-run`
- [ ] Test variable preview: `template-forge --show-variables`
- [ ] Test validation: `template-forge --validate`
- [ ] Modify config and test conditional generation
- [ ] Add custom code and test preservation on regeneration
- [ ] Run automated tests: `pytest tests/test_edge_cases.py -v`

## Lessons from Edge Cases

1. **Defensive Programming**: Always provide defaults for optional values
2. **Graceful Degradation**: Warnings instead of errors for non-critical issues
3. **Clear Feedback**: Verbose mode shows what's happening under the hood
4. **Safe Transforms**: Type conversions handle failure gracefully
5. **Array Safety**: Empty arrays and bounds checking prevent crashes
6. **Namespace Protection**: Prevents accidental token collisions
7. **Conditional Logic**: Templates and hooks can be context-aware
8. **Preservation Robustness**: Custom code survives structural changes

## Future Edge Cases to Add

- [ ] Circular template includes (should detect and error)
- [ ] Very large files (performance testing)
- [ ] Binary file handling (should skip or error gracefully)
- [ ] Concurrent generation (thread safety)
- [ ] Hook timeout testing (REQ-AUT-013)
- [ ] Malformed preservation markers (REQ-PRV-071)
- [ ] Nested preservation blocks (should error per REQ-PRV-061)
