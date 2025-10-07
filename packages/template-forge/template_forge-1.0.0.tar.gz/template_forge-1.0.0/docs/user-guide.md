# Template Forge User Guide

A comprehensive guide to installing, configuring, and using Template Forge for automated code generation from structured data.

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Data Sources](#data-sources)
- [Templates](#templates)
- [Content Preservation](#content-preservation)
- [Advanced Features](#advanced-features)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### From PyPI (Recommended)

```bash
pip install template-forge
```

### From Source

1. Clone the repository:
   ```bash
   git clone https://github.com/CarloFornari/template_forge.git
   cd template_forge
   ```

2. Install in development mode:
   ```bash
   pip install -e .
   ```

### Verify Installation

```bash
# Check if Template Forge is installed
python -c "import template_forge; print('Template Forge installed successfully')"

# Validate a configuration file
python validate_config.py --help
```

## Quick Start

### 1. Create Your First Project

```bash
mkdir my-template-project
cd my-template-project
```

### 2. Create a Data File

Create `data.json`:
```json
{
  "application": {
    "name": "MyApp",
    "version": "1.0.0",
    "description": "My awesome application"
  },
  "database": {
    "host": "localhost",
    "port": 5432
  }
}
```

### 3. Create a Template

Create `README.md.j2`:
```markdown
# {{ app_name }}

Version: {{ version }}
Description: {{ description }}

## Database Configuration
- Host: {{ db_host }}
- Port: {{ db_port }}

<!-- @PRESERVE_START -->
<!-- Add your custom documentation here -->
<!-- @PRESERVE_END -->
```

### 4. Create Configuration

Create `config.yaml`:
```yaml
template_dir: "."

inputs:
  - path: "data.json"
    tokens:
      - name: "app_name"
        key: "application.name"
      - name: "version"
        key: "application.version"
      - name: "description"
        key: "application.description"
      - name: "db_host"
        key: "database.host"
      - name: "db_port"
        key: "database.port"

templates:
  - template: "README.md.j2"
    output: "README.md"
```

### 5. Generate Output

```bash
python -m template_forge config.yaml
```

Your `README.md` will be generated with data from your JSON file!

## Configuration

### Configuration File Structure

The `config.yaml` file controls how Template Forge extracts data and generates files:

```yaml
# Directory containing template files (default: ".")
template_dir: "./templates"

# Input data sources
inputs:
  - path: "data.json"
    tokens:
      - name: "token_name"
        key: "path.to.value"
        regex: "optional_regex"
        transform: "optional_transform"

# Static values (no extraction needed)
static_tokens:
  company: "ACME Corp"
  year: 2025

# Output templates to process
templates:
  - template: "template.j2"
    output: "output.txt"
    tokens:
      template_specific: "value"

# Jinja2 engine options (optional)
jinja_options:
  trim_blocks: true
  lstrip_blocks: true
```

### Validation

Always validate your configuration before running:

```bash
python validate_config.py config.yaml
```

This will check for:
- Missing required fields
- Invalid file paths
- Duplicate token names
- Unknown configuration options

## Data Sources

Template Forge supports multiple structured data formats:

### JSON Files

**Example**: `config.json`
```json
{
  "server": {
    "name": "web-server",
    "port": 8080,
    "ssl": {
      "enabled": true,
      "cert_path": "/etc/ssl/cert.pem"
    }
  },
  "features": ["auth", "logging", "metrics"]
}
```

**Configuration**:
```yaml
inputs:
  - path: "config.json"
    tokens:
      - name: "server_name"
        key: "server.name"
      - name: "server_port"
        key: "server.port"
      - name: "ssl_enabled"
        key: "server.ssl.enabled"
      - name: "features"
        key: "features"  # Extracts entire array
```

### YAML Files

**Example**: `app.yaml`
```yaml
application:
  name: ConfigManager
  version: 2.3.1
  features:
    - real-time-sync
    - encryption
environments:
  production:
    debug: false
    log_level: WARN
  development:
    debug: true
    log_level: DEBUG
```

**Configuration**:
```yaml
inputs:
  - path: "app.yaml"
    tokens:
      - name: "app_name"
        key: "application.name"
      - name: "features"
        key: "application.features"
      - name: "environments"
        key: "environments"  # Extracts entire nested object
```

### XML Files

**Example**: `config.xml`
```xml
<application name="MyApp" version="1.0">
  <database>
    <host>localhost</host>
    <port>5432</port>
  </database>
  <features>
    <feature name="auth" enabled="true"/>
    <feature name="logging" enabled="false"/>
  </features>
</application>
```

**Configuration**:
```yaml
inputs:
  - path: "config.xml"
    tokens:
      - name: "app_name"
        key: "application.@name"  # @ for attributes
      - name: "app_version"
        key: "application.@version"
      - name: "db_host"
        key: "application.database.host"
      - name: "db_port"
        key: "application.database.port"
```

### AUTOSAR XML (ARXML)

**Example**: `ecu.arxml`
```xml
<AUTOSAR>
  <AR-PACKAGES>
    <AR-PACKAGE>
      <SHORT-NAME>ECU_Package</SHORT-NAME>
      <ELEMENTS>
        <ECU-INSTANCE>
          <SHORT-NAME>MyECU</SHORT-NAME>
          <SW-VERSION>1.2.3</SW-VERSION>
        </ECU-INSTANCE>
      </ELEMENTS>
    </AR-PACKAGE>
  </AR-PACKAGES>
</AUTOSAR>
```

**Configuration**:
```yaml
inputs:
  - path: "ecu.arxml"
    tokens:
      - name: "ecu_name"
        key: "AUTOSAR.AR-PACKAGES.AR-PACKAGE.ELEMENTS.ECU-INSTANCE.SHORT-NAME"
      - name: "sw_version"
        key: "AUTOSAR.AR-PACKAGES.AR-PACKAGE.ELEMENTS.ECU-INSTANCE.SW-VERSION"
```

## Templates

### Basic Jinja2 Templates

Templates use Jinja2 syntax with extracted tokens:

```jinja2
# {{ app_name }} Configuration File

[application]
name = {{ app_name }}
version = {{ version }}
debug = {{ debug_mode | lower }}

[database]
host = {{ db_host }}
port = {{ db_port }}

{% if features %}
[features]
{% for feature in features %}
{{ feature }} = enabled
{% endfor %}
{% endif %}
```

### Custom Filters

Template Forge provides additional filters:

```jinja2
{{ class_name | pascal_case }}     # MyClassName
{{ variable_name | snake_case }}   # my_variable_name
{{ text | upper }}                 # UPPERCASE
{{ config | pyjson }}              # Python-compatible JSON
```

### Conditional Generation

Use Jinja2 conditionals for dynamic content:

```jinja2
{% if environment == "production" %}
LOG_LEVEL=WARN
DEBUG=false
{% else %}
LOG_LEVEL=DEBUG
DEBUG=true
{% endif %}

{% if ssl_enabled %}
SSL_CERT_PATH={{ ssl_cert_path }}
SSL_KEY_PATH={{ ssl_key_path }}
{% endif %}
```

### Loops and Arrays

Process arrays and objects:

```jinja2
# Features
{% for feature in features %}
- {{ feature }}
{% endfor %}

# Environment Variables
{% for env_name, env_config in environments.items() %}
## {{ env_name | title }} Environment
Debug: {{ env_config.debug }}
Log Level: {{ env_config.log_level }}

{% endfor %}
```

## Content Preservation

### How Preservation Works

Content preservation allows you to maintain custom code sections when regenerating files:

1. **Add markers** to your templates
2. **Generate files** for the first time
3. **Add custom content** between the markers
4. **Regenerate** - custom content is preserved

### Preservation Markers

Use comment-style markers appropriate for your file type:

#### Python/Shell/YAML
```python
# @PRESERVE_START
# Your custom code here
def custom_function():
    pass
# @PRESERVE_END
```

#### C++/Java/JavaScript
```cpp
/* @PRESERVE_START */
// Custom implementation
void customFunction() {
    // Your code here
}
/* @PRESERVE_END */
```

#### HTML/XML
```html
<!-- @PRESERVE_START -->
<div class="custom-content">
  Custom HTML content
</div>
<!-- @PRESERVE_END -->
```

#### SQL
```sql
/* @PRESERVE_START */
-- Custom indexes
CREATE INDEX idx_custom ON table_name(column);
/* @PRESERVE_END */
```

### Preservation Example

**Template**: `config.py.j2`
```python
#!/usr/bin/env python3
"""
{{ app_name }} Configuration
Generated from template
"""

# Generated configuration
APP_NAME = "{{ app_name }}"
VERSION = "{{ version }}"

# @PRESERVE_START
# Add your custom configuration here
# This will be preserved across regenerations
# @PRESERVE_END

# More generated content
DATABASE_URL = "{{ database_url }}"
```

**First generation** creates:
```python
#!/usr/bin/env python3
"""
MyApp Configuration
Generated from template
"""

# Generated configuration
APP_NAME = "MyApp"
VERSION = "1.0.0"

# @PRESERVE_START
# Add your custom configuration here
# This will be preserved across regenerations
# @PRESERVE_END

# More generated content
DATABASE_URL = "postgresql://localhost:5432/myapp"
```

**After adding custom content**:
```python
# @PRESERVE_START
# Add your custom configuration here
CUSTOM_SETTING = "my_value"
FEATURE_FLAGS = {
    "new_ui": True,
    "beta_features": False
}
# @PRESERVE_END
```

**Subsequent regenerations** will preserve your custom content while updating other parts.

### Preservation Validation

Template Forge validates preservation markers:

- **Paired markers**: Every `@PRESERVE_START` must have a matching `@PRESERVE_END`
- **No nesting**: Preservation blocks cannot be nested
- **Consistent style**: Markers should use the same comment style throughout

## Advanced Features

### Token Transformations

Apply transformations to extracted values:

```yaml
data_sources:
  - type: json
    path: data.json
    extract:
      - key: "app.name"
        as: "app_name_upper"
        transform: "upper"      # UPPERCASE
      - key: "config.port"
        as: "port_number"
        transform: "int"        # Convert to integer
      - key: "className"
        as: "class_snake"
        transform: "snake_case" # my_class_name
```

**Available transformations:**

**String Case:**
- `upper` - Convert to UPPERCASE
- `lower` - Convert to lowercase
- `title` - Convert To Title Case
- `capitalize` - Capitalize first letter only

**String Formatting:**
- `strip` - Remove leading/trailing whitespace
- `snake_case` - Convert to snake_case (MyVar → my_var)
- `camel_case` - Convert to camelCase (my_var → MyVar)

**Type Conversions:**
- `int` - Convert to integer
- `float` - Convert to floating-point number
- `bool` - Convert to boolean (true/false, 1/0, yes/no, on/off)

**Collection Operations:**
- `len` - Get length of string, list, or collection
- `any` - True if any element is truthy (for lists)
- `all` - True if all elements are truthy (for lists)
- `sum` - Sum numeric values in a list
- `max` - Get maximum value from a list
- `min` - Get minimum value from a list
- `unique` - Remove duplicates from a list

**Examples:**

```yaml
# Type conversion
- key: "user_id"
  as: "user_id_int"
  transform: "int"

# Case conversion
- key: "ClassName"
  as: "class_file"
  transform: "snake_case"  # → class_name

# Collection operations
- key: "port_numbers"
  as: "max_port"
  transform: "max"  # [8080, 3000, 5432] → 5432

# Boolean conversion
- key: "enabled"
  as: "is_enabled"
  transform: "bool"  # "yes" → true
```

### Regex Filtering

Extract parts of values using regex:

```yaml
tokens:
  - name: "version_major"
    key: "version"
    regex: '^(\d+)\.'  # Extract "1" from "1.2.3"
  - name: "port_number"
    key: "connection_string"
    regex: ':(\d+)/'   # Extract port from URL
```

### Template-Specific Tokens

Override global tokens for specific templates:

```yaml
templates:
  - template: "docker-compose.yml.j2"
    output: "docker-compose.yml"
    tokens:
      environment: "production"
      replicas: 3
  - template: "docker-compose.yml.j2"
    output: "docker-compose.dev.yml"
    tokens:
      environment: "development"
      replicas: 1
```

### Multiple Data Sources

Combine data from multiple files:

```yaml
inputs:
  - path: "app-config.json"
    tokens:
      - name: "app_name"
        key: "name"
  - path: "database.yaml"
    tokens:
      - name: "db_host"
        key: "host"
  - path: "features.xml"
    tokens:
      - name: "features"
        key: "feature-list.feature"
```

### Custom Jinja2 Options

Customize the Jinja2 environment:

```yaml
jinja_options:
  trim_blocks: true           # Remove newlines after blocks
  lstrip_blocks: true         # Remove leading whitespace
  keep_trailing_newline: false # Don't preserve final newline
  block_start_string: "<%"    # Custom block delimiters
  block_end_string: "%>"
  variable_start_string: "<%" # Custom variable delimiters
  variable_end_string: "%>"
```

## Examples

### Example 1: API Documentation Generation

Generate OpenAPI documentation from service definitions.

**Data**: `api-spec.yaml`
```yaml
service:
  name: UserService
  version: v1
  base_path: /api/v1
endpoints:
  - path: /users
    method: GET
    description: List all users
  - path: /users/{id}
    method: GET
    description: Get user by ID
```

**Template**: `openapi.yaml.j2`
```yaml
openapi: 3.0.0
info:
  title: {{ service_name }}
  version: {{ service_version }}
paths:
{% for endpoint in endpoints %}
  {{ endpoint.path }}:
    {{ endpoint.method | lower }}:
      summary: {{ endpoint.description }}
      # @PRESERVE_START
      # Add custom endpoint configuration
      # @PRESERVE_END
{% endfor %}
```

### Example 2: Infrastructure as Code

Generate Terraform configurations from environment definitions.

**Data**: `environments.json`
```json
{
  "environments": {
    "staging": {
      "instance_count": 2,
      "instance_type": "t3.small",
      "region": "us-west-2"
    },
    "production": {
      "instance_count": 5,
      "instance_type": "t3.large",
      "region": "us-east-1"
    }
  }
}
```

**Template**: `terraform.tf.j2`
```hcl
{% for env_name, config in environments.items() %}
# {{ env_name | title }} Environment
resource "aws_instance" "{{ env_name }}_servers" {
  count         = {{ config.instance_count }}
  instance_type = "{{ config.instance_type }}"
  ami           = data.aws_ami.{{ env_name }}.id
  
  tags = {
    Name        = "{{ env_name }}-server-${count.index + 1}"
    Environment = "{{ env_name }}"
  }
  
  # @PRESERVE_START
  # Add custom instance configuration for {{ env_name }}
  # @PRESERVE_END
}

{% endfor %}
```

### Example 3: Code Generation

Generate Python data classes from schema definitions.

**Data**: `schema.json`
```json
{
  "models": [
    {
      "name": "User",
      "fields": [
        {"name": "id", "type": "int", "required": true},
        {"name": "email", "type": "str", "required": true},
        {"name": "name", "type": "str", "required": false}
      ]
    },
    {
      "name": "Post", 
      "fields": [
        {"name": "id", "type": "int", "required": true},
        {"name": "title", "type": "str", "required": true},
        {"name": "content", "type": "str", "required": true},
        {"name": "author_id", "type": "int", "required": true}
      ]
    }
  ]
}
```

**Template**: `models.py.j2`
```python
from dataclasses import dataclass
from typing import Optional

{% for model in models %}
@dataclass
class {{ model.name }}:
    """{{ model.name }} model."""
    
{% for field in model.fields %}
    {{ field.name }}: {% if not field.required %}Optional[{% endif %}{{ field.type }}{% if not field.required %}]{% endif %}{% if not field.required %} = None{% endif %}
{% endfor %}

    # @PRESERVE_START
    # Add custom methods for {{ model.name }}
    # @PRESERVE_END

{% endfor %}
```

## Troubleshooting

### Common Issues

#### 1. Template Not Found
```
Error: Template file not found: template.j2
```

**Solution**: Check the `template_dir` path in your configuration:
```yaml
template_dir: "./templates"  # Correct path to template directory
```

#### 2. Token Extraction Failed
```
Warning: Could not extract token 'app_name' from path 'application.name'
```

**Solutions**:
- Verify the key path matches your data structure
- Check if the input file exists and is valid
- Use `python validate_config.py config.yaml` to validate paths

#### 3. Invalid YAML Configuration
```
Error: Invalid YAML syntax: mapping values are not allowed here
```

**Solution**: Check YAML indentation and syntax:
```yaml
# Correct
inputs:
  - path: "data.json"
    tokens:
      - name: "token"
        key: "path"

# Incorrect (indentation issue)
inputs:
- path: "data.json"
  tokens:
    - name: "token"
      key: "path"
```

#### 4. Preservation Markers Not Working
```
Warning: Unmatched preservation marker @PRESERVE_START
```

**Solutions**:
- Ensure every `@PRESERVE_START` has a matching `@PRESERVE_END`
- Use consistent comment style throughout the file
- Don't nest preservation blocks

#### 5. Missing Dependencies
```
ModuleNotFoundError: No module named 'yaml'
```

**Solution**: Install Template Forge which includes all dependencies:
```bash
pip install template-forge
```

### Debug Mode

Enable verbose logging to diagnose issues:

```bash
python -m template_forge config.yaml --verbose
```

This shows:
- Token extraction details
- Template processing steps
- File operations
- Error details

### Validation

Always validate your configuration before running:

```bash
# Validate configuration
python validate_config.py config.yaml

# Validate with strict mode (warnings become errors)
python validate_config.py --strict config.yaml

# Validate multiple files
python validate_config.py examples/*/config.yaml
```

### Getting Help

1. **Check Examples**: Look in the `examples/` directory for working configurations
2. **Read Error Messages**: Template Forge provides detailed error descriptions
3. **Use Validation**: Run `validate_config.py` to catch issues early
4. **Enable Debug Mode**: Use `--verbose` for detailed execution information

### Performance Tips

1. **Minimize Regex Usage**: Regex processing is slower than direct key extraction
2. **Use Specific Paths**: Avoid extracting large objects when you only need specific values
3. **Template Optimization**: Minimize complex Jinja2 logic in templates
4. **File Organization**: Keep templates in a dedicated directory for faster loading

---

## Next Steps

- **Explore Examples**: Check out the `examples/` directory for real-world use cases
- **Advanced Configuration**: Read the [Configuration Reference](configuration.md)
- **Development**: See the [Development Guide](development.md) to extend Template Forge
- **API Integration**: Check the [API Documentation](API.md) for programmatic usage