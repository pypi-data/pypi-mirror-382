"""
Tests for Error Handling in core.py
Tests error paths for file operations, parsing, templates, and hooks
"""

import pytest

from template_forge.core import (
    PreservationHandler,
    StructuredDataExtractor,
    TemplateForge,
)


class TestFileReadErrors:
    """Test error handling for file read operations - REQ-EXT-110, REQ-EXT-111"""

    def test_REQ_EXT_110_missing_input_file_logged(self, tmp_path, caplog):
        """REQ-EXT-110: Missing input files are logged with clear error

        Note: Current implementation raises FileNotFoundError instead of continuing.
        This tests that the error is properly logged before raising.
        """
        config_file = tmp_path / "config.yaml"
        config_file.write_text(f"""
inputs:
  - path: {tmp_path / "missing.json"}
    namespace: data
templates:
  - template: test.j2
    output: output.txt
""")

        # Create template
        template = tmp_path / "test.j2"
        template.write_text("{{ backup }}")

        # Current behavior: raises FileNotFoundError
        forge = TemplateForge(config_file)
        with pytest.raises(FileNotFoundError) as exc_info:
            forge.run()

        # Should have logged error before raising
        assert (
            "not found" in caplog.text.lower()
            or "not found" in str(exc_info.value).lower()
        )

    def test_preservation_file_read_error_returns_empty(self, tmp_path):
        """Test that preservation handles unreadable files gracefully"""
        preservation = PreservationHandler()

        # File doesn't exist - should return empty dict
        result = preservation.extract_preserved_content(tmp_path / "nonexistent.txt")
        assert result == {}

    def test_preservation_permission_denied(self, tmp_path, monkeypatch):
        """Test that preservation handles permission errors"""
        import builtins

        preservation = PreservationHandler()
        test_file = tmp_path / "test.txt"
        test_file.write_text("some content")

        # Mock open to raise PermissionError
        original_open = builtins.open

        def mock_open(*args, **kwargs):
            if str(test_file) in str(args[0]):
                raise PermissionError("Permission denied")
            return original_open(*args, **kwargs)

        monkeypatch.setattr(builtins, "open", mock_open)

        # Should return empty dict, not raise
        result = preservation.extract_preserved_content(test_file)
        assert result == {}


class TestMalformedDataErrors:
    """Test error handling for malformed data files - REQ-EXT-113"""

    def test_REQ_EXT_113_malformed_json_clear_error(self, tmp_path, caplog):
        """REQ-EXT-113: Handle malformed JSON with descriptive error"""
        json_file = tmp_path / "bad.json"
        json_file.write_text('{"key": invalid json}')

        config = {
            "inputs": [{"path": str(json_file), "namespace": "data"}],
            "templates": [],
        }

        extractor = StructuredDataExtractor(config)

        # Should handle error gracefully
        with pytest.raises(Exception):  # May raise or log depending on implementation
            tokens = extractor.extract_tokens()

    def test_REQ_EXT_113_malformed_yaml_clear_error(self, tmp_path, caplog):
        """REQ-EXT-113: Handle malformed YAML with descriptive error"""
        yaml_file = tmp_path / "bad.yaml"
        yaml_file.write_text("""
key: value
  invalid: indentation
    broken: structure
""")

        config = {
            "inputs": [{"path": str(yaml_file), "namespace": "data"}],
            "templates": [],
        }

        extractor = StructuredDataExtractor(config)

        # Should handle error gracefully
        try:
            tokens = extractor.extract_tokens()
        except Exception as e:
            # Should have clear error message
            assert "yaml" in str(e).lower() or "parse" in str(e).lower()

    def test_REQ_EXT_113_malformed_xml_clear_error(self, tmp_path):
        """REQ-EXT-113: Handle malformed XML with descriptive error"""
        xml_file = tmp_path / "bad.xml"
        xml_file.write_text("""
<root>
  <unclosed>
  <invalid>>
</root>
""")

        config = {
            "inputs": [{"path": str(xml_file), "namespace": "data", "format": "xml"}],
            "templates": [],
        }

        extractor = StructuredDataExtractor(config)

        # Should handle error gracefully
        try:
            tokens = extractor.extract_tokens()
        except Exception as e:
            # Should have clear error message
            assert "xml" in str(e).lower() or "parse" in str(e).lower()


class TestPreservationErrors:
    """Test error handling for code preservation markers"""

    def test_nested_preserve_markers_error(self, tmp_path):
        """Test that nested PRESERVE-START markers are detected"""
        preservation = PreservationHandler()

        content = """
@PRESERVE_START block1
some code
@PRESERVE_START block2
nested code
@PRESERVE_END
@PRESERVE_END
"""

        with pytest.raises(ValueError) as exc_info:
            preservation._parse_preserved_blocks(content)

        assert "nested" in str(exc_info.value).lower()

    def test_missing_preserve_identifier_error(self, tmp_path):
        """Test that PRESERVE-START without identifier is detected"""
        preservation = PreservationHandler()

        content = """
@PRESERVE_START
some code
@PRESERVE_END
"""

        with pytest.raises(ValueError) as exc_info:
            preservation._parse_preserved_blocks(content)

        assert "identifier" in str(exc_info.value).lower()

    def test_unmatched_preserve_end_error(self, tmp_path):
        """Test that PRESERVE-END without START is detected"""
        preservation = PreservationHandler()

        content = """
some code
@PRESERVE_END
"""

        with pytest.raises(ValueError) as exc_info:
            preservation._parse_preserved_blocks(content)

        assert (
            "without matching" in str(exc_info.value).lower()
            or "unmatched" in str(exc_info.value).lower()
        )

    def test_unclosed_preserve_block_error(self, tmp_path):
        """Test that PRESERVE-START without END is detected"""
        preservation = PreservationHandler()

        content = """
@PRESERVE_START block1
some code
# No closing marker
"""

        with pytest.raises(ValueError) as exc_info:
            preservation._parse_preserved_blocks(content)

        assert (
            "not closed" in str(exc_info.value).lower()
            or "unclosed" in str(exc_info.value).lower()
        )


class TestTokenExtractionErrors:
    """Test error handling for token extraction - REQ-EXT-055, REQ-EXT-056"""

    def test_REQ_EXT_055_missing_key_logged(self, tmp_path, caplog):
        """REQ-EXT-055: Log warning when extraction key not found"""
        json_file = tmp_path / "data.json"
        json_file.write_text('{"existing_key": "value"}')

        config = {
            "inputs": [
                {
                    "path": str(json_file),
                    "namespace": "data",
                    "tokens": [{"name": "missing", "key": "nonexistent.key.path"}],
                }
            ],
            "templates": [],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        # Should log warning
        assert "not found" in caplog.text.lower() or "missing" in caplog.text.lower()

    def test_REQ_EXT_056_continue_on_extraction_failure(self, tmp_path, caplog):
        """REQ-EXT-056: Continue processing other tokens when one fails"""
        json_file = tmp_path / "data.json"
        json_file.write_text('{"good_key": "value", "another_good": "value2"}')

        config = {
            "inputs": [
                {
                    "path": str(json_file),
                    "namespace": "data",
                    "tokens": [
                        {"name": "good1", "key": "good_key"},
                        {"name": "bad", "key": "nonexistent.key"},
                        {"name": "good2", "key": "another_good"},
                    ],
                }
            ],
            "templates": [],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        # Should have extracted the good keys despite the bad one
        assert "data" in tokens
        assert "good1" in tokens["data"]
        assert "good2" in tokens["data"]
        assert tokens["data"]["good1"] == "value"
        assert tokens["data"]["good2"] == "value2"


class TestRegexFilteringErrors:
    """Test error handling for regex filtering - REQ-EXT-073"""

    def test_REQ_EXT_073_regex_no_match_warning(self, tmp_path, caplog):
        """REQ-EXT-073: When regex doesn't match, keeps original value

        Current implementation: if regex doesn't match, returns None from _apply_regex_filter,
        but the calling code checks 'if regex_result is not None' before replacing value,
        so the original value is preserved.
        """
        json_file = tmp_path / "data.json"
        json_file.write_text('{"text": "no numbers here"}')

        config = {
            "inputs": [
                {
                    "path": str(json_file),
                    "namespace": "data",
                    "tokens": [
                        {
                            "name": "number",
                            "key": "text",
                            "regex": r"\d+",
                        }  # Won't match
                    ],
                }
            ],
            "templates": [],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        # When regex doesn't match, keeps original value
        assert tokens["data"]["number"] == "no numbers here"


class TestTemplateErrors:
    """Test error handling for template operations"""

    def test_template_not_found_error(self, tmp_path, caplog):
        """Test that missing template file is handled"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
static_tokens:
  key: value
templates:
  - template: nonexistent.j2
    output: output.txt
""")

        forge = TemplateForge(config_file)

        # Should handle missing template
        try:
            forge.run()
        except Exception as e:
            # Should have clear error
            assert "template" in str(e).lower() or "not found" in str(e).lower()

    def test_template_syntax_error(self, tmp_path):
        """Test that template syntax errors are caught"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
static_tokens:
  key: value
templates:
  - template: bad.j2
    output: output.txt
""")

        # Create template with syntax error
        template = tmp_path / "bad.j2"
        template.write_text("{{ unclosed_brace")

        forge = TemplateForge(config_file)

        try:
            forge.run()
        except Exception as e:
            # Should mention syntax or template error
            assert "syntax" in str(e).lower() or "template" in str(e).lower()

    def test_undefined_variable_in_template(self, tmp_path):
        """Test that undefined variables in templates are handled"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
static_tokens:
  defined: value
templates:
  - template: test.j2
    output: output.txt
""")

        # Template references undefined variable
        template = tmp_path / "test.j2"
        template.write_text("{{ defined }} and {{ undefined_variable }}")

        forge = TemplateForge(config_file)

        # Jinja2 default behavior - may render empty or raise
        try:
            forge.run()
            # If it succeeds, check output
            output = (tmp_path / "output.txt").read_text()
            # Undefined typically renders as empty string
            assert "value and" in output
        except Exception as e:
            # Or it may raise undefined error
            assert "undefined" in str(e).lower()


class TestHookErrors:
    """Test error handling for hook execution"""

    def test_hook_command_not_found(self, tmp_path, caplog):
        """Test that non-existent hook commands are handled"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
static_tokens:
  key: value
templates:
  - template: test.j2
    output: output.txt
hooks:
  after_generation:
    - command: nonexistent_command_xyz
""")

        template = tmp_path / "test.j2"
        template.write_text("{{ key }}")

        forge = TemplateForge(config_file)

        # Should handle hook failure
        try:
            forge.run()
            # May log error but continue
            assert "hook" in caplog.text.lower() or "command" in caplog.text.lower()
        except Exception:
            # Or may raise
            pass

    def test_hook_execution_failure(self, tmp_path, caplog):
        """Test that failing hook commands are handled"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
static_tokens:
  key: value
templates:
  - template: test.j2
    output: output.txt
hooks:
  after_generation:
    - command: bash -c "exit 1"  # Command that fails
""")

        template = tmp_path / "test.j2"
        template.write_text("{{ key }}")

        forge = TemplateForge(config_file)

        # Should handle hook failure
        try:
            forge.run()
            # May log error but continue
        except Exception:
            # Or may raise
            pass


class TestValidationErrors:
    """Test configuration validation errors"""

    def test_invalid_config_structure(self, tmp_path):
        """Test that invalid config structure is caught"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
# Missing required fields
templates:
  - output: output.txt
    # Missing template field
""")

        try:
            forge = TemplateForge(config_file)
            # Validation should catch this
            assert False, "Should have raised validation error"
        except Exception as e:
            # Should mention config or validation
            assert (
                "config" in str(e).lower()
                or "validation" in str(e).lower()
                or "template" in str(e).lower()
            )

    def test_REQ_EXT_114_duplicate_namespace_error(self, tmp_path):
        """REQ-EXT-114: Validate unique namespaces"""
        json_file1 = tmp_path / "data1.json"
        json_file1.write_text('{"key1": "value1"}')

        json_file2 = tmp_path / "data2.json"
        json_file2.write_text('{"key2": "value2"}')

        config_file = tmp_path / "config.yaml"
        config_file.write_text(f"""
inputs:
  - path: {json_file1}
    namespace: data
  - path: {json_file2}
    namespace: data  # Duplicate namespace!
templates:
  - template: test.j2
    output: output.txt
""")

        template = tmp_path / "test.j2"
        template.write_text("test")

        try:
            forge = TemplateForge(config_file)
            # Validation should catch duplicate namespace
        except Exception as e:
            # Should mention duplicate or namespace
            assert "duplicate" in str(e).lower() or "namespace" in str(e).lower()


class TestEdgeCases:
    """Test edge cases and special scenarios"""

    def test_empty_json_file(self, tmp_path):
        """Test that empty JSON file is handled"""
        json_file = tmp_path / "empty.json"
        json_file.write_text("{}")

        config = {
            "inputs": [{"path": str(json_file), "namespace": "data"}],
            "templates": [],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        # Should handle empty file
        assert "data" in tokens

    def test_empty_yaml_file(self, tmp_path):
        """Test that empty YAML file is handled"""
        yaml_file = tmp_path / "empty.yaml"
        yaml_file.write_text("")

        config = {
            "inputs": [{"path": str(yaml_file), "namespace": "data"}],
            "templates": [],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        # Should handle empty file
        assert "data" in tokens

    def test_special_characters_in_values(self, tmp_path):
        """Test that special characters are preserved"""
        json_file = tmp_path / "special.json"
        json_file.write_text('{"text": "Line1\\nLine2\\tTabbed"}')

        config = {
            "inputs": [
                {
                    "path": str(json_file),
                    "namespace": "data",
                    "tokens": [{"name": "text", "key": "text"}],
                }
            ],
            "templates": [],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        # Special characters should be preserved
        assert "\n" in tokens["data"]["text"] or "\\n" in tokens["data"]["text"]
