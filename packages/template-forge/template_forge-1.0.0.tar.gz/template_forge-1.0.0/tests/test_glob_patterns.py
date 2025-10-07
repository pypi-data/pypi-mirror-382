"""Tests for glob pattern support (REQ-ADV-001, REQ-ADV-006).

These tests verify that file paths in input configurations can use
glob patterns to match multiple files, with support for different
match strategies.
"""

import pytest

from template_forge.core import StructuredDataExtractor


class TestGlobPatternExtraction:
    """Integration tests for glob patterns in extraction workflow."""

    def test_REQ_ADV_001_extract_from_glob_pattern(self, tmp_path):
        """Test full extraction workflow with glob pattern."""
        # Create test files
        (tmp_path / "ecu1.arxml").write_text(
            '<?xml version="1.0"?>'
            "<AUTOSAR><AR-PACKAGES><AR-PACKAGE>"
            "<SHORT-NAME>ECU1</SHORT-NAME>"
            "</AR-PACKAGE></AR-PACKAGES></AUTOSAR>"
        )
        (tmp_path / "ecu2.arxml").write_text(
            '<?xml version="1.0"?>'
            "<AUTOSAR><AR-PACKAGES><AR-PACKAGE>"
            "<SHORT-NAME>ECU2</SHORT-NAME>"
            "</AR-PACKAGE></AR-PACKAGES></AUTOSAR>"
        )

        config = {
            "inputs": [
                {
                    "path": str(tmp_path / "*.arxml"),
                    "namespace": "arxml",
                    "match": "first",
                    "tokens": [
                        {
                            "name": "ecu_name",
                            "key": "AR-PACKAGES.AR-PACKAGE.SHORT-NAME",
                        }
                    ],
                }
            ],
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }
        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert "arxml" in tokens
        assert "ecu_name" in tokens["arxml"]
        # Should extract from first file (ecu1.arxml)
        assert tokens["arxml"]["ecu_name"] == "ECU1"

    def test_REQ_ADV_001_glob_in_config_yaml(self, tmp_path):
        """Test glob pattern with token extraction (simplified test)."""
        # Create test files
        autosar_dir = tmp_path / "autosar"
        autosar_dir.mkdir()
        (autosar_dir / "ecu.arxml").write_text(
            '<?xml version="1.0"?>'
            "<AUTOSAR><AR-PACKAGES><AR-PACKAGE>"
            "<SHORT-NAME>TestECU</SHORT-NAME>"
            "</AR-PACKAGE></AR-PACKAGES></AUTOSAR>"
        )

        # Test extraction directly
        config = {
            "inputs": [
                {
                    "path": "autosar/*.arxml",
                    "namespace": "arxml",
                    "match": "first",
                    "tokens": [
                        {
                            "name": "ecu_name",
                            "key": "AR-PACKAGES.AR-PACKAGE.SHORT-NAME",
                        }
                    ],
                }
            ],
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }
        extractor = StructuredDataExtractor(config)
        extractor.config_dir = tmp_path
        tokens = extractor.extract_tokens()

        assert "arxml" in tokens
        assert "ecu_name" in tokens["arxml"]
        assert tokens["arxml"]["ecu_name"] == "TestECU"

    def test_REQ_ADV_001_glob_with_nested_directories(self, tmp_path):
        """Test glob pattern with nested directory structure."""
        # Create nested structure
        level1 = tmp_path / "level1"
        level2 = level1 / "level2"
        level2.mkdir(parents=True)

        (level2 / "data.json").write_text('{"name": "found_it"}')
        (tmp_path / "other.json").write_text('{"name": "wrong_file"}')

        config = {
            "inputs": [
                {
                    "path": str(tmp_path / "**" / "data.json"),
                    "namespace": "json",
                    "match": "first",
                }
            ],
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }
        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert "json" in tokens
        assert tokens["json"]["name"] == "found_it"

    def test_REQ_ADV_001_single_wildcard_pattern(self, tmp_path):
        """Test glob pattern with single wildcard (*.json)."""
        (tmp_path / "file1.json").write_text('{"name": "file1"}')
        (tmp_path / "file2.json").write_text('{"name": "file2"}')
        (tmp_path / "readme.txt").write_text("Not a JSON file")

        config = {
            "inputs": [
                {
                    "path": str(tmp_path / "*.json"),
                    "namespace": "data",
                    "match": "first",
                }
            ],
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }
        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert "data" in tokens
        assert "name" in tokens["data"]
        # Should use first matching file alphabetically
        assert tokens["data"]["name"] == "file1"

    def test_REQ_ADV_001_no_match_raises_error(self, tmp_path):
        """Test that glob pattern with no matches raises FileNotFoundError."""
        config = {
            "inputs": [
                {
                    "path": str(tmp_path / "*.nonexistent"),
                    "namespace": "data",
                    "match": "first",
                }
            ],
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }
        extractor = StructuredDataExtractor(config)

        with pytest.raises(FileNotFoundError) as exc_info:
            extractor.extract_tokens()

        error_msg = str(exc_info.value)
        assert "No files found matching pattern" in error_msg
        assert "*.nonexistent" in error_msg

    def test_REQ_ADV_001_multiple_files_uses_first(self, tmp_path):
        """Test that 'first' strategy uses alphabetically first matching file."""
        (tmp_path / "aaa.yaml").write_text("name: aaa")
        (tmp_path / "bbb.yaml").write_text("name: bbb")
        (tmp_path / "ccc.yaml").write_text("name: ccc")

        config = {
            "inputs": [
                {
                    "path": str(tmp_path / "*.yaml"),
                    "namespace": "config",
                    "match": "first",
                }
            ],
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }
        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert "config" in tokens
        assert tokens["config"]["name"] == "aaa"

    def test_REQ_ADV_001_error_if_multiple_raises(self, tmp_path):
        """Test that 'error_if_multiple' strategy raises with multiple matches."""
        (tmp_path / "file1.json").write_text('{"name": "file1"}')
        (tmp_path / "file2.json").write_text('{"name": "file2"}')

        config = {
            "inputs": [
                {
                    "path": str(tmp_path / "*.json"),
                    "namespace": "data",
                    "match": "error_if_multiple",
                }
            ],
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }
        extractor = StructuredDataExtractor(config)

        with pytest.raises(ValueError) as exc_info:
            extractor.extract_tokens()

        error_msg = str(exc_info.value)
        assert "Multiple files match pattern" in error_msg
        assert "file1.json" in error_msg
        assert "file2.json" in error_msg

    def test_REQ_ADV_001_error_if_multiple_accepts_single(self, tmp_path):
        """Test that 'error_if_multiple' strategy accepts single match."""
        (tmp_path / "only_file.json").write_text('{"name": "only"}')

        config = {
            "inputs": [
                {
                    "path": str(tmp_path / "*.json"),
                    "namespace": "data",
                    "match": "error_if_multiple",
                }
            ],
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }
        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert "data" in tokens
        assert tokens["data"]["name"] == "only"

    def test_REQ_ADV_001_plain_path_still_works(self, tmp_path):
        """Test that non-glob paths still work as before."""
        (tmp_path / "data.json").write_text('{"name": "test"}')

        config = {
            "inputs": [
                {
                    "path": str(tmp_path / "data.json"),
                    "namespace": "data",
                }
            ],
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }
        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert "data" in tokens
        assert tokens["data"]["name"] == "test"


class TestRealWorldScenarios:
    """Real-world usage scenarios for glob patterns."""

    def test_autosar_project_with_multiple_ecus(self, tmp_path):
        """Realistic AUTOSAR project with multiple ECU files."""
        autosar_dir = tmp_path / "config" / "autosar" / "ecus"
        autosar_dir.mkdir(parents=True)

        # Create multiple ECU configuration files
        for i in range(1, 4):
            (autosar_dir / f"ECU{i}_config.arxml").write_text(
                f'<?xml version="1.0"?>'
                f"<AUTOSAR><AR-PACKAGES><AR-PACKAGE>"
                f"<SHORT-NAME>ECU{i}</SHORT-NAME>"
                f"</AR-PACKAGE></AR-PACKAGES></AUTOSAR>"
            )

        config = {
            "inputs": [
                {
                    "path": str(tmp_path / "config" / "**" / "*.arxml"),
                    "namespace": "arxml",
                    "match": "first",
                    "tokens": [
                        {
                            "name": "ecu_name",
                            "key": "AR-PACKAGES.AR-PACKAGE.SHORT-NAME",
                        }
                    ],
                }
            ],
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }
        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert "arxml" in tokens
        assert "ecu_name" in tokens["arxml"]
        # Should extract from first matching file
        assert tokens["arxml"]["ecu_name"] == "ECU1"

    def test_yaml_config_with_environment_variants(self, tmp_path):
        """Multiple YAML config files for different environments."""
        configs_dir = tmp_path / "configs"
        configs_dir.mkdir()

        (configs_dir / "dev.yaml").write_text("environment: development\nport: 8000")
        (configs_dir / "prod.yaml").write_text("environment: production\nport: 443")
        (configs_dir / "test.yaml").write_text("environment: testing\nport: 9000")

        # Use glob to get first alphabetically (dev.yaml)
        config = {
            "inputs": [
                {
                    "path": str(configs_dir / "*.yaml"),
                    "namespace": "config",
                    "match": "first",
                }
            ],
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }
        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert tokens["config"]["environment"] == "development"


class TestEdgeCases:
    """Edge case tests for glob pattern handling."""

    def test_glob_with_spaces_in_path(self, tmp_path):
        """Test glob pattern with spaces in directory/file names."""
        subdir = tmp_path / "my config"
        subdir.mkdir()
        (subdir / "data.json").write_text('{"name": "test"}')

        config = {
            "inputs": [
                {
                    "path": str(tmp_path / "my config" / "*.json"),
                    "namespace": "data",
                    "match": "first",
                }
            ],
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }
        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert "data" in tokens
        assert tokens["data"]["name"] == "test"

    def test_glob_with_special_characters(self, tmp_path):
        """Test glob pattern with special characters in filenames."""
        (tmp_path / "config-v1.0.yaml").write_text("name: version1")
        (tmp_path / "config-v2.0.yaml").write_text("name: version2")

        config = {
            "inputs": [
                {
                    "path": str(tmp_path / "config-*.yaml"),
                    "namespace": "data",
                    "match": "first",
                }
            ],
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }
        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert "data" in tokens
        assert tokens["data"]["name"] in ["version1", "version2"]

    def test_glob_empty_directory(self, tmp_path):
        """Test glob pattern in empty directory."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        config = {
            "inputs": [
                {
                    "path": str(empty_dir / "*.json"),
                    "namespace": "data",
                    "match": "first",
                }
            ],
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }
        extractor = StructuredDataExtractor(config)

        with pytest.raises(FileNotFoundError) as exc_info:
            extractor.extract_tokens()

        assert "No files found matching pattern" in str(exc_info.value)


class TestDocumentationExamples:
    """Tests to verify examples from documentation work correctly."""

    def test_REQ_ADV_001_example_from_docs(self, tmp_path):
        """Test the example from requirements document."""
        # Example from REQ-ADV-001:
        # inputs:
        #   - path: "autosar/*.arxml"
        #     namespace: arxml
        #     match: first

        autosar_dir = tmp_path / "autosar"
        autosar_dir.mkdir()
        (autosar_dir / "ecu1.arxml").write_text(
            '<?xml version="1.0"?>'
            "<AUTOSAR><AR-PACKAGES><AR-PACKAGE>"
            "<SHORT-NAME>ECU1</SHORT-NAME>"
            "</AR-PACKAGE></AR-PACKAGES></AUTOSAR>"
        )
        (autosar_dir / "ecu2.arxml").write_text(
            '<?xml version="1.0"?>'
            "<AUTOSAR><AR-PACKAGES><AR-PACKAGE>"
            "<SHORT-NAME>ECU2</SHORT-NAME>"
            "</AR-PACKAGE></AR-PACKAGES></AUTOSAR>"
        )

        config = {
            "inputs": [
                {
                    "path": str(autosar_dir / "*.arxml"),
                    "namespace": "arxml",
                    "match": "first",
                    "tokens": [
                        {
                            "name": "ecu_name",
                            "key": "AR-PACKAGES.AR-PACKAGE.SHORT-NAME",
                        }
                    ],
                }
            ],
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }
        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert "arxml" in tokens
        assert "ecu_name" in tokens["arxml"]
        assert tokens["arxml"]["ecu_name"] in ["ECU1", "ECU2"]
