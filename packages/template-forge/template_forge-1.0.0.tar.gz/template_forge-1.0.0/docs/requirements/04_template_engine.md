# Template Engine - Requirements

## 1. Template Format

**REQ-TPL-001**: The system shall use Jinja2 as the template engine.

**REQ-TPL-002**: Template files shall have a `.j2` extension by convention (but not enforced).

**REQ-TPL-003**: Templates shall support the full Jinja2 syntax and features.

**REQ-TPL-004**: Templates shall have access to all extracted and static tokens as variables.

## 2. Template Processing

**REQ-TPL-010**: The system shall load templates from the file system using `FileSystemLoader`.

**REQ-TPL-011**: The system shall resolve template paths relative to `template_dir` if specified.

**REQ-TPL-012**: If `template_dir` is not specified, paths shall be resolved relative to the configuration file.

**REQ-TPL-013**: The system shall process each template independently.

**REQ-TPL-014**: The system shall continue processing remaining templates if one template fails.

**REQ-TPL-015**: The system shall log errors for template processing failures including template name and error details.

## 3. Jinja2 Features

**REQ-TPL-020**: Templates shall support Jinja2 variable interpolation: `{{ variable_name }}`

**REQ-TPL-021**: Templates shall support Jinja2 control structures:
- `{% if condition %}...{% endif %}`
- `{% for item in list %}...{% endfor %}`
- `{% while condition %}...{% endwhile %}`

**REQ-TPL-022**: Templates shall support Jinja2 filters: `{{ variable | filter }}`

**REQ-TPL-023**: Templates shall support Jinja2 tests: `{% if variable is defined %}`

**REQ-TPL-024**: Templates shall support Jinja2 macros and template inheritance.

**REQ-TPL-025**: Templates shall support Jinja2 whitespace control.

## 4. Built-in Filters

**REQ-TPL-030**: The system shall provide all standard Jinja2 built-in filters:
- String filters: `upper`, `lower`, `title`, `capitalize`, `trim`, `replace`
- List filters: `join`, `sort`, `reverse`, `first`, `last`, `length`
- Number filters: `abs`, `round`, `int`, `float`
- Other filters: `default`, `escape`, `safe`, `format`

**REQ-TPL-031**: The system shall support the `regex_replace` filter for string manipulation.

**REQ-TPL-032**: Custom filters can be added via the Jinja2 environment configuration.

## 5. Template Variables

**REQ-TPL-040**: All extracted tokens shall be available as template variables.

**REQ-TPL-041**: All static tokens shall be available as template variables.

**REQ-TPL-042**: Template-specific tokens shall override global tokens with the same name.

**REQ-TPL-043**: Variables shall preserve their data types (strings, numbers, lists, dictionaries).

**REQ-TPL-044**: Nested structures shall be accessible using dot notation or bracket notation.

**REQ-TPL-045**: Undefined variables shall trigger a Jinja2 undefined error.

## 6. Output Generation

**REQ-TPL-050**: The system shall write rendered template output to the specified output file.

**REQ-TPL-051**: The system shall create output directories if they don't exist.

**REQ-TPL-052**: The system shall overwrite existing output files without warning.

**REQ-TPL-053**: The system shall preserve file encoding (UTF-8) in output files.

**REQ-TPL-054**: The system shall handle code preservation markers during output generation.

## 7. Jinja2 Environment Configuration

**REQ-TPL-060**: The system shall support configuring the following Jinja2 environment options:
- `trim_blocks`: Remove first newline after block
- `lstrip_blocks`: Strip leading whitespace before blocks  
- `keep_trailing_newline`: Preserve trailing newline

**REQ-TPL-061**: Default Jinja2 options shall be used if not specified in configuration.

**REQ-TPL-062**: Custom Jinja2 options shall apply to all template processing.

## 8. Template Errors

**REQ-TPL-070**: The system shall catch and report Jinja2 syntax errors with template name and line number.

**REQ-TPL-071**: The system shall catch and report undefined variable errors.

**REQ-TPL-072**: The system shall catch and report template not found errors.

**REQ-TPL-073**: Template errors shall not terminate the entire process; other templates shall continue processing.

## 9. Comments

**REQ-TPL-080**: Templates shall support Jinja2 comments: `{# comment #}`

**REQ-TPL-081**: Comments shall not appear in generated output.

**REQ-TPL-082**: Multi-line comments shall be supported.

## 10. Whitespace Control

**REQ-TPL-090**: Templates shall support Jinja2 whitespace control using `-`:
- `{{- variable }}`: Strip whitespace before
- `{{ variable -}}`: Strip whitespace after
- `{%- if -%}`: Strip whitespace around control structures

**REQ-TPL-091**: Global whitespace behavior shall be configurable via `trim_blocks` and `lstrip_blocks`.

## 11. Template Includes

**REQ-TPL-100**: Templates shall support including other templates: `{% include 'header.j2' %}`

**REQ-TPL-101**: Included templates shall have access to the same variables as the parent template.

**REQ-TPL-102**: Include paths shall be resolved relative to `template_dir`.

## 12. Template Inheritance

**REQ-TPL-110**: Templates shall support inheritance using `{% extends 'base.j2' %}`

**REQ-TPL-111**: Child templates shall be able to override parent blocks: `{% block name %}...{% endblock %}`

**REQ-TPL-112**: Multiple levels of inheritance shall be supported.

## 14. Template Validation

**REQ-TPL-120**: The system shall provide a `--validate-templates` flag to check template syntax without generation.

**REQ-TPL-121**: Template validation shall check for:
- Valid Jinja2 syntax
- Undefined variable references (with warnings, not errors)
- Template file existence
- Include/extends references validity

**REQ-TPL-122**: Validation errors shall report:
- Template file path
- Line number (if applicable)
- Error type and description
- Suggested fixes when possible

**REQ-TPL-123**: Template validation shall use the actual token context from configuration to detect undefined variables.

**REQ-TPL-124**: Validation shall support a "strict" mode that treats undefined variables as errors.

**REQ-TPL-125**: Validation shall check circular includes/extends references.

**REQ-TPL-126**: Validation shall verify that all required blocks are defined in child templates.

**REQ-TPL-127**: Validation results shall be displayed in a clear, actionable format:
```
✓ templates/main.cpp.j2 - OK
✗ templates/header.hpp.j2:15 - Undefined variable 'module_version'
  Suggestion: Add 'module_version' to static_tokens or inputs
✗ templates/config.yaml.j2:8 - Template not found: 'base_config.j2'
```

## 15. Conditional Template Generation

**REQ-TPL-130**: The system shall support conditional template generation based on token values.

**REQ-TPL-131**: Each template entry in configuration shall support an optional `when` condition:
```yaml
templates:
  - template: docker.yml.j2
    output: docker-compose.yml
    when: "deployment_type == 'docker'"
```

**REQ-TPL-132**: The `when` condition shall be evaluated as a Jinja2 expression with access to all tokens.

**REQ-TPL-133**: Supported condition operators:
- Equality: `==`, `!=`
- Comparison: `<`, `>`, `<=`, `>=`
- Logical: `and`, `or`, `not`
- Membership: `in`, `not in`
- Tests: `is defined`, `is not defined`

**REQ-TPL-134**: If a `when` condition evaluates to `false`, the template shall be skipped silently.

**REQ-TPL-135**: Skipped templates shall be logged at DEBUG level.

**REQ-TPL-136**: Templates without a `when` condition shall always be generated.

**REQ-TPL-137**: Condition evaluation errors shall be reported clearly with the template name and condition.

**REQ-TPL-138**: Example conditional template configurations:
```yaml
templates:
  # Generate only for production
  - template: prod-config.j2
    output: config/production.yaml
    when: "environment == 'production'"
  
  # Generate if feature flag is enabled
  - template: feature.cpp.j2
    output: src/feature.cpp
    when: "features.advanced_mode is defined and features.advanced_mode"
  
  # Generate based on platform
  - template: linux-specific.sh.j2
    output: scripts/setup.sh
    when: "platform in ['linux', 'unix']"
  
  # Complex condition
  - template: optimized.cpp.j2
    output: src/optimized.cpp
    when: "optimization_level >= 2 and not debug_mode"
```

## 16. Examples

### Basic Variable Interpolation
```jinja2
# Application: {{ app_name }}
Version: {{ version }}
Author: {{ author }}
```

### Loops and Conditionals
```jinja2
{% for module in modules %}
## Module: {{ module.name }}
Type: {{ module.type }}
{% if module.enabled %}
Status: ENABLED
{% else %}
Status: DISABLED
{% endif %}
{% endfor %}
```

### Filters
```jinja2
# {{ app_name | upper }}
Version: {{ version | default('1.0.0') }}
Modules: {{ module_names | join(', ') }}
```

### Nested Data Access
```jinja2
Database: {{ config.database.host }}:{{ config.database.port }}
User: {{ config.database.credentials.username }}
```

### Whitespace Control
```jinja2
{%- for item in items %}
  - {{ item }}
{%- endfor %}
```

### Template Inheritance
Base template (`base.py.j2`):
```jinja2
#!/usr/bin/env python3
"""{{ description }}"""

{% block imports %}
import sys
{% endblock %}

{% block main %}
def main():
    pass
{% endblock %}

if __name__ == "__main__":
    main()
```

Child template (`app.py.j2`):
```jinja2
{% extends 'base.py.j2' %}

{% block imports %}
{{ super() }}
import json
import yaml
{% endblock %}

{% block main %}
def main():
    print("{{ app_name }}")
    print("Version: {{ version }}")
{% endblock %}
```
