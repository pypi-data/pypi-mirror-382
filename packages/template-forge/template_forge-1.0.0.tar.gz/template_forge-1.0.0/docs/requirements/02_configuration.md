# Configuration File - Requirements

## 1. Configuration File Format

**REQ-CFG-001**: The syste**REQ-CFG-034**: Example showing coexistence of static and namespaced tokens:
```yaml
# Configuration showing coexistence
inputs:
  - path: project.json
    namespace: project        # Creates project.version, project.name, etc.
  - path: database.xml
    namespace: database       # Creates database.host, database.port, etc.

static_tokens:
  # Hierarchical static tokens
  company:
    name: "ACME Corp"
    year: 2025
  build:
    type: "release"
    optimization: "O3"
  # Flat static tokens
  author: "John Doe"
  license: "MIT"

# Template usage - all coexist:
# {{ project.version }}    - from namespaced input
# {{ database.host }}      - from namespaced input
# {{ company.name }}       - from static hierarchy
# {{ author }}             - from flat static token
```

## 5. Template ConfigurationL format for configuration files.

**REQ-CFG-002**: The configuration file shall have a `.yaml` or `.yml` extension.

**REQ-CFG-003**: The system shall validate the configuration file syntax before processing.

**REQ-CFG-004**: The system shall provide clear error messages for invalid YAML syntax including line numbers.

## 2. Configuration Structure

**REQ-CFG-010**: The configuration file shall support the following top-level keys:
- `inputs`: List of input data files and token extraction rules
- `static_tokens`: Dictionary of static key-value pairs
- `templates`: List of templates to process
- `template_dir`: Base directory for template files
- `jinja_options`: Jinja2 environment configuration

**REQ-CFG-011**: For data extraction, at least one of the following shall be defined:
- `inputs`: To extract data from external files
- `static_tokens`: To provide static key-value pairs

**REQ-CFG-012**: For output generation, at least one of the following shall be defined:
- `templates`: Explicit list of templates to process
- `template_dir`: Directory containing template files to discover

**REQ-CFG-013**: The configuration file shall define at least one data extraction mechanism (REQ-CFG-011) AND at least one output generation mechanism (REQ-CFG-012).

**REQ-CFG-014**: The system shall validate configuration structure and report a clear error if:
- Neither `inputs` nor `static_tokens` are defined (no data source)
- Neither `templates` nor `template_dir` are defined (no output target)
- Both data extraction and output generation requirements are not met

## 3. Input Configuration

**REQ-CFG-020**: Each input entry shall specify:
- `path` (required): Relative or absolute path to the input file
- `namespace` (required): Hierarchical namespace for extracted tokens to prevent collisions
- `tokens` (optional): List of token extraction rules
- `format` (optional): Explicit format override (json, yaml, xml, arxml)

**REQ-CFG-021**: The `namespace` shall organize tokens hierarchically to avoid collisions:
- All tokens extracted from an input file shall be placed under the specified namespace
- Namespaces create a dictionary structure: `namespace.token_name`
- Namespaces prevent accidental token name collisions between different input files

**REQ-CFG-022**: If no `tokens` are specified for an input, all top-level keys shall be extracted under the namespace.

**REQ-CFG-023**: Each token extraction rule shall specify:
- `name` (required): Name of the token to create (will be prefixed by namespace)
- `key` (required): Dot-notation path to extract data from the input file
- `regex` (optional): Regular expression filter to apply
- `transform` (optional): Transformation to apply (upper, lower, title, capitalize)

**REQ-CFG-024**: Token extraction keys shall support:
- Dot notation for nested objects: `project.metadata.version`
- Array indexing: `users[0].name`
- Wildcard for all array elements: `modules[*].name`
- Object extraction: `config.database.*`

**REQ-CFG-025**: Example input configuration with namespaces:
```yaml
inputs:
  - path: project.json
    namespace: project
    tokens:
      - name: version         # Accessible as: project.version
        key: application.version
      - name: name           # Accessible as: project.name
        key: application.name

  - path: library.json
    namespace: library
    tokens:
      - name: version         # Accessible as: library.version (no collision!)
        key: library.version
      - name: name           # Accessible as: library.name
        key: library.name
```

## 4. Static Tokens

**REQ-CFG-030**: The `static_tokens` section shall define key-value pairs that are available to all templates.

**REQ-CFG-031**: Static token values shall support strings, numbers, booleans, lists, and dictionaries.

**REQ-CFG-032**: Static tokens may use hierarchical structure (nested dictionaries) to organize related values.

**REQ-CFG-033**: Static tokens and namespaced input tokens coexist peacefully in the template context:
- Static tokens are available at the root level or in their own hierarchy: `{{ author }}`, `{{ company.name }}`
- Namespaced input tokens are available under their namespace: `{{ project.version }}`, `{{ database.host }}`
- They do not collide unless they use the exact same path (e.g., both define `company.name`)

**REQ-CFG-034**: Example showing coexistence of static and namespaced tokens:
```yaml
static_tokens:
  company:
    name: "ACME Corp"
    year: 2025
  build:
    type: "release"
    optimization: "O3"
  # Flat tokens for simple values
  author: "John Doe"
  license: "MIT"
```

## 5. Template Configuration

**REQ-CFG-040**: Each template entry shall specify:
- `template` (required): Path to the Jinja2 template file (relative to `template_dir`)
- `output` (required): Path for the generated output file
- `tokens` (optional): Additional tokens specific to this template

**REQ-CFG-041**: Template-specific tokens shall override global and static tokens with the same name.

**REQ-CFG-042**: Output paths shall support directory creation if they don't exist.

**REQ-CFG-043**: Template paths shall be resolved relative to `template_dir` if specified, otherwise relative to the configuration file location.

## 6. Jinja2 Options

**REQ-CFG-050**: The `jinja_options` section shall support standard Jinja2 environment options:
- `trim_blocks` (boolean): Remove first newline after block
- `lstrip_blocks` (boolean): Strip leading spaces before blocks
- `keep_trailing_newline` (boolean): Keep trailing newline in templates

**REQ-CFG-051**: If `jinja_options` is not specified, the system shall use default Jinja2 settings.

## 7. Path Resolution

**REQ-CFG-060**: Relative input file paths shall be resolved relative to the configuration file directory.

**REQ-CFG-061**: Absolute paths shall be used as-is without modification.

**REQ-CFG-062**: Template directory paths shall be resolved relative to the configuration file directory.

**REQ-CFG-063**: Output file paths shall be resolved relative to the current working directory.

## 8. Validation

**REQ-CFG-070**: The system shall validate that all referenced input files exist before processing.

**REQ-CFG-071**: The system shall validate that all template files exist before processing.

**REQ-CFG-072**: The system shall validate that token extraction keys are valid dot-notation syntax.

**REQ-CFG-073**: The system shall log warnings for tokens that cannot be extracted from input files.

**REQ-CFG-074**: The system shall detect and log warnings for token name collisions only between:
- Static tokens and namespaced input tokens (if they share the same top-level key)
- Template-specific tokens and any other tokens with the same full path

**REQ-CFG-075**: Token namespace collisions shall be prevented by design:
- Each input file must specify a unique `namespace`
- Tokens from different inputs are automatically isolated by their namespace
- Collision detection is only needed for static tokens and template-specific overrides

**REQ-CFG-076**: If a collision is detected, the system shall log a warning with:
- Token path that is being overridden
- Source of the original value
- Source of the overriding value
- Final value that will be used

**REQ-CFG-077**: Example collision warning message:
```
WARNING: Token collision detected
  Token: 'project.version'
  Original: '1.0.0' from project namespace (project.json)
  Override: '2.0.0' from template-specific tokens (main.cpp.j2)
  Result: Using '2.0.0' for this template
```

## 9. Configuration Discovery

**REQ-CFG-080**: The system shall automatically search for a configuration file if none is specified on the command line.

**REQ-CFG-081**: Configuration file discovery shall search in the following order:
1. `config.yaml` in current directory
2. `config.yml` in current directory
3. `.template-forge.yaml` in current directory
4. `.template-forge.yml` in current directory
5. `template-forge.yaml` in current directory
6. `template-forge.yml` in current directory

**REQ-CFG-082**: The system shall use the first configuration file found during discovery.

**REQ-CFG-083**: If no configuration file is found, the system shall display an error message suggesting to create one or use `--init`.

**REQ-CFG-084**: The system shall log which configuration file was found and used (at DEBUG level).

**REQ-CFG-085**: Configuration discovery shall be skipped if the `--config` flag is explicitly provided.

## 10. Smart Defaults

**REQ-CFG-090**: The system shall provide sensible default values for optional configuration keys:
- `template_dir`: Current directory (`.`)
- `jinja_options.trim_blocks`: `true`
- `jinja_options.lstrip_blocks`: `true`
- `jinja_options.keep_trailing_newline`: `true`

**REQ-CFG-091**: When no `inputs` are specified, the system shall operate in "static-only" mode using only `static_tokens`.

**REQ-CFG-092**: When no `templates` are specified but template files exist in `template_dir`, the system shall warn the user.

**REQ-CFG-093**: If an input file has no `tokens` specified, the system shall extract all top-level keys automatically.

**REQ-CFG-094**: If an input file has no `format` specified, the system shall auto-detect format from file extension.

**REQ-CFG-095**: Smart defaults shall be logged at DEBUG level so users can see what values are being used.

## 11. Configuration Includes

**REQ-CFG-100**: The configuration file shall support an `includes` key to reference other YAML files.

**REQ-CFG-101**: Include syntax shall be: `includes: [file1.yaml, file2.yaml]` or `includes: file.yaml`

**REQ-CFG-102**: Included files shall be merged into the main configuration with the following rules:
- Lists are concatenated (inputs, templates)
- Dictionaries are merged (static_tokens, jinja_options)
- Main config values override included values for conflicting keys

**REQ-CFG-103**: Include paths shall be resolved relative to the file containing the `includes` directive.

**REQ-CFG-104**: The system shall support nested includes (included files can include other files).

**REQ-CFG-105**: The system shall detect and prevent circular includes (A includes B, B includes A).

**REQ-CFG-106**: The system shall log all included files at DEBUG level.

**REQ-CFG-107**: If an included file does not exist, the system shall fail with a clear error message.

**REQ-CFG-108**: Included files shall use the same YAML structure as the main configuration file.

**REQ-CFG-109**: Include processing shall happen before validation to ensure the merged configuration is validated as a whole.

**REQ-CFG-110**: Example include usage:
```yaml
# config.yaml
includes:
  - common-tokens.yaml
  - project-specific.yaml

templates:
  - template: main.cpp.j2
    output: src/main.cpp
```

```yaml
# common-tokens.yaml
static_tokens:
  company: "ACME Corp"
  year: 2025
  license: "MIT"
```

## 12. Example Configuration

```yaml
# Input data sources with namespaces to prevent collisions
inputs:
  - path: data.json
    namespace: app            # All tokens under 'app' namespace
    tokens:
      - name: name            # Accessible as: app.name
        key: application.name
      - name: version         # Accessible as: app.version
        key: application.version
      - name: modules         # Accessible as: app.modules
        key: modules[*]

  - path: config.xml
    namespace: database       # All tokens under 'database' namespace
    format: xml
    tokens:
      - name: host           # Accessible as: database.host
        key: configuration.host
      - name: port           # Accessible as: database.port
        key: configuration.port
      - name: config         # Accessible as: database.config
        key: configuration.*

# Static values (hierarchical structure)
static_tokens:
  build:
    author: "John Doe"
    year: 2025
    license: "MIT"
  company:
    name: "ACME Corp"
    website: "https://acme.com"

# Template directory
template_dir: ./templates

# Jinja2 options
jinja_options:
  trim_blocks: true
  lstrip_blocks: true
  keep_trailing_newline: true

# Output templates
templates:
  - template: app.py.j2
    output: src/app.py
    tokens:
      # Template-specific override (optional)
      custom_var: "template-specific-value"
  
  - template: README.md.j2
    output: README.md

# Template usage examples:
# {{ app.name }} - Application name
# {{ app.version }} - Application version
# {{ app.modules[0] }} - First module
# {{ database.host }} - Database host
# {{ database.port }} - Database port
# {{ build.author }} - Build author from static tokens
# {{ company.name }} - Company name from static tokens
```
