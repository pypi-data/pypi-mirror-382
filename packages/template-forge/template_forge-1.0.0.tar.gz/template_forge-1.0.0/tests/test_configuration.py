"""
Test suite for Configuration Requirements (REQ-CFG-*)

Each test function maps to one or more specific requirements from:
docs/requirements/02_configuration.md
"""

import pytest
import yaml

from template_forge.core import StructuredDataExtractor, TemplateForge


class TestConfigurationFormat:
    """Tests for REQ-CFG-001 through REQ-CFG-004: Configuration File Format"""

    def test_REQ_CFG_001_yaml_format(self, tmp_path):
        """REQ-CFG-001: System shall use YAML format for configuration"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
inputs:
  - path: test.json
    namespace: test
static_tokens:
  test_key: test_value
templates:
  - template: test.j2
    output: test.txt
""")

        # Should load without error
        with open(config_file) as f:
            config = yaml.safe_load(f)

        assert isinstance(config, dict)
        assert "inputs" in config
        assert "static_tokens" in config

    def test_REQ_CFG_003_validate_syntax(self, tmp_path):
        """REQ-CFG-003: System validates configuration syntax before processing"""
        config_file = tmp_path / "bad_config.yaml"
        config_file.write_text("""
inputs:
  - path: test.json
    namespace: test
  invalid yaml: [unclosed bracket
""")

        with pytest.raises(yaml.YAMLError), open(config_file) as f:
            yaml.safe_load(f)


class TestConfigurationStructure:
    """Tests for REQ-CFG-010 through REQ-CFG-014: Configuration Structure"""

    def test_REQ_CFG_011_requires_data_source(self, tmp_path):
        """REQ-CFG-011: At least one data extraction mechanism required"""
        # Config with neither inputs nor static_tokens
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
templates:
  - template: test.j2
    output: test.txt
""")

        with pytest.raises(
            RuntimeError,
            match="Configuration must define at least one data extraction mechanism",
        ):
            forge = TemplateForge(config_file)

    def test_REQ_CFG_012_requires_output_target(self, tmp_path):
        """REQ-CFG-012: At least one output generation mechanism required"""
        # Config with neither templates nor template_dir
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
static_tokens:
  key: value
""")

        with pytest.raises(
            RuntimeError,
            match="Configuration must define at least one output generation mechanism",
        ):
            forge = TemplateForge(config_file)

    def test_REQ_CFG_013_requires_both_data_and_output(self, tmp_path):
        """REQ-CFG-013: Must define data extraction AND output generation"""
        # Valid config with both
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
static_tokens:
  key: value
templates:
  - template: test.j2
    output: test.txt
""")

        # Should not raise
        forge = TemplateForge(config_file)
        assert forge is not None

    def test_REQ_CFG_014_validates_structure(self, tmp_path):
        """REQ-CFG-014: System validates structure and reports clear errors"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
# No data source or output target
random_key: value
""")

        with pytest.raises(
            RuntimeError,
            match="Configuration must define at least one data extraction mechanism",
        ):
            forge = TemplateForge(config_file)


class TestInputConfiguration:
    """Tests for REQ-CFG-020 through REQ-CFG-025: Input Configuration"""

    def test_REQ_CFG_020_input_required_fields(self, tmp_path):
        """REQ-CFG-020: Each input must specify path and namespace"""
        json_file = tmp_path / "test.json"
        json_file.write_text('{"key": "value"}')

        config = {
            "inputs": [{"path": str(json_file), "namespace": "test"}],
            "templates": [{"template": "test.j2", "output": "test.txt"}],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert "test" in tokens

    def test_REQ_CFG_021_namespace_creates_hierarchy(self, tmp_path):
        """REQ-CFG-021: Namespace organizes tokens hierarchically"""
        json_file = tmp_path / "test.json"
        json_file.write_text('{"app_name": "MyApp", "version": "1.0"}')

        config = {
            "inputs": [
                {
                    "path": str(json_file),
                    "namespace": "project",
                    "tokens": [
                        {"name": "name", "key": "app_name"},
                        {"name": "ver", "key": "version"},
                    ],
                }
            ],
            "templates": [{"template": "test.j2", "output": "test.txt"}],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        # Tokens should be under namespace
        assert "project" in tokens
        assert "name" in tokens["project"]
        assert "ver" in tokens["project"]
        assert tokens["project"]["name"] == "MyApp"
        assert tokens["project"]["ver"] == "1.0"

    def test_REQ_CFG_022_default_extraction_all_keys(self, tmp_path):
        """REQ-CFG-022: If no tokens specified, extract all top-level keys"""
        json_file = tmp_path / "test.json"
        json_file.write_text('{"key1": "value1", "key2": "value2", "key3": "value3"}')

        config = {
            "inputs": [
                {
                    "path": str(json_file),
                    "namespace": "test",
                    # No tokens specified
                }
            ],
            "templates": [{"template": "test.j2", "output": "test.txt"}],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        # All top-level keys should be extracted
        assert "test" in tokens
        assert "key1" in tokens["test"]
        assert "key2" in tokens["test"]
        assert "key3" in tokens["test"]

    def test_REQ_CFG_023_token_extraction_fields(self, tmp_path):
        """REQ-CFG-023: Token extraction rules specify name and key"""
        json_file = tmp_path / "test.json"
        json_file.write_text('{"nested": {"value": "test"}}')

        config = {
            "inputs": [
                {
                    "path": str(json_file),
                    "namespace": "ns",
                    "tokens": [{"name": "my_token", "key": "nested.value"}],
                }
            ],
            "templates": [{"template": "test.j2", "output": "test.txt"}],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert tokens["ns"]["my_token"] == "test"

    def test_REQ_CFG_024_dot_notation_support(self, tmp_path):
        """REQ-CFG-024: Token keys support dot notation, arrays, wildcards"""
        json_file = tmp_path / "test.json"
        json_file.write_text("""
{
  "project": {
    "metadata": {
      "version": "1.0.0"
    }
  },
  "users": [
    {"name": "Alice"},
    {"name": "Bob"}
  ]
}
""")

        config = {
            "inputs": [
                {
                    "path": str(json_file),
                    "namespace": "data",
                    "tokens": [
                        {"name": "ver", "key": "project.metadata.version"},
                        {"name": "first_user", "key": "users[0].name"},
                        {"name": "all_users", "key": "users[*].name"},
                    ],
                }
            ],
            "templates": [{"template": "test.j2", "output": "test.txt"}],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert tokens["data"]["ver"] == "1.0.0"
        assert tokens["data"]["first_user"] == "Alice"
        assert tokens["data"]["all_users"] == ["Alice", "Bob"]

    def test_REQ_CFG_025_namespace_prevents_collisions(self, tmp_path):
        """REQ-CFG-025: Namespaces prevent token collisions between files"""
        # Two files with same token names
        file1 = tmp_path / "project.json"
        file1.write_text('{"version": "1.0", "name": "Project1"}')

        file2 = tmp_path / "library.json"
        file2.write_text('{"version": "2.0", "name": "Library1"}')

        config = {
            "inputs": [
                {
                    "path": str(file1),
                    "namespace": "project",
                    "tokens": [
                        {"name": "version", "key": "version"},
                        {"name": "name", "key": "name"},
                    ],
                },
                {
                    "path": str(file2),
                    "namespace": "library",
                    "tokens": [
                        {"name": "version", "key": "version"},
                        {"name": "name", "key": "name"},
                    ],
                },
            ],
            "templates": [{"template": "test.j2", "output": "test.txt"}],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        # Both versions should exist without collision
        assert tokens["project"]["version"] == "1.0"
        assert tokens["library"]["version"] == "2.0"
        assert tokens["project"]["name"] == "Project1"
        assert tokens["library"]["name"] == "Library1"


class TestStaticTokens:
    """Tests for REQ-CFG-030 through REQ-CFG-034: Static Tokens"""

    def test_REQ_CFG_030_static_tokens_available(self, tmp_path):
        """REQ-CFG-030: Static tokens available to all templates"""
        config = {
            "static_tokens": {"author": "John Doe", "year": 2025, "license": "MIT"},
            "templates": [{"template": "test.j2", "output": "test.txt"}],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert tokens["author"] == "John Doe"
        assert tokens["year"] == 2025
        assert tokens["license"] == "MIT"

    def test_REQ_CFG_031_static_token_types(self, tmp_path):
        """REQ-CFG-031: Static tokens support various types"""
        config = {
            "static_tokens": {
                "string_val": "text",
                "number_val": 42,
                "bool_val": True,
                "list_val": [1, 2, 3],
                "dict_val": {"key": "value"},
            },
            "templates": [{"template": "test.j2", "output": "test.txt"}],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert isinstance(tokens["string_val"], str)
        assert isinstance(tokens["number_val"], int)
        assert isinstance(tokens["bool_val"], bool)
        assert isinstance(tokens["list_val"], list)
        assert isinstance(tokens["dict_val"], dict)

    def test_REQ_CFG_032_hierarchical_static_tokens(self, tmp_path):
        """REQ-CFG-032: Static tokens support hierarchical structure"""
        config = {
            "static_tokens": {
                "company": {"name": "ACME Corp", "year": 2025},
                "build": {"type": "release", "optimization": "O3"},
            },
            "templates": [{"template": "test.j2", "output": "test.txt"}],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert tokens["company"]["name"] == "ACME Corp"
        assert tokens["company"]["year"] == 2025
        assert tokens["build"]["type"] == "release"

    def test_REQ_CFG_033_static_and_namespaced_coexist(self, tmp_path):
        """REQ-CFG-033: Static and namespaced tokens coexist peacefully"""
        json_file = tmp_path / "test.json"
        json_file.write_text('{"version": "1.0"}')

        config = {
            "inputs": [
                {
                    "path": str(json_file),
                    "namespace": "project",
                    "tokens": [{"name": "version", "key": "version"}],
                }
            ],
            "static_tokens": {"author": "John Doe", "company": {"name": "ACME"}},
            "templates": [{"template": "test.j2", "output": "test.txt"}],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        # Both should coexist
        assert tokens["project"]["version"] == "1.0"
        assert tokens["author"] == "John Doe"
        assert tokens["company"]["name"] == "ACME"


class TestValidation:
    """Tests for REQ-CFG-070 through REQ-CFG-077: Validation"""

    def test_REQ_CFG_070_validate_input_files_exist(self, tmp_path, caplog):
        """REQ-CFG-070: Validate input files exist before processing"""
        config = {
            "inputs": [
                {"path": str(tmp_path / "nonexistent.json"), "namespace": "test"}
            ],
            "templates": [{"template": "test.j2", "output": "test.txt"}],
        }

        extractor = StructuredDataExtractor(config)

        # Should raise FileNotFoundError for missing input files
        with pytest.raises(FileNotFoundError, match="Input file not found"):
            tokens = extractor.extract_tokens()

    def test_REQ_CFG_073_warn_for_missing_tokens(self, tmp_path, caplog):
        """REQ-CFG-073: Log warnings for tokens that cannot be extracted"""
        json_file = tmp_path / "test.json"
        json_file.write_text('{"existing_key": "value"}')

        config = {
            "inputs": [
                {
                    "path": str(json_file),
                    "namespace": "test",
                    "tokens": [{"name": "missing", "key": "nonexistent.key"}],
                }
            ],
            "templates": [{"template": "test.j2", "output": "test.txt"}],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        # Should log warning
        assert any("Could not extract" in record.message for record in caplog.records)

    def test_REQ_CFG_094_auto_detect_format(self, tmp_path):
        """REQ-CFG-094: Auto-detect format from file extension"""
        json_file = tmp_path / "test.json"
        json_file.write_text('{"key": "value"}')

        yaml_file = tmp_path / "test.yaml"
        yaml_file.write_text("key: value")

        config = {
            "inputs": [
                {
                    "path": str(json_file),
                    "namespace": "json_data",
                    # No format specified
                },
                {
                    "path": str(yaml_file),
                    "namespace": "yaml_data",
                    # No format specified
                },
            ],
            "templates": [{"template": "test.j2", "output": "test.txt"}],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        # Both should extract correctly
        assert "json_data" in tokens
        assert "yaml_data" in tokens


class TestConfigurationDiscovery:
    """Tests for REQ-CFG-080 through REQ-CFG-085: Configuration Discovery"""

    def test_REQ_CFG_081_discovery_order(self, tmp_path, monkeypatch):
        """REQ-CFG-081: Configuration discovery searches in correct order"""
        # This is tested in CLI tests
        # Just verify the order is documented correctly
        from template_forge.cli import discover_config

        # Create multiple config files
        (tmp_path / "config.yaml").write_text(
            "static_tokens: {key1: value1}\ntemplates: [{template: t.j2, output: o.txt}]"
        )
        (tmp_path / ".template-forge.yaml").write_text(
            "static_tokens: {key2: value2}\ntemplates: [{template: t.j2, output: o.txt}]"
        )

        monkeypatch.chdir(tmp_path)

        # Should find config.yaml first (higher priority)
        found = discover_config()
        assert found is not None
        assert found.name == "config.yaml"

    def test_REQ_CFG_082_use_first_found(self, tmp_path, monkeypatch):
        """REQ-CFG-082: Use first configuration file found"""
        from template_forge.cli import discover_config

        (tmp_path / "config.yaml").write_text(
            "static_tokens: {first: true}\ntemplates: [{template: t.j2, output: o.txt}]"
        )
        (tmp_path / "config.yml").write_text(
            "static_tokens: {second: true}\ntemplates: [{template: t.j2, output: o.txt}]"
        )

        monkeypatch.chdir(tmp_path)

        found = discover_config()
        assert found.name == "config.yaml"  # Not config.yml


class TestSmartDefaults:
    """Tests for REQ-CFG-090 through REQ-CFG-095: Smart Defaults"""

    def test_REQ_CFG_091_static_only_mode(self, tmp_path):
        """REQ-CFG-091: System operates in static-only mode when no inputs"""
        config = {
            "static_tokens": {"key": "value"},
            "templates": [{"template": "test.j2", "output": "test.txt"}],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        # Should work with only static tokens
        assert tokens["key"] == "value"

    def test_REQ_CFG_093_auto_extract_all_keys(self, tmp_path):
        """REQ-CFG-093: Auto-extract all top-level keys when no tokens specified"""
        json_file = tmp_path / "test.json"
        json_file.write_text('{"a": 1, "b": 2, "c": 3}')

        config = {
            "inputs": [
                {
                    "path": str(json_file),
                    "namespace": "auto",
                    # No tokens specified
                }
            ],
            "templates": [{"template": "test.j2", "output": "test.txt"}],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        # All keys should be extracted
        assert tokens["auto"]["a"] == 1
        assert tokens["auto"]["b"] == 2
        assert tokens["auto"]["c"] == 3


class TestNamespaceValidation:
    """Tests for namespace uniqueness and collision detection"""

    def test_REQ_EXT_094_duplicate_namespace_error(self, tmp_path):
        """REQ-EXT-094: Duplicate namespaces result in validation error"""
        file1 = tmp_path / "file1.json"
        file1.write_text('{"key": "value1"}')

        file2 = tmp_path / "file2.json"
        file2.write_text('{"key": "value2"}')

        config = {
            "inputs": [
                {
                    "path": str(file1),
                    "namespace": "duplicate",  # Same namespace
                },
                {
                    "path": str(file2),
                    "namespace": "duplicate",  # Same namespace
                },
            ],
            "templates": [{"template": "test.j2", "output": "test.txt"}],
        }

        extractor = StructuredDataExtractor(config)

        with pytest.raises(ValueError, match="Duplicate namespace"):
            tokens = extractor.extract_tokens()

    def test_REQ_EXT_094_unique_namespaces_allowed(self, tmp_path):
        """REQ-EXT-094: Unique namespaces work correctly"""
        file1 = tmp_path / "file1.json"
        file1.write_text('{"key": "value1"}')

        file2 = tmp_path / "file2.json"
        file2.write_text('{"key": "value2"}')

        config = {
            "inputs": [
                {"path": str(file1), "namespace": "namespace1"},
                {"path": str(file2), "namespace": "namespace2"},
            ],
            "templates": [{"template": "test.j2", "output": "test.txt"}],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        # Should work fine with unique namespaces
        assert "namespace1" in tokens
        assert "namespace2" in tokens
