# Template Forge Examples

This directory contains organized examples demonstrating different use cases of Template Forge.

## Example Categories

### 📁 `basic/`
**Status:** ✅ Working  
Basic examples showing fundamental Template Forge usage:
- Simple JSON configuration extraction
- Basic template rendering
- Configuration file generation
- Code preservation basics

**Requirements Covered:** REQ-CFG-020-025, REQ-EXT-010-014, REQ-PRV-010-044

---

### 📁 `advanced-features/`
**Status:** ✅ Working  
**NEW!** Comprehensive demonstration of advanced features:
- Configuration includes (modular configs)
- Conditional template generation
- Post-generation hooks with conditions
- Template inheritance (base + child templates)
- Multiple code preservation blocks
- Hierarchical static tokens
- Template-specific token overrides
- Jinja2 environment options

**Requirements Covered:** REQ-CFG-032, REQ-CFG-041, REQ-CFG-050, REQ-TPL-110-138, REQ-PRV-030-102, REQ-AUT-001-093

---

### 📁 `cpp-project/`
**Status:** ✅ Working  
C++ project generation examples:
- XML project file parsing
- C++ code generation from metadata
- Build system configuration

**Requirements Covered:** REQ-EXT-030-038

---

### 📁 `docker/`
**Status:** ✅ Working  
Docker and containerization examples:
- YAML deployment configuration
- Docker Compose file generation
- Container orchestration setup

**Requirements Covered:** REQ-EXT-020-024

---

### 📁 `python-class/`
**Status:** ✅ Working  
Python code generation examples:
- Class generation from JSON metadata
- Structured data extraction
- Python module scaffolding

**Requirements Covered:** REQ-EXT-010-014, REQ-TPL-020-024

---

### 📁 `autosar/`
**Status:** ✅ Working  
AUTOSAR automotive examples:
- ARXML file parsing
- ECU configuration extraction
- Automotive software generation

**Requirements Covered:** REQ-EXT-040-046

---

### 📁 `yaml-config/`
**Status:** ✅ Working  
YAML configuration processing:
- Complex YAML parsing
- Nested data extraction
- Configuration validation generation
- Multiple preservation blocks

**Requirements Covered:** REQ-EXT-020-024, REQ-PRV-030-044

---

### 📁 `edge-cases/`
**Status:** ✅ Working  
**NEW!** Comprehensive edge case testing:
- Empty arrays and null value handling
- Deep nesting (5+ levels) extraction
- Transform operations on unexpected types
- Regex filtering with no matches
- Array index out of bounds handling
- XML attributes vs text content
- Boolean variations (true/yes/on)
- Conditional template generation
- Token collision detection
- Code preservation across regenerations
- Conditional hooks execution

This example is designed for testing and validation, demonstrating robust error handling and graceful degradation in challenging scenarios.

**Requirements Covered:** REQ-CFG-074-077, REQ-EXT-052-074, REQ-TPL-130-138, REQ-PRV-042-043, REQ-AUT-030-033

---

## Running Examples

Each subdirectory contains:
- **Input files**: Data files (JSON, YAML, XML, ARXML)
- **Templates**: Jinja2 template files (*.j2)
- **Configuration**: YAML config files
- **README**: Specific usage instructions

To run an example:

```bash
cd examples/basic
template-forge config.yaml
```

## CLI Features Demonstrated

### Validation
```bash
# Validate configuration
template-forge config.yaml --validate

# Validate templates
template-forge config.yaml --validate-templates
```

### Preview Modes
```bash
# Dry run - preview without writing files
template-forge config.yaml --dry-run

# Show all available variables
template-forge config.yaml --show-variables

# Show diff of changes
template-forge config.yaml --diff
```

### Hook Control
```bash
# Skip post-generation hooks
template-forge config.yaml --no-hooks
```

### Verbosity
```bash
# Enable verbose logging
template-forge config.yaml --verbose
```

## Requirements Coverage

This examples directory demonstrates implementation of:

- **REQ-CFG-xxx**: Configuration file format, structure, includes, validation
- **REQ-EXT-xxx**: Data extraction from JSON, YAML, XML, ARXML
- **REQ-TPL-xxx**: Template processing, inheritance, conditionals
- **REQ-PRV-xxx**: Code preservation across regenerations
- **REQ-CLI-xxx**: Command-line interface features
- **REQ-AUT-xxx**: Post-generation hooks and automation

See individual example READMEs for specific requirement coverage.

## Example Complexity Levels

1. **Beginner**: `basic/`, `docker/`, `python-class/`
2. **Intermediate**: `cpp-project/`, `yaml-config/`, `autosar/`
3. **Advanced**: `advanced-features/`, `edge-cases/`

Start with basic examples to learn fundamentals, then progress to advanced features. The `edge-cases/` example is particularly useful for understanding error handling and boundary conditions.

## File Organization

```
examples/
├── README.md                 # This file
├── basic/                    # Basic usage examples
│   ├── settings.json         # Input data
│   ├── config.yaml          # Configuration
│   └── *.j2                 # Templates
├── advanced-features/       # Advanced features demo
├── cpp-project/             # C++ generation
├── docker/                  # Container setup
├── python-class/            # Python code gen
├── autosar/                 # AUTOSAR examples
├── yaml-config/             # YAML processing
└── edge-cases/              # Edge case testing
    ├── README.md            # Detailed documentation
    ├── QUICK_REFERENCE.md   # Quick testing guide
    ├── edge-data.json       # JSON edge cases
    ├── edge-config.xml      # XML edge cases
    ├── edge-tokens.yaml     # YAML edge cases
    ├── config.yaml          # Test configuration
    └── templates/           # Test templates
```