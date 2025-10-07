# Python Class Generation Example

This example shows how to generate Python classes and modules from various input sources.

## Files in this example:

- `classes.h` - C header file with class definitions
- `version.py` - Python version information
- `class_template.py.j2` - Jinja2 template for Python class generation
- `config.yaml` - Template Forge configuration

## Use Cases

This example demonstrates:
- Parsing C header files to extract class definitions
- Generating Python wrapper classes
- Creating version modules with metadata
- Code scaffolding for Python projects

## Usage

```bash
cd examples/python-class
template-forge config.yaml
```

## Expected Output

Generates Python modules with:
- Class definitions based on C headers
- Method signatures and docstrings
- Version information and metadata
- Type hints and modern Python features

## Key Concepts Demonstrated

1. **Mixed Input Sources**: Process different file formats in one project
2. **Code Scaffolding**: Generate boilerplate Python code
3. **Type Mapping**: Convert C types to Python equivalents
4. **Documentation Generation**: Create docstrings from metadata
5. **Module Organization**: Structure Python packages properly