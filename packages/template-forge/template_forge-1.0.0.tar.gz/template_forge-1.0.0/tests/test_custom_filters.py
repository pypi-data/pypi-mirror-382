"""Tests for REQ-ADV-005: Custom Jinja2 Filter Registration

This module tests the support for loading custom Jinja2 filters from external
Python modules via configuration.
"""

import sys

from template_forge.core import StructuredDataExtractor, TemplateProcessor


class TestBasicFilterLoading:
    """Test basic custom filter loading functionality."""

    def test_REQ_ADV_005_load_filter_from_module(self, tmp_path):
        """Test loading a custom filter from a Python module."""
        # Create a custom filter module
        filter_module = tmp_path / "custom_filters.py"
        filter_module.write_text("""
def reverse_string(value):
    '''Reverse a string.'''
    return value[::-1]

def add_prefix(value, prefix='PREFIX'):
    '''Add a prefix to a string.'''
    return f"{prefix}_{value}"
""")

        # Add module path to sys.path
        sys.path.insert(0, str(tmp_path))

        try:
            config = {
                "custom_filters": [
                    {
                        "module": "custom_filters",
                        "filters": ["reverse_string", "add_prefix"],
                    }
                ],
                "static_tokens": {"test_value": "hello"},
                "templates": [{"template": "t.j2", "output": "o.txt"}],
            }

            extractor = StructuredDataExtractor(config)
            tokens = extractor.extract_tokens()

            processor = TemplateProcessor(config, tokens)

            # Verify filters are registered
            assert "reverse_string" in processor.env.filters
            assert "add_prefix" in processor.env.filters

            # Test the filters work
            template_str = "{{ test_value | reverse_string }}"
            template = processor.env.from_string(template_str)
            result = template.render(tokens)
            assert result == "olleh"

            # Test filter with arguments
            template_str = "{{ test_value | add_prefix('CUSTOM') }}"
            template = processor.env.from_string(template_str)
            result = template.render(tokens)
            assert result == "CUSTOM_hello"

        finally:
            # Clean up sys.path
            sys.path.remove(str(tmp_path))

    def test_REQ_ADV_005_filter_rename(self, tmp_path):
        """Test renaming a filter during registration."""
        filter_module = tmp_path / "my_filters.py"
        filter_module.write_text("""
def sanitize_filename(value):
    '''Remove unsafe characters from filename.'''
    import re
    return re.sub(r'[^a-zA-Z0-9_-]', '_', value)
""")

        sys.path.insert(0, str(tmp_path))

        try:
            config = {
                "custom_filters": [
                    {
                        "module": "my_filters",
                        "filters": [
                            {"safe_filename": "sanitize_filename"}  # Rename
                        ],
                    }
                ],
                "static_tokens": {"file_name": "my file/name.txt"},
                "templates": [{"template": "t.j2", "output": "o.txt"}],
            }

            extractor = StructuredDataExtractor(config)
            tokens = extractor.extract_tokens()

            processor = TemplateProcessor(config, tokens)

            # Verify filter is registered with new name
            assert "safe_filename" in processor.env.filters
            assert "sanitize_filename" not in processor.env.filters

            # Test the filter works
            template_str = "{{ file_name | safe_filename }}"
            template = processor.env.from_string(template_str)
            result = template.render(tokens)
            assert result == "my_file_name_txt"

        finally:
            sys.path.remove(str(tmp_path))

    def test_REQ_ADV_005_multiple_modules(self, tmp_path):
        """Test loading filters from multiple modules."""
        # Create first module
        module1 = tmp_path / "filters_a.py"
        module1.write_text("""
def double_value(value):
    '''Double a numeric value.'''
    return value * 2
""")

        # Create second module
        module2 = tmp_path / "filters_b.py"
        module2.write_text("""
def triple_value(value):
    '''Triple a numeric value.'''
    return value * 3
""")

        sys.path.insert(0, str(tmp_path))

        try:
            config = {
                "custom_filters": [
                    {"module": "filters_a", "filters": ["double_value"]},
                    {"module": "filters_b", "filters": ["triple_value"]},
                ],
                "static_tokens": {"number": 5},
                "templates": [{"template": "t.j2", "output": "o.txt"}],
            }

            extractor = StructuredDataExtractor(config)
            tokens = extractor.extract_tokens()

            processor = TemplateProcessor(config, tokens)

            # Verify both filters are registered
            assert "double_value" in processor.env.filters
            assert "triple_value" in processor.env.filters

            # Test both filters
            template_str = "{{ number | double_value }}"
            template = processor.env.from_string(template_str)
            assert template.render(tokens) == "10"

            template_str = "{{ number | triple_value }}"
            template = processor.env.from_string(template_str)
            assert template.render(tokens) == "15"

        finally:
            sys.path.remove(str(tmp_path))


class TestFilterArguments:
    """Test filters with various argument signatures."""

    def test_REQ_ADV_005_filter_with_default_argument(self, tmp_path):
        """Test filter with default argument."""
        filter_module = tmp_path / "arg_filters.py"
        filter_module.write_text("""
def pad_string(value, width=10, char=' '):
    '''Pad a string to specified width.'''
    return str(value).ljust(width, char)
""")

        sys.path.insert(0, str(tmp_path))

        try:
            config = {
                "custom_filters": [
                    {"module": "arg_filters", "filters": ["pad_string"]}
                ],
                "static_tokens": {"text": "hello"},
                "templates": [{"template": "t.j2", "output": "o.txt"}],
            }

            extractor = StructuredDataExtractor(config)
            tokens = extractor.extract_tokens()
            processor = TemplateProcessor(config, tokens)

            # Test with default arguments
            template_str = "{{ text | pad_string }}"
            template = processor.env.from_string(template_str)
            result = template.render(tokens)
            assert result == "hello     "
            assert len(result) == 10

            # Test with custom width
            template_str = "{{ text | pad_string(15) }}"
            template = processor.env.from_string(template_str)
            result = template.render(tokens)
            assert len(result) == 15

            # Test with custom char
            template_str = "{{ text | pad_string(10, '-') }}"
            template = processor.env.from_string(template_str)
            result = template.render(tokens)
            assert result == "hello-----"

        finally:
            sys.path.remove(str(tmp_path))

    def test_REQ_ADV_005_filter_with_multiple_args(self, tmp_path):
        """Test filter with multiple required arguments."""
        filter_module = tmp_path / "multi_arg_filters.py"
        filter_module.write_text("""
def format_range(value, min_val, max_val):
    '''Format a value with min/max range.'''
    return f"{value} (range: {min_val}-{max_val})"
""")

        sys.path.insert(0, str(tmp_path))

        try:
            config = {
                "custom_filters": [
                    {"module": "multi_arg_filters", "filters": ["format_range"]}
                ],
                "static_tokens": {"value": 50},
                "templates": [{"template": "t.j2", "output": "o.txt"}],
            }

            extractor = StructuredDataExtractor(config)
            tokens = extractor.extract_tokens()
            processor = TemplateProcessor(config, tokens)

            template_str = "{{ value | format_range(0, 100) }}"
            template = processor.env.from_string(template_str)
            result = template.render(tokens)
            assert result == "50 (range: 0-100)"

        finally:
            sys.path.remove(str(tmp_path))


class TestErrorHandling:
    """Test error handling for custom filter loading."""

    def test_REQ_ADV_005_module_not_found_error(self, tmp_path, caplog):
        """Test error when module cannot be imported."""
        config = {
            "custom_filters": [
                {"module": "nonexistent_module", "filters": ["some_filter"]}
            ],
            "static_tokens": {},
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()
        processor = TemplateProcessor(config, tokens)

        # Should log error but not crash
        assert (
            "Failed to import custom filter module 'nonexistent_module'" in caplog.text
        )

    def test_REQ_ADV_005_function_not_found_error(self, tmp_path, caplog):
        """Test error when function is not found in module."""
        filter_module = tmp_path / "missing_func.py"
        filter_module.write_text("""
def existing_filter(value):
    return value
""")

        sys.path.insert(0, str(tmp_path))

        try:
            config = {
                "custom_filters": [
                    {"module": "missing_func", "filters": ["nonexistent_function"]}
                ],
                "static_tokens": {},
                "templates": [{"template": "t.j2", "output": "o.txt"}],
            }

            extractor = StructuredDataExtractor(config)
            tokens = extractor.extract_tokens()
            processor = TemplateProcessor(config, tokens)

            # Should log error
            assert (
                "Function 'nonexistent_function' not found in module 'missing_func'"
                in caplog.text
            )

        finally:
            sys.path.remove(str(tmp_path))

    def test_REQ_ADV_005_non_callable_error(self, tmp_path, caplog):
        """Test error when specified name is not callable."""
        filter_module = tmp_path / "non_callable.py"
        filter_module.write_text("""
# This is a constant, not a function
MY_CONSTANT = 42
""")

        sys.path.insert(0, str(tmp_path))

        try:
            config = {
                "custom_filters": [
                    {"module": "non_callable", "filters": ["MY_CONSTANT"]}
                ],
                "static_tokens": {},
                "templates": [{"template": "t.j2", "output": "o.txt"}],
            }

            extractor = StructuredDataExtractor(config)
            tokens = extractor.extract_tokens()
            processor = TemplateProcessor(config, tokens)

            # Should log error
            assert (
                "'MY_CONSTANT' in module 'non_callable' is not callable" in caplog.text
            )

        finally:
            sys.path.remove(str(tmp_path))

    def test_REQ_ADV_005_invalid_config_format(self, tmp_path, caplog):
        """Test warning for invalid configuration format."""
        config = {
            "custom_filters": [
                "not_a_dict"  # Should be a dict
            ],
            "static_tokens": {},
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()
        processor = TemplateProcessor(config, tokens)

        # Should log warning
        assert "Invalid custom filter configuration" in caplog.text

    def test_REQ_ADV_005_missing_module_key(self, tmp_path, caplog):
        """Test warning when 'module' key is missing."""
        config = {
            "custom_filters": [
                {
                    "filters": ["some_filter"]
                    # Missing 'module' key
                }
            ],
            "static_tokens": {},
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()
        processor = TemplateProcessor(config, tokens)

        # Should log warning
        assert "Custom filter config missing 'module' key" in caplog.text

    def test_REQ_ADV_005_missing_filters_key(self, tmp_path, caplog):
        """Test warning when 'filters' key is missing."""
        config = {
            "custom_filters": [
                {
                    "module": "some_module"
                    # Missing 'filters' key
                }
            ],
            "static_tokens": {},
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()
        processor = TemplateProcessor(config, tokens)

        # Should log warning
        assert "No filters specified for module 'some_module'" in caplog.text


class TestRealWorldScenarios:
    """Test real-world use cases for custom filters."""

    def test_REQ_ADV_005_domain_specific_filters(self, tmp_path):
        """Test loading domain-specific filters (e.g., AUTOSAR)."""
        filter_module = tmp_path / "autosar_filters.py"
        filter_module.write_text("""
def format_component_name(value, prefix='SWC'):
    '''Format AUTOSAR component name.'''
    return f"{prefix}_{value.replace(' ', '_').upper()}"

def calculate_can_id(base_id, offset=0):
    '''Calculate CAN message ID.'''
    return hex(int(base_id, 16) + offset)
""")

        sys.path.insert(0, str(tmp_path))

        try:
            config = {
                "custom_filters": [
                    {
                        "module": "autosar_filters",
                        "filters": ["format_component_name", "calculate_can_id"],
                    }
                ],
                "static_tokens": {
                    "component": "engine control",
                    "base_can_id": "0x100",
                },
                "templates": [{"template": "t.j2", "output": "o.txt"}],
            }

            extractor = StructuredDataExtractor(config)
            tokens = extractor.extract_tokens()
            processor = TemplateProcessor(config, tokens)

            # Test component name formatting
            template_str = "{{ component | format_component_name }}"
            template = processor.env.from_string(template_str)
            result = template.render(tokens)
            assert result == "SWC_ENGINE_CONTROL"

            # Test with custom prefix
            template_str = "{{ component | format_component_name('APP') }}"
            template = processor.env.from_string(template_str)
            result = template.render(tokens)
            assert result == "APP_ENGINE_CONTROL"

            # Test CAN ID calculation
            template_str = "{{ base_can_id | calculate_can_id(5) }}"
            template = processor.env.from_string(template_str)
            result = template.render(tokens)
            assert result == "0x105"

        finally:
            sys.path.remove(str(tmp_path))

    def test_REQ_ADV_005_chaining_custom_and_builtin_filters(self, tmp_path):
        """Test chaining custom filters with built-in filters."""
        filter_module = tmp_path / "chain_filters.py"
        filter_module.write_text("""
def wrap_quotes(value):
    '''Wrap value in quotes.'''
    return f'"{value}"'
""")

        sys.path.insert(0, str(tmp_path))

        try:
            config = {
                "custom_filters": [
                    {"module": "chain_filters", "filters": ["wrap_quotes"]}
                ],
                "static_tokens": {"text": "hello world"},
                "templates": [{"template": "t.j2", "output": "o.txt"}],
            }

            extractor = StructuredDataExtractor(config)
            tokens = extractor.extract_tokens()
            processor = TemplateProcessor(config, tokens)

            # Chain custom filter with built-in upper filter
            template_str = "{{ text | upper | wrap_quotes }}"
            template = processor.env.from_string(template_str)
            result = template.render(tokens)
            assert result == '"HELLO WORLD"'

            # Chain in different order
            template_str = "{{ text | wrap_quotes | upper }}"
            template = processor.env.from_string(template_str)
            result = template.render(tokens)
            assert result == '"HELLO WORLD"'

        finally:
            sys.path.remove(str(tmp_path))

    def test_REQ_ADV_005_filter_with_template_generation(self, tmp_path):
        """Test using custom filters in actual template generation."""
        filter_module = tmp_path / "code_filters.py"
        filter_module.write_text("""
def c_variable_name(value):
    '''Convert to valid C variable name.'''
    import re
    # Remove invalid characters
    name = re.sub(r'[^a-zA-Z0-9_]', '_', value)
    # Ensure doesn't start with digit
    if name and name[0].isdigit():
        name = '_' + name
    return name

def c_define_name(value):
    '''Convert to C define name (uppercase with underscores).'''
    import re
    name = re.sub(r'[^a-zA-Z0-9_]', '_', value)
    return name.upper()
""")

        sys.path.insert(0, str(tmp_path))

        try:
            config = {
                "template_dir": str(tmp_path),
                "custom_filters": [
                    {
                        "module": "code_filters",
                        "filters": ["c_variable_name", "c_define_name"],
                    }
                ],
                "static_tokens": {"signal_name": "Engine.RPM", "max_value": "8000"},
                "templates": [{"template": "t.j2", "output": "o.txt"}],
            }

            template_file = tmp_path / "header.h.j2"
            template_file.write_text(
                """
#ifndef {{ signal_name | c_define_name }}_H
#define {{ signal_name | c_define_name }}_H

#define MAX_{{ signal_name | c_define_name }} {{ max_value }}

extern int {{ signal_name | c_variable_name }};

#endif
""".strip()
            )

            extractor = StructuredDataExtractor(config)
            tokens = extractor.extract_tokens()
            processor = TemplateProcessor(config, tokens)

            # Render the template
            template = processor.env.get_template("header.h.j2")
            result = template.render(tokens)

            # Verify the output
            assert "#ifndef ENGINE_RPM_H" in result
            assert "#define ENGINE_RPM_H" in result
            assert "#define MAX_ENGINE_RPM 8000" in result
            assert "extern int Engine_RPM;" in result

        finally:
            sys.path.remove(str(tmp_path))


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_REQ_ADV_005_empty_custom_filters_config(self, tmp_path):
        """Test with empty custom_filters list."""
        config = {
            "custom_filters": [],
            "static_tokens": {},
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()
        processor = TemplateProcessor(config, tokens)

        # Should not crash, built-in filters should still work
        assert "upper" in processor.env.filters

    def test_REQ_ADV_005_no_custom_filters_config(self, tmp_path):
        """Test without custom_filters key in config."""
        config = {
            "static_tokens": {},
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()
        processor = TemplateProcessor(config, tokens)

        # Should work normally with built-in filters only
        assert "upper" in processor.env.filters

    def test_REQ_ADV_005_filter_overwrites_builtin(self, tmp_path, caplog):
        """Test that custom filter can overwrite built-in filter."""
        filter_module = tmp_path / "overwrite_filters.py"
        filter_module.write_text("""
def upper(value):
    '''Custom upper that adds exclamation.'''
    return value.upper() + '!'
""")

        sys.path.insert(0, str(tmp_path))

        try:
            config = {
                "custom_filters": [
                    {"module": "overwrite_filters", "filters": ["upper"]}
                ],
                "static_tokens": {"text": "hello"},
                "templates": [{"template": "t.j2", "output": "o.txt"}],
            }

            extractor = StructuredDataExtractor(config)
            tokens = extractor.extract_tokens()
            processor = TemplateProcessor(config, tokens)

            # Custom filter should be used
            template_str = "{{ text | upper }}"
            template = processor.env.from_string(template_str)
            result = template.render(tokens)
            assert result == "HELLO!"

        finally:
            sys.path.remove(str(tmp_path))

    def test_REQ_ADV_005_invalid_filter_spec_dict(self, tmp_path, caplog):
        """Test invalid filter spec with multiple keys in dict."""
        filter_module = tmp_path / "valid_filter.py"
        filter_module.write_text("""
def my_filter(value):
    return value
""")

        sys.path.insert(0, str(tmp_path))

        try:
            config = {
                "custom_filters": [
                    {
                        "module": "valid_filter",
                        "filters": [
                            {
                                "name1": "func1",
                                "name2": "func2",
                            }  # Invalid: multiple keys
                        ],
                    }
                ],
                "static_tokens": {},
                "templates": [{"template": "t.j2", "output": "o.txt"}],
            }

            extractor = StructuredDataExtractor(config)
            tokens = extractor.extract_tokens()
            processor = TemplateProcessor(config, tokens)

            # Should log warning
            assert "Invalid filter spec" in caplog.text

        finally:
            sys.path.remove(str(tmp_path))


# Additional coverage tests for error paths


def test_custom_filter_import_error(tmp_path, caplog):
    """Test handling ImportError when loading custom filter module (lines 150-154)"""
    import logging

    caplog.set_level(logging.ERROR)

    from template_forge.core import StructuredDataExtractor, TemplateProcessor

    config = {
        "custom_filters": [
            {"module": "nonexistent_module_xyz", "filters": ["some_func"]}
        ],
        "static_tokens": {"test": "value"},
        "templates": [{"template": "t.j2", "output": "o.txt"}],
    }

    (tmp_path / "t.j2").write_text("{{test}}")

    extractor = StructuredDataExtractor(config)
    tokens = extractor.extract_tokens()
    processor = TemplateProcessor(config, tokens)

    # Should log error about failed import
    assert "Failed to import custom filter module" in caplog.text


def test_custom_filter_function_not_found(tmp_path, caplog):
    """Test handling when filter function doesn't exist in module (lines 216-222)"""
    import logging
    import sys

    caplog.set_level(logging.ERROR)

    from template_forge.core import StructuredDataExtractor, TemplateProcessor

    # Create a module with a function
    module_code = """
def existing_function(s):
    return s.upper()
"""
    (tmp_path / "test_module.py").write_text(module_code)

    try:
        sys.path.insert(0, str(tmp_path))

        config = {
            "custom_filters": [
                {
                    "module": "test_module",
                    "filters": ["nonexistent_function"],  # This function doesn't exist
                }
            ],
            "static_tokens": {"test": "value"},
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }

        (tmp_path / "t.j2").write_text("{{test}}")

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()
        processor = TemplateProcessor(config, tokens)

        # Should log error about function not found
        assert "not found in module" in caplog.text

    finally:
        sys.path.remove(str(tmp_path))


def test_custom_filter_not_callable(tmp_path, caplog):
    """Test handling when filter 'function' is not callable (line 207)"""
    import logging
    import sys

    caplog.set_level(logging.ERROR)

    from template_forge.core import StructuredDataExtractor, TemplateProcessor

    # Create a module with a non-callable attribute (module-level constant)
    module_code = """# Module-level constant, not a function
NOT_CALLABLE = "This is a constant string, not a function"
"""
    (tmp_path / "filter_mod.py").write_text(module_code)

    try:
        sys.path.insert(0, str(tmp_path))

        config = {
            "custom_filters": [{"module": "filter_mod", "filters": ["NOT_CALLABLE"]}],
            "static_tokens": {"test": "value"},
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }

        (tmp_path / "t.j2").write_text("{{test}}")

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()
        processor = TemplateProcessor(config, tokens)

        # Should log error about not callable
        assert "is not callable" in caplog.text

    finally:
        if str(tmp_path) in sys.path:
            sys.path.remove(str(tmp_path))


def test_template_discovery_no_templates_found(tmp_path, caplog):
    """Test warning when template_dir has no .j2 files (lines 171-174)"""
    import logging

    caplog.set_level(logging.WARNING)

    from template_forge.core import TemplateForge

    # Create empty template directory
    template_dir = tmp_path / "templates"
    template_dir.mkdir()

    config_file = tmp_path / "config.yaml"
    config_file.write_text(f"""
static_tokens:
  test: value
template_dir: {template_dir}
""")

    forge = TemplateForge(config_file)
    forge.run()

    # Should log warning about no templates found
    assert "No .j2 templates found" in caplog.text
