"""
Additional coverage tests for edge cases
"""

import logging


def test_no_templates_defined_error(tmp_path, caplog):
    """Test error when config has neither templates nor template_dir (line 207)"""
    caplog.set_level(logging.ERROR)

    from template_forge.core import TemplateProcessor

    config = {
        "static_tokens": {"test": "value"}
        # No 'templates' or 'template_dir'
    }

    tokens = {"test": "value"}
    processor = TemplateProcessor(config, tokens)
    processor.process_templates()

    # Should log error about no templates
    assert "No templates defined" in caplog.text


def test_invalid_filter_spec_type(tmp_path, caplog):
    """Test handling of invalid filter spec type (lines 171-174)"""
    import logging
    import sys

    caplog.set_level(logging.WARNING)

    from template_forge.core import StructuredDataExtractor, TemplateProcessor

    # Create a valid module
    module_code = """
def valid_filter(s):
    return s.upper()
"""
    (tmp_path / "valid_module.py").write_text(module_code)

    try:
        sys.path.insert(0, str(tmp_path))

        config = {
            "custom_filters": [
                {
                    "module": "valid_module",
                    "filters": [
                        123  # Invalid: not a string or dict
                    ],
                }
            ],
            "static_tokens": {"test": "value"},
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }

        (tmp_path / "t.j2").write_text("{{test}}")

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()
        processor = TemplateProcessor(config, tokens)

        # Should log warning about invalid filter spec
        assert "Invalid filter spec" in caplog.text

    finally:
        if str(tmp_path) in sys.path:
            sys.path.remove(str(tmp_path))


def test_generic_import_error_in_custom_filter(tmp_path, caplog):
    """Test handling of generic exceptions during module import (lines 97-104)"""
    import logging
    import sys

    caplog.set_level(logging.ERROR)

    from template_forge.core import StructuredDataExtractor, TemplateProcessor

    # Create a module that raises an exception on import
    module_code = """
raise RuntimeError("Intentional error during import")
"""
    (tmp_path / "bad_module.py").write_text(module_code)

    try:
        sys.path.insert(0, str(tmp_path))

        config = {
            "custom_filters": [{"module": "bad_module", "filters": ["some_func"]}],
            "static_tokens": {"test": "value"},
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }

        (tmp_path / "t.j2").write_text("{{test}}")

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()
        processor = TemplateProcessor(config, tokens)

        # Should log error about import failure
        assert "Error importing custom filter module" in caplog.text

    finally:
        if str(tmp_path) in sys.path:
            sys.path.remove(str(tmp_path))
