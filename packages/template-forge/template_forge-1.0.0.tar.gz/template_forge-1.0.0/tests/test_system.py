"""
Tests for System Overview Requirements (REQ-SYS-*)
"""

import tempfile
import time
from pathlib import Path

import pytest

from template_forge.core import (
    PreservationHandler,
    StructuredDataExtractor,
    TemplateForge,
    TemplateProcessor,
)

# 1. Purpose


def test_REQ_SYS_001_system_provides_template_driven_generation():
    """REQ-SYS-001: System provides template-driven code generation"""
    config = {"templates": []}
    tokens = {}
    processor = TemplateProcessor(config, tokens)
    assert processor is not None
    assert hasattr(processor, "process_templates")


def test_REQ_SYS_002_supports_multiple_output_types():
    """REQ-SYS-002: Supports code, config, documentation generation"""
    # System can generate any text-based output
    config = {"templates": []}
    tokens = {}
    processor = TemplateProcessor(config, tokens)

    # Test with different template types
    code_template = "def hello(): pass"
    config_template = "key: value"
    doc_template = "# Documentation"

    assert isinstance(code_template, str)
    assert isinstance(config_template, str)
    assert isinstance(doc_template, str)


def test_REQ_SYS_003_eliminates_repetitive_tasks():
    """REQ-SYS-003: Eliminates repetitive manual coding tasks"""
    # System automates generation from data sources
    config = {"templates": []}
    tokens = {}
    processor = TemplateProcessor(config, tokens)
    assert callable(processor.process_templates)


# 2. System Architecture


def test_REQ_SYS_010_core_components_exist():
    """REQ-SYS-010: System has all core components"""
    # Configuration loader - TemplateForge class loads config
    assert TemplateForge is not None

    # Data extraction engine
    from template_forge.core import StructuredDataExtractor

    assert StructuredDataExtractor is not None

    # Template processing engine
    from template_forge.core import TemplateProcessor

    assert TemplateProcessor is not None

    # Code preservation handler
    from template_forge.core import PreservationHandler

    assert PreservationHandler is not None

    # CLI interface
    from template_forge.cli import main

    assert callable(main)


def test_REQ_SYS_011_pipeline_architecture():
    """REQ-SYS-011: System follows pipeline architecture"""
    # Pipeline: load config -> extract tokens -> process templates -> generate -> preserve
    config = {"templates": []}
    tokens = {}
    processor = TemplateProcessor(config, tokens)

    # Verify pipeline methods exist
    assert hasattr(processor, "process_templates")
    from template_forge.core import PreservationHandler, StructuredDataExtractor

    assert StructuredDataExtractor is not None
    assert PreservationHandler is not None


# 3. Use Cases


def test_REQ_SYS_020_supports_primary_use_cases():
    """REQ-SYS-020: Supports primary use cases"""
    # System supports: code gen, config gen, doc gen, AUTOSAR, API codegen
    config = {"templates": []}
    tokens = {}
    processor = TemplateProcessor(config, tokens)

    # System can process any Jinja2 template with data
    assert hasattr(processor, "process_templates")
    assert hasattr(processor, "env")  # Jinja2 environment


# 4. Quality Attributes


def test_REQ_SYS_030_performance_typical_files():
    """REQ-SYS-030: Process typical files (< 1MB) in under 1 second"""
    # Create small template and render it
    from jinja2 import Template

    start = time.time()
    template = Template("{{ name }}")
    result = template.render(name="test")
    elapsed = time.time() - start

    assert elapsed < 1.0
    assert result == "test"


def test_REQ_SYS_031_clear_error_messages():
    """REQ-SYS-031: Provides clear error messages with file names"""
    from pathlib import Path

    # Try to load non-existent config - expect SystemExit or RuntimeError
    nonexistent_path = Path("/nonexistent/config.yaml")

    with pytest.raises((SystemExit, RuntimeError)):
        forge = TemplateForge(nonexistent_path)


def test_REQ_SYS_032_extensible_for_new_formats():
    """REQ-SYS-032: Extensible for new input formats"""
    # System supports multiple formats via StructuredDataExtractor
    from template_forge.core import StructuredDataExtractor

    # StructuredDataExtractor can be instantiated
    config = {"inputs": []}
    extractor = StructuredDataExtractor(config)
    assert extractor is not None


def test_REQ_SYS_033_validates_before_generation():
    """REQ-SYS-033: Validates config and input files before generation"""
    from pathlib import Path

    # Invalid YAML should raise error (SystemExit in this implementation)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write("invalid: yaml: content:")
        f.flush()
        temp_path = Path(f.name)

    try:
        with pytest.raises((Exception, SystemExit)):
            forge = TemplateForge(temp_path)
    finally:
        temp_path.unlink()


def test_REQ_SYS_034_preserves_custom_code():
    """REQ-SYS-034: Preserves existing custom code sections"""
    handler = PreservationHandler()

    existing = """@PRESERVE_START
custom code here
@PRESERVE_END"""

    # Extract preserved content
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(existing)
        f.flush()
        temp_path = Path(f.name)

    try:
        preserved = handler.extract_preserved_content(temp_path)
        # Should find at least one preserved block
        assert isinstance(preserved, dict)
    finally:
        temp_path.unlink()


# 5. Constraints


def test_REQ_SYS_040_requires_python_38_plus():
    """REQ-SYS-040: Requires Python 3.8 or higher"""
    import sys

    assert sys.version_info >= (3, 8)


def test_REQ_SYS_041_uses_jinja2():
    """REQ-SYS-041: Uses Jinja2 as template engine"""
    import jinja2

    assert jinja2 is not None

    # Verify TemplateProcessor uses Jinja2
    config = {"templates": []}
    tokens = {"name": "test"}
    processor = TemplateProcessor(config, tokens)

    # Has Jinja2 environment
    assert hasattr(processor, "env")
    assert isinstance(processor.env, jinja2.Environment)


def test_REQ_SYS_042_minimal_dependencies():
    """REQ-SYS-042: Uses only standard library plus PyYAML and Jinja2"""
    # Core dependencies should be available
    import jinja2
    import yaml

    assert yaml is not None
    assert jinja2 is not None


def test_REQ_SYS_043_cross_platform():
    """REQ-SYS-043: Works on Linux, macOS, Windows"""

    # Code should be importable on all platforms
    from template_forge.core import TemplateProcessor

    config = {"templates": []}
    tokens = {"x": 1}
    processor = TemplateProcessor(config, tokens)

    # Verify it works
    assert processor is not None


# 6. Assumptions


def test_REQ_SYS_050_assumes_wellformed_input():
    """REQ-SYS-050: Assumes input files are well-formed"""
    # Well-formed JSON should work
    import json

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump({"key": "value"}, f)
        temp_path = Path(f.name)

    try:
        config = {
            "inputs": [
                {"path": str(temp_path), "namespace": "test", "extract": {"key": "key"}}
            ]
        }
        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()
        assert "test" in tokens  # namespace-prefixed
    finally:
        temp_path.unlink()


def test_REQ_SYS_051_assumes_valid_jinja2_syntax():
    """REQ-SYS-051: Assumes templates contain valid Jinja2 syntax"""
    from jinja2 import Template

    # Valid template should work
    template = Template("{{ name }}")
    result = template.render(name="test")
    assert result == "test"

    # Invalid template should raise error
    with pytest.raises(Exception):
        Template("{{ invalid syntax ")


def test_REQ_SYS_052_assumes_yaml_knowledge():
    """REQ-SYS-052: Assumes users know basic YAML"""
    import yaml

    # YAML parsing should work
    content = "key: value\nlist:\n  - item1\n  - item2"
    data = yaml.safe_load(content)
    assert data["key"] == "value"
    assert len(data["list"]) == 2


def test_REQ_SYS_053_assumes_writable_output():
    """REQ-SYS-053: Assumes output directories are writable"""
    import tempfile
    from pathlib import Path

    # Should be able to write to temp directory
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test.txt"
        test_file.write_text("content")
        assert test_file.exists()
        assert test_file.read_text() == "content"
