# Template Forge - Requirements Documentation

This directory contains the comprehensive requirements documentation for Template Forge, organized by functional area.

## Requirements Organization

The requirements are organized into seven main documents:

### 1. [System Overview](01_system_overview.md)
**Purpose**: High-level system requirements, architecture, use cases, and quality attributes.

**Coverage**:
- System purpose and objectives
- Architecture components
- Primary use cases
- Quality attributes (performance, usability, extensibility)
- Technical constraints
- Assumptions

**Requirement IDs**: `REQ-SYS-xxx`

---

### 2. [Configuration File](02_configuration.md)
**Purpose**: Configuration file format, structure, validation, and advanced features.

**Coverage**:
- YAML configuration format
- Configuration structure (inputs, static_tokens, templates)
- Token extraction rules syntax
- Template configuration
- Jinja2 options
- Path resolution rules
- Configuration validation
- **Configuration discovery** (auto-find config files)
- **Smart defaults** (sensible default values)
- **Configuration includes** (modular, reusable config fragments)

**Requirement IDs**: `REQ-CFG-xxx`

---

### 3. [Data Extraction](03_data_extraction.md)
**Purpose**: Input file formats, data extraction mechanisms, and token generation.

**Coverage**:
- Supported input formats (JSON, YAML, XML, ARXML)
- Format-specific parsing requirements
- Token extraction using dot notation
- Array and object wildcards
- Data transformations (upper, lower, title, capitalize)
- Regular expression filtering
- Error handling for extraction

**Requirement IDs**: `REQ-EXT-xxx`

---

### 4. [Template Engine](04_template_engine.md)
**Purpose**: Jinja2 template processing, features, validation, and output generation.

**Coverage**:
- Jinja2 template syntax support
- Template processing workflow
- Built-in filters and custom filters
- Template variables and data access
- Output file generation
- Whitespace control
- Template inheritance and includes
- Error handling for templates
- **Template validation** (syntax checking before generation)
- **Conditional templates** (generate based on token values)

**Requirement IDs**: `REQ-TPL-xxx`

---

### 5. [Code Preservation](05_code_preservation.md)
**Purpose**: Mechanism for preserving custom code sections during file regeneration.

**Coverage**:
- Preservation marker syntax (`@PRESERVE_START`, `@PRESERVE_END`)
- Content extraction from existing files
- Content injection into regenerated files
- Block matching logic
- Validation of preservation markers
- Error handling
- Use cases and examples

**Requirement IDs**: `REQ-PRV-xxx`

---

### 6. [Command-Line Interface](06_cli.md)
**Purpose**: Command-line interface requirements, options, modes, and behavior.

**Coverage**:
- Command syntax and arguments
- Configuration discovery
- **Dry run mode** (preview without writing files)
- **Variable preview** (show all available tokens)
- **Diff preview** (show changes before applying)
- **Interactive init** (wizard for creating config files)
- **Better error context** (helpful, actionable error messages)
- Validation mode
- Help message format and content
- Logging and output formatting
- Exit codes
- Error handling
- Color support
- Path handling

**Requirement IDs**: `REQ-CLI-xxx`

---

### 7. [Automation and Hooks](07_automation.md)
**Purpose**: Post-generation automation and hook system for integrating with external tools.

**Coverage**:
- Post-generation hooks (run commands after generation)
- Hook configuration and execution
- Error handling and timeout management
- Conditional hook execution
- Working directory specification
- Shell command support
- Security considerations
- CLI integration (--no-hooks flag)

**Requirement IDs**: `REQ-AUT-xxx`

---

## Requirement ID Structure

Each requirement has a unique identifier following this pattern:

```
REQ-<AREA>-<NUMBER>
```

Where:
- **AREA**: Three-letter code for the functional area
  - `SYS`: System Overview
  - `CFG`: Configuration
  - `EXT`: Data Extraction
  - `TPL`: Template Engine
  - `PRV`: Code Preservation (PRV for PreserVation)
  - `CLI`: Command-Line Interface
  - `AUT`: Automation and Hooks

- **NUMBER**: Three-digit sequential number (001-999)

### Examples:
- `REQ-SYS-001`: System Purpose requirement
- `REQ-CFG-020`: Configuration input section requirement
- `REQ-EXT-010`: JSON parsing requirement
- `REQ-TPL-030`: Jinja2 filters requirement
- `REQ-PRV-010`: Preservation marker format requirement
- `REQ-CLI-050`: Validation mode requirement
- `REQ-AUT-010`: Post-generation hook execution requirement

## Traceability

Requirements are organized hierarchically within each document:

1. **Major Sections**: Functional groupings (e.g., "Supported Input Formats")
2. **Requirements**: Individual testable requirements with unique IDs
3. **Examples**: Code examples demonstrating requirement implementation

## Using These Requirements

### For Development
- Each requirement should map to implementation code or test cases
- Use requirement IDs in commit messages and code comments
- Reference requirements in code documentation

### For Testing
- Create test cases that verify each requirement
- Use requirement IDs to track test coverage
- Ensure all requirements have corresponding tests

### For Documentation
- Reference requirements in user-facing documentation
- Link requirements to example code and tutorials
- Update requirements when adding new features

## Version History

| Version | Date       | Changes                                     |
|---------|------------|---------------------------------------------|
| 1.0     | 2025-10-03 | Initial requirements documentation created  |
|         |            | Reverse-engineered from existing codebase  |

## Maintenance

When updating requirements:

1. **Adding New Requirements**:
   - Use the next available sequential number in the appropriate area
   - Add the requirement to the relevant document
   - Update the traceability matrix (if maintained)

2. **Modifying Requirements**:
   - Keep the same requirement ID when updating content
   - Document changes in commit messages
   - Update related test cases

3. **Deprecating Requirements**:
   - Mark as deprecated but keep in documentation
   - Add note explaining why deprecated
   - Document replacement requirement if applicable

## Related Documentation

- [User Guide](../USER_GUIDE.md): How to use Template Forge
- [API Documentation](../API.md): API reference for developers
- [Development Guide](../DEVELOPMENT.md): Development practices and architecture
- [Examples](../../examples/): Working examples demonstrating features

## Questions or Feedback

For questions about requirements or to suggest improvements:
- Open an issue: https://github.com/CarloFornari/template_forge/issues
- Discuss: https://github.com/CarloFornari/template_forge/discussions
