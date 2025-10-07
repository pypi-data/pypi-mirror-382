# Advanced Features Example

This example demonstrates advanced Template Forge features including:

## Features Demonstrated

### 1. Configuration Includes (REQ-CFG-100-109)
- Modular configuration with `!include` directive
- Reusable configuration fragments
- Shared settings across projects

### 2. Conditional Templates (REQ-TPL-130-138)
- Templates that generate only when conditions are met
- Boolean conditions
- Comparison operators
- Defined/undefined checks

### 3. Post-Generation Hooks (REQ-AUT-001-093)
- Automated post-processing commands
- Conditional hook execution
- Error handling strategies (ignore/warn/fail)
- Working directory specification

### 4. Template Inheritance (REQ-TPL-110-112)
- Base templates with blocks
- Child templates extending parents
- Multiple inheritance levels

### 5. Multiple Code Preservation Blocks (REQ-PRV-030-044)
- Multiple preserved sections per file
- Unique identifiers for each block
- Various comment styles

### 6. Hierarchical Static Tokens (REQ-CFG-032)
- Nested token structures
- Organized configuration

### 7. Template-Specific Tokens (REQ-CFG-041)
- Override global tokens
- Per-template configuration

### 8. Jinja2 Options (REQ-CFG-050-051)
- Whitespace control
- Block trimming
- Custom Jinja2 settings

## File Structure

```
advanced-features/
├── config.yaml              # Main configuration (uses includes)
├── config-includes/         # Modular configuration fragments
│   ├── common-tokens.yaml   # Shared static tokens
│   └── deployment.yaml      # Deployment-specific settings
├── project-data.json        # Input data
├── templates/
│   ├── base.j2              # Base template for inheritance
│   ├── application.py.j2    # Python app (extends base)
│   ├── docker-compose.yml.j2# Docker (conditional)
│   ├── kubernetes.yaml.j2   # K8s (conditional)
│   └── README.md.j2         # Documentation
└── README.md                # This file
```

## Usage Examples

### Basic Generation
```bash
template-forge config.yaml
```

### Dry Run (Preview)
```bash
template-forge config.yaml --dry-run
```

### Show Variables
```bash
template-forge config.yaml --show-variables
```

### Validate Configuration
```bash
template-forge config.yaml --validate
```

### Validate Templates
```bash
template-forge config.yaml --validate-templates
```

### Generate Without Hooks
```bash
template-forge config.yaml --no-hooks
```

### Show Diff
```bash
# Generate once
template-forge config.yaml

# Make changes to project-data.json
# Then preview differences
template-forge config.yaml --diff
```

## What This Example Demonstrates

### Configuration Includes
The main `config.yaml` uses `!include` to load:
- `common-tokens.yaml` - Shared project metadata
- `deployment.yaml` - Deployment configuration

This allows reusing common settings across multiple projects.

### Conditional Templates
Templates include `when` conditions:
- `docker-compose.yml.j2` - Only generates if `deployment_type == 'docker'`
- `kubernetes.yaml.j2` - Only generates if `deployment_type == 'kubernetes'`

### Post-Generation Hooks
Hooks demonstrate:
- Code formatting (Python Black)
- Dependency installation (pip)
- Conditional execution based on deployment type
- Error handling with `on_error` setting

### Template Inheritance
- `base.j2` - Defines common structure with blocks
- `application.py.j2` - Extends base, fills in blocks

### Multiple Preservation Blocks
Generated files include multiple preserved sections:
- `custom_imports` - For custom imports
- `custom_methods` - For custom functions
- `custom_config` - For configuration overrides
- `custom_tests` - For test cases

## Try Different Scenarios

### Scenario 1: Docker Deployment
In `project-data.json`, set:
```json
"deployment_type": "docker"
```
Then run: `template-forge config.yaml`

Result: Generates docker-compose.yml, runs Docker-related hooks

### Scenario 2: Kubernetes Deployment
In `project-data.json`, set:
```json
"deployment_type": "kubernetes"
```
Then run: `template-forge config.yaml`

Result: Generates kubernetes.yaml instead of docker-compose.yml

### Scenario 3: Development Mode
In `project-data.json`, set:
```json
"environment": "development",
"debug_mode": true
```

Result: Generates files with debug settings, skips production hooks

## Expected Output

Generated files will be created in `../../output/advanced/`:
- `application.py` - Main Python application (always)
- `README.md` - Project documentation (always)
- `docker-compose.yml` - Only if deployment_type=='docker'
- `kubernetes.yaml` - Only if deployment_type=='kubernetes'

## Hooks Executed

1. **Format Python code** - Runs `black` on generated Python files
2. **Install dependencies** - Runs `pip install -r requirements.txt` (conditional)
3. **Build Docker image** - Only if deployment_type=='docker'
4. **Apply Kubernetes config** - Only if deployment_type=='kubernetes'

## Learning Points

1. **Modularity**: Configuration includes keep configs DRY
2. **Flexibility**: Conditional templates adapt to your needs
3. **Automation**: Hooks integrate with your workflow
4. **Maintainability**: Code preservation protects custom code
5. **Scalability**: Template inheritance reduces duplication

## Requirements Covered

- REQ-CFG-100-109: Configuration includes
- REQ-CFG-032: Hierarchical static tokens
- REQ-CFG-041: Template-specific tokens
- REQ-CFG-050-051: Jinja2 options
- REQ-TPL-110-112: Template inheritance
- REQ-TPL-130-138: Conditional templates
- REQ-PRV-030-044: Multiple preservation blocks
- REQ-AUT-001-093: Post-generation hooks
- REQ-AUT-030-033: Conditional hooks
