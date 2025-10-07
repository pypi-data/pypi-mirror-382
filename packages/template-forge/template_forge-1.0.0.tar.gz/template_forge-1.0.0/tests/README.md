# Template Forge Test Suite

This directory contains comprehensive unit and integration tests for the Template Forge project.

## Test Structure

### Unit Tests

- **`test_extractor.py`** - Tests for `StructuredDataExtractor` class
  - Token extraction from JSON, YAML, XML, ARXML files
  - Regex filtering and value transformations
  - Error handling for missing/invalid files
  - Case-insensitive key matching
  - Array and nested object handling

- **`test_processor.py`** - Tests for `TemplateProcessor` class
  - Jinja2 template processing
  - Custom filter registration and functionality
  - Template-specific token overrides
  - Output directory creation
  - Error handling for missing templates

- **`test_template_forge.py`** - Tests for `TemplateForge` main class
  - Configuration loading from YAML files
  - Error handling for invalid configurations
  - Integration between extractor and processor components
  - Logging configuration

### Integration Tests

- **`test_integration.py`** - End-to-end workflow tests
  - Complete file-to-output generation workflows
  - Multi-format token extraction scenarios
  - Template-specific token override validation
  - Complex regex and transformation combinations
  - Error scenarios (missing files, unsupported formats)

## Running Tests

### Run All Tests
```bash
python tests/run_tests.py
```

### Run Specific Test Suites
```bash
python tests/run_tests.py extractor    # StructuredDataExtractor tests
python tests/run_tests.py processor    # TemplateProcessor tests  
python tests/run_tests.py forge        # TemplateForge tests
python tests/run_tests.py integration  # Integration tests
```

### Alternative Test Runner
If you have pytest installed:
```bash
pytest tests/ -v
```

## Test Coverage

The test suite covers:

### StructuredDataExtractor (16 tests)
- ✅ Initialization and configuration
- ✅ File format support validation  
- ✅ JSON/YAML/XML/ARXML parsing
- ✅ Dot notation key path extraction
- ✅ Regex filtering with capture groups
- ✅ Value transformations (type conversions, case changes)
- ✅ Array handling and indexing
- ✅ XML attribute extraction
- ✅ Error handling for unsupported formats
- ✅ Missing file error handling
- ✅ Case-insensitive key matching

### TemplateProcessor (11 tests)  
- ✅ Jinja2 environment setup
- ✅ Custom filter registration (snake_case, camel_case, etc.)
- ✅ Template rendering with tokens
- ✅ Loop and conditional processing
- ✅ Template-specific token overrides
- ✅ Output directory auto-creation
- ✅ Template error handling
- ✅ Missing template file handling

### TemplateForge (10 tests)
- ✅ YAML configuration loading
- ✅ Configuration validation
- ✅ Error handling for invalid YAML
- ✅ Component orchestration
- ✅ Logging setup and output
- ✅ End-to-end execution flow

### Integration Tests (7 tests)
- ✅ Complete multi-format workflow
- ✅ Token extraction accuracy across all formats
- ✅ Template generation with real data
- ✅ Complex regex and transformation scenarios
- ✅ Template-specific token override workflows
- ✅ Error handling integration
- ✅ File format validation

## Test Fixtures

Tests use temporary files and directories that are automatically cleaned up after each test. The integration tests create realistic sample data files that mirror the examples in the main project.

## Key Test Scenarios

1. **Multi-format Token Extraction**: Validates extraction from JSON, YAML, XML, and ARXML files using unified dot notation
2. **Regex Processing**: Tests complex regex patterns with capture groups and transformations
3. **Template Generation**: Verifies Jinja2 template rendering with extracted tokens
4. **Error Handling**: Ensures graceful handling of invalid configurations, missing files, and unsupported formats
5. **Custom Filters**: Validates all custom Jinja2 filters for case transformations
6. **Token Overrides**: Tests template-specific token precedence over global tokens

## Dependencies

- Python 3.8+
- PyYAML (for configuration parsing)
- Jinja2 (for template processing)
- unittest (built-in, for test framework)

Optional:
- pytest (alternative test runner)
- pytest-cov (for coverage reporting)

## Coverage Reporting

To run tests with coverage reporting (requires pytest-cov):
```bash
pytest tests/ --cov=template_generator --cov-report=html
```

This generates an HTML coverage report in `htmlcov/index.html`.