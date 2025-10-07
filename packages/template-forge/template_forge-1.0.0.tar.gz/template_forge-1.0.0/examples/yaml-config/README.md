# YAML Configuration Example

This example demonstrates comprehensive YAML parsing capabilities of Template Forge, including:

- **Basic value extraction** from nested structures
- **Array extraction** for lists of items
- **Complex object extraction** for nested configuration objects
- **Sub-key object handling** where accessing non-leaf nodes returns complete objects/arrays
- **Content preservation** using `@PRESERVE_START`/`@PRESERVE_END` markers

## Files

- `app-config.yaml` - Complex YAML configuration file with nested structures
- `config.yaml` - Template Forge configuration defining token extraction rules
- `app-summary.md.j2` - Jinja2 template generating a Markdown summary
- `config-validation.py.j2` - Jinja2 template generating a Python validation class

## Key Features Demonstrated

### Object vs. Value Extraction
When extracting tokens from YAML, Template Forge handles both individual values and complex objects:

```yaml
# Individual value extraction
- name: "app_name"
  key: "application.name"          # Returns: "ConfigManager"

# Object extraction (sub-keys become complete objects)
- name: "database_config"
  key: "application.database"      # Returns: entire database object with sub-keys

# Array extraction
- name: "features"
  key: "application.features"      # Returns: ["real-time-sync", "multi-tenant", ...]
```

### Preservation Markers
Both templates include preservation markers for custom content:

**Markdown template (HTML comments):**
```html
<!-- @PRESERVE_START -->
<!-- Add custom environment documentation here -->
<!-- @PRESERVE_END -->
```

**Python template (Python comments):**
```python
# @PRESERVE_START
# Add custom validation rules here
# @PRESERVE_END
```

### Nested Object Handling
The example shows how accessing non-leaf nodes returns complete objects:

- `application.database` → Returns complete database configuration object
- `environments` → Returns all environment configurations as a nested object
- `deployment.scaling` → Returns complete scaling configuration

## Generated Output

### app-summary.md
- Markdown document with application overview
- Formatted database and environment configurations
- Feature listing and deployment information
- Preserved content sections for custom documentation

### config_validator.py
- Python class for configuration validation
- Type hints and comprehensive error checking
- Extracted objects properly formatted as Python dictionaries
- Preserved content sections for custom validation logic

## Usage

```bash
# From the yaml-config directory
template-forge config.yaml

# Or from the project root
template-forge examples/yaml-config/config.yaml
```

## Generated Files Location

The output files are generated in the `output/` directory:
- `output/app-summary.md`
- `output/config_validator.py`

## Testing the Output

The generated Python validator can be executed directly:

```bash
cd output
python config_validator.py
```

This will run all validation checks and display a summary of the configuration.

## Complex Data Structure Support

This example demonstrates Template Forge's ability to handle:

1. **Multi-level nesting** - Objects within objects (e.g., `application.database.primary`)
2. **Mixed data types** - Strings, integers, booleans, arrays, and objects
3. **Dynamic arrays** - Lists of objects with varying structures
4. **Conditional content** - Environment-specific configurations
5. **Type preservation** - Maintains original YAML data types in output

The YAML parsing capability makes Template Forge ideal for configuration management, infrastructure as code, and any scenario requiring structured data transformation.