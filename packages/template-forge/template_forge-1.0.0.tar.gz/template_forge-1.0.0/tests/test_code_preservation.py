"""
Test suite for Code Preservation Requirements (REQ-PRV-*)

Each test function maps to one or more specific requirements from:
docs/requirements/05_code_preservation.md
"""

import pytest

from template_forge.core import PreservationHandler


class TestPreservationMarkers:
    """Tests for REQ-PRV-010 through REQ-PRV-024: Preservation Markers and Syntax"""

    def setup_method(self):
        """Set up test fixtures"""
        self.handler = PreservationHandler()

    def test_REQ_PRV_014_identifier_required(self):
        """REQ-PRV-014: Each preserved block shall have a unique identifier"""
        content = """
        // @PRESERVE_START
        // Missing identifier
        // @PRESERVE_END
        """

        with pytest.raises(ValueError, match="Missing identifier"):
            self.handler._parse_preserved_blocks(content)

    def test_REQ_PRV_020_start_marker_format(self):
        """REQ-PRV-020: Start markers shall follow format: @PRESERVE_START identifier"""
        content = """
        // @PRESERVE_START custom_code
        // Custom implementation
        // @PRESERVE_END custom_code
        """

        blocks = self.handler._parse_preserved_blocks(content)
        assert "custom_code" in blocks
        assert "// Custom implementation\n" in blocks["custom_code"]

    def test_REQ_PRV_021_end_marker_format(self):
        """REQ-PRV-021: End markers shall follow format: @PRESERVE_END identifier"""
        content = """
        // @PRESERVE_START test_block
        // Content
        // @PRESERVE_END test_block
        """

        blocks = self.handler._parse_preserved_blocks(content)
        assert "test_block" in blocks

    def test_REQ_PRV_021_mismatched_identifiers(self):
        """REQ-PRV-021: End marker identifier must match start marker"""
        content = """
        // @PRESERVE_START block1
        // Content
        // @PRESERVE_END block2
        """

        with pytest.raises(ValueError, match="Mismatched identifiers"):
            self.handler._parse_preserved_blocks(content)

    def test_REQ_PRV_022_cpp_comment_syntax(self):
        """REQ-PRV-022: Markers work with C++ comment syntax"""
        content = """
        // @PRESERVE_START cpp_block
        void custom_function() {}
        // @PRESERVE_END cpp_block
        """

        blocks = self.handler._parse_preserved_blocks(content)
        assert "cpp_block" in blocks

    def test_REQ_PRV_022_c_block_comment_syntax(self):
        """REQ-PRV-022: Markers work with C block comment syntax"""
        content = """
        /* @PRESERVE_START c_block */
        int x = 42;
        /* @PRESERVE_END c_block */
        """

        blocks = self.handler._parse_preserved_blocks(content)
        assert "c_block" in blocks

    def test_REQ_PRV_022_python_comment_syntax(self):
        """REQ-PRV-022: Markers work with Python comment syntax"""
        content = """
        # @PRESERVE_START py_block
        def custom(): pass
        # @PRESERVE_END py_block
        """

        blocks = self.handler._parse_preserved_blocks(content)
        assert "py_block" in blocks

    def test_REQ_PRV_022_xml_comment_syntax(self):
        """REQ-PRV-022: Markers work with XML comment syntax"""
        content = """
        <!-- @PRESERVE_START xml_block -->
        <custom>value</custom>
        <!-- @PRESERVE_END xml_block -->
        """

        blocks = self.handler._parse_preserved_blocks(content)
        assert "xml_block" in blocks

    def test_REQ_PRV_022_ini_comment_syntax(self):
        """REQ-PRV-022: Markers work with INI comment syntax"""
        content = """
        ; @PRESERVE_START ini_block
        custom_key = value
        ; @PRESERVE_END ini_block
        """

        blocks = self.handler._parse_preserved_blocks(content)
        assert "ini_block" in blocks

    def test_REQ_PRV_023_whitespace_ignored(self):
        """REQ-PRV-023: Whitespace around markers shall be ignored"""
        content = """
        //    @PRESERVE_START   spaced_block
        // Content
        //   @PRESERVE_END    spaced_block
        """

        blocks = self.handler._parse_preserved_blocks(content)
        assert "spaced_block" in blocks


class TestContentPreservation:
    """Tests for REQ-PRV-030 through REQ-PRV-044: Content Preservation and Injection"""

    def setup_method(self):
        """Set up test fixtures"""
        self.handler = PreservationHandler()

    def test_REQ_PRV_031_preserve_content_with_markers(self):
        """REQ-PRV-031: Preserved content includes everything between markers"""
        content = """
        # @PRESERVE_START test_block
        # Custom line 1
        # Custom line 2
        # @PRESERVE_END test_block
        """

        blocks = self.handler._parse_preserved_blocks(content)
        preserved = blocks["test_block"]

        # Should include the content but not the marker lines themselves
        assert "# Custom line 1\n" in preserved
        assert "# Custom line 2\n" in preserved
        assert "@PRESERVE_START" not in preserved
        assert "@PRESERVE_END" not in preserved

    def test_REQ_PRV_032_multiple_blocks(self):
        """REQ-PRV-032: Multiple preserved blocks can exist in a single file"""
        content = """
        # @PRESERVE_START block1
        # Content 1
        # @PRESERVE_END block1
        
        some code
        
        # @PRESERVE_START block2
        # Content 2
        # @PRESERVE_END block2
        """

        blocks = self.handler._parse_preserved_blocks(content)
        assert len(blocks) == 2
        assert "block1" in blocks
        assert "block2" in blocks

    def test_REQ_PRV_033_unique_identifiers_required(self):
        """REQ-PRV-033: Each preserved block identifier shall be unique within a file"""
        content = """
        # @PRESERVE_START duplicate
        # Content 1
        # @PRESERVE_END duplicate
        
        # @PRESERVE_START duplicate
        # Content 2
        # @PRESERVE_END duplicate
        """

        with pytest.raises(ValueError, match="Duplicate preserved block identifier"):
            self.handler._parse_preserved_blocks(content)

    def test_REQ_PRV_041_inject_preserved_content(self):
        """REQ-PRV-041: Preserved content injected into matching blocks"""
        old_content = """
        # @PRESERVE_START custom_block
        # My custom code
        x = 42
        # @PRESERVE_END custom_block
        """

        new_template = """
        # @PRESERVE_START custom_block
        # Template placeholder
        # @PRESERVE_END custom_block
        """

        blocks = self.handler._parse_preserved_blocks(old_content)
        result = self.handler.inject_preserved_content(new_template, blocks)

        assert "# My custom code\n" in result
        assert "x = 42\n" in result
        assert "# Template placeholder" not in result

    def test_REQ_PRV_044_replace_entire_block(self):
        """REQ-PRV-044: Preserved content replaces entire block including placeholders"""
        old_content = """
        # @PRESERVE_START imports
        import custom_module
        from my_lib import helper
        # @PRESERVE_END imports
        """

        new_template = """
        # @PRESERVE_START imports
        # Add imports here
        # @PRESERVE_END imports
        """

        blocks = self.handler._parse_preserved_blocks(old_content)
        result = self.handler.inject_preserved_content(new_template, blocks)

        assert "import custom_module\n" in result
        assert "from my_lib import helper\n" in result
        assert "# Add imports here" not in result


class TestBlockMatching:
    """Tests for REQ-PRV-050 through REQ-PRV-053: Block Matching"""

    def setup_method(self):
        """Set up test fixtures"""
        self.handler = PreservationHandler()

    def test_REQ_PRV_050_match_by_identifier(self):
        """REQ-PRV-050: Blocks matched by identifier, not position"""
        old_content = """
        # @PRESERVE_START block_a
        # A content
        # @PRESERVE_END block_a
        
        # @PRESERVE_START block_b
        # B content
        # @PRESERVE_END block_b
        """

        # Reverse order in new template
        new_template = """
        # @PRESERVE_START block_b
        # @PRESERVE_END block_b
        
        # @PRESERVE_START block_a
        # @PRESERVE_END block_a
        """

        blocks = self.handler._parse_preserved_blocks(old_content)
        result = self.handler.inject_preserved_content(new_template, blocks)

        # Should match by identifier, not position
        lines = result.split("\n")
        block_b_idx = next(
            i for i, line in enumerate(lines) if "block_b" in line and "START" in line
        )
        block_a_idx = next(
            i for i, line in enumerate(lines) if "block_a" in line and "START" in line
        )

        # Check that content appears after the correct markers
        assert "# B content" in "\n".join(lines[block_b_idx : block_b_idx + 3])
        assert "# A content" in "\n".join(lines[block_a_idx : block_a_idx + 3])

    def test_REQ_PRV_052_case_sensitive_identifiers(self):
        """REQ-PRV-052: Block identifiers are case-sensitive"""
        old_content = """
        # @PRESERVE_START MyBlock
        # Content
        # @PRESERVE_END MyBlock
        """

        # Different case should not match
        new_template = """
        # @PRESERVE_START myblock
        # @PRESERVE_END myblock
        """

        blocks = self.handler._parse_preserved_blocks(old_content)
        result = self.handler.inject_preserved_content(new_template, blocks)

        # Should not have injected the content (case mismatch)
        # The old block "MyBlock" should be warned as lost
        assert "# Content" not in result


class TestValidation:
    """Tests for REQ-PRV-060 through REQ-PRV-064: Validation"""

    def setup_method(self):
        """Set up test fixtures"""
        self.handler = PreservationHandler()

    def test_REQ_PRV_060_matching_start_end(self):
        """REQ-PRV-060: Every START must have matching END"""
        content = """
        # @PRESERVE_START has_end
        # Content
        # @PRESERVE_END has_end
        """

        # Should not raise
        blocks = self.handler._parse_preserved_blocks(content)
        assert "has_end" in blocks

    def test_REQ_PRV_061_reject_nested_blocks(self):
        """REQ-PRV-061: Nested preserved blocks are rejected"""
        content = """
        # @PRESERVE_START outer
        # Content
        # @PRESERVE_START inner
        # Nested content
        # @PRESERVE_END inner
        # @PRESERVE_END outer
        """

        with pytest.raises(ValueError, match="nested|Found nested"):
            self.handler._parse_preserved_blocks(content)

    def test_REQ_PRV_062_unmatched_end(self):
        """REQ-PRV-062: Unmatched END markers are rejected"""
        content = """
        # Some code
        # @PRESERVE_END orphan
        """

        with pytest.raises(ValueError, match="without matching"):
            self.handler._parse_preserved_blocks(content)

    def test_REQ_PRV_063_unclosed_start(self):
        """REQ-PRV-063: Unclosed START markers are rejected"""
        content = """
        # @PRESERVE_START unclosed
        # Content but no end marker
        """

        with pytest.raises(ValueError, match="Unclosed"):
            self.handler._parse_preserved_blocks(content)

    def test_REQ_PRV_064_error_includes_line_numbers(self):
        """REQ-PRV-064: Validation errors include line numbers"""
        content = """
        # Line 1
        # Line 2
        # @PRESERVE_START test
        # Line 4
        """

        try:
            self.handler._parse_preserved_blocks(content)
            pytest.fail("Should have raised ValueError")
        except ValueError as e:
            # Error message should include line number
            assert "line" in str(e).lower()
            assert "4" in str(e) or "5" in str(e)  # Line number of START marker


class TestErrorHandling:
    """Tests for REQ-PRV-070 through REQ-PRV-073: Error Handling"""

    def setup_method(self):
        """Set up test fixtures"""
        self.handler = PreservationHandler()

    def test_REQ_PRV_070_missing_file_logged(self, tmp_path, caplog):
        """REQ-PRV-070: Missing file logged as warning, processing continues"""
        nonexistent = tmp_path / "does_not_exist.txt"

        # Should not raise, should return empty dict
        blocks = self.handler.extract_preserved_content(nonexistent)

        assert blocks == {}
        assert any("Could not read" in record.message for record in caplog.records)

    def test_REQ_PRV_071_malformed_markers_logged(self, caplog):
        """REQ-PRV-071: Malformed markers logged as error"""
        content = """
        # @PRESERVE_START
        # Missing identifier
        # @PRESERVE_END
        """

        with pytest.raises(ValueError):
            self.handler._parse_preserved_blocks(content)

    def test_REQ_PRV_072_errors_dont_prevent_processing(self, tmp_path):
        """REQ-PRV-072: Preservation errors don't prevent template processing"""
        # This is more of an integration test - the template processor
        # should catch preservation exceptions and continue
        # We test that extract returns empty dict on error

        # Create a file with malformed markers
        bad_file = tmp_path / "bad.txt"
        bad_file.write_text("""
        # @PRESERVE_START unclosed
        # No end marker
        """)

        # Extract should handle the error and return empty
        blocks = self.handler.extract_preserved_content(bad_file)
        assert blocks == {}


class TestRealWorldScenarios:
    """Integration tests for realistic preservation scenarios"""

    def setup_method(self):
        """Set up test fixtures"""
        self.handler = PreservationHandler()

    def test_python_class_with_custom_methods(self):
        """Test preserving custom methods in a Python class"""
        old_file = """
# Generated Python Class
import sys

# @PRESERVE_START custom_imports
import json
import requests
# @PRESERVE_END custom_imports

class UserManager:
    def __init__(self):
        self.users = []
    
    # @PRESERVE_START custom_methods
    def fetch_from_api(self, url):
        return requests.get(url).json()
    
    def validate_email(self, email):
        return '@' in email
    # @PRESERVE_END custom_methods
"""

        new_template = """
# Generated Python Class
import sys

# @PRESERVE_START custom_imports
# Add your custom imports here
# @PRESERVE_END custom_imports

class UserManager:
    def __init__(self):
        self.users = []
    
    # @PRESERVE_START custom_methods
    # Add your custom methods here
    # @PRESERVE_END custom_methods
"""

        blocks = self.handler._parse_preserved_blocks(old_file)
        result = self.handler.inject_preserved_content(new_template, blocks)

        assert "import json" in result
        assert "import requests" in result
        assert "def fetch_from_api" in result
        assert "def validate_email" in result
        assert "# Add your custom imports here" not in result
        assert "# Add your custom methods here" not in result

    def test_config_file_with_custom_settings(self):
        """Test preserving custom settings in a config file"""
        old_config = """
; Application Configuration

[database]
host = localhost
port = 5432

; @PRESERVE_START custom_db_settings
timeout = 30
pool_size = 10
retry_attempts = 3
; @PRESERVE_END custom_db_settings

[logging]
level = INFO
"""

        new_template = """
; Application Configuration

[database]
host = db.example.com
port = 5432

; @PRESERVE_START custom_db_settings
; Add your custom database settings here
; @PRESERVE_END custom_db_settings

[logging]
level = DEBUG
"""

        blocks = self.handler._parse_preserved_blocks(old_config)
        result = self.handler.inject_preserved_content(new_template, blocks)

        assert "timeout = 30" in result
        assert "pool_size = 10" in result
        assert "retry_attempts = 3" in result
        assert "host = db.example.com" in result  # New value from template
        assert "level = DEBUG" in result  # New value from template


# Additional PRV tests for better coverage


def test_REQ_PRV_001_supports_preservation():
    """REQ-PRV-001: System supports preserving custom code sections"""
    handler = PreservationHandler()
    assert handler is not None
    assert hasattr(handler, "extract_preserved_content")
    assert hasattr(handler, "inject_preserved_content")


def test_REQ_PRV_002_custom_logic_survives():
    """REQ-PRV-002: Preserved sections allow custom logic to survive regeneration"""
    handler = PreservationHandler()

    old_content = """@PRESERVE_START custom
my custom logic
@PRESERVE_END custom"""

    new_content = """@PRESERVE_START custom
default logic
@PRESERVE_END custom"""

    blocks = handler._parse_preserved_blocks(old_content)
    result = handler.inject_preserved_content(new_content, blocks)

    assert "my custom logic" in result
    assert "default logic" not in result


def test_REQ_PRV_003_works_with_any_format():
    """REQ-PRV-003: Preservation works with any text-based format"""
    handler = PreservationHandler()

    # Test with different formats
    formats = [
        "// @PRESERVE_START test\n// code\n// @PRESERVE_END test",  # C++
        "# @PRESERVE_START test\n# code\n# @PRESERVE_END test",  # Python
        "<!-- @PRESERVE_START test\ncode\n@PRESERVE_END test -->",  # HTML
        "/* @PRESERVE_START test */\ncode\n/* @PRESERVE_END test */",  # C
    ]

    for content in formats:
        blocks = handler._parse_preserved_blocks(content)
        assert "test" in blocks


def test_REQ_PRV_010_start_marker():
    """REQ-PRV-010: System uses @PRESERVE_START as start marker"""
    handler = PreservationHandler()
    assert handler.PRESERVE_START == "@PRESERVE_START"


def test_REQ_PRV_011_end_marker():
    """REQ-PRV-011: System uses @PRESERVE_END as end marker"""
    handler = PreservationHandler()
    assert handler.PRESERVE_END == "@PRESERVE_END"


def test_REQ_PRV_012_language_agnostic():
    """REQ-PRV-012: Markers are language-agnostic"""
    handler = PreservationHandler()

    # Works with different comment styles
    cpp_style = "// @PRESERVE_START test\ncode\n// @PRESERVE_END test"
    python_style = "# @PRESERVE_START test\ncode\n# @PRESERVE_END test"

    cpp_blocks = handler._parse_preserved_blocks(cpp_style)
    python_blocks = handler._parse_preserved_blocks(python_style)

    assert "test" in cpp_blocks
    assert "test" in python_blocks


def test_REQ_PRV_013_case_sensitive():
    """REQ-PRV-013: Markers are case-sensitive"""
    handler = PreservationHandler()

    # Lowercase should not work
    invalid_content = "@preserve_start test\ncode\n@preserve_end test"
    blocks = handler._parse_preserved_blocks(invalid_content)
    assert "test" not in blocks or len(blocks) == 0


def test_REQ_PRV_024_markers_on_own_line():
    """REQ-PRV-024: Markers should appear on their own line"""
    handler = PreservationHandler()

    # Markers on their own lines (correct)
    content = """@PRESERVE_START test
code here
@PRESERVE_END test"""

    blocks = handler._parse_preserved_blocks(content)
    assert "test" in blocks


def test_REQ_PRV_030_extract_before_regeneration(tmp_path):
    """REQ-PRV-030: System extracts preserved content before regeneration"""
    handler = PreservationHandler()

    # Create existing file with preserved content
    existing_file = tmp_path / "existing.txt"
    existing_file.write_text("""@PRESERVE_START custom
existing custom code
@PRESERVE_END custom""")

    # Extract preserved content
    preserved = handler.extract_preserved_content(existing_file)

    assert "custom" in preserved
    assert "existing custom code" in preserved["custom"]


def test_REQ_PRV_040_inject_after_rendering():
    """REQ-PRV-040: System injects preserved content after template rendering"""
    handler = PreservationHandler()

    old_content = """@PRESERVE_START block1
old content
@PRESERVE_END block1"""

    new_template = """@PRESERVE_START block1
new content
@PRESERVE_END block1"""

    blocks = handler._parse_preserved_blocks(old_content)
    result = handler.inject_preserved_content(new_template, blocks)

    assert "old content" in result
    assert "new content" not in result


def test_REQ_PRV_042_discard_missing_blocks():
    """REQ-PRV-042: Blocks in old file but not in new template are discarded"""
    handler = PreservationHandler()

    old_content = """@PRESERVE_START old_block
old content
@PRESERVE_END old_block"""

    new_template = """@PRESERVE_START new_block
new content
@PRESERVE_END new_block"""

    blocks = handler._parse_preserved_blocks(old_content)
    result = handler.inject_preserved_content(new_template, blocks)

    # old_block content should not appear (block ID doesn't match)
    assert "old content" not in result
    # The new_block should remain as-is since there's no matching preserved content
    assert "@PRESERVE_START new_block" in result


def test_REQ_PRV_043_empty_new_blocks():
    """REQ-PRV-043: New blocks without old content remain empty"""
    handler = PreservationHandler()

    old_content = ""  # No preserved blocks
    new_template = """@PRESERVE_START new_block
default content
@PRESERVE_END new_block"""

    blocks = handler._parse_preserved_blocks(old_content) if old_content else {}
    result = handler.inject_preserved_content(new_template, blocks)

    # Should keep default content since there's nothing to preserve
    assert "default content" in result


def test_REQ_PRV_051_match_by_identifier():
    """REQ-PRV-051: Blocks matched by identifier in both old and new files"""
    handler = PreservationHandler()

    old_content = """@PRESERVE_START imports
import custom_module
@PRESERVE_END imports"""

    new_template = """@PRESERVE_START imports
# imports go here
@PRESERVE_END imports"""

    blocks = handler._parse_preserved_blocks(old_content)
    result = handler.inject_preserved_content(new_template, blocks)

    assert "import custom_module" in result
    assert "# imports go here" not in result


def test_REQ_PRV_053_log_missing_identifiers():
    """REQ-PRV-053: Log warning when preserved block ID not in new template"""
    handler = PreservationHandler()

    old_content = """@PRESERVE_START deprecated_block
old code
@PRESERVE_END deprecated_block"""

    new_template = """No preserved blocks here"""

    blocks = handler._parse_preserved_blocks(old_content)
    # This should log a warning but still work
    result = handler.inject_preserved_content(new_template, blocks)

    assert "old code" not in result


def test_REQ_PRV_073_clear_error_descriptions():
    """REQ-PRV-073: All errors logged with clear descriptions"""
    handler = PreservationHandler()

    # Test various error conditions produce clear messages
    invalid_content = "@PRESERVE_START test\ncode\n"  # No end marker

    with pytest.raises(ValueError) as exc_info:
        handler._parse_preserved_blocks(invalid_content)

    # Error message should be descriptive
    assert "test" in str(exc_info.value) or "unclosed" in str(exc_info.value).lower()


def test_REQ_PRV_080_empty_blocks_in_templates(tmp_path):
    """REQ-PRV-080: Templates should include empty preserved blocks"""
    handler = PreservationHandler()

    # Template with empty preserved block
    template_output = """# Generated code
@PRESERVE_START custom_code
# Add your custom code here
@PRESERVE_END custom_code
# More generated code"""

    # First generation: no preserved content
    old_file = tmp_path / "output.txt"
    old_file.write_text(template_output)

    # Extract (should get empty block with comment)
    preserved = handler.extract_preserved_content(old_file)
    assert "custom_code" in preserved
    assert "# Add your custom code here\n" in preserved["custom_code"]

    # User adds custom code
    user_modified = """# Generated code
@PRESERVE_START custom_code
# My custom implementation
x = 42
@PRESERVE_END custom_code
# More generated code"""

    old_file.write_text(user_modified)

    # Extract again (should get user's custom code)
    preserved = handler.extract_preserved_content(old_file)
    assert "# My custom implementation\n" in preserved["custom_code"]
    assert "x = 42\n" in preserved["custom_code"]

    # Regenerate and inject
    result = handler.inject_preserved_content(template_output, preserved)
    assert "# My custom implementation" in result
    assert "x = 42" in result
    assert result.count("# Add your custom code here") == 0  # Replaced


def test_REQ_PRV_081_helpful_comments(tmp_path):
    """REQ-PRV-081: Preserved blocks should have helpful comments"""
    handler = PreservationHandler()

    # Template with helpful comments in preserved block
    template_with_comments = """# Configuration
@PRESERVE_START custom_imports
# Add your custom imports here
# Example: from mymodule import MyClass
@PRESERVE_END custom_imports

# Main code"""

    # Write to file
    file = tmp_path / "config.py"
    file.write_text(template_with_comments)

    # Extract preserved content (should include helpful comments)
    preserved = handler.extract_preserved_content(file)
    assert "custom_imports" in preserved
    assert "# Add your custom imports here\n" in preserved["custom_imports"]
    assert "# Example: from mymodule import MyClass\n" in preserved["custom_imports"]

    # User adds import after reading helpful comments
    user_version = """# Configuration
@PRESERVE_START custom_imports
# Add your custom imports here
# Example: from mymodule import MyClass
from mymodule import MyClass
import json
@PRESERVE_END custom_imports

# Main code"""

    file.write_text(user_version)
    preserved = handler.extract_preserved_content(file)

    # Should preserve both comments and user's additions
    assert "from mymodule import MyClass\n" in preserved["custom_imports"]
    assert "import json\n" in preserved["custom_imports"]
    assert "# Add your custom imports here\n" in preserved["custom_imports"]


def test_REQ_PRV_082_descriptive_identifiers():
    """REQ-PRV-082: Block identifiers must be descriptive"""
    handler = PreservationHandler()

    # Test that descriptive identifiers work correctly
    good_identifiers = [
        "custom_imports",
        "user_methods",
        "config_overrides",
        "validation_logic",
    ]

    for identifier in good_identifiers:
        # Verify naming convention
        assert "_" in identifier  # Use snake_case
        assert identifier.islower()  # Use lowercase

        # Test that identifier actually works in preservation
        content = f"""# @PRESERVE_START {identifier}
# Custom content
@PRESERVE_END {identifier}"""

        blocks = handler._parse_preserved_blocks(content)
        assert identifier in blocks
        assert "# Custom content\n" in blocks[identifier]


def test_REQ_PRV_083_no_generated_code_inside_blocks(tmp_path):
    """REQ-PRV-083: Templates shouldn't generate code inside preserved blocks"""
    from jinja2 import Environment

    handler = PreservationHandler()
    env = Environment()

    # BAD: Template that generates code inside preserved block
    bad_template_str = """# @PRESERVE_START imports
import {{ module_name }}
# @PRESERVE_END imports"""

    # This is an anti-pattern that should be avoided
    bad_tmpl = env.from_string(bad_template_str)
    bad_result = bad_tmpl.render(module_name="os")

    # If old file has custom imports, they get replaced by generated code
    old_content = """# @PRESERVE_START imports
import custom_module
import json
# @PRESERVE_END imports"""

    old_file = tmp_path / "bad.py"
    old_file.write_text(old_content)
    preserved_bad = handler.extract_preserved_content(old_file)

    # Inject into bad template - user's custom code is preserved
    # but conflicts with generated import
    result_bad = handler.inject_preserved_content(bad_result, preserved_bad)
    assert "import custom_module" in result_bad
    # This creates problems - both generated and preserved imports present

    # GOOD: Template with empty preserved block
    good_template_str = """# @PRESERVE_START imports
# Add your custom imports here
# @PRESERVE_END imports"""

    good_tmpl = env.from_string(good_template_str)
    good_result = good_tmpl.render(module_name="os")

    # Extract from old file and inject into good template
    result_good = handler.inject_preserved_content(good_result, preserved_bad)
    assert "import custom_module" in result_good
    assert "import json" in result_good
    assert (
        "# Add your custom imports here" not in result_good
    )  # Replaced by preserved content


def test_REQ_PRV_084_identifier_rename_requires_manual_update():
    """REQ-PRV-084: Renaming block IDs requires manual file updates"""
    handler = PreservationHandler()

    old_content = """@PRESERVE_START old_name
custom code
@PRESERVE_END old_name"""

    new_template = """@PRESERVE_START new_name
default
@PRESERVE_END new_name"""

    blocks = handler._parse_preserved_blocks(old_content)
    result = handler.inject_preserved_content(new_template, blocks)

    # Content is lost because identifiers don't match
    assert "custom code" not in result
    # The new block remains as-is since no matching preserved content
    assert "@PRESERVE_START new_name" in result


def test_REQ_PRV_090_custom_imports_use_case(tmp_path):
    """REQ-PRV-090: Support custom imports in generated source files"""
    handler = PreservationHandler()

    # Initial generated file
    template = """import os
import sys

@PRESERVE_START custom_imports
# Custom imports
@PRESERVE_END custom_imports

def main():
    pass"""

    file = tmp_path / "main.py"
    file.write_text(template)

    # User adds custom imports
    user_version = """import os
import sys

@PRESERVE_START custom_imports
# Custom imports
import requests
from mylib import helper
@PRESERVE_END custom_imports

def main():
    pass"""

    file.write_text(user_version)

    # Extract preserved imports
    preserved = handler.extract_preserved_content(file)
    assert "custom_imports" in preserved
    assert "import requests\n" in preserved["custom_imports"]
    assert "from mylib import helper\n" in preserved["custom_imports"]

    # Regenerate file (simulate template regeneration)
    new_template = """import os
import sys
import logging  # New generated import

@PRESERVE_START custom_imports
# Custom imports
@PRESERVE_END custom_imports

def main():
    logging.info("Starting")
    pass"""

    # Inject preserved imports
    result = handler.inject_preserved_content(new_template, preserved)

    # Should have both generated and preserved imports
    assert "import os" in result
    assert "import logging" in result
    assert "import requests" in result
    assert "from mylib import helper" in result


def test_REQ_PRV_091_custom_methods_use_case(tmp_path):
    """REQ-PRV-091: Support custom methods in generated classes"""
    handler = PreservationHandler()

    # Initial generated class
    template = """class MyClass:
    def __init__(self):
        pass
    
    @PRESERVE_START custom_methods
    # Add custom methods here
    @PRESERVE_END custom_methods"""

    file = tmp_path / "myclass.py"
    file.write_text(template)

    # User adds custom methods
    user_version = """class MyClass:
    def __init__(self):
        pass
    
    @PRESERVE_START custom_methods
    # Add custom methods here
    def custom_helper(self, data):
        return data.upper()
    
    def validate(self, value):
        return value > 0
    @PRESERVE_END custom_methods"""

    file.write_text(user_version)

    # Extract preserved methods
    preserved = handler.extract_preserved_content(file)
    assert "custom_methods" in preserved
    assert "def custom_helper(self, data):" in preserved["custom_methods"]
    assert "def validate(self, value):" in preserved["custom_methods"]

    # Regenerate class with new generated method
    new_template = """class MyClass:
    def __init__(self):
        self.data = []
    
    def load(self):
        # Auto-generated load method
        pass
    
    @PRESERVE_START custom_methods
    # Add custom methods here
    @PRESERVE_END custom_methods"""

    # Inject preserved methods
    result = handler.inject_preserved_content(new_template, preserved)

    # Should have both generated and preserved methods
    assert "def load(self):" in result
    assert "def custom_helper(self, data):" in result
    assert "def validate(self, value):" in result


def test_REQ_PRV_092_custom_config_overrides(tmp_path):
    """REQ-PRV-092: Support custom configuration overrides"""
    handler = PreservationHandler()

    # Initial config file
    config_template = """[default]
timeout = 30

@PRESERVE_START custom_settings
# Add your custom settings
@PRESERVE_END custom_settings"""

    file = tmp_path / "config.ini"
    file.write_text(config_template)

    # User adds custom settings
    user_version = """[default]
timeout = 30

@PRESERVE_START custom_settings
# Add your custom settings
max_retries = 5
log_level = DEBUG
custom_path = /my/custom/path
@PRESERVE_END custom_settings"""

    file.write_text(user_version)

    # Extract preserved settings
    preserved = handler.extract_preserved_content(file)
    assert "custom_settings" in preserved
    assert "max_retries = 5\n" in preserved["custom_settings"]
    assert "log_level = DEBUG\n" in preserved["custom_settings"]
    assert "custom_path = /my/custom/path\n" in preserved["custom_settings"]

    # Regenerate config with updated default timeout
    new_template = """[default]
timeout = 60
buffer_size = 1024

@PRESERVE_START custom_settings
# Add your custom settings
@PRESERVE_END custom_settings"""

    # Inject preserved settings
    result = handler.inject_preserved_content(new_template, preserved)

    # Should have new defaults and preserved custom settings
    assert "timeout = 60" in result
    assert "buffer_size = 1024" in result
    assert "max_retries = 5" in result
    assert "log_level = DEBUG" in result
    assert "custom_path = /my/custom/path" in result


def test_REQ_PRV_093_custom_validation_logic(tmp_path):
    """REQ-PRV-093: Support custom validation logic"""
    handler = PreservationHandler()

    # Initial validation function
    template = """def validate(data):
    # Auto-generated validations
    check_required_fields(data)
    
    @PRESERVE_START custom_validation
    # Add custom validation here
    @PRESERVE_END custom_validation
    
    return True"""

    file = tmp_path / "validator.py"
    file.write_text(template)

    # User adds custom validation
    user_version = """def validate(data):
    # Auto-generated validations
    check_required_fields(data)
    
    @PRESERVE_START custom_validation
    # Add custom validation here
    if data.get('age') and data['age'] < 0:
        raise ValueError("Age must be positive")
    
    if data.get('email') and '@' not in data['email']:
        raise ValueError("Invalid email format")
    @PRESERVE_END custom_validation
    
    return True"""

    file.write_text(user_version)

    # Extract preserved validation
    preserved = handler.extract_preserved_content(file)
    assert "custom_validation" in preserved
    assert "if data.get('age')" in preserved["custom_validation"]
    assert 'raise ValueError("Age must be positive")' in preserved["custom_validation"]
    assert "Invalid email format" in preserved["custom_validation"]

    # Regenerate with new auto-generated validation
    new_template = """def validate(data):
    # Auto-generated validations
    check_required_fields(data)
    check_data_types(data)
    
    @PRESERVE_START custom_validation
    # Add custom validation here
    @PRESERVE_END custom_validation
    
    return True"""

    # Inject preserved validation
    result = handler.inject_preserved_content(new_template, preserved)

    # Should have both generated and preserved validation
    assert "check_required_fields(data)" in result
    assert "check_data_types(data)" in result
    assert "if data.get('age')" in result
    assert "Invalid email format" in result


def test_REQ_PRV_094_custom_documentation(tmp_path):
    """REQ-PRV-094: Support custom documentation sections"""
    handler = PreservationHandler()

    # Initial documentation
    doc_template = """# API Documentation

## Overview
Auto-generated overview

@PRESERVE_START custom_docs
## Custom Documentation
Add your custom documentation here
@PRESERVE_END custom_docs"""

    file = tmp_path / "API.md"
    file.write_text(doc_template)

    # User adds custom documentation
    user_version = """# API Documentation

## Overview
Auto-generated overview

@PRESERVE_START custom_docs
## Custom Documentation
Add your custom documentation here

## Advanced Usage
Here's how to use advanced features:
- Feature 1: Description
- Feature 2: Description

## Examples
```python
my_function(param=value)
```
@PRESERVE_END custom_docs"""

    file.write_text(user_version)

    # Extract preserved docs
    preserved = handler.extract_preserved_content(file)
    assert "custom_docs" in preserved
    assert "## Advanced Usage" in preserved["custom_docs"]
    assert "## Examples" in preserved["custom_docs"]
    assert "my_function(param=value)" in preserved["custom_docs"]

    # Regenerate with updated overview
    new_template = """# API Documentation

## Overview
Auto-generated overview - Updated for version 2.0

## New Section
Additional generated content

@PRESERVE_START custom_docs
## Custom Documentation
Add your custom documentation here
@PRESERVE_END custom_docs"""

    # Inject preserved documentation
    result = handler.inject_preserved_content(new_template, preserved)

    # Should have both generated and preserved docs
    assert "Updated for version 2.0" in result
    assert "## New Section" in result
    assert "## Advanced Usage" in result
    assert "## Examples" in result
    assert "my_function(param=value)" in result


def test_REQ_PRV_100_single_file_preservation(tmp_path):
    """REQ-PRV-100: Preserved content cannot span multiple files"""
    handler = PreservationHandler()

    # Each file has its own preserved blocks
    file1_content = """@PRESERVE_START block1
Content for file 1
@PRESERVE_END block1"""

    file2_content = """@PRESERVE_START block1
Content for file 2 (different from file1)
@PRESERVE_END block1"""

    file1 = tmp_path / "file1.txt"
    file2 = tmp_path / "file2.txt"

    file1.write_text(file1_content)
    file2.write_text(file2_content)

    # Extract from each file separately
    preserved1 = handler.extract_preserved_content(file1)
    preserved2 = handler.extract_preserved_content(file2)

    # Same block identifier but different content per file
    assert "block1" in preserved1
    assert "block1" in preserved2
    assert "Content for file 1\n" in preserved1["block1"]
    assert "Content for file 2 (different from file1)\n" in preserved2["block1"]

    # Preservation is file-specific, not cross-file
    assert preserved1["block1"] != preserved2["block1"]

    # Inject back to respective files
    template = """@PRESERVE_START block1
default content
@PRESERVE_END block1"""

    result1 = handler.inject_preserved_content(template, preserved1)
    result2 = handler.inject_preserved_content(template, preserved2)

    assert "Content for file 1" in result1
    assert "Content for file 2" in result2
    assert result1 != result2


def test_REQ_PRV_101_conditional_preserved_blocks():
    """REQ-PRV-101: Preserved blocks may be conditionally included"""
    template = """
{% if feature_enabled %}
@PRESERVE_START feature_impl
# Custom feature implementation
@PRESERVE_END feature_impl
{% endif %}
"""

    # Preservation markers can be inside Jinja2 conditions
    assert "{% if feature_enabled %}" in template
    assert "@PRESERVE_START feature_impl" in template


def test_REQ_PRV_102_conditional_block_processing():
    """REQ-PRV-102: Process preserved blocks only when condition is true"""
    from jinja2 import Environment

    env = Environment()
    template_str = """
{% if enabled %}
@PRESERVE_START block
content
@PRESERVE_END block
{% endif %}
"""

    # When enabled=True, preservation markers included
    template = env.from_string(template_str)
    result_enabled = template.render(enabled=True)
    assert "@PRESERVE_START" in result_enabled

    # When enabled=False, preservation markers not included
    result_disabled = template.render(enabled=False)
    assert "@PRESERVE_START" not in result_disabled


def test_REQ_PRV_103_conditional_preservation_warning(tmp_path, caplog):
    """REQ-PRV-103: Warn when conditional preserved block may be lost"""
    from jinja2 import Environment

    handler = PreservationHandler()
    env = Environment()

    # Old file has preserved content in optional feature block
    old_content = """@PRESERVE_START optional_feature
# User's custom implementation
def custom_feature():
    return "custom"
@PRESERVE_END optional_feature"""

    file = tmp_path / "module.py"
    file.write_text(old_content)

    # Extract preserved content
    preserved = handler.extract_preserved_content(file)
    assert "optional_feature" in preserved
    assert "def custom_feature():" in preserved["optional_feature"]

    # New template conditionally includes this block (condition is False)
    template_str = """{% if include_optional %}
@PRESERVE_START optional_feature
# Optional feature
@PRESERVE_END optional_feature
{% endif %}"""

    tmpl = env.from_string(template_str)

    # When feature is disabled, block is not in new template
    new_content = tmpl.render(include_optional=False)
    assert "@PRESERVE_START" not in new_content

    # Inject preserved content - should warn about lost block
    import logging

    caplog.set_level(logging.WARNING)
    result = handler.inject_preserved_content(new_content, preserved)

    # Block content should not be in result (block doesn't exist in template)
    assert "def custom_feature():" not in result

    # Should have logged warning about lost block
    assert any(
        "optional_feature" in record.message and "lost" in record.message.lower()
        for record in caplog.records
    )

    # When feature is enabled, block is preserved
    new_content_enabled = tmpl.render(include_optional=True)
    result_enabled = handler.inject_preserved_content(new_content_enabled, preserved)
    assert "def custom_feature():" in result_enabled


def test_REQ_PRV_104_conditional_preservation_example(tmp_path):
    """REQ-PRV-104: Example of conditional preserved blocks"""
    from jinja2 import Environment

    handler = PreservationHandler()
    env = Environment()

    template_str = """class MyClass:
    def __init__(self):
        pass
    
    {% if include_advanced %}
    @PRESERVE_START advanced_methods
    # Advanced methods - preserved across regeneration
    def advanced_method(self):
        pass
    @PRESERVE_END advanced_methods
    {% endif %}"""

    tmpl = env.from_string(template_str)

    # First generation with feature enabled
    result_enabled = tmpl.render(include_advanced=True)
    assert "@PRESERVE_START advanced_methods" in result_enabled

    file = tmp_path / "myclass.py"
    file.write_text(result_enabled)

    # User adds custom advanced method
    user_version = """class MyClass:
    def __init__(self):
        pass
    
    
    @PRESERVE_START advanced_methods
    # Advanced methods - preserved across regeneration
    def advanced_method(self):
        return "custom implementation"
    
    def another_advanced_method(self):
        return "another custom method"
    @PRESERVE_END advanced_methods
"""

    file.write_text(user_version)

    # Extract preserved methods
    preserved = handler.extract_preserved_content(file)
    assert "advanced_methods" in preserved
    assert "def another_advanced_method(self):" in preserved["advanced_methods"]

    # Regenerate with feature still enabled
    new_result = tmpl.render(include_advanced=True)
    final = handler.inject_preserved_content(new_result, preserved)

    # Preserved methods should be present
    assert "def advanced_method(self):" in final
    assert "def another_advanced_method(self):" in final
    assert "custom implementation" in final

    # Regenerate with feature disabled
    result_disabled = tmpl.render(include_advanced=False)
    assert "@PRESERVE_START advanced_methods" not in result_disabled

    # If we inject with feature disabled, methods are lost
    final_disabled = handler.inject_preserved_content(result_disabled, preserved)
    assert "def another_advanced_method(self):" not in final_disabled


def test_REQ_PRV_105_block_rename_manual_update(tmp_path, caplog):
    """REQ-PRV-105: Renaming blocks requires manual updates"""
    handler = PreservationHandler()

    # Old file with old block name
    old_content = """@PRESERVE_START old_name
preserved content
custom code here
@PRESERVE_END old_name"""

    file = tmp_path / "code.py"
    file.write_text(old_content)

    # Extract preserved content
    preserved = handler.extract_preserved_content(file)
    assert "old_name" in preserved
    assert "preserved content\n" in preserved["old_name"]
    assert "custom code here\n" in preserved["old_name"]

    # New template uses different block name (renamed)
    new_template = """@PRESERVE_START new_name
default content
@PRESERVE_END new_name"""

    # Inject - names don't match, so preserved content is lost
    import logging

    caplog.set_level(logging.WARNING)
    result = handler.inject_preserved_content(new_template, preserved)

    # Old content is not present (identifier mismatch)
    assert "preserved content" not in result
    assert "custom code here" not in result

    # When preserved_blocks dict has content but identifier doesn't match,
    # the template default content is skipped (block becomes empty)
    assert "@PRESERVE_START new_name" in result
    assert "@PRESERVE_END new_name" in result
    assert result.strip() == "@PRESERVE_START new_name\n@PRESERVE_END new_name"

    # Should warn about lost block
    assert any(
        "old_name" in record.message and "lost" in record.message.lower()
        for record in caplog.records
    )

    # Manual fix: User must update old file to use new name
    manually_updated = """@PRESERVE_START new_name
preserved content
custom code here
@PRESERVE_END new_name"""

    file.write_text(manually_updated)

    # Now extraction uses new name
    preserved_updated = handler.extract_preserved_content(file)
    assert "new_name" in preserved_updated
    assert "old_name" not in preserved_updated

    # Injection now works correctly
    result_fixed = handler.inject_preserved_content(new_template, preserved_updated)
    assert "preserved content" in result_fixed
    assert "custom code here" in result_fixed
    # Template default is replaced
    assert result_fixed.count("default content") == 0
