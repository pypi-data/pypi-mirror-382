# C++ Project Generation Example

This example shows how to generate C++ source code from XML project metadata.

## Files in this example:

- `project.xml` - XML project metadata with build configuration
- `main.cpp.j2` - Jinja2 template for generating C++ main file
- `config.yaml` - Template Forge configuration

## Input Data (`project.xml`)

Contains project metadata including:
- Project name, version, and author information
- Build configuration and dependencies
- Compiler settings and target specifications

## Usage

```bash
cd examples/cpp-project
template-forge config.yaml
```

## Expected Output

Generates a complete C++ main file with:
- Header includes based on project dependencies
- Version information from XML metadata
- Main function with project-specific initialization
- Build configuration comments

## Key Concepts Demonstrated

1. **XML Parsing**: Extract data from structured XML files
2. **Code Generation**: Generate source code from metadata
3. **Conditional Logic**: Use Jinja2 conditionals in templates
4. **List Processing**: Handle arrays of dependencies and includes
5. **String Formatting**: Format code with proper indentation