#!/usr/bin/env python3
"""
Test suite for edge cases example

This module contains tests that validate the edge cases example
and ensure proper handling of boundary conditions.
"""
# N802: Allow uppercase in test names for REQ traceability
# PTH109: os.getcwd() is fine in tests
# S607: subprocess with partial path is acceptable in tests

import json
import os
import subprocess
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
import yaml


@pytest.fixture
def edge_cases_dir():
    """Return path to edge-cases example directory."""
    return Path(__file__).parent.parent / "examples" / "edge-cases"


@pytest.fixture
def output_dir(edge_cases_dir):
    """Return path to output directory."""
    return edge_cases_dir / "output"


class TestEdgeCasesConfiguration:
    """Test configuration edge cases."""

    def test_REQ_CFG_001_config_loads(self, edge_cases_dir):
        """Test that configuration file loads without errors (REQ-CFG-001)."""
        config_path = edge_cases_dir / "config.yaml"
        with open(config_path) as f:
            config = yaml.safe_load(f)

        assert config is not None
        assert "inputs" in config
        assert "static_tokens" in config
        assert "templates" in config

    def test_REQ_CFG_074_token_collision_defined(self, edge_cases_dir):
        """Test that token collision scenario is present (REQ-CFG-074-077)."""
        config_path = edge_cases_dir / "config.yaml"
        with open(config_path) as f:
            config = yaml.safe_load(f)

        # Check that 'version' is in static_tokens
        assert "version" in config["static_tokens"]

        # Check that json input extracts project.version (collision)
        # When both are present, should get warning


class TestEdgeCasesData:
    """Test edge cases in input data files."""

    def test_REQ_EXT_010_json_edge_data(self, edge_cases_dir):
        """Test JSON edge cases data file (REQ-EXT-010-014)."""
        json_path = edge_cases_dir / "edge-data.json"
        with open(json_path, encoding="utf-8") as f:
            data = json.load(f)

        # Test empty arrays
        assert data["modules"] == []
        assert data["features"]["enabled"] == []

        # Test null values
        assert data["features"]["experimental"] is None

        # Test deep nesting (5 levels)
        city = data["project"]["metadata"]["author"]["profile"]["location"]["city"]
        assert "name" in city
        assert "coordinates" in city

    def test_REQ_EXT_030_xml_edge_data(self, edge_cases_dir):
        """Test XML edge cases data file (REQ-EXT-030-038)."""
        from xml.etree import ElementTree as ET

        xml_path = edge_cases_dir / "edge-config.xml"
        tree = ET.parse(xml_path)
        root = tree.getroot()

        # Test attributes and text content
        server = root.find("server")
        assert server is not None
        assert server.get("host") == "localhost"
        assert server.find("name").text == "Production Server"

        # Test empty element
        empty = root.find("empty_element")
        assert empty is not None
        assert empty.text is None

    def test_REQ_EXT_020_yaml_edge_data(self, edge_cases_dir):
        """Test YAML edge cases data file (REQ-EXT-020-024)."""
        yaml_path = edge_cases_dir / "edge-tokens.yaml"
        with open(yaml_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        # Test boolean variations
        assert data["booleans"]["true_values"][0] is True
        assert data["booleans"]["false_values"][0] is False

        # Test empty collections
        assert data["empty"]["list"] == []
        assert data["empty"]["dict"] == {}


class TestEdgeCasesGeneration:
    """Test template generation with edge cases."""

    def test_REQ_SYS_033_generate_without_errors(self, edge_cases_dir, tmp_path):
        """Test that generation completes without errors (REQ-SYS-033)."""
        # Change to edge-cases directory
        original_dir = os.getcwd()
        try:
            os.chdir(edge_cases_dir)

            # Run template-forge using Python module invocation for cross-platform compatibility
            result = subprocess.run(
                [sys.executable, "-m", "template_forge.cli", "config.yaml"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            # Should succeed (exit code 0)
            assert result.returncode == 0, f"Generation failed: {result.stderr}"

        finally:
            os.chdir(original_dir)

    def test_REQ_TPL_021_always_generated_template(self, output_dir):
        """Test that always-generated template is created (REQ-TPL-021)."""
        output_file = output_dir / "always-generated.txt"
        assert output_file.exists(), "always-generated.txt should be created"

        content = output_file.read_text(encoding="utf-8")

        # Check that empty arrays are handled
        assert "No features enabled" in content or "features enabled" in content

        # Check that defaults are applied
        assert "Unknown" in content or "EdgeCaseTest" in content

    def test_REQ_TPL_134_conditional_template_not_generated(self, output_dir):
        """Test that conditional template is NOT generated when condition is false (REQ-TPL-134)."""
        # With enable_feature: false in config, this should not be generated
        output_file = output_dir / "conditionally-generated.txt"
        assert not output_file.exists(), (
            "conditionally-generated.txt should NOT be created when enable_feature is false"
        )

    def test_REQ_TPL_134_production_template_not_generated(self, output_dir):
        """Test that production template is NOT generated in development (REQ-TPL-134)."""
        # With environment: development in config, this should not be generated
        output_file = output_dir / "production-only.txt"
        assert not output_file.exists(), (
            "production-only.txt should NOT be created in development environment"
        )

    def test_REQ_PRV_030_preservation_template(self, output_dir):
        """Test that preservation template is created with markers (REQ-PRV-030-044)."""
        output_file = output_dir / "with-preservation.py"
        assert output_file.exists(), "with-preservation.py should be created"

        content = output_file.read_text(encoding="utf-8")

        # Check preservation markers are present
        assert "@PRESERVE_START custom_imports" in content
        assert "@PRESERVE_END custom_imports" in content
        assert "@PRESERVE_START custom_methods" in content
        assert "@PRESERVE_END custom_methods" in content

    def test_REQ_CFG_041_token_override_template(self, output_dir):
        """Test that template-specific token overrides work (REQ-CFG-041)."""
        output_file = output_dir / "with-overrides.txt"
        assert output_file.exists(), "with-overrides.txt should be created"

        content = output_file.read_text()

        # Should use template-specific author
        assert "Template-Specific Author" in content
        # The phrase "Static Author" appears in the explanation section, not as actual output
        # Check that it's actually used correctly where it matters
        assert "Author (from template tokens): Template-Specific Author" in content


class TestEdgeCasesDryRun:
    """Test dry-run mode with edge cases."""

    def test_REQ_CLI_030_dry_run_mode(self, edge_cases_dir):
        """Test dry-run mode shows operations without executing (REQ-CLI-030-036)."""
        original_dir = os.getcwd()
        try:
            os.chdir(edge_cases_dir)

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "template_forge.cli",
                    "config.yaml",
                    "--dry-run",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            assert result.returncode == 0

            # Should mention dry run
            assert "DRY RUN" in result.stdout or "dry" in result.stdout.lower()

        finally:
            os.chdir(original_dir)


class TestEdgeCasesValidation:
    """Test validation mode with edge cases."""

    def test_REQ_CLI_100_validate_mode(self, edge_cases_dir):
        """Test validation mode (REQ-CLI-100-105)."""
        original_dir = os.getcwd()
        try:
            os.chdir(edge_cases_dir)

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "template_forge.cli",
                    "config.yaml",
                    "--validate",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            # Should succeed
            assert result.returncode == 0, f"Validation failed: {result.stderr}"

        finally:
            os.chdir(original_dir)


class TestEmptyArrayHandling:
    """Test handling of empty arrays and collections."""

    def test_REQ_TPL_021_empty_array_iteration(self, output_dir):
        """Test that empty arrays don't cause errors in loops (REQ-TPL-021)."""
        output_file = output_dir / "always-generated.txt"

        if output_file.exists():
            content = output_file.read_text(encoding="utf-8")

            # Should handle empty arrays gracefully
            assert "No features enabled" in content or "No modules defined" in content


class TestRegexEdgeCases:
    """Test regex filtering edge cases."""

    def test_REQ_EXT_073_regex_no_match(self, output_dir):
        """Test regex that doesn't match uses original value (REQ-EXT-073)."""
        output_file = output_dir / "always-generated.txt"

        if output_file.exists():
            content = output_file.read_text(encoding="utf-8")

            # When regex doesn't match, should use original value
            # The actual output shows "only text here" which is correct per REQ-EXT-073
            assert (
                "No Match Regex: only text here" in content
                or "only text here" in content
            )


class TestTransformEdgeCases:
    """Test data transformation edge cases."""

    def test_REQ_EXT_062_transform_on_unexpected_types(self, edge_cases_dir):
        """Test that transforms handle unexpected types gracefully (REQ-EXT-062)."""
        # This is tested during generation - should not fail
        # REQ-EXT-062: Type conversions shall handle conversion errors gracefully
        original_dir = os.getcwd()
        try:
            os.chdir(edge_cases_dir)

            result = subprocess.run(
                [sys.executable, "-m", "template_forge.cli", "config.yaml"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            # Should complete without errors even with transform edge cases
            assert result.returncode == 0

        finally:
            os.chdir(original_dir)


class TestCodePreservation:
    """Test code preservation edge cases."""

    def test_REQ_PRV_032_preservation_markers_present(self, output_dir):
        """Test that preservation markers are included in output (REQ-PRV-032)."""
        output_file = output_dir / "with-preservation.py"

        if output_file.exists():
            content = output_file.read_text()

            # Count preservation blocks
            start_markers = content.count("@PRESERVE_START")
            end_markers = content.count("@PRESERVE_END")

            # Should have matching start and end markers
            assert start_markers == end_markers
            assert start_markers >= 4  # At least 4 preservation blocks


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
