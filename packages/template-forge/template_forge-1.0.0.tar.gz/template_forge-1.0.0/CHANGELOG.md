# Changelog

All notable changes to Template Forge will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-10-07

### Added
- Initial release of Template Forge
- Jinja2-based templating engine for code generation
- Support for multiple data formats (JSON, YAML, XML/ARXML)
- Configuration-driven template processing
- Code preservation with configurable markers
- Conditional template generation
- Post-generation automation hooks
- Custom Jinja2 filters support
- Template variable derivation
- Environment-based tokens
- Glob pattern support for template discovery
- Comprehensive CLI with multiple modes:
  - Standard generation mode
  - Dry-run mode (`--dry-run`)
  - Variable preview mode (`--show-variables`)
  - Diff preview mode (`--diff`)
  - Validation mode (`--validate`)
- Color-coded terminal output
- Detailed logging and error reporting
- Extensive test coverage (89%)
- Type-safe implementation with mypy strict mode
- Complete documentation and examples
- 9 example projects demonstrating various use cases

### Features by Category

#### Data Extraction
- Multi-format data extraction (JSON, YAML, XML)
- Safe XML parsing with defusedxml
- Cross-input field references
- Array operations and filtering
- Nested data structure access

#### Template Engine
- Jinja2 template processing
- Custom filter registration
- Built-in utility filters (snake_case, camelCase, etc.)
- Template-specific token overrides
- Conditional template generation

#### Code Preservation
- Configurable preservation markers
- Multi-line block preservation
- Custom marker patterns
- Preservation across regeneration

#### Automation
- Post-generation hooks
- Conditional hook execution
- Environment variable support
- Working directory configuration
- Timeout and error handling
- Multiple error modes (fail/warn/skip)

#### CLI Features
- Automatic config discovery
- Flexible configuration paths
- Multiple output modes
- Exit code standards
- Help documentation
- Color output control

### Documentation
- Comprehensive README with quickstart
- Detailed user guide
- API documentation
- Configuration reference
- Development guide
- AI integration guide
- Publishing guidelines
- 9 documented examples

### Development
- 681 passing tests
- 89% test coverage
- Mypy strict type checking
- Ruff linting (100% clean)
- Security scanning with bandit
- Pre-commit hooks
- Automated publishing checks

[1.0.0]: https://github.com/CarloFornari/template_forge/releases/tag/v1.0.0
