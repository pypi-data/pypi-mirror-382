# Conditional Template Generation Feature

## Overview

Template Forge now supports conditional template generation using the `when` clause in template configurations. This allows you to selectively generate templates based on runtime conditions evaluated using Jinja2 expressions.

## Implementation Summary

**Requirements Covered**: REQ-TPL-130 through REQ-TPL-138

**Feature**: Templates can be conditionally generated based on token values using Jinja2 expressions.

## How It Works

When processing templates, Template Forge now:
1. Checks if a template has a `when` condition defined
2. Evaluates the condition as a Jinja2 expression using the available tokens
3. Skips the template if the condition evaluates to false
4. Logs the skip reason at DEBUG level for transparency

## Configuration Syntax

Add a `when` field to any template configuration:

```yaml
templates:
  # Always generated - no condition
  - template: always.j2
    output: output/always.txt
  
  # Only generated when enable_feature is true
  - template: feature.j2
    output: output/feature.txt
    when: "enable_feature == true"
  
  # Only generated for production environment
  - template: production.j2
    output: output/production.txt
    when: "environment == 'production'"
  
  # Complex condition with multiple operators
  - template: complex.j2
    output: output/complex.txt
    when: "version >= 2 and platform == 'linux'"
```

## Supported Operators

All Jinja2 comparison and logical operators are supported:

### Comparison Operators
- `==` - Equal to
- `!=` - Not equal to
- `<` - Less than
- `>` - Greater than
- `<=` - Less than or equal to
- `>=` - Greater than or equal to

### Logical Operators
- `and` - Logical AND
- `or` - Logical OR
- `not` - Logical NOT

### Membership Operators
- `in` - Check if value is in list
- `not in` - Check if value is not in list

### Jinja2 Tests
- `is defined` - Check if variable exists
- `is undefined` - Check if variable doesn't exist
- `is none` - Check if variable is None
- Other Jinja2 built-in tests

## Examples

### Example 1: Environment-Based Generation

```yaml
static_tokens:
  environment: "development"

templates:
  # Generated in all environments
  - template: common-config.j2
    output: config/common.yaml
  
  # Only in development
  - template: dev-config.j2
    output: config/dev.yaml
    when: "environment == 'development'"
  
  # Only in production
  - template: prod-config.j2
    output: config/prod.yaml
    when: "environment == 'production'"
```

### Example 2: Feature Flags

```yaml
static_tokens:
  enable_docker: true
  enable_kubernetes: false
  enable_monitoring: true

templates:
  - template: app.py
    output: src/app.py
  
  - template: dockerfile.j2
    output: Dockerfile
    when: "enable_docker"
  
  - template: k8s-deployment.yaml.j2
    output: k8s/deployment.yaml
    when: "enable_kubernetes"
  
  - template: monitoring-config.yaml.j2
    output: monitoring/config.yaml
    when: "enable_monitoring"
```

### Example 3: Version-Based Generation

```yaml
inputs:
  - path: project.json
    namespace: project
    tokens:
      - name: version
        key: version

templates:
  - template: readme.md.j2
    output: README.md
  
  - template: legacy-support.js.j2
    output: src/legacy.js
    when: "project.version < 2"
  
  - template: modern-features.js.j2
    output: src/modern.js
    when: "project.version >= 2"
```

### Example 4: Complex Conditions

```yaml
static_tokens:
  platform: "linux"
  arch: "x64"
  optimization_level: 2

templates:
  - template: optimized-build.sh.j2
    output: scripts/build.sh
    when: "platform in ['linux', 'darwin'] and optimization_level >= 2"
  
  - template: debug-build.sh.j2
    output: scripts/debug-build.sh
    when: "optimization_level < 2 or arch == 'arm'"
```

## Logging

When templates are skipped due to unmet conditions:

```
DEBUG - Skipping template 'feature.j2' (condition 'enable_feature == true' not met)
```

When condition evaluation fails:

```
WARNING - Failed to evaluate condition 'invalid syntax' for template 'template.j2': <error>
WARNING - Skipping template 'template.j2' due to condition evaluation error
```

## Best Practices

1. **Keep Conditions Simple**: Use clear, readable conditions
2. **Use Boolean Tokens**: Prefer `enable_feature` over `enable_feature == true`
3. **Document Conditions**: Add comments explaining why templates are conditional
4. **Test Both Paths**: Verify templates are generated/skipped correctly
5. **Use Descriptive Token Names**: Make condition intent clear

## Error Handling

- **Invalid Syntax**: If a `when` expression has invalid syntax, the template is skipped and a warning is logged
- **Undefined Variables**: Missing tokens in conditions cause the template to be skipped
- **Safe Default**: On any error, templates are skipped rather than generated incorrectly

## Testing

The feature includes comprehensive tests:

- `test_REQ_TPL_130_conditional_template_generation` - Basic functionality
- `test_REQ_TPL_131_when_condition_syntax` - Optional `when` field
- `test_REQ_TPL_132_when_condition_evaluation` - Jinja2 expression evaluation
- `test_REQ_TPL_133_condition_operators` - Operator support
- `test_REQ_TPL_134_false_condition_skips_template` - Skip behavior
- Edge cases tests in `test_edge_cases.py`

## Real-World Use Cases

### Use Case 1: Multi-Environment Deployments

Generate different configurations for dev, staging, and production:

```yaml
static_tokens:
  environment: "{{ ENV | default('development') }}"

templates:
  - template: database-config.yaml.j2
    output: config/database.yaml
    when: "environment in ['development', 'staging']"
  
  - template: database-prod.yaml.j2
    output: config/database.yaml
    when: "environment == 'production'"
```

### Use Case 2: Progressive Feature Rollout

Control which features are included in builds:

```yaml
static_tokens:
  features:
    analytics: true
    experimental_ui: false
    beta_api: true

templates:
  - template: analytics-module.py.j2
    output: src/analytics.py
    when: "features.analytics"
  
  - template: experimental-ui.tsx.j2
    output: src/ui/experimental.tsx
    when: "features.experimental_ui"
  
  - template: beta-api.py.j2
    output: src/api/beta.py
    when: "features.beta_api"
```

### Use Case 3: Platform-Specific Files

Generate platform-specific build scripts or configurations:

```yaml
static_tokens:
  target_platform: "linux"

templates:
  - template: build-linux.sh.j2
    output: scripts/build.sh
    when: "target_platform == 'linux'"
  
  - template: build-windows.bat.j2
    output: scripts/build.bat
    when: "target_platform == 'windows'"
  
  - template: build-macos.sh.j2
    output: scripts/build.sh
    when: "target_platform == 'darwin'"
```

## Compatibility with Post-Generation Hooks

Conditional template generation works seamlessly with conditional hooks:

```yaml
templates:
  - template: docker-compose.yml.j2
    output: docker-compose.yml
    when: "enable_docker"

hooks:
  post_generate:
    - command: "docker-compose validate"
      description: "Validate Docker Compose file"
      when: "enable_docker"
```

Both the template AND the hook will be conditionally executed based on the same token.

## Migration Guide

If you have existing templates that should be conditional:

1. **Identify Conditional Templates**: Find templates that should only be generated sometimes
2. **Define Control Tokens**: Add boolean or string tokens to control generation
3. **Add `when` Clauses**: Update template configs with appropriate conditions
4. **Test Both Scenarios**: Verify templates are generated/skipped correctly
5. **Update Documentation**: Document which templates are conditional and why

## Performance Impact

- **Negligible**: Condition evaluation adds <1ms per template
- **Early Exit**: Skipped templates don't incur template rendering cost
- **No File I/O**: Skipped templates don't create output files

## Conclusion

Conditional template generation adds powerful control over which files are generated, enabling:
- Environment-specific configurations
- Feature flag-driven development
- Platform-specific builds
- Progressive rollouts
- Cleaner output directories

The feature integrates seamlessly with existing Template Forge functionality while maintaining backward compatibility.
