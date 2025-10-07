# Template Forge Documentation

This directory contains the complete documentation for Template Forge.

---

## 📚 Documentation Structure

### User Documentation

Quick start and practical guides for end users:

- **[index.md](index.md)** - Documentation homepage
- **[getting-started.md](getting-started.md)** - 20-minute comprehensive tutorial
- **[installation.md](installation.md)** - Installation and setup
- **[user-guide.md](user-guide.md)** - Complete user guide with all features
- **[configuration.md](configuration.md)** - Full configuration reference

### Developer Documentation

Technical documentation for developers:

- **[api.md](api.md)** - Python API reference
- **[development.md](development.md)** - Development setup and contributing guidelines
- **[publishing.md](publishing.md)** - How to publish to PyPI

### Technical Requirements

Detailed specifications for architects and technical leads:

- **[requirements/](requirements/)** - Complete system requirements
  - [README.md](requirements/README.md) - Requirements overview
  - [01_system_overview.md](requirements/01_system_overview.md) - System architecture (REQ-SYS)
  - [02_configuration.md](requirements/02_configuration.md) - Configuration system (REQ-CFG)
  - [03_data_extraction.md](requirements/03_data_extraction.md) - Data extraction (REQ-EXT)
  - [04_template_engine.md](requirements/04_template_engine.md) - Template engine (REQ-TPL)
  - [05_code_preservation.md](requirements/05_code_preservation.md) - Code preservation (REQ-PRV)
  - [06_cli.md](requirements/06_cli.md) - CLI interface (REQ-CLI)
  - [07_automation.md](requirements/07_automation.md) - Automation & hooks (REQ-AUT)

---

## 🎯 Documentation by Audience

### New Users (5 minutes)
Start here to get productive quickly:
1. **[getting-started.md](getting-started.md)** - Quick start section (5 minutes)
2. **[Examples](../examples/)** - Working examples

### Learning Users (20 minutes)
Understand core concepts and patterns:
1. **[getting-started.md](getting-started.md)** - Complete guide from basics to advanced
2. **[user-guide.md](user-guide.md)** - Complete feature documentation
3. **[Examples](../examples/)** - 7 real-world scenarios

### Advanced Users
Reference documentation:
1. **[configuration.md](configuration.md)** - All configuration options
2. **[api.md](api.md)** - Python API reference
3. **[requirements/](requirements/)** - Technical specifications

### Developers & Contributors
Development documentation:
1. **[development.md](development.md)** - Development setup
2. **[../CONTRIBUTING.md](../CONTRIBUTING.md)** - Contribution guidelines
3. **[publishing.md](publishing.md)** - Release process
4. **[requirements/](requirements/)** - Implementation specs

### Architects & Technical Leads
System specifications:
1. **[requirements/README.md](requirements/README.md)** - Requirements overview
2. **[requirements/01_system_overview.md](requirements/01_system_overview.md)** - Architecture
3. All requirements documents for detailed specs

---

## 📖 Reading Guide

### Linear Path (Beginner → Expert)

1. **Quick Start** (5 min)
   - [getting-started.md](getting-started.md)

2. **Core Concepts** (20 min)
   - [getting-started.md](getting-started.md)

3. **Complete Guide** (1 hour)
   - [user-guide.md](user-guide.md)
   - [configuration.md](configuration.md)

4. **Examples** (hands-on practice)
   - [../examples/](../examples/)

5. **Advanced Topics** (as needed)
   - [api.md](api.md)
   - [requirements/](requirements/)

---

## 🔗 Requirements Traceability

All requirements are traceable through the codebase:

- **REQ-SYS-xxx**: System architecture requirements → [01_system_overview.md](requirements/01_system_overview.md)
- **REQ-CFG-xxx**: Configuration requirements → [02_configuration.md](requirements/02_configuration.md)
- **REQ-EXT-xxx**: Data extraction requirements → [03_data_extraction.md](requirements/03_data_extraction.md)
- **REQ-TPL-xxx**: Template engine requirements → [04_template_engine.md](requirements/04_template_engine.md)
- **REQ-PRV-xxx**: Code preservation requirements → [05_code_preservation.md](requirements/05_code_preservation.md)
- **REQ-CLI-xxx**: CLI requirements → [06_cli.md](requirements/06_cli.md)
- **REQ-AUT-xxx**: Automation requirements → [07_automation.md](requirements/07_automation.md)

Each requirement has:
- ✅ Specification in requirements docs
- ✅ Implementation in source code
- ✅ Test coverage in test suite (403 tests)
- ✅ Traceability through REQ-* identifiers

---

## 🌐 Building Documentation Website

Template Forge uses [MkDocs](https://www.mkdocs.org/) with [Material theme](https://squidfunk.github.io/mkdocs-material/) for documentation.

### Local Preview

```bash
# Install documentation dependencies
pip install template-forge[docs]

# Serve documentation locally
mkdocs serve

# Open browser to http://127.0.0.1:8000
```

### Build Static Site

```bash
# Build documentation
mkdocs build

# Output in site/ directory
```

### Deploy to GitHub Pages

```bash
# Deploy to gh-pages branch
mkdocs gh-deploy
```

### Configuration

Documentation configuration is in [../mkdocs.yml](../mkdocs.yml):
- Navigation structure
- Theme settings (Material with dark mode)
- Markdown extensions
- Plugin configuration

---

## 📝 Documentation Standards

### Markdown Files

- Use clear, descriptive headings
- Include code examples
- Add cross-references to related docs
- Use emojis sparingly for visual hierarchy
- Keep line length reasonable for readability

### Code Examples

- Always provide complete, working examples
- Include expected output
- Add comments explaining key concepts
- Test all examples before committing

### Requirements Documents

- Use REQ-XXX-YYY format for identifiers
- Link requirements to tests
- Document design decisions
- Include examples and use cases

---

## 🔄 Maintenance

### Adding New Features

When adding new features:

1. Update relevant requirements document
2. Add user documentation to user-guide.md
3. Update configuration reference if needed
4. Add examples to examples/
5. Update API docs if public API changes
6. Add requirement traceability

### Publishing New Version

See [publishing.md](publishing.md) for complete publishing workflow.

---

## 📞 Help & Support

- **Questions?** [GitHub Discussions](https://github.com/CarloFornari/template_forge/discussions)
- **Issues?** [GitHub Issues](https://github.com/CarloFornari/template_forge/issues)
- **Contributing?** See [../CONTRIBUTING.md](../CONTRIBUTING.md)

---

<div align="center">

**Documentation maintained with ❤️ by the Template Forge community**

[🏠 Home](index.md) | [🚀 Quick Start](getting-started.md) | [📖 User Guide](user-guide.md) | [🔧 API](api.md)

</div>
