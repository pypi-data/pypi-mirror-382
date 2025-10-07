# Welcome to Template Forge

<div align="center">

**Stop writing boilerplate. Start building features.**

[![PyPI version](https://img.shields.io/pypi/v/template-forge.svg)](https://pypi.org/project/template-forge/)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-403%20passing-brightgreen)]()
[![License](https://img.shields.io/badge/license-MIT-green)](../LICENSE)

[Get Started](getting-started.md){ .md-button .md-button--primary }
[View Examples](../examples/){ .md-button }

</div>

---

## What is Template Forge?

Template Forge transforms your structured data (JSON, YAML, XML, ARXML) into **any text-based output**—code, configurations, documentation, infrastructure—using the power of Jinja2 templates.

**Think of it as "mail merge" for developers.**

---

## Quick Example

**Input Data** (`app.json`):
```json
{
  "service": {
    "name": "UserAPI",
    "port": 8080,
    "endpoints": ["users", "auth", "profile"]
  }
}
```

**Template** (`service.py.j2`):
```python
# Generated {{ service.name }} Service
from flask import Flask
app = Flask("{{ service.name }}")

{% for endpoint in service.endpoints %}
@app.route("/{{ endpoint }}")
def {{ endpoint }}():
    return {"endpoint": "{{ endpoint }}"}
{% endfor %}

if __name__ == "__main__":
    app.run(port={{ service.port }})
```

**Generate**:
```bash
pip install template-forge
template-forge config.yaml
```

**Output** - Fully functional Python service!

---

## Key Features

### 📊 Universal Data Support
Parse JSON, YAML, XML, and ARXML with intelligent extraction using dot notation, array operations, and wildcards.

### 🎨 Powerful Templates
Full Jinja2 support with custom filters, conditional generation, foreach iteration, and matrix generation.

### 🛡️ Code Preservation
Keep your custom code sections safe across regenerations with smart preservation markers.

### ⚙️ Advanced Automation
Pre/post hooks, conditional execution, template inheritance, and complete pipeline control.

---

## Why Template Forge?

### The Problem

Development teams waste **hours** on repetitive tasks:

- ✍️ Manually writing boilerplate code for each microservice
- 🔄 Keeping configurations synchronized across environments
- 📚 Maintaining documentation that's always out of sync
- 😱 Losing custom code when regenerating files

### The Solution

```
One Data Source + Templates = Everything Generated Consistently
```

**Benefits:**

- ⚡ **10x faster** - Generate in seconds what takes hours manually
- 🎯 **Zero errors** - No copy-paste mistakes or typos
- 🔄 **Always in sync** - Update data once, regenerate everything
- 🛡️ **Safe** - Custom code preserved automatically
- 📈 **Scalable** - From 1 file to 1000 files with same effort

---

## Use Cases

### 🏗️ Microservices
Generate consistent API endpoints, Docker configs, K8s manifests, and documentation across all services.

### ⚙️ Multi-Environment Configs
Create dev, staging, and production configurations from a single data source.

### 💻 Code Generation
Generate type-safe classes, DTOs, validators, and boilerplate from data models.

### 🚗 Automotive (AUTOSAR)
Transform ARXML into C headers, configuration files, and system documentation.

### 📝 Documentation
Keep API docs, config references, and guides synchronized with your code.

### 🔧 Build Systems
Generate CMake, Makefiles, or build configurations from project metadata.

---

## Getting Started

### :material-rocket-launch: Getting Started Guide
Get from installation to expert in one comprehensive guide with clear time-based sections.
**[Start Here →](getting-started.md)**

- ⚡ **Quick Start** (5 minutes) - Get generating immediately
- 📚 **Core Concepts** (10 minutes) - Understand how it works
- 🎓 **Deep Dive** (20+ minutes) - Master advanced features

### :material-lightbulb-on: Examples
Explore 7 real-world examples with complete code, data, and configurations.
**[Browse Examples →](../examples/)**

### :material-api: API Reference
Detailed documentation for all configuration options and programmatic usage.
**[View API Docs →](api.md)**

---

## Documentation Structure

### 📖 User Documentation

- **[Getting Started Guide](getting-started.md)** - 20-minute comprehensive tutorial
- **[User Guide](user-guide.md)** - Complete feature documentation
- **[Configuration Reference](configuration.md)** - Full config.yaml specification
- **[Installation Guide](installation.md)** - Setup and requirements

### 🔧 Developer Documentation

- **[API Reference](api.md)** - Python API documentation
- **[Development Guide](development.md)** - Contributing and extending
- **[Publishing Guide](publishing.md)** - How to publish new versions

### 📋 Technical Specifications

For developers, architects, and technical leads who need detailed requirements:

- **[Requirements Overview](requirements/README.md)** - Complete system requirements
- **[System Architecture (REQ-SYS)](requirements/01_system_overview.md)** - System design and architecture
- **[Configuration System (REQ-CFG)](requirements/02_configuration.md)** - Configuration specifications
- **[Data Extraction (REQ-EXT)](requirements/03_data_extraction.md)** - Data processing requirements
- **[Template Engine (REQ-TPL)](requirements/04_template_engine.md)** - Template processing specs
- **[Code Preservation (REQ-PRV)](requirements/05_code_preservation.md)** - Preservation system
- **[CLI Interface (REQ-CLI)](requirements/06_cli.md)** - Command-line interface
- **[Automation (REQ-AUT)](requirements/07_automation.md)** - Hooks and automation

These requirements provide:
- ✅ Complete functional specifications with traceability
- 🏗️ System architecture and design decisions
- 🧪 Test coverage mapping (403 tests → requirements)
- 📊 Implementation guidelines and patterns

---

## Installation

```bash
# From PyPI (recommended)
pip install template-forge

# Verify installation
template-forge --version

# Start generating!
template-forge config.yaml
```

**Requirements:** Python 3.8+

---

## What's Next?

Choose your path:

1. **[Start with the Getting Started guide](getting-started.md)** - Best for all learners (quick start + deep dive)
2. **[Explore examples](../examples/)** - Best for learning by example
3. **[Review requirements](requirements/README.md)** - Best for technical specifications
4. **[Dive into API docs](api.md)** - Best for advanced users and integration

---

## Community & Support

- **GitHub**: [CarloFornari/template_forge](https://github.com/CarloFornari/template_forge)
- **Issues**: [Report bugs or request features](https://github.com/CarloFornari/template_forge/issues)
- **Discussions**: [Ask questions and share ideas](https://github.com/CarloFornari/template_forge/discussions)

---

<div align="center">

**Ready to stop writing boilerplate?**

[Get Started Now →](getting-started.md)

Made with ❤️ by [Carlo Fornari](https://github.com/CarloFornari)

</div>
