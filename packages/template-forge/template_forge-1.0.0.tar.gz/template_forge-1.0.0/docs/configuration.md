# Template Forge Configuration Reference

Complete reference for all configuration options in Template Forge `config.yaml` files.

## Table of Contents

- [Configuration File Structure](#configuration-file-structure)
- [Root Level Options](#root-level-options)
- [Input Configuration](#input-configuration)
- [Token Configuration](#token-configuration)
- [Template Configuration](#template-configuration)
- [Static Tokens](#static-tokens)
- [Jinja2 Options](#jinja2-options)
- [Examples](#examples)
- [Validation](#validation)

## Configuration File Structure

Template Forge uses YAML configuration files with the following top-level structure:

```yaml
# Optional: Directory containing template files (default: ".")
template_dir: string

# Optional: Input data sources
inputs:
  - path: string
    tokens: [token_config, ...]

# Optional: Static token values
static_tokens:
  key: value

# Required: Template files to process
templates:
  - template: string
    output: string
    tokens: {key: value}

# Optional: Jinja2 engine configuration  
jinja_options:
  option: value
```

## Root Level Options

### template_dir

**Type**: `string`  
**Default**: `"."`  
**Required**: No

Directory containing Jinja2 template files. Can be absolute or relative to the configuration file.

```yaml
template_dir: "./templates"
template_dir: "/absolute/path/to/templates"
template_dir: "../shared/templates"
```

## Input Configuration

### inputs

**Type**: `array`  
**Required**: No (but either `inputs` or `static_tokens` should be present)

List of input data sources for token extraction.

```yaml
inputs:
  - path: "data.json"
    tokens:
      - name: "app_name"
        key: "application.name"
  - path: "config.yaml"
    tokens:
      - name: "version"
        key: "app.version"
```

#### Input Object Properties

##### path

**Type**: `string`  
**Required**: Yes

Path to the input data file. Can be absolute or relative to the configuration file.

**Supported file formats**:
- `.json` - JSON files
- `.yaml`, `.yml` - YAML files  
- `.xml` - XML files
- `.arxml` - AUTOSAR XML files

```yaml
path: "./data/config.json"
path: "/absolute/path/to/data.yaml"
path: "../shared/data.xml"
```

##### tokens

**Type**: `array`  
**Required**: No

List of tokens to extract from this input file.

## Token Configuration

Each token defines how to extract a value from the input data.

### Basic Token Structure

```yaml
tokens:
  - name: "token_name"        # Required
    key: "path.to.value"      # Required
    regex: "pattern"          # Optional
    transform: "transform"    # Optional
    default: "fallback"       # Optional
```

### Token Properties

#### name

**Type**: `string`  
**Required**: Yes

Unique name for the token. Used in templates as `{{ token_name }}`.

**Rules**:
- Must be unique within the configuration
- Should be valid Python identifier (letters, numbers, underscore)
- Cannot start with a number

```yaml
name: "app_name"
name: "database_host"
name: "feature_list"
```

#### key

**Type**: `string`  
**Required**: Yes

Dot-notation path to the value in the input data structure.

**JSON/YAML Examples**:
```yaml
key: "application.name"           # Simple nested access
key: "database.connections[0]"    # Array index access  
key: "config.servers.web.host"    # Deep nested access
```

**XML Examples**:
```yaml
key: "root.element.child"         # Element hierarchy
key: "element.@attribute"         # Attribute access (use @)
key: "catalog.book[0].title"      # Array access in XML
```

**AUTOSAR Examples**:
```yaml
key: "AUTOSAR.AR-PACKAGES.AR-PACKAGE.SHORT-NAME"
key: "ECU-INSTANCE.SW-VERSION"
```

#### regex

**Type**: `string`  
**Required**: No

Regular expression pattern to extract part of the value. Uses the first capture group if present, otherwise the entire match.

```yaml
# Extract version number without 'v' prefix
key: "version"
regex: "v(.+)"              # "v1.2.3" -> "1.2.3"

# Extract domain from email
key: "email"  
regex: "@(.+)$"             # "user@example.com" -> "example.com"

# Extract port from URL
key: "database_url"
regex: ":(\d+)/"            # "postgres://host:5432/db" -> "5432"
```

#### transform

**Type**: `string`  
**Required**: No

Transformation to apply to the extracted value.

**Available transformations**:

| Transform | Description | Example |
|-----------|-------------|---------|
| `upper` | Convert to uppercase | `hello` → `HELLO` |
| `lower` | Convert to lowercase | `HELLO` → `hello` |
| `capitalize` | Capitalize first letter | `hello` → `Hello` |
| `strip` | Remove leading/trailing whitespace | `" text "` → `"text"` |
| `int` | Convert to integer | `"42"` → `42` |
| `float` | Convert to float | `"3.14"` → `3.14` |
| `bool` | Convert to boolean | `"true"` → `True` |
| `snake_case` | Convert to snake_case | `MyClass` → `my_class` |
| `camel_case` | Convert to camelCase | `my_var` → `myVar` |
| `pascal_case` | Convert to PascalCase | `my_class` → `MyClass` |
| `kebab_case` | Convert to kebab-case | `MyClass` → `my-class` |

```yaml
# Convert to uppercase
- name: "app_name_upper"
  key: "app.name"
  transform: "upper"

# Convert class name to snake_case
- name: "class_file"
  key: "class.name"
  transform: "snake_case"

# Convert string to integer
- name: "port_number"
  key: "server.port"
  transform: "int"
```

#### default

**Type**: `string`  
**Required**: No

Default value to use if the key path is not found or extraction fails.

```yaml
- name: "debug_mode"
  key: "app.debug"
  default: "false"

- name: "timeout"
  key: "config.timeout"
  default: "30"
  transform: "int"
```

## Template Configuration

### templates

**Type**: `array`  
**Required**: Yes

List of templates to process and their output destinations.

```yaml
templates:
  - template: "config.ini.j2"
    output: "./output/config.ini"
  - template: "README.md.j2"
    output: "./README.md"
    tokens:
      template_specific: "value"
```

#### Template Object Properties

##### template

**Type**: `string`  
**Required**: Yes

Path to the Jinja2 template file, relative to `template_dir`.

```yaml
template: "config.ini.j2"
template: "docker/Dockerfile.j2"
template: "docs/README.md.j2"
```

##### output

**Type**: `string`  
**Required**: Yes

Path where the generated file should be written. Can be absolute or relative to the configuration file.

```yaml
output: "./generated/config.ini"
output: "/absolute/path/to/output.txt"
output: "../shared/generated.md"
```

##### tokens

**Type**: `object`  
**Required**: No

Template-specific tokens that override global tokens for this template only.

```yaml
templates:
  - template: "app.conf.j2"
    output: "./prod-app.conf"
    tokens:
      environment: "production"
      debug: false
  - template: "app.conf.j2" 
    output: "./dev-app.conf"
    tokens:
      environment: "development"
      debug: true
```

## Static Tokens

### static_tokens

**Type**: `object`  
**Required**: No

Fixed values that don't require extraction from input files.

```yaml
static_tokens:
  company: "ACME Corporation"
  year: 2025
  version: "1.0.0"
  author:
    name: "John Doe"
    email: "john@acme.com"
  features:
    - "authentication"
    - "logging"
    - "monitoring"
```

**Usage in templates**:
```jinja2
Generated by {{ company }}
Copyright {{ year }}
Version: {{ version }}

Author: {{ author.name }} <{{ author.email }}>

Features:
{% for feature in features %}
- {{ feature }}
{% endfor %}
```

## Jinja2 Options

### jinja_options

**Type**: `object`  
**Required**: No

Configuration options for the Jinja2 template engine.

```yaml
jinja_options:
  trim_blocks: true
  lstrip_blocks: true
  keep_trailing_newline: false
  block_start_string: "<%"
  block_end_string: "%>"
  variable_start_string: "<<%"
  variable_end_string: "%>>"
```

#### Available Options

##### trim_blocks

**Type**: `boolean`  
**Default**: `true`

Remove the first newline after a block (e.g., `{% if %}`, `{% for %}`).

```yaml
trim_blocks: true   # Recommended for cleaner output
trim_blocks: false  # Preserve all newlines
```

##### lstrip_blocks

**Type**: `boolean`  
**Default**: `true`

Strip leading spaces and tabs from the start of a line to a block.

```yaml
lstrip_blocks: true   # Remove indentation before blocks
lstrip_blocks: false  # Preserve indentation
```

##### keep_trailing_newline

**Type**: `boolean`  
**Default**: `true`

Preserve the trailing newline when rendering templates.

```yaml
keep_trailing_newline: true   # Keep final newline
keep_trailing_newline: false  # Remove final newline
```

##### Custom Delimiters

Change the delimiters used for Jinja2 syntax:

```yaml
# Change block delimiters
block_start_string: "<%"      # Default: "{%"
block_end_string: "%>"        # Default: "%}"

# Change variable delimiters  
variable_start_string: "<<%"  # Default: "{{"
variable_end_string: "%>>"    # Default: "}}"

# Change comment delimiters
comment_start_string: "<#"    # Default: "{#"
comment_end_string: "#>"      # Default: "#}"
```

**Template with custom delimiters**:
```
<% if app_name %>
Application: <<% app_name %>>
<% endif %>

<# This is a comment #>
```

## Examples

### Complete Configuration Example

```yaml
# Template directory
template_dir: "./templates"

# Input data sources
inputs:
  # Application configuration
  - path: "./data/app.json"
    tokens:
      - name: "app_name"
        key: "application.name"
      - name: "app_version"
        key: "application.version"
      - name: "app_description"
        key: "application.description"
      
  # Database configuration
  - path: "./data/database.yaml"
    tokens:
      - name: "db_host"
        key: "database.host"
      - name: "db_port"
        key: "database.port"
        transform: "int"
      - name: "db_ssl"
        key: "database.ssl"
        transform: "bool"
        default: "true"
      
  # Feature configuration from XML
  - path: "./data/features.xml"
    tokens:
      - name: "features"
        key: "configuration.features.feature"
      - name: "license_type"
        key: "configuration.@license"

# Static values
static_tokens:
  company: "ACME Corporation"
  generated_date: "2025-09-15"
  copyright_year: 2025
  build_info:
    builder: "Template Forge"
    version: "1.0.0"

# Templates to process
templates:
  # Application configuration
  - template: "app.conf.j2"
    output: "./output/app.conf"
    
  # Docker configuration
  - template: "docker-compose.yml.j2"
    output: "./output/docker-compose.yml"
    tokens:
      environment: "production"
      replicas: 3
      
  # Development Docker configuration
  - template: "docker-compose.yml.j2"
    output: "./output/docker-compose.dev.yml"
    tokens:
      environment: "development"
      replicas: 1
      
  # Documentation
  - template: "README.md.j2"
    output: "./README.md"

# Jinja2 configuration
jinja_options:
  trim_blocks: true
  lstrip_blocks: true
  keep_trailing_newline: true
```

### Multi-Environment Configuration

```yaml
template_dir: "./templates"

inputs:
  - path: "./environments.json"
    tokens:
      - name: "environments"
        key: "environments"

static_tokens:
  project_name: "MyProject"
  generated_by: "Template Forge"

templates:
  # Generate config for each environment
  - template: "app-config.j2"
    output: "./configs/production.conf"
    tokens:
      current_env: "production"
      debug: false
      
  - template: "app-config.j2"
    output: "./configs/staging.conf"
    tokens:
      current_env: "staging"
      debug: true
      
  - template: "app-config.j2"
    output: "./configs/development.conf"
    tokens:
      current_env: "development"
      debug: true
```

### Complex Data Extraction

```yaml
inputs:
  - path: "./microservices.yaml"
    tokens:
      # Extract service names as array
      - name: "service_names"
        key: "services"
        
      # Extract specific service configuration
      - name: "api_gateway_port"
        key: "services.api-gateway.port"
        transform: "int"
        
      # Extract database configuration with fallback
      - name: "primary_db"
        key: "databases.primary.host"
        default: "localhost"
        
      # Extract version with regex
      - name: "major_version"
        key: "version"
        regex: "^(\d+)\."
        
      # Transform service names to file names
      - name: "service_configs"
        key: "services"
        transform: "snake_case"

templates:
  # Generate individual service configs
  - template: "service.conf.j2"
    output: "./configs/{{ service_name | snake_case }}.conf"
```

## Validation

### Configuration Validation

Always validate your configuration before running Template Forge:

```bash
# Validate single configuration
python validate_config.py config.yaml

# Validate with strict mode (warnings become errors)
python validate_config.py --strict config.yaml

# Validate multiple configurations
python validate_config.py configs/*.yaml

# Verbose validation output
python validate_config.py --verbose config.yaml
```

### Common Validation Errors

#### Missing Required Fields
```yaml
# Error: Missing required field 'templates'
inputs:
  - path: "data.json"
    tokens:
      - name: "test"
        key: "value"
# templates: []  # This is required!
```

#### Invalid File Paths
```yaml
# Error: Input file not found
inputs:
  - path: "nonexistent.json"  # File doesn't exist
    tokens: [...]
```

#### Duplicate Token Names
```yaml
# Error: Duplicate token name 'app_name'
tokens:
  - name: "app_name"
    key: "application.name"
  - name: "app_name"  # Duplicate!
    key: "app.title"
```

#### Invalid Data Types
```yaml
# Error: 'template_dir' must be a string
template_dir: 123  # Should be string

# Error: 'inputs' must be a list
inputs: "invalid"  # Should be array

# Error: 'static_tokens' must be an object
static_tokens: ["invalid"]  # Should be object
```

### Best Practices

1. **Always validate** configuration files before use
2. **Use meaningful token names** that describe their purpose
3. **Provide default values** for optional configuration
4. **Organize tokens logically** by grouping related extractions
5. **Use appropriate transformations** to ensure correct data types
6. **Document complex regex patterns** with comments
7. **Test extraction paths** with sample data before deploying

---

For more information, see:
- [User Guide](user-guide.md) - Complete usage instructions
- [Development Guide](development.md) - Contributing and extending
- [API Reference](API.md) - Python API documentation