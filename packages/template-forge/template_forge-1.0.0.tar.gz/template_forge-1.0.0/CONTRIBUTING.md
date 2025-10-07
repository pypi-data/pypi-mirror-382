# Contributing to Template Forge

Thank you for your interest in contributing to Template Forge! This document provides guidelines and information for contributors.

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When creating a bug report, include:

- A clear and descriptive title
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Your environment (OS, Python version, package version)
- Relevant configuration files and error messages

### Suggesting Enhancements

Enhancement suggestions are welcome! Please provide:

- A clear and descriptive title
- A detailed description of the proposed feature
- Examples of how the feature would be used
- Any relevant mockups or examples

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Install development dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```
3. **Make your changes** following our coding standards
4. **Add tests** for any new functionality
5. **Run the test suite** to ensure all tests pass:
   ```bash
   python tests/run_tests.py
   ```
6. **Update documentation** if needed
7. **Commit your changes** with a clear commit message
8. **Push to your fork** and submit a pull request

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git

### Installation

1. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/template_forge.git
   cd template_forge
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install in development mode:
   ```bash
   pip install -e ".[dev]"
   ```

### Running Tests

```bash
# Run all tests
python tests/run_tests.py

# Run specific test suites
python tests/run_tests.py extractor
python tests/run_tests.py processor
python tests/run_tests.py integration

# With pytest (if available)
pytest tests/ -v

# With coverage
pytest tests/ --cov=template_forge --cov-report=html
```

### Code Style

We use several tools to maintain code quality:

- **Black** for code formatting:
  ```bash
  black template_forge/ tests/
  ```

- **Flake8** for linting:
  ```bash
  flake8 template_forge/ tests/
  ```

- **MyPy** for type checking:
  ```bash
  mypy template_forge/
  ```

### Project Structure

```
template_forge/
├── template_forge/          # Main package
│   ├── __init__.py         # Package initialization
│   ├── core.py             # Core classes
│   └── cli.py              # Command-line interface
├── tests/                  # Test suite
│   ├── test_extractor.py   # Extractor tests
│   ├── test_processor.py   # Processor tests
│   ├── test_template_forge.py  # Main class tests
│   └── test_integration.py # Integration tests
├── templates/              # Example templates
├── examples/               # Example data files
└── docs/                   # Documentation
```

## Coding Guidelines

### Python Style

- Follow PEP 8 style guidelines
- Use type hints for function parameters and return values
- Write docstrings for all public functions and classes
- Keep functions focused and reasonably sized
- Use meaningful variable and function names

### Testing

- Write tests for all new functionality
- Maintain or improve test coverage
- Use descriptive test names
- Follow the AAA pattern (Arrange, Act, Assert)
- Mock external dependencies appropriately

### Documentation

- Update README.md for user-facing changes
- Add docstrings to new functions and classes
- Include examples for new features

## Adding New Features

### New File Format Support

To add support for a new file format:

1. Add the file extension to `SUPPORTED_FORMATS` in `core.py`
2. Implement parsing logic in `_load_file` method
3. Add extraction logic in `_extract_from_file` method
4. Add comprehensive tests
5. Update documentation with examples

### New Transforms

To add new value transformations:

1. Add the transform to `_apply_transform` method
2. Add corresponding tests
3. Document the new transform in README.md

### New Jinja2 Filters

To add new Jinja2 filters:

1. Add the filter to `_register_custom_filters` method
2. Add comprehensive tests
3. Document the filter usage

## Release Process

1. Update version in `template_forge/__init__.py` and `pyproject.toml`
2. Update CHANGELOG.md with new features and fixes
3. Run full test suite
4. Create a release PR
5. Tag the release after merging
6. Build and upload to PyPI

## Getting Help

If you need help:

- Check the documentation and examples
- Search existing issues
- Ask questions in discussions
- Contact the maintainers

Thank you for contributing to Template Forge!