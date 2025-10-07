# Template Forge Development Guide

A comprehensive guide for developers who want to contribute to Template Forge, add features, or understand the codebase architecture.

## Table of Contents

- [Development Setup](#development-setup)
- [Project Architecture](#project-architecture)
- [Testing](#testing)
- [Adding Features](#adding-features)
- [Code Standards](#code-standards)
- [Contributing](#contributing)
- [Release Process](#release-process)

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- Virtual environment tool (venv, conda, etc.)

### Initial Setup

1. **Fork and clone the repository**:
   ```bash
   git clone https://github.com/YourUsername/template_forge.git
   cd template_forge
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install in development mode**:
   ```bash
   pip install -e ".[dev]"
   ```

4. **Verify the setup**:
   ```bash
   python -m pytest tests/ -v
   python validate_config.py examples/basic/config.yaml
   ```

### Development Dependencies

The development installation includes:

- **pytest**: Testing framework
- **pytest-cov**: Coverage reporting
- **black**: Code formatting
- **flake8**: Linting
- **mypy**: Type checking
- **pyyaml**: YAML processing
- **jinja2**: Template engine

## Project Architecture

### Directory Structure

```
template_forge/
├── template_forge/           # Main package
│   ├── __init__.py          # Package exports
│   ├── core.py              # Core classes and functionality
│   ├── cli.py               # Command-line interface
│   └── types.py             # Type definitions and protocols
├── tests/                    # Test suite
│   ├── __init__.py
│   ├── test_extractor.py    # Data extraction tests
│   ├── test_processor.py    # Template processing tests
│   ├── test_integration.py  # End-to-end tests
│   └── test_marker_preservation.py  # Preservation tests
├── examples/                 # Example configurations
│   ├── basic/               # Simple examples
│   ├── python-class/        # Python code generation
│   ├── docker/              # Container configuration
│   ├── autosar/             # Automotive examples
│   └── yaml-config/         # YAML processing examples
├── docs/                     # Documentation
└── pyproject.toml           # Project configuration
```

### Core Classes

#### 1. StructuredDataExtractor
**Location**: `template_forge/core.py`

**Purpose**: Extracts tokens from structured data files (JSON, YAML, XML, ARXML).

**Key Methods**:
- `extract_tokens()`: Main entry point for token extraction
- `_extract_from_file()`: Process a single input file
- `_extract_from_dict()`: Navigate nested dictionaries using key paths
- `_load_file()`: Load and parse different file formats

**Adding Support for New File Formats**:

1. **Update supported formats**:
   ```python
   SUPPORTED_FORMATS: Dict[str, str] = {
       '.json': 'json',
       '.yaml': 'yaml', 
       '.yml': 'yaml',
       '.xml': 'xml',
       '.arxml': 'arxml',
       '.new_format': 'new_format'  # Add your format
   }
   ```

2. **Add format handler**:
   ```python
   def _load_file(self, file_path: Path, format_type: str) -> Dict[str, Any]:
       # ... existing code ...
       
       elif format_type == 'new_format':
           # Add your parser here
           return self._parse_new_format(file_path)
   ```

3. **Implement parser**:
   ```python
   def _parse_new_format(self, file_path: Path) -> Dict[str, Any]:
       """Parse new format files."""
       # Your implementation here
       pass
   ```

#### 2. PreservationHandler
**Location**: `template_forge/core.py`

**Purpose**: Manages content preservation between template regenerations.

**Key Methods**:
- `extract_preserved_content()`: Extract preserved blocks from existing files
- `inject_preserved_content()`: Inject preserved content into new output
- `_parse_preserved_blocks()`: Parse preservation markers

**Adding New Comment Styles**:

1. **Define comment patterns**:
   ```python
   COMMENT_PATTERNS = [
       (r'#\s*@PRESERVE_START', r'#\s*@PRESERVE_END'),        # Python/Shell
       (r'//\s*@PRESERVE_START', r'//\s*@PRESERVE_END'),      # C++/Java
       (r'/\*\s*@PRESERVE_START', r'\*/\s*@PRESERVE_END'),    # C-style
       (r'<!--\s*@PRESERVE_START', r'-->\s*@PRESERVE_END'),   # HTML/XML
       (r';\s*@PRESERVE_START', r';\s*@PRESERVE_END'),        # INI/Assembly
       # Add your pattern here
       (r'%\s*@PRESERVE_START', r'%\s*@PRESERVE_END'),        # MATLAB/LaTeX
   ]
   ```

#### 3. TemplateProcessor
**Location**: `template_forge/core.py`

**Purpose**: Processes Jinja2 templates with extracted tokens and preservation.

**Key Methods**:
- `process_templates()`: Process all configured templates
- `_process_single_template()`: Process one template with preservation
- `_register_custom_filters()`: Register custom Jinja2 filters

**Adding Custom Filters**:

1. **Add to filter registration**:
   ```python
   def _register_custom_filters(self):
       # ... existing filters ...
       
       # Add your custom filter
       def my_custom_filter(value):
           """Your custom transformation."""
           return value.upper().replace('_', '-')
       
       self.env.filters['my_filter'] = my_custom_filter
   ```

2. **Use in templates**:
   ```jinja2
   {{ variable_name | my_filter }}
   ```

#### 4. TemplateForge
**Location**: `template_forge/core.py`

**Purpose**: Main orchestrator class that coordinates the entire workflow.

**Key Methods**:
- `run()`: Execute the complete template generation workflow
- `_setup_logging()`: Configure logging based on options

## Testing

### Running Tests

#### All Tests
```bash
# Run complete test suite
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=template_forge --cov-report=html

# Run specific test categories
python tests/run_tests.py
```

#### Specific Test Files
```bash
# Test data extraction
python -m pytest tests/test_extractor.py -v

# Test template processing  
python -m pytest tests/test_processor.py -v

# Test preservation functionality
python -m pytest tests/test_marker_preservation.py -v

# Test integration workflows
python -m pytest tests/test_integration.py -v
```

#### Individual Tests
```bash
# Run specific test method
python -m pytest tests/test_extractor.py::TestStructuredDataExtractor::test_extract_from_dict_simple -v
```

### Test Structure

#### Unit Tests
- **test_extractor.py**: Data extraction from various formats
- **test_processor.py**: Template processing and custom filters
- **test_template_forge.py**: Main workflow orchestration

#### Integration Tests
- **test_integration.py**: End-to-end workflows
- **test_marker_preservation.py**: Content preservation scenarios

#### Test Coverage
Current test coverage: **61 tests covering all core functionality**

### Writing New Tests

#### Example Unit Test
```python
import unittest
from template_forge.core import StructuredDataExtractor

class TestNewFeature(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.config = {
            'inputs': [{
                'path': 'test_data.json',
                'tokens': [{'name': 'test', 'key': 'test.value'}]
            }]
        }
        self.extractor = StructuredDataExtractor(self.config)
    
    def test_new_functionality(self):
        """Test description."""
        # Arrange
        test_data = {'test': {'value': 'expected'}}
        
        # Act
        result = self.extractor._extract_from_dict(test_data, 'test.value')
        
        # Assert
        self.assertEqual(result, 'expected')
    
    def tearDown(self):
        """Clean up after each test method."""
        pass
```

#### Example Integration Test
```python
def test_complete_workflow(self):
    """Test complete template generation workflow."""
    # Create test files
    test_config = {
        'template_dir': self.test_dir,
        'inputs': [...],
        'templates': [...]
    }
    
    # Run workflow
    forge = TemplateForge(test_config)
    forge.run()
    
    # Verify outputs
    self.assertTrue(output_file.exists())
    self.assertIn('expected_content', output_file.read_text())
```

### Test Data Management

#### Creating Test Files
```python
def setUp(self):
    """Create temporary test files."""
    self.test_dir = tempfile.mkdtemp()
    
    # Create test data file
    test_data = {'app': {'name': 'TestApp'}}
    with open(f'{self.test_dir}/data.json', 'w') as f:
        json.dump(test_data, f)
    
    # Create test template
    template_content = "App: {{ app_name }}"
    with open(f'{self.test_dir}/template.j2', 'w') as f:
        f.write(template_content)

def tearDown(self):
    """Clean up test files."""
    shutil.rmtree(self.test_dir)
```

## Adding Features

### 1. Adding New Data Transformations

**Goal**: Add a new transformation like `reverse` or `base64_encode`.

**Implementation**:

1. **Add to transformation mapping** in `StructuredDataExtractor._apply_transform()`:
   ```python
   def _apply_transform(self, value: Any, transform: str) -> Any:
       """Apply transformation to extracted value."""
       transformations = {
           # ... existing transformations ...
           'reverse': lambda x: x[::-1] if isinstance(x, str) else x,
           'base64_encode': lambda x: base64.b64encode(x.encode()).decode() if isinstance(x, str) else x,
       }
       
       if transform in transformations:
           return transformations[transform](value)
       # ... rest of method
   ```

2. **Add tests**:
   ```python
   def test_reverse_transform(self):
       """Test reverse transformation."""
       config = {'inputs': []}
       extractor = StructuredDataExtractor(config)
       result = extractor._apply_transform("hello", "reverse")
       self.assertEqual(result, "olleh")
   ```

3. **Update documentation** in `user-guide.md`.

### 2. Adding New Jinja2 Filters

**Goal**: Add custom filters for template processing.

**Implementation**:

1. **Add to filter registration** in `TemplateProcessor._register_custom_filters()`:
   ```python
   def _register_custom_filters(self):
       # ... existing filters ...
       
       def pluralize(word, count):
           """Pluralize word based on count."""
           if count == 1:
               return word
           # Simple pluralization rules
           if word.endswith('y'):
               return word[:-1] + 'ies'
           elif word.endswith(('s', 'sh', 'ch', 'x', 'z')):
               return word + 'es'
           else:
               return word + 's'
       
       self.env.filters['pluralize'] = pluralize
   ```

2. **Add tests**:
   ```python
   def test_pluralize_filter(self):
       """Test pluralize filter functionality."""
       processor = TemplateProcessor(self.config, {})
       filter_func = processor.env.filters['pluralize']
       
       self.assertEqual(filter_func('cat', 1), 'cat')
       self.assertEqual(filter_func('cat', 2), 'cats')
       self.assertEqual(filter_func('city', 2), 'cities')
   ```

### 3. Adding New File Format Support

**Goal**: Add support for TOML files.

**Implementation**:

1. **Install dependencies**:
   ```bash
   pip install toml
   ```

2. **Update supported formats**:
   ```python
   SUPPORTED_FORMATS: Dict[str, str] = {
       # ... existing formats ...
       '.toml': 'toml',
   }
   ```

3. **Add parser**:
   ```python
   def _load_file(self, file_path: Path, format_type: str) -> Dict[str, Any]:
       # ... existing parsers ...
       
       elif format_type == 'toml':
           import toml
           with open(file_path, 'r', encoding='utf-8') as f:
               return toml.load(f)
   ```

4. **Add tests**:
   ```python
   def test_load_toml_file(self):
       """Test TOML file loading."""
       toml_content = """
       [app]
       name = "TestApp"
       version = "1.0.0"
       """
       toml_file = self.test_dir / "test.toml"
       toml_file.write_text(toml_content)
       
       extractor = StructuredDataExtractor({})
       result = extractor._load_file(toml_file, 'toml')
       
       self.assertEqual(result['app']['name'], 'TestApp')
   ```

### 4. Adding Configuration Validation Rules

**Goal**: Add new validation rules to `validate_config.py`.

**Implementation**:

1. **Add validation method**:
   ```python
   def _validate_security_settings(self, security: Any) -> None:
       """Validate security configuration section."""
       if not isinstance(security, dict):
           self.errors.append("'security' must be an object")
           return
       
       # Check required security fields
       required_fields = ['encryption', 'authentication']
       for field in required_fields:
           if field not in security:
               self.errors.append(f"Missing required security field: {field}")
   ```

2. **Call from main validation**:
   ```python
   def _validate_config(self, config: Dict[str, Any], config_dir: Path) -> bool:
       # ... existing validations ...
       
       # Validate security settings
       if 'security' in config:
           self._validate_security_settings(config['security'])
   ```

## Code Standards

### Code Style

Template Forge follows PEP 8 with these specific guidelines:

#### Formatting
```bash
# Format code with black
black template_forge/ tests/

# Check formatting
black --check template_forge/ tests/
```

#### Linting
```bash
# Run flake8 linter
flake8 template_forge/ tests/

# Configuration in pyproject.toml
[tool.flake8]
max-line-length = 88
extend-ignore = E203, W503
```

#### Type Checking
```bash
# Run mypy type checker
mypy template_forge/

# Configuration in pyproject.toml
[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
```

### Documentation Standards

#### Docstrings
Use Google-style docstrings:

```python
def extract_tokens(self) -> Dict[str, Any]:
    """Extract tokens from all configured input sources.
    
    Processes all input files defined in the configuration,
    extracts tokens using specified key paths, and applies
    any transformations or regex filters.
    
    Returns:
        Dictionary mapping token names to their extracted values.
        
    Raises:
        ValueError: If configuration is invalid.
        FileNotFoundError: If input file is missing.
        
    Example:
        >>> extractor = StructuredDataExtractor(config)
        >>> tokens = extractor.extract_tokens()
        >>> print(tokens['app_name'])
        'MyApplication'
    """
```

#### Comments
- Use clear, descriptive comments for complex logic
- Avoid obvious comments
- Include TODO comments for future improvements

#### Type Hints
Use comprehensive type hints:

```python
from typing import Any, Dict, List, Optional, Protocol, Union

def process_data(
    data: Dict[str, Any], 
    filters: Optional[List[str]] = None
) -> Union[str, Dict[str, Any]]:
    """Process data with optional filters."""
    pass
```

### Git Workflow

#### Branch Naming
- `feature/feature-name`: New features
- `bugfix/issue-description`: Bug fixes  
- `docs/update-description`: Documentation updates
- `refactor/component-name`: Code refactoring

#### Commit Messages
Follow conventional commits:

```
feat: add support for TOML file format

- Add TOML parser to StructuredDataExtractor
- Update supported formats list
- Add comprehensive tests for TOML parsing
- Update documentation with TOML examples

Closes #123
```

#### Pull Request Process
1. Create feature branch from `main`
2. Implement changes with tests
3. Update documentation
4. Run full test suite
5. Submit pull request with clear description

## Contributing

### Getting Started

1. **Find an Issue**: Look for issues labeled `good-first-issue` or `help-wanted`
2. **Discuss**: Comment on the issue to discuss your approach
3. **Fork**: Fork the repository to your GitHub account
4. **Implement**: Make your changes following the coding standards
5. **Test**: Ensure all tests pass and add new tests for your changes
6. **Document**: Update documentation as needed
7. **Submit**: Create a pull request

### Types of Contributions

#### Bug Fixes
- Report bugs with minimal reproduction cases
- Include system information and error messages
- Propose fixes with tests

#### Feature Requests  
- Describe the use case and problem being solved
- Provide examples of desired behavior
- Discuss implementation approach

#### Documentation
- Fix typos and improve clarity
- Add examples and use cases
- Translate documentation to other languages

#### Performance Improvements
- Profile performance bottlenecks
- Implement optimizations with benchmarks
- Maintain backward compatibility

### Code Review Process

#### For Contributors
- Respond to feedback promptly
- Make requested changes in separate commits
- Keep pull requests focused and small

#### For Reviewers
- Provide constructive feedback
- Test changes locally when possible
- Focus on code quality, performance, and maintainability

## Release Process

### Version Management

Template Forge uses semantic versioning (SemVer):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

#### Pre-Release
1. **Update version** in `pyproject.toml`
2. **Update CHANGELOG.md** with new features and fixes
3. **Run full test suite**: `python -m pytest tests/ -v`
4. **Validate examples**: `python validate_config.py examples/*/config.yaml`
5. **Build documentation** and verify links
6. **Test installation** in clean environment

#### Release
1. **Create release tag**: `git tag v1.2.3`
2. **Push tag**: `git push origin v1.2.3`
3. **Build package**: `python -m build`
4. **Upload to PyPI**: `python -m twine upload dist/*`
5. **Create GitHub release** with changelog

#### Post-Release
1. **Update main branch** with any release fixes
2. **Monitor PyPI** for successful upload
3. **Update documentation** links if needed
4. **Announce release** in relevant channels

### Development Workflow

#### Feature Development
1. Create feature branch: `git checkout -b feature/new-feature`
2. Implement changes with tests
3. Run test suite: `python -m pytest tests/ -v`
4. Update documentation
5. Submit pull request

#### Bug Fixes
1. Create bugfix branch: `git checkout -b bugfix/issue-description`
2. Write failing test that reproduces the bug
3. Implement fix
4. Verify test passes
5. Submit pull request

#### Testing Changes
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test categories
python -m pytest tests/test_extractor.py -v
python -m pytest tests/test_processor.py -v
python -m pytest tests/test_integration.py -v

# Run with coverage
python -m pytest tests/ --cov=template_forge --cov-report=html

# Test CLI functionality
template-forge examples/basic/config.yaml
```

---

## Resources

- **GitHub Repository**: [template_forge](https://github.com/CarloFornari/template_forge)
- **Issue Tracker**: [GitHub Issues](https://github.com/CarloFornari/template_forge/issues)
- **Discussions**: [GitHub Discussions](https://github.com/CarloFornari/template_forge/discussions)
- **Documentation**: [User Guide](user-guide.md) | [API Reference](API.md)

## Getting Help

1. **Check Documentation**: Read the User Guide and API reference
2. **Search Issues**: Look for existing issues and solutions
3. **Ask Questions**: Use GitHub Discussions for general questions
4. **Report Bugs**: Create detailed bug reports with reproduction steps

Happy coding! 🚀