# 📖 Getting Started with Template Forge

Welcome to Template Forge! This guide takes you from installation to confident usage.

**Choose your path:**
- ⚡ **[Quick Start (5 minutes)](#quick-start-5-minutes)** - Get generating immediately
- 📚 **[Core Concepts (10 minutes)](#core-concepts-10-minutes)** - Understand how it works
- 🎓 **[Deep Dive (20+ minutes)](#deep-dive)** - Master advanced features

---

## ⚡ Quick Start (5 Minutes)

### Step 1: Install (30 seconds)

```bash
pip install template-forge
```

Verify:
```bash
template-forge --version
```

---

### Step 2: Create Your First Project (2 minutes)

Create a project directory:
```bash
mkdir my-first-template
cd my-first-template
```

**Create `data.json`:**
```json
{
  "application": {
    "name": "HelloWorld",
    "version": "1.0.0",
    "description": "My first Template Forge project",
    "features": ["logging", "config", "api"]
  }
}
```

**Create `app.py.j2`:**
```python
"""
{{ application.name }} - {{ application.description }}
Version: {{ application.version }}
"""

class {{ application.name }}:
    """Main application class"""
    
    VERSION = "{{ application.version }}"
    
    def __init__(self):
        self.name = "{{ application.name }}"
        self.features = {{ application.features }}
    
    def run(self):
        print(f"Starting {self.name} v{self.VERSION}")
        print(f"Enabled features: {', '.join(self.features)}")

if __name__ == "__main__":
    app = {{ application.name }}()
    app.run()
```

**Create `config.yaml`:**
```yaml
inputs:
  - path: "data.json"
    namespace: "application"

templates:
  - template: "app.py.j2"
    output: "app.py"
```

---

### Step 3: Generate! (5 seconds)

```bash
template-forge config.yaml
```

**Check the result:**
```bash
cat app.py
python app.py
```

You should see:
```
Starting HelloWorld v1.0.0
Enabled features: logging, config, api
```

**🎉 Success!** You just generated your first file with Template Forge!

**What happened?**
1. Template Forge read your `data.json`
2. Extracted the `application` data as tokens
3. Processed `app.py.j2` with Jinja2
4. Generated `app.py` with real values

**Try this:** Change `data.json` values and regenerate—instant update!

---

## 📚 Core Concepts (10 Minutes)

### What is Template Forge?

Template Forge is a Python tool that generates text files from structured data using templates. Think of it as **"mail merge" for developers**.

**The Three Components:**

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│  Your Data  │────▶│ Template     │────▶│  Generated   │
│ (JSON/YAML/ │     │ Forge        │     │  Files       │
│  XML)       │     │ + Templates  │     │              │
└─────────────┘     └──────────────┘     └──────────────┘
```

1. **Data Sources**: Your structured data (JSON, YAML, XML, ARXML)
2. **Templates**: Jinja2 templates that define output structure
3. **Configuration**: YAML file that connects data to templates

**When to use it:**
- ✅ Generating code from data models
- ✅ Creating environment-specific configurations
- ✅ Maintaining synchronized documentation
- ✅ Automating repetitive file creation
- ✅ AUTOSAR/automotive code generation

**When NOT to use it:**
- ❌ Runtime template rendering (use Jinja2 directly)
- ❌ Database-driven content (use an ORM)
- ❌ Real-time generation (it's a build tool)

### Key Concepts Explained

#### 1. Data Sources

Your structured data files. Supported formats:
- **JSON**: `.json`
- **YAML**: `.yaml`, `.yml`
- **XML**: `.xml`
- **ARXML**: `.arxml` (AUTOSAR XML)

Example `data.json`:
```json
{
  "app": {
    "name": "MyApp",
    "version": "1.0.0"
  }
}
```

#### 2. Templates

Jinja2 template files (usually `.j2` extension) that define your output structure.

Example `template.txt.j2`:
```
Application: {{ app.name }}
Version: {{ app.version }}
```

#### 3. Tokens

Variables extracted from your data that can be used in templates.

```yaml
inputs:
  - path: "data.json"
    tokens:
      - name: "app_name"
        key: "app.name"
```

Use in template: `{{ app_name }}`

#### 4. Namespaces

Organize tokens to avoid naming conflicts:

```yaml
inputs:
  - path: "data.json"
    namespace: "app"
```

Use in template: `{{ app.name }}`

#### 5. Configuration File

The YAML file (`config.yaml`) that ties everything together:

```yaml
inputs:          # Where your data comes from
  - path: "data.json"
    namespace: "app"

templates:       # What to generate
  - template: "output.j2"
    output: "output.txt"
```

---

## 🎓 Deep Dive

Ready to go deeper? The sections below cover advanced usage and patterns.

### Understanding Configuration in Detail

#### Basic Structure

```yaml
# Optional: Where templates are located
template_dir: "templates"

# Optional: Where to write output files  
output_directory: "output"

# Required: Data sources
inputs:
  - path: "data.json"
    namespace: "app"

# Optional: Static values
static_tokens:
  company: "ACME Corp"
  year: "2025"

# Required: Templates to process
templates:
  - template: "file.j2"
    output: "file.txt"
```

#### Input Configuration Patterns

##### Simple Namespace Extraction
```yaml
inputs:
  - path: "data.json"
    namespace: "app"
```
All top-level keys from `data.json` accessible as `{{ app.key }}`

##### Specific Token Extraction
```yaml
inputs:
  - path: "data.json"
    tokens:
      - name: "app_name"
        key: "application.name"
      - name: "version"
        key: "application.version"
```
Use as: `{{ app_name }}` and `{{ version }}`

##### Mix Both Approaches
```yaml
inputs:
  - path: "data.json"
    namespace: "app"
    tokens:
      - name: "special_value"
        key: "deep.nested.value"
```

#### Template Configuration Patterns

##### Basic Template
```yaml
templates:
  - template: "source.j2"
    output: "destination.txt"
```

##### With Custom Template Directory
```yaml
template_dir: "my-templates"

templates:
  - template: "file.j2"        # Looks in my-templates/file.j2
    output: "output/file.txt"  # Creates output directory
```

---

### Working with Data

Learn how to extract and use data from various sources.

#### Extracting Data with Key Paths

Use dot notation to navigate nested structures:

**Data** (`config.json`):
```json
{
  "server": {
    "web": {
      "host": "localhost",
      "port": 8080
    }
  }
}
```

**Config**:
```yaml
inputs:
  - path: "config.json"
    tokens:
      - name: "host"
        key: "server.web.host"
      - name: "port"
        key: "server.web.port"
```

**Template**:
```
Server: {{ host }}:{{ port }}
```

**Result**:
```
Server: localhost:8080
```

#### Working with Arrays

**Data** (`team.json`):
```json
{
  "team": {
    "members": [
      {"name": "Alice", "role": "Developer"},
      {"name": "Bob", "role": "Designer"},
      {"name": "Carol", "role": "Manager"}
    ]
  }
}
```

**Config**:
```yaml
inputs:
  - path: "team.json"
    namespace: "team"
```

**Template**:
```
Team Members:
{% for member in team.members %}
- {{ member.name }} ({{ member.role }})
{% endfor %}
```

**Result**:
```
Team Members:
- Alice (Developer)
- Bob (Designer)
- Carol (Manager)
```

#### Multiple Data Sources

You can combine data from multiple files:

**Config**:
```yaml
inputs:
  - path: "app-info.json"
    namespace: "app"
  - path: "build-info.json"
    namespace: "build"
  - path: "deployment.yaml"
    namespace: "deploy"

static_tokens:
  generated_date: "2025-10-04"
```

**Template** can use all namespaces:
```
App: {{ app.name }}
Build: {{ build.number }}
Environment: {{ deploy.environment }}
Generated: {{ generated_date }}
```

---

### Creating Templates

Templates use [Jinja2 syntax](https://jinja.palletsprojects.com/templates/). Here are the essentials:

#### Variables

```jinja2
{{ variable_name }}
{{ namespace.key }}
{{ nested.data.value }}
```

#### Conditionals

```jinja2
{% if condition %}
  Content when true
{% elif other_condition %}
  Content when other is true
{% else %}
  Content when all false
{% endif %}
```

Example:
```jinja2
{% if app.debug_mode %}
DEBUG = True
{% else %}
DEBUG = False
{% endif %}
```

#### Loops

```jinja2
{% for item in items %}
  {{ item }}
{% endfor %}
```

With index:
```jinja2
{% for item in items %}
{{ loop.index }}. {{ item }}
{% endfor %}
```

#### Filters

Transform values:
```jinja2
{{ name | upper }}              # UPPERCASE
{{ name | lower }}              # lowercase
{{ name | title }}              # Title Case
{{ items | length }}            # Count
{{ items | join(', ') }}        # Join array
```

#### Comments

```jinja2
{# This is a comment and won't appear in output #}
```

#### Whitespace Control

```jinja2
{%- if condition -%}    # Remove whitespace before and after
  Content
{%- endif -%}
```

---

### Common Patterns

Real-world examples showing how to use Template Forge effectively.

#### Pattern 1: Environment-Specific Configs

**Data** (`environments.json`):
```json
{
  "dev": {
    "db_host": "localhost",
    "debug": true
  },
  "prod": {
    "db_host": "prod-db.example.com",
    "debug": false
  }
}
```

**Template** (`config.py.j2`):
```python
# {{ environment | upper }} Configuration

DATABASE_HOST = "{{ config.db_host }}"
DEBUG = {{ config.debug | string | upper }}
```

**Config**:
```yaml
inputs:
  - path: "environments.json"
    tokens:
      - name: "config"
        key: "dev"    # Change to "prod" for production

static_tokens:
  environment: "development"

templates:
  - template: "config.py.j2"
    output: "config.py"
```

#### Pattern 2: Code Generation from Models

**Data** (`models.json`):
```json
{
  "models": [
    {
      "name": "User",
      "fields": [
        {"name": "id", "type": "int"},
        {"name": "email", "type": "str"},
        {"name": "active", "type": "bool"}
      ]
    },
    {
      "name": "Post",
      "fields": [
        {"name": "id", "type": "int"},
        {"name": "title", "type": "str"},
        {"name": "content", "type": "str"}
      ]
    }
  ]
}
```

**Template** (`models.py.j2`):
```python
"""Auto-generated data models"""
from dataclasses import dataclass

{% for model in models.models %}
@dataclass
class {{ model.name }}:
    {% for field in model.fields %}
    {{ field.name }}: {{ field.type }}
    {% endfor %}
{% endfor %}
```

#### Pattern 3: Documentation from Code Metadata

**Data** (`api.yaml`):
```yaml
api:
  endpoints:
    - path: "/users"
      method: GET
      description: "List all users"
      auth_required: true
    - path: "/users/{id}"
      method: GET
      description: "Get user by ID"
      auth_required: true
    - path: "/public/status"
      method: GET
      description: "Check API status"
      auth_required: false
```

**Template** (`API.md.j2`):
```markdown
# API Documentation

## Endpoints

{% for endpoint in api.endpoints %}
### {{ endpoint.method }} {{ endpoint.path }}

{{ endpoint.description }}

{% if endpoint.auth_required %}
🔒 **Authentication required**
{% else %}
🌐 **Public endpoint**
{% endif %}

---
{% endfor %}
```

---

## 🎯 Next Steps

### Continue Learning

**Explore More Features:**
1. **[User Guide](user-guide.md)** - Complete feature reference
   - Conditional template generation
   - Foreach iteration and matrix generation
   - Code preservation markers
   - Hooks and automation

2. **[Configuration Reference](configuration.md)** - All configuration options
   - Detailed input specifications
   - Template configuration
   - Advanced features

3. **[Examples](../examples/)** - Real-world use cases
   - Basic usage patterns
   - Advanced features demo
   - AUTOSAR automotive projects
   - Docker configurations
   - C++ project generation

4. **[API Documentation](api.md)** - Programmatic usage
   - Python API reference
   - Custom filters and functions
   - Integration patterns

### Tips for Success

1. 💡 **Start Simple**: Begin with basic templates and add complexity gradually
2. 📝 **Use Comments**: Document your templates and configs
3. ✅ **Validate Early**: Run `template-forge config.yaml` frequently
4. 👀 **Check Examples**: Browse `examples/` directory for inspiration
5. 🔄 **Version Control**: Keep templates, configs, and data in git

### Getting Help

- **Syntax errors?** Check YAML indentation and Jinja2 syntax
- **Template not generating?** Use `template-forge -v config.yaml` for verbose output
- **Need examples?** See the [examples directory](../examples/)
- **Found a bug?** [Open an issue](https://github.com/CarloFornari/template-forge/issues)

### Technical Specifications

For developers and technical leads who need detailed requirements:

- **[Requirements Overview](requirements/README.md)** - Complete system requirements
- **[System Architecture](requirements/01_system_overview.md)** - Design and architecture (REQ-SYS)
- **[Configuration Specs](requirements/02_configuration.md)** - Configuration system (REQ-CFG)
- **[Data Extraction](requirements/03_data_extraction.md)** - Data processing (REQ-EXT)
- **[Template Engine](requirements/04_template_engine.md)** - Template processing (REQ-TPL)
- **[Code Preservation](requirements/05_code_preservation.md)** - Preservation markers (REQ-PRV)
- **[CLI Interface](requirements/06_cli.md)** - Command-line interface (REQ-CLI)
- **[Automation](requirements/07_automation.md)** - Hooks and automation (REQ-AUT)

These documents provide:
- ✅ Detailed functional specifications
- ✅ Requirement traceability (REQ-* identifiers)
- ✅ System architecture and design decisions
- ✅ Implementation guidelines
- ✅ Test coverage mapping

---

<div align="center">

**Ready to automate everything?** 🚀

[📖 User Guide](user-guide.md) | [💡 Examples](../examples/) | [🔧 API Reference](api.md) | [📋 Requirements](requirements/README.md)

</div>
