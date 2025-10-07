# Advanced Features Requirements

## Overview
This document specifies advanced features for template-forge to support more complex use cases without requiring custom Python code.

---

## REQ-ADV: Advanced Features

### REQ-ADV-001: File Glob Pattern Support
**Priority:** High  
**Status:** Proposed

The system SHALL support glob patterns in input file paths to automatically discover and process matching files.

**Rationale:**  
Users should not need to know exact filenames or write Python code to discover files dynamically.

**Acceptance Criteria:**
- Input paths support standard glob patterns (*, **, ?, [])
- First matching file is used when multiple matches exist
- Clear error if no files match the pattern
- Relative paths resolved from config file location

**Examples:**
```yaml
inputs:
  - path: "autosar/*.arxml"
    namespace: arxml
    format: xml
  
  - path: "config/**/*.yaml"
    namespace: config
    format: yaml
    match: first  # Optional: 'first', 'all', 'error_if_multiple'
```

---

### REQ-ADV-002: Derived/Computed Tokens
**Priority:** High  
**Status:** Proposed

The system SHALL support deriving token values from other tokens or context using transformations.

**Rationale:**  
Common transformations (case conversion, regex extraction, string manipulation) should not require custom Python code.

**Acceptance Criteria:**
- Tokens can reference other tokens using ${token_name} syntax
- Built-in transformations available (lowercase, uppercase, snake_case, camel_case, etc.)
- Regex extraction and replacement supported
- Transformations can be chained

**Examples:**
```yaml
static_tokens:
  # Reference another token
  project_dir: "${workspace_name}"
  
  # Apply transformations
  component_prefix:
    value: "${workspace_name}"
    transforms:
      - regex_extract: "^([A-Z][a-z]+)+"
      - regex_replace:
          pattern: "([A-Z][a-z]+)(HI[ABC])"
          replacement: "\\1_\\2"
      - lowercase
  
  # Simple transformations
  module_name:
    value: "${project_name}"
    transform: snake_case
```

---

### REQ-ADV-003: Cross-Input Token References
**Priority:** High  
**Status:** Proposed

The system SHALL allow static tokens to reference values extracted from input files.

**Rationale:**  
Users often need to extract a value from one file and use it in multiple templates without repetition.

**Acceptance Criteria:**
- Static tokens can reference namespace.key paths
- Wildcard (*) supported for extracting first key
- Array indexing supported
- Clear error if referenced path doesn't exist

**Examples:**
```yaml
inputs:
  - path: "config.yaml"
    namespace: yaml_config
    format: yaml

static_tokens:
  # Extract first key from SoftwareComponents.*
  component_name:
    from_input: "yaml_config.SoftwareComponents.*[0]"
  
  # Extract specific nested value
  version:
    from_input: "yaml_config.project.version"
    default: "1.0.0"  # Optional default if not found
```

---

### REQ-ADV-004: Environment and Context Variables
**Priority:** Medium  
**Status:** Proposed

The system SHALL provide access to environment variables and execution context as tokens.

**Rationale:**  
Templates often need access to current directory, environment variables, or execution time information.

**Acceptance Criteria:**
- ${ENV.VAR_NAME} syntax for environment variables
- ${CWD} for current working directory (absolute path)
- ${CWD.basename} for directory name only
- ${CONFIG_DIR} for config file directory
- ${TIMESTAMP} for current ISO timestamp
- ${DATE} for current date
- Clear error if required env var is missing

**Examples:**
```yaml
static_tokens:
  # Environment variables
  user: "${ENV.USER}"
  home: "${ENV.HOME}"
  
  # Context variables
  workspace_dir: "${CWD}"
  workspace_name: "${CWD.basename}"
  config_location: "${CONFIG_DIR}"
  
  # Time variables
  generated_at: "${TIMESTAMP}"
  build_date: "${DATE}"
  
  # With defaults
  api_key:
    value: "${ENV.API_KEY}"
    required: true  # Error if not set
  
  debug_mode:
    value: "${ENV.DEBUG}"
    default: "false"
```

---

### REQ-ADV-005: Custom Filter Registration
**Priority:** Medium  
**Status:** Proposed

The system SHALL support registering custom Jinja2 filters via configuration.

**Rationale:**  
Domain-specific filters should not require forking template-forge or modifying core code.

**Acceptance Criteria:**
- Custom filters specified in config file
- Filters loaded from importable Python modules
- Filters available in all templates
- Clear error if filter module/function not found
- Filters can accept arguments

**Examples:**
```yaml
custom_filters:
  - module: "myproject.filters"
    filters:
      - format_port_name
      - get_interface_type
      - calculate_checksum
  
  - module: "common_filters"
    filters:
      - safe_filename: sanitize_path  # Rename filter
```

**Usage in templates:**
```jinja2
{{ port_name | format_port_name(prefix='RTE') }}
{{ data | calculate_checksum }}
```

---

### REQ-ADV-006: Multiple File Input Strategies
**Priority:** Medium  
**Status:** Proposed

The system SHALL support different strategies when multiple files match a glob pattern.

**Rationale:**  
Different use cases require different behaviors (use first, merge all, error on multiple).

**Acceptance Criteria:**
- 'first' strategy: Use first matching file (default)
- 'all' strategy: Merge data from all matching files
- 'error_if_multiple' strategy: Fail if more than one match
- 'list' strategy: Create list of all extracted data

**Examples:**
```yaml
inputs:
  # Use first matching file
  - path: "config/*.yaml"
    namespace: config
    match: first
  
  # Merge all matching files
  - path: "modules/**/*.json"
    namespace: modules
    match: all
    merge_strategy: deep  # or 'shallow'
  
  # Error if multiple matches
  - path: "main*.arxml"
    namespace: arxml
    match: error_if_multiple
  
  # Create list of all files
  - path: "components/*.yaml"
    namespace: components
    match: list  # Results in array of extracted data
```

---

### REQ-ADV-007: Token Resolution Order
**Priority:** High  
**Status:** Proposed

The system SHALL resolve tokens in the correct order to support dependencies.

**Rationale:**  
Derived tokens may depend on other derived tokens or input data.

**Acceptance Criteria:**
- Environment/context variables resolved first
- Input files processed next
- Static tokens resolved in dependency order
- Circular dependencies detected and reported
- Clear error messages for unresolved references

**Resolution Order:**
1. Environment variables (${ENV.*})
2. Context variables (${CWD}, ${CONFIG_DIR}, etc.)
3. Input files (all inputs processed)
4. Static tokens (topologically sorted by dependencies)
5. Template-specific token overrides

---

### REQ-ADV-008: Token Reference Syntax
**Priority:** High  
**Status:** Proposed

The system SHALL use a consistent syntax for referencing tokens and applying transformations.

**Syntax Specification:**

**Variable Reference:**
```yaml
"${variable_name}"
"${namespace.nested.key}"
"${ENV.VAR_NAME}"
"${CWD.basename}"
```

**With Transformations (Short Form):**
```yaml
value: "${variable_name}"
transform: lowercase
```

**With Transformations (Full Form):**
```yaml
value: "${variable_name}"
transforms:
  - lowercase
  - snake_case
  - regex_replace:
      pattern: "^(.+)_v\\d+$"
      replacement: "\\1"
```

**With Default Values:**
```yaml
value: "${ENV.OPTIONAL_VAR}"
default: "default_value"
```

**With Required Flag:**
```yaml
value: "${ENV.REQUIRED_VAR}"
required: true
error_message: "REQUIRED_VAR must be set"
```

---

## Implementation Notes

### Backward Compatibility
All new features SHALL maintain backward compatibility with existing configs:
- Existing configs without advanced features work unchanged
- New syntax is opt-in (old syntax remains valid)
- No breaking changes to current behavior

### Performance Considerations
- Glob pattern matching should be efficient for large directory trees
- Token resolution should be lazy where possible
- File reading should be cached to avoid multiple reads

### Error Messages
All error messages SHALL be clear and actionable:
- Show which token/input caused the error
- Suggest corrections for common mistakes
- Include file path and line number where applicable

### Documentation Requirements
- All features documented with examples
- Migration guide for Python code to pure config
- Best practices for complex token derivations

---

## Testing Requirements

### Unit Tests
- REQ-ADV-001: Test glob patterns (*, **, ?, [])
- REQ-ADV-002: Test all built-in transformations
- REQ-ADV-003: Test cross-input references with wildcards
- REQ-ADV-004: Test all context variables
- REQ-ADV-005: Test custom filter loading
- REQ-ADV-006: Test all match strategies
- REQ-ADV-007: Test dependency resolution
- REQ-ADV-008: Test all syntax variations

### Integration Tests
- Complete A2L generator example using only YAML config
- Multi-file project with glob patterns and derived tokens
- Error handling for all failure modes

### Edge Cases
- Empty glob matches
- Circular token dependencies
- Missing environment variables
- Invalid regex patterns
- Malformed transformation syntax

---

## Success Metrics

### Code Reduction
- A2L generator: 261 lines → ~10 lines (or pure CLI)
- Other similar projects should see 80-90% reduction in boilerplate

### User Experience
- Users can accomplish common tasks without Python code
- Configuration is self-documenting
- Error messages guide users to solutions

### Maintainability
- New transformations easy to add
- Custom filters isolated from core
- Clear separation of concerns
