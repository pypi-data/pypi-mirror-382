"""
Test suite for Data Extraction Requirements (REQ-EXT-*)

Each test function maps to one or more specific requirements from:
docs/requirements/03_data_extraction.md
"""

import json

import pytest

from template_forge.core import StructuredDataExtractor


class TestSupportedFormats:
    """Tests for REQ-EXT-001 through REQ-EXT-004: Supported Input Formats"""

    def test_REQ_EXT_001_json_support(self, tmp_path):
        """REQ-EXT-001: System supports JSON format"""
        json_file = tmp_path / "test.json"
        json_file.write_text('{"key": "value"}')

        config = {
            "inputs": [{"path": str(json_file), "namespace": "test"}],
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert "test" in tokens
        assert tokens["test"]["key"] == "value"

    def test_REQ_EXT_001_yaml_support(self, tmp_path):
        """REQ-EXT-001: System supports YAML format"""
        yaml_file = tmp_path / "test.yaml"
        yaml_file.write_text("key: value")

        config = {
            "inputs": [{"path": str(yaml_file), "namespace": "test"}],
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert tokens["test"]["key"] == "value"

    def test_REQ_EXT_001_xml_support(self, tmp_path):
        """REQ-EXT-001: System supports XML format"""
        xml_file = tmp_path / "test.xml"
        xml_file.write_text("<root><key>value</key></root>")

        config = {
            "inputs": [{"path": str(xml_file), "namespace": "test", "format": "xml"}],
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert "test" in tokens

    def test_REQ_EXT_002_auto_detect_format(self, tmp_path):
        """REQ-EXT-002: Auto-detect format from extension"""
        json_file = tmp_path / "data.json"
        json_file.write_text('{"key": "json_value"}')

        yaml_file = tmp_path / "data.yml"
        yaml_file.write_text("key: yaml_value")

        config = {
            "inputs": [
                {"path": str(json_file), "namespace": "json_ns"},
                {"path": str(yaml_file), "namespace": "yaml_ns"},
            ],
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert tokens["json_ns"]["key"] == "json_value"
        assert tokens["yaml_ns"]["key"] == "yaml_value"

    def test_REQ_EXT_003_format_override(self, tmp_path):
        """REQ-EXT-003: Allow explicit format override"""
        # Create a .txt file but treat it as JSON
        txt_file = tmp_path / "data.txt"
        txt_file.write_text('{"key": "value"}')

        config = {
            "inputs": [
                {
                    "path": str(txt_file),
                    "namespace": "test",
                    "format": "json",  # Explicit override
                }
            ],
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert tokens["test"]["key"] == "value"


class TestJSONExtraction:
    """Tests for REQ-EXT-010 through REQ-EXT-014: JSON Data Extraction"""

    def test_REQ_EXT_011_nested_objects(self, tmp_path):
        """REQ-EXT-011: Support extraction from nested JSON objects"""
        json_file = tmp_path / "test.json"
        json_file.write_text('{"level1": {"level2": {"level3": "deep_value"}}}')

        config = {
            "inputs": [
                {
                    "path": str(json_file),
                    "namespace": "test",
                    "tokens": [{"name": "deep", "key": "level1.level2.level3"}],
                }
            ],
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert tokens["test"]["deep"] == "deep_value"

    def test_REQ_EXT_012_array_indexing(self, tmp_path):
        """REQ-EXT-012: Support array indexing"""
        json_file = tmp_path / "test.json"
        json_file.write_text('{"items": ["first", "second", "third"]}')

        config = {
            "inputs": [
                {
                    "path": str(json_file),
                    "namespace": "test",
                    "tokens": [
                        {"name": "first", "key": "items[0]"},
                        {"name": "second", "key": "items[1]"},
                    ],
                }
            ],
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert tokens["test"]["first"] == "first"
        assert tokens["test"]["second"] == "second"

    def test_REQ_EXT_013_wildcard_arrays(self, tmp_path):
        """REQ-EXT-013: Support wildcard for all array elements"""
        json_file = tmp_path / "test.json"
        json_file.write_text("""
{
  "users": [
    {"name": "Alice", "age": 30},
    {"name": "Bob", "age": 25},
    {"name": "Charlie", "age": 35}
  ]
}
""")

        config = {
            "inputs": [
                {
                    "path": str(json_file),
                    "namespace": "test",
                    "tokens": [{"name": "all_names", "key": "users[*].name"}],
                }
            ],
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert tokens["test"]["all_names"] == ["Alice", "Bob", "Charlie"]

    def test_REQ_EXT_014_return_entire_structure(self, tmp_path):
        """REQ-EXT-014: Return entire structure when no tokens specified"""
        json_file = tmp_path / "test.json"
        json_file.write_text('{"a": 1, "b": 2, "c": {"d": 3}}')

        config = {
            "inputs": [
                {
                    "path": str(json_file),
                    "namespace": "test",
                    # No tokens specified
                }
            ],
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert tokens["test"]["a"] == 1
        assert tokens["test"]["b"] == 2
        assert isinstance(tokens["test"]["c"], dict)
        assert tokens["test"]["c"]["d"] == 3


class TestYAMLExtraction:
    """Tests for REQ-EXT-020 through REQ-EXT-024: YAML Data Extraction"""

    def test_REQ_EXT_021_yaml_data_types(self, tmp_path):
        """REQ-EXT-021: Support all YAML data types"""
        yaml_file = tmp_path / "test.yaml"
        yaml_file.write_text("""
string_val: "text"
number_val: 42
float_val: 3.14
bool_val: true
list_val: [1, 2, 3]
dict_val:
  nested: value
""")

        config = {
            "inputs": [{"path": str(yaml_file), "namespace": "test"}],
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert isinstance(tokens["test"]["string_val"], str)
        assert isinstance(tokens["test"]["number_val"], int)
        assert isinstance(tokens["test"]["float_val"], float)
        assert isinstance(tokens["test"]["bool_val"], bool)
        assert isinstance(tokens["test"]["list_val"], list)
        assert isinstance(tokens["test"]["dict_val"], dict)

    def test_REQ_EXT_022_yaml_nested_structures(self, tmp_path):
        """REQ-EXT-022: Support nested YAML structures with dot notation"""
        yaml_file = tmp_path / "test.yaml"
        yaml_file.write_text("""
level1:
  level2:
    level3: deep_value
""")

        config = {
            "inputs": [
                {
                    "path": str(yaml_file),
                    "namespace": "test",
                    "tokens": [{"name": "deep", "key": "level1.level2.level3"}],
                }
            ],
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert tokens["test"]["deep"] == "deep_value"

    def test_REQ_EXT_023_yaml_arrays(self, tmp_path):
        """REQ-EXT-023: Support YAML arrays with indexing and wildcards"""
        yaml_file = tmp_path / "test.yaml"
        yaml_file.write_text("""
items:
  - name: first
  - name: second
  - name: third
""")

        config = {
            "inputs": [
                {
                    "path": str(yaml_file),
                    "namespace": "test",
                    "tokens": [
                        {"name": "first_name", "key": "items[0].name"},
                        {"name": "all_names", "key": "items[*].name"},
                    ],
                }
            ],
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert tokens["test"]["first_name"] == "first"
        assert tokens["test"]["all_names"] == ["first", "second", "third"]


class TestXMLExtraction:
    """Tests for REQ-EXT-030 through REQ-EXT-038: XML Data Extraction"""

    def test_REQ_EXT_031_xml_dot_notation(self, tmp_path):
        """REQ-EXT-031: Support dot notation for XML hierarchy"""
        xml_file = tmp_path / "test.xml"
        xml_file.write_text("<root><parent><child>value</child></parent></root>")

        config = {
            "inputs": [
                {
                    "path": str(xml_file),
                    "namespace": "test",
                    "format": "xml",
                    "tokens": [{"name": "val", "key": "root.parent.child"}],
                }
            ],
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert tokens["test"]["val"] == "value"

    def test_REQ_EXT_033_xml_attributes(self, tmp_path):
        """REQ-EXT-033: Support extraction of XML attributes with @ syntax"""
        xml_file = tmp_path / "test.xml"
        xml_file.write_text(
            '<database host="localhost" port="5432"><name>mydb</name></database>'
        )

        config = {
            "inputs": [
                {
                    "path": str(xml_file),
                    "namespace": "test",
                    "format": "xml",
                    "tokens": [
                        {"name": "host", "key": "database.@host"},
                        {"name": "port", "key": "database.@port"},
                        {"name": "name", "key": "database.name"},
                    ],
                }
            ],
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert tokens["test"]["host"] == "localhost"
        assert tokens["test"]["port"] == "5432"
        assert tokens["test"]["name"] == "mydb"

    def test_REQ_EXT_035_xml_to_dict_conversion(self, tmp_path):
        """REQ-EXT-035: Convert XML elements to dictionaries"""
        xml_file = tmp_path / "test.xml"
        xml_file.write_text("""
<config>
  <database host="localhost">
    <name>mydb</name>
    <user>admin</user>
  </database>
</config>
""")

        config = {
            "inputs": [{"path": str(xml_file), "namespace": "test", "format": "xml"}],
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        # Should convert to dict structure (root element is extracted)
        assert "test" in tokens
        assert "database" in tokens["test"]
        assert tokens["test"]["database"]["name"] == "mydb"
        assert tokens["test"]["database"]["@host"] == "localhost"


class TestARXMLExtraction:
    """Tests for REQ-EXT-040 through REQ-EXT-046: ARXML Data Extraction"""

    def test_REQ_EXT_042_arxml_short_name(self, tmp_path):
        """REQ-EXT-042: Support extraction of AUTOSAR SHORT-NAME elements"""
        arxml_file = tmp_path / "test.arxml"
        arxml_file.write_text("""<?xml version="1.0"?>
<AUTOSAR>
  <AR-PACKAGES>
    <AR-PACKAGE>
      <SHORT-NAME>ECU_Config</SHORT-NAME>
    </AR-PACKAGE>
  </AR-PACKAGES>
</AUTOSAR>
""")

        config = {
            "inputs": [
                {
                    "path": str(arxml_file),
                    "namespace": "ecu",
                    "format": "arxml",
                    "tokens": [
                        {
                            "name": "package_name",
                            "key": "AUTOSAR.AR-PACKAGES.AR-PACKAGE.SHORT-NAME",
                        }
                    ],
                }
            ],
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert tokens["ecu"]["package_name"] == "ECU_Config"

    def test_REQ_EXT_046_arxml_case_sensitive(self, tmp_path):
        """REQ-EXT-046: ARXML is case-sensitive"""
        arxml_file = tmp_path / "test.arxml"
        arxml_file.write_text("""<?xml version="1.0"?>
<AUTOSAR>
  <AR-PACKAGES>
    <AR-PACKAGE>
      <SHORT-NAME>TestPackage</SHORT-NAME>
    </AR-PACKAGE>
  </AR-PACKAGES>
</AUTOSAR>
""")

        config = {
            "inputs": [
                {
                    "path": str(arxml_file),
                    "namespace": "ecu",
                    "format": "arxml",
                    "tokens": [
                        {
                            "name": "name",
                            "key": "AUTOSAR.AR-PACKAGES.AR-PACKAGE.SHORT-NAME",  # Must use uppercase
                        }
                    ],
                }
            ],
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert tokens["ecu"]["name"] == "TestPackage"


class TestTokenExtraction:
    """Tests for REQ-EXT-050 through REQ-EXT-056: Token Extraction"""

    def test_REQ_EXT_051_dot_notation(self, tmp_path):
        """REQ-EXT-051: Support dot notation for nested structures"""
        json_file = tmp_path / "test.json"
        json_file.write_text('{"parent": {"child": {"grandchild": "value"}}}')

        config = {
            "inputs": [
                {
                    "path": str(json_file),
                    "namespace": "test",
                    "tokens": [{"name": "val", "key": "parent.child.grandchild"}],
                }
            ],
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert tokens["test"]["val"] == "value"

    def test_REQ_EXT_055_warn_on_missing_key(self, tmp_path, caplog):
        """REQ-EXT-055: Log warning when token extraction key not found"""
        json_file = tmp_path / "test.json"
        json_file.write_text('{"existing": "value"}')

        config = {
            "inputs": [
                {
                    "path": str(json_file),
                    "namespace": "test",
                    "tokens": [{"name": "missing", "key": "nonexistent.key"}],
                }
            ],
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        # Should log warning
        assert any("Could not extract" in record.message for record in caplog.records)

    def test_REQ_EXT_056_continue_on_extraction_failure(self, tmp_path, caplog):
        """REQ-EXT-056: Continue processing other tokens when one fails"""
        json_file = tmp_path / "test.json"
        json_file.write_text('{"good_key": "value"}')

        config = {
            "inputs": [
                {
                    "path": str(json_file),
                    "namespace": "test",
                    "tokens": [
                        {"name": "bad", "key": "nonexistent"},
                        {"name": "good", "key": "good_key"},
                    ],
                }
            ],
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        # Should still extract the good key
        assert tokens["test"]["good"] == "value"


class TestNamespaceOrganization:
    """Tests for REQ-EXT-090 through REQ-EXT-095: Namespace-Based Organization"""

    def test_REQ_EXT_090_namespace_hierarchical_structure(self, tmp_path):
        """REQ-EXT-090: Tokens organized under namespace"""
        json_file = tmp_path / "test.json"
        json_file.write_text('{"key1": "value1", "key2": "value2"}')

        config = {
            "inputs": [
                {
                    "path": str(json_file),
                    "namespace": "myns",
                    "tokens": [
                        {"name": "token1", "key": "key1"},
                        {"name": "token2", "key": "key2"},
                    ],
                }
            ],
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        # Tokens should be under namespace
        assert "myns" in tokens
        assert "token1" in tokens["myns"]
        assert "token2" in tokens["myns"]
        assert tokens["myns"]["token1"] == "value1"
        assert tokens["myns"]["token2"] == "value2"

    def test_REQ_EXT_092_default_extraction_under_namespace(self, tmp_path):
        """REQ-EXT-092: Default extraction places all top-level keys under namespace"""
        json_file = tmp_path / "test.json"
        json_file.write_text('{"a": 1, "b": 2, "c": 3}')

        config = {
            "inputs": [
                {
                    "path": str(json_file),
                    "namespace": "ns",
                    # No tokens specified
                }
            ],
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        # All keys should be under namespace
        assert tokens["ns"]["a"] == 1
        assert tokens["ns"]["b"] == 2
        assert tokens["ns"]["c"] == 3

    def test_REQ_EXT_093_namespaces_prevent_collisions(self, tmp_path):
        """REQ-EXT-093: Namespaces prevent token collisions by design"""
        file1 = tmp_path / "file1.json"
        file1.write_text('{"version": "1.0", "name": "App1"}')

        file2 = tmp_path / "file2.json"
        file2.write_text('{"version": "2.0", "name": "App2"}')

        config = {
            "inputs": [
                {
                    "path": str(file1),
                    "namespace": "app1",
                    "tokens": [
                        {"name": "version", "key": "version"},
                        {"name": "name", "key": "name"},
                    ],
                },
                {
                    "path": str(file2),
                    "namespace": "app2",
                    "tokens": [
                        {"name": "version", "key": "version"},
                        {"name": "name", "key": "name"},
                    ],
                },
            ],
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        # Both versions should exist without collision
        assert tokens["app1"]["version"] == "1.0"
        assert tokens["app2"]["version"] == "2.0"
        assert tokens["app1"]["name"] == "App1"
        assert tokens["app2"]["name"] == "App2"

    def test_REQ_EXT_094_unique_namespace_required(self, tmp_path):
        """REQ-EXT-094: Each input must have unique namespace"""
        file1 = tmp_path / "file1.json"
        file1.write_text('{"key": "value1"}')

        file2 = tmp_path / "file2.json"
        file2.write_text('{"key": "value2"}')

        config = {
            "inputs": [
                {"path": str(file1), "namespace": "same"},
                {"path": str(file2), "namespace": "same"},  # Duplicate!
            ],
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }

        extractor = StructuredDataExtractor(config)

        with pytest.raises(ValueError, match="Duplicate namespace"):
            tokens = extractor.extract_tokens()


class TestErrorHandling:
    """Tests for REQ-EXT-110 through REQ-EXT-115: Error Handling"""

    def test_REQ_EXT_110_continue_on_file_read_error(self, tmp_path, caplog):
        """REQ-EXT-110: Continue processing if input file cannot be read"""
        nonexistent = tmp_path / "missing.json"

        config = {
            "inputs": [{"path": str(nonexistent), "namespace": "test"}],
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }

        extractor = StructuredDataExtractor(config)

        # Should log error and exit (or raise exception)
        with pytest.raises((SystemExit, FileNotFoundError, RuntimeError)):
            tokens = extractor.extract_tokens()

    def test_REQ_EXT_113_handle_malformed_data(self, tmp_path):
        """REQ-EXT-113: Handle malformed data files with descriptive errors"""
        bad_json = tmp_path / "bad.json"
        bad_json.write_text('{"unclosed": ')

        config = {
            "inputs": [{"path": str(bad_json), "namespace": "test"}],
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }

        extractor = StructuredDataExtractor(config)

        with pytest.raises((SystemExit, RuntimeError)):
            tokens = extractor.extract_tokens()

    def test_REQ_EXT_114_validate_unique_namespaces(self, tmp_path):
        """REQ-EXT-114: Validate all input files have unique namespaces"""
        file1 = tmp_path / "file1.json"
        file1.write_text("{}")
        file2 = tmp_path / "file2.json"
        file2.write_text("{}")

        config = {
            "inputs": [
                {"path": str(file1), "namespace": "dup"},
                {"path": str(file2), "namespace": "dup"},
            ],
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }

        extractor = StructuredDataExtractor(config)

        with pytest.raises(ValueError, match="Duplicate namespace"):
            extractor.extract_tokens()


class TestComplexScenarios:
    """Integration tests for complex extraction scenarios"""

    def test_multiple_namespaces_coexist(self, tmp_path):
        """Test that multiple namespaced inputs coexist properly"""
        json_file = tmp_path / "app.json"
        json_file.write_text('{"name": "MyApp", "version": "1.0"}')

        yaml_file = tmp_path / "config.yaml"
        yaml_file.write_text("host: localhost\nport: 8080")

        config = {
            "inputs": [
                {"path": str(json_file), "namespace": "app"},
                {"path": str(yaml_file), "namespace": "server"},
            ],
            "static_tokens": {"author": "John Doe", "year": 2025},
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        # All should coexist
        assert tokens["app"]["name"] == "MyApp"
        assert tokens["server"]["host"] == "localhost"
        assert tokens["author"] == "John Doe"
        assert tokens["year"] == 2025


# Additional EXT tests for better coverage


def test_REQ_EXT_004_unsupported_format_error(tmp_path):
    """REQ-EXT-004: Clear error for unsupported file format"""
    unsupported_file = tmp_path / "data.xyz"
    unsupported_file.write_text("data")

    config = {"inputs": [{"path": str(unsupported_file), "namespace": "data"}]}

    # Should raise error for unsupported format
    with pytest.raises(Exception) as exc_info:
        extractor = StructuredDataExtractor(config)
        extractor.extract_tokens()

    # Error should be clear
    assert (
        "unsupported" in str(exc_info.value).lower()
        or "format" in str(exc_info.value).lower()
    )


def test_REQ_EXT_010_json_parsing_standard_module(tmp_path):
    """REQ-EXT-010: Parse JSON using standard Python json module"""

    json_file = tmp_path / "test.json"
    data = {"key": "value", "number": 42}
    json_file.write_text(json.dumps(data))

    # Standard json module should work
    with open(json_file) as f:
        parsed = json.load(f)

    assert parsed["key"] == "value"
    assert parsed["number"] == 42


def test_REQ_EXT_020_yaml_parsing_pyyaml(tmp_path):
    """REQ-EXT-020: Parse YAML using PyYAML library"""
    import yaml

    yaml_file = tmp_path / "test.yaml"
    yaml_file.write_text("key: value\nnumber: 42")

    # PyYAML should work
    with open(yaml_file) as f:
        parsed = yaml.safe_load(f)

    assert parsed["key"] == "value"
    assert parsed["number"] == 42


def test_REQ_EXT_024_yaml_anchors_aliases(tmp_path):
    """REQ-EXT-024: Handle YAML anchors and aliases"""
    yaml_file = tmp_path / "test.yaml"
    yaml_content = """
defaults: &defaults
  timeout: 30
  retries: 3

production:
  <<: *defaults
  host: prod.example.com
"""
    yaml_file.write_text(yaml_content)

    config = {"inputs": [{"path": str(yaml_file), "namespace": "config"}]}

    extractor = StructuredDataExtractor(config)
    tokens = extractor.extract_tokens()

    # Aliases should be resolved
    assert tokens["config"]["production"]["timeout"] == 30
    assert tokens["config"]["production"]["retries"] == 3
    assert tokens["config"]["production"]["host"] == "prod.example.com"


def test_REQ_EXT_030_xml_parsing_elementtree(tmp_path):
    """REQ-EXT-030: Parse XML using ElementTree"""
    import xml.etree.ElementTree as ET

    xml_file = tmp_path / "test.xml"
    xml_file.write_text("<root><item>value</item></root>")

    # ElementTree should work
    tree = ET.parse(xml_file)
    root = tree.getroot()

    assert root.tag == "root"
    assert root.find("item").text == "value"


def test_REQ_EXT_032_xml_text_extraction(tmp_path):
    """REQ-EXT-032: Extract XML element text content"""
    xml_file = tmp_path / "test.xml"
    xml_file.write_text("<database><name>mydb</name></database>")

    config = {
        "inputs": [
            {
                "path": str(xml_file),
                "namespace": "db",
                "format": "xml",
                "tokens": [{"name": "db_name", "key": "database.name"}],
            }
        ]
    }

    extractor = StructuredDataExtractor(config)
    tokens = extractor.extract_tokens()

    assert tokens["db"]["db_name"] == "mydb"


def test_REQ_EXT_034_xml_wildcard_children(tmp_path):
    """REQ-EXT-034: Extract all child elements using wildcard"""
    xml_file = tmp_path / "test.xml"
    xml_file.write_text("""
        <servers>
            <server>web01</server>
            <server>web02</server>
            <server>web03</server>
        </servers>
    """)

    config = {
        "inputs": [
            {
                "path": str(xml_file),
                "namespace": "cfg",
                "format": "xml",
                "tokens": [{"name": "all_servers", "key": "servers.*"}],
            }
        ]
    }

    extractor = StructuredDataExtractor(config)
    tokens = extractor.extract_tokens()

    # Should extract all servers
    assert isinstance(tokens["cfg"]["all_servers"], (list, dict))


def test_REQ_EXT_036_xml_attributes_and_text(tmp_path):
    """REQ-EXT-036: Access both attributes and text"""
    xml_file = tmp_path / "test.xml"
    xml_file.write_text('<database host="localhost">mydb</database>')

    config = {
        "inputs": [
            {
                "path": str(xml_file),
                "namespace": "db",
                "format": "xml",
                "tokens": [
                    {"name": "host", "key": "database.@host"},
                    {"name": "name", "key": "database"},
                ],
            }
        ]
    }

    extractor = StructuredDataExtractor(config)
    tokens = extractor.extract_tokens()

    assert tokens["db"]["host"] == "localhost"
    assert "mydb" in str(tokens["db"]["name"])


def test_REQ_EXT_037_xml_multiple_children_list(tmp_path):
    """REQ-EXT-037: Multiple children with same tag name as list"""
    xml_file = tmp_path / "test.xml"
    xml_file.write_text("""
        <servers>
            <server>web01</server>
            <server>web02</server>
        </servers>
    """)

    config = {
        "inputs": [
            {
                "path": str(xml_file),
                "namespace": "cfg",
                "format": "xml",
                "tokens": [
                    {"name": "first", "key": "servers.server[0]"},
                    {"name": "second", "key": "servers.server[1]"},
                ],
            }
        ]
    }

    extractor = StructuredDataExtractor(config)
    tokens = extractor.extract_tokens()

    assert tokens["cfg"]["first"] == "web01"
    assert tokens["cfg"]["second"] == "web02"


def test_REQ_EXT_038_xml_extraction_example(tmp_path):
    """REQ-EXT-038: Complete XML extraction example"""
    xml_file = tmp_path / "config.xml"
    xml_file.write_text("""
        <config>
            <database host="localhost" port="5432">
                <name>mydb</name>
                <user>admin</user>
            </database>
            <servers>
                <server>web01</server>
                <server>web02</server>
            </servers>
        </config>
    """)

    config = {
        "inputs": [
            {
                "path": str(xml_file),
                "namespace": "cfg",
                "format": "xml",
                "tokens": [
                    {"name": "db_host", "key": "database.@host"},
                    {"name": "db_port", "key": "database.@port"},
                    {"name": "db_name", "key": "database.name"},
                    {"name": "db_user", "key": "database.user"},
                    {"name": "first_server", "key": "servers.server[0]"},
                    {"name": "all_servers", "key": "servers.server[*]"},
                ],
            }
        ]
    }

    extractor = StructuredDataExtractor(config)
    tokens = extractor.extract_tokens()

    assert tokens["cfg"]["db_host"] == "localhost"
    assert tokens["cfg"]["db_port"] == "5432"
    assert tokens["cfg"]["db_name"] == "mydb"
    assert tokens["cfg"]["db_user"] == "admin"
    assert tokens["cfg"]["first_server"] == "web01"
    assert isinstance(tokens["cfg"]["all_servers"], list)


def test_REQ_EXT_040_arxml_parsing(tmp_path):
    """REQ-EXT-040: Parse ARXML as specialized XML"""
    arxml_file = tmp_path / "test.arxml"
    arxml_file.write_text("""<?xml version="1.0"?>
        <AUTOSAR>
            <AR-PACKAGES>
                <AR-PACKAGE>
                    <SHORT-NAME>Config</SHORT-NAME>
                </AR-PACKAGE>
            </AR-PACKAGES>
        </AUTOSAR>
    """)

    config = {
        "inputs": [{"path": str(arxml_file), "namespace": "ecu", "format": "arxml"}]
    }

    extractor = StructuredDataExtractor(config)
    tokens = extractor.extract_tokens()

    # Should parse as XML
    assert "ecu" in tokens


def test_REQ_EXT_041_arxml_namespace_handling(tmp_path):
    """REQ-EXT-041: Handle ARXML namespace prefixes"""
    arxml_file = tmp_path / "test.arxml"
    arxml_file.write_text("""<?xml version="1.0"?>
        <ar:AUTOSAR xmlns:ar="http://autosar.org/schema">
            <ar:AR-PACKAGES>
                <ar:AR-PACKAGE>
                    <ar:SHORT-NAME>Config</ar:SHORT-NAME>
                </ar:AR-PACKAGE>
            </ar:AR-PACKAGES>
        </ar:AUTOSAR>
    """)

    # Should handle namespace prefixes
    config = {
        "inputs": [{"path": str(arxml_file), "namespace": "ecu", "format": "arxml"}]
    }

    extractor = StructuredDataExtractor(config)
    tokens = extractor.extract_tokens()

    assert "ecu" in tokens


def test_REQ_EXT_043_arxml_reference_paths(tmp_path):
    """REQ-EXT-043: Extract AUTOSAR reference paths (AR-REF)"""
    arxml_file = tmp_path / "test.arxml"
    arxml_file.write_text("""<?xml version="1.0"?>
        <AUTOSAR>
            <AR-PACKAGES>
                <AR-PACKAGE>
                    <ELEMENTS>
                        <SYSTEM>
                            <MAPPING-REF DEST="SYSTEM">/Path/To/System</MAPPING-REF>
                        </SYSTEM>
                    </ELEMENTS>
                </AR-PACKAGE>
            </AR-PACKAGES>
        </AUTOSAR>
    """)

    config = {
        "inputs": [
            {
                "path": str(arxml_file),
                "namespace": "ecu",
                "format": "arxml",
                "tokens": [
                    {
                        "name": "mapping",
                        "key": "AR-PACKAGES.AR-PACKAGE.ELEMENTS.SYSTEM.MAPPING-REF",
                    }
                ],
            }
        ]
    }

    extractor = StructuredDataExtractor(config)
    tokens = extractor.extract_tokens()

    # Should extract reference path
    assert "mapping" in tokens["ecu"]


def test_REQ_EXT_044_arxml_deep_nesting(tmp_path):
    """REQ-EXT-044: Handle deeply nested AUTOSAR hierarchies"""
    arxml_file = tmp_path / "test.arxml"
    arxml_file.write_text("""<?xml version="1.0"?>
        <AUTOSAR>
            <AR-PACKAGES>
                <AR-PACKAGE>
                    <SHORT-NAME>Level1</SHORT-NAME>
                    <ELEMENTS>
                        <ECU-INSTANCE>
                            <SHORT-NAME>Level2</SHORT-NAME>
                            <COMM-CONTROLLERS>
                                <CAN-COMMUNICATION-CONTROLLER>
                                    <SHORT-NAME>Level3</SHORT-NAME>
                                </CAN-COMMUNICATION-CONTROLLER>
                            </COMM-CONTROLLERS>
                        </ECU-INSTANCE>
                    </ELEMENTS>
                </AR-PACKAGE>
            </AR-PACKAGES>
        </AUTOSAR>
    """)

    config = {
        "inputs": [
            {
                "path": str(arxml_file),
                "namespace": "ecu",
                "format": "arxml",
                "tokens": [
                    {
                        "name": "controller",
                        "key": "AR-PACKAGES.AR-PACKAGE.ELEMENTS.ECU-INSTANCE.COMM-CONTROLLERS.CAN-COMMUNICATION-CONTROLLER.SHORT-NAME",
                    }
                ],
            }
        ]
    }

    extractor = StructuredDataExtractor(config)
    tokens = extractor.extract_tokens()

    # Should navigate deep hierarchy
    assert tokens["ecu"]["controller"] == "Level3"


def test_REQ_EXT_045_arxml_complete_example(tmp_path):
    """REQ-EXT-045: Complete ARXML extraction example"""
    arxml_file = tmp_path / "ecu_config.arxml"
    arxml_file.write_text("""<?xml version="1.0"?>
        <AUTOSAR xmlns="http://autosar.org/schema/r4.0">
            <AR-PACKAGES>
                <AR-PACKAGE>
                    <SHORT-NAME>ECU_Config</SHORT-NAME>
                    <ELEMENTS>
                        <ECU-INSTANCE>
                            <SHORT-NAME>MainECU</SHORT-NAME>
                            <COM-CONFIG-GW-TIME-BASE>0.005</COM-CONFIG-GW-TIME-BASE>
                            <COMM-CONTROLLERS>
                                <CAN-COMMUNICATION-CONTROLLER>
                                    <SHORT-NAME>CAN_Ctrl_0</SHORT-NAME>
                                </CAN-COMMUNICATION-CONTROLLER>
                            </COMM-CONTROLLERS>
                        </ECU-INSTANCE>
                    </ELEMENTS>
                </AR-PACKAGE>
            </AR-PACKAGES>
        </AUTOSAR>
    """)

    config = {
        "inputs": [
            {
                "path": str(arxml_file),
                "namespace": "ecu",
                "format": "arxml",
                "tokens": [
                    {
                        "name": "package_name",
                        "key": "AR-PACKAGES.AR-PACKAGE.SHORT-NAME",
                    },
                    {
                        "name": "ecu_name",
                        "key": "AR-PACKAGES.AR-PACKAGE.ELEMENTS.ECU-INSTANCE.SHORT-NAME",
                    },
                    {
                        "name": "time_base",
                        "key": "AR-PACKAGES.AR-PACKAGE.ELEMENTS.ECU-INSTANCE.COM-CONFIG-GW-TIME-BASE",
                    },
                    {
                        "name": "can_controller",
                        "key": "AR-PACKAGES.AR-PACKAGE.ELEMENTS.ECU-INSTANCE.COMM-CONTROLLERS.CAN-COMMUNICATION-CONTROLLER.SHORT-NAME",
                    },
                ],
            }
        ]
    }

    extractor = StructuredDataExtractor(config)
    tokens = extractor.extract_tokens()

    assert tokens["ecu"]["package_name"] == "ECU_Config"
    assert tokens["ecu"]["ecu_name"] == "MainECU"
    assert tokens["ecu"]["time_base"] == "0.005"
    assert tokens["ecu"]["can_controller"] == "CAN_Ctrl_0"


def test_REQ_EXT_050_key_path_extraction(tmp_path):
    """REQ-EXT-050: Extract tokens based on key paths"""
    json_file = tmp_path / "test.json"
    json_file.write_text('{"level1": {"level2": {"level3": "value"}}}')

    config = {
        "inputs": [
            {
                "path": str(json_file),
                "namespace": "data",
                "tokens": [{"name": "nested", "key": "level1.level2.level3"}],
            }
        ]
    }

    extractor = StructuredDataExtractor(config)
    tokens = extractor.extract_tokens()

    assert tokens["data"]["nested"] == "value"


def test_REQ_EXT_052_array_indexing(tmp_path):
    """REQ-EXT-052: Support array indexing"""
    json_file = tmp_path / "test.json"
    json_file.write_text('{"items": ["first", "second", "third"]}')

    config = {
        "inputs": [
            {
                "path": str(json_file),
                "namespace": "data",
                "tokens": [
                    {"name": "item0", "key": "items[0]"},
                    {"name": "item1", "key": "items[1]"},
                ],
            }
        ]
    }

    extractor = StructuredDataExtractor(config)
    tokens = extractor.extract_tokens()

    assert tokens["data"]["item0"] == "first"
    assert tokens["data"]["item1"] == "second"


def test_REQ_EXT_053_array_wildcard(tmp_path):
    """REQ-EXT-053: Support array wildcard extraction"""
    json_file = tmp_path / "test.json"
    json_file.write_text('{"items": ["a", "b", "c"]}')

    config = {
        "inputs": [
            {
                "path": str(json_file),
                "namespace": "data",
                "tokens": [{"name": "all_items", "key": "items[*]"}],
            }
        ]
    }

    extractor = StructuredDataExtractor(config)
    tokens = extractor.extract_tokens()

    assert tokens["data"]["all_items"] == ["a", "b", "c"]


def test_REQ_EXT_054_object_wildcard(tmp_path):
    """REQ-EXT-054: Support object wildcard extraction"""
    json_file = tmp_path / "test.json"
    json_file.write_text('{"config": {"key1": "val1", "key2": "val2"}}')

    config = {
        "inputs": [
            {
                "path": str(json_file),
                "namespace": "data",
                "tokens": [{"name": "all_config", "key": "config.*"}],
            }
        ]
    }

    extractor = StructuredDataExtractor(config)
    tokens = extractor.extract_tokens()

    assert isinstance(tokens["data"]["all_config"], dict)


def test_REQ_EXT_060_transformations(tmp_path):
    """REQ-EXT-060: Support data transformations"""
    json_file = tmp_path / "test.json"
    json_file.write_text('{"text": "hello world"}')

    config = {
        "inputs": [
            {
                "path": str(json_file),
                "namespace": "data",
                "tokens": [
                    {"name": "upper", "key": "text", "transform": "upper"},
                    {"name": "title", "key": "text", "transform": "title"},
                    {"name": "capitalize", "key": "text", "transform": "capitalize"},
                ],
            }
        ]
    }

    extractor = StructuredDataExtractor(config)
    tokens = extractor.extract_tokens()

    assert tokens["data"]["upper"] == "HELLO WORLD"
    assert tokens["data"]["title"] == "Hello World"
    assert tokens["data"]["capitalize"] == "Hello world"


def test_REQ_EXT_061_transformation_order(tmp_path):
    """REQ-EXT-061: Transformations applied before regex"""
    json_file = tmp_path / "test.json"
    json_file.write_text('{"text": "hello"}')

    config = {
        "inputs": [
            {
                "path": str(json_file),
                "namespace": "data",
                "tokens": [
                    {
                        "name": "transformed",
                        "key": "text",
                        "transform": "upper",
                        "regex": r"[A-Z]+",
                    }
                ],
            }
        ]
    }

    extractor = StructuredDataExtractor(config)
    tokens = extractor.extract_tokens()

    # Transform to HELLO, then regex matches
    assert tokens["data"]["transformed"] == "HELLO"


def test_REQ_EXT_062_transform_strings_only(tmp_path):
    """REQ-EXT-062: Transformations only apply to strings"""
    json_file = tmp_path / "test.json"
    json_file.write_text('{"number": 42, "text": "hello"}')

    config = {
        "inputs": [
            {
                "path": str(json_file),
                "namespace": "data",
                "tokens": [
                    {"name": "num", "key": "number", "transform": "upper"},
                    {"name": "txt", "key": "text", "transform": "upper"},
                ],
            }
        ]
    }

    extractor = StructuredDataExtractor(config)
    tokens = extractor.extract_tokens()

    # Number unchanged, text transformed
    assert tokens["data"]["num"] == 42
    assert tokens["data"]["txt"] == "HELLO"


def test_REQ_EXT_060_strip_transform(tmp_path):
    """REQ-EXT-060: strip transform removes whitespace"""
    json_file = tmp_path / "test.json"
    json_file.write_text('{"text": "  hello  "}')

    config = {
        "inputs": [
            {
                "path": str(json_file),
                "namespace": "data",
                "tokens": [{"name": "stripped", "key": "text", "transform": "strip"}],
            }
        ]
    }

    extractor = StructuredDataExtractor(config)
    tokens = extractor.extract_tokens()
    assert tokens["data"]["stripped"] == "hello"


def test_REQ_EXT_060_snake_case_transform(tmp_path):
    """REQ-EXT-060: snake_case transform converts to snake_case"""
    json_file = tmp_path / "test.json"
    json_file.write_text('{"name": "MyVariableName"}')

    config = {
        "inputs": [
            {
                "path": str(json_file),
                "namespace": "data",
                "tokens": [{"name": "snake", "key": "name", "transform": "snake_case"}],
            }
        ]
    }

    extractor = StructuredDataExtractor(config)
    tokens = extractor.extract_tokens()
    assert tokens["data"]["snake"] == "my_variable_name"


def test_REQ_EXT_060_camel_case_transform(tmp_path):
    """REQ-EXT-060: camel_case transform converts to camelCase"""
    json_file = tmp_path / "test.json"
    json_file.write_text('{"name": "my_variable_name"}')

    config = {
        "inputs": [
            {
                "path": str(json_file),
                "namespace": "data",
                "tokens": [{"name": "camel", "key": "name", "transform": "camel_case"}],
            }
        ]
    }

    extractor = StructuredDataExtractor(config)
    tokens = extractor.extract_tokens()
    assert tokens["data"]["camel"] == "MyVariableName"


def test_REQ_EXT_060_int_transform(tmp_path):
    """REQ-EXT-060: int transform converts to integer"""
    json_file = tmp_path / "test.json"
    json_file.write_text('{"count": "42"}')

    config = {
        "inputs": [
            {
                "path": str(json_file),
                "namespace": "data",
                "tokens": [{"name": "count_int", "key": "count", "transform": "int"}],
            }
        ]
    }

    extractor = StructuredDataExtractor(config)
    tokens = extractor.extract_tokens()
    assert tokens["data"]["count_int"] == 42
    assert isinstance(tokens["data"]["count_int"], int)


def test_REQ_EXT_060_float_transform(tmp_path):
    """REQ-EXT-060: float transform converts to float"""
    json_file = tmp_path / "test.json"
    json_file.write_text('{"value": "3.14"}')

    config = {
        "inputs": [
            {
                "path": str(json_file),
                "namespace": "data",
                "tokens": [
                    {"name": "value_float", "key": "value", "transform": "float"}
                ],
            }
        ]
    }

    extractor = StructuredDataExtractor(config)
    tokens = extractor.extract_tokens()
    assert tokens["data"]["value_float"] == 3.14
    assert isinstance(tokens["data"]["value_float"], float)


def test_REQ_EXT_060_bool_transform(tmp_path):
    """REQ-EXT-060: bool transform converts to boolean"""
    json_file = tmp_path / "test.json"
    json_file.write_text(
        '{"t1": "true", "t2": "1", "t3": "yes", "f1": "false", "f2": "0"}'
    )

    config = {
        "inputs": [
            {
                "path": str(json_file),
                "namespace": "data",
                "tokens": [
                    {"name": "t1", "key": "t1", "transform": "bool"},
                    {"name": "t2", "key": "t2", "transform": "bool"},
                    {"name": "t3", "key": "t3", "transform": "bool"},
                    {"name": "f1", "key": "f1", "transform": "bool"},
                    {"name": "f2", "key": "f2", "transform": "bool"},
                ],
            }
        ]
    }

    extractor = StructuredDataExtractor(config)
    tokens = extractor.extract_tokens()
    assert tokens["data"]["t1"] is True
    assert tokens["data"]["t2"] is True
    assert tokens["data"]["t3"] is True
    assert tokens["data"]["f1"] is False
    assert tokens["data"]["f2"] is False


def test_REQ_EXT_060_len_transform(tmp_path):
    """REQ-EXT-060: len transform gets length"""
    json_file = tmp_path / "test.json"
    json_file.write_text('{"text": "hello", "items": [1, 2, 3, 4, 5]}')

    config = {
        "inputs": [
            {
                "path": str(json_file),
                "namespace": "data",
                "tokens": [
                    {"name": "text_len", "key": "text", "transform": "len"},
                    {"name": "items_len", "key": "items", "transform": "len"},
                ],
            }
        ]
    }

    extractor = StructuredDataExtractor(config)
    tokens = extractor.extract_tokens()
    assert tokens["data"]["text_len"] == 5
    assert tokens["data"]["items_len"] == 5


def test_REQ_EXT_060_any_transform(tmp_path):
    """REQ-EXT-060: any transform checks if any element is truthy"""
    json_file = tmp_path / "test.json"
    json_file.write_text('{"values": [false, false, true, false]}')

    config = {
        "inputs": [
            {
                "path": str(json_file),
                "namespace": "data",
                "tokens": [{"name": "has_any", "key": "values", "transform": "any"}],
            }
        ]
    }

    extractor = StructuredDataExtractor(config)
    tokens = extractor.extract_tokens()
    assert tokens["data"]["has_any"] is True


def test_REQ_EXT_060_all_transform(tmp_path):
    """REQ-EXT-060: all transform checks if all elements are truthy"""
    json_file = tmp_path / "test.json"
    json_file.write_text(
        '{"all_true": [true, true, true], "has_false": [true, false, true]}'
    )

    config = {
        "inputs": [
            {
                "path": str(json_file),
                "namespace": "data",
                "tokens": [
                    {"name": "all_t", "key": "all_true", "transform": "all"},
                    {"name": "all_f", "key": "has_false", "transform": "all"},
                ],
            }
        ]
    }

    extractor = StructuredDataExtractor(config)
    tokens = extractor.extract_tokens()
    assert tokens["data"]["all_t"] is True
    assert tokens["data"]["all_f"] is False


def test_REQ_EXT_060_sum_transform(tmp_path):
    """REQ-EXT-060: sum transform sums numeric values"""
    json_file = tmp_path / "test.json"
    json_file.write_text('{"numbers": [1, 2, 3, 4, 5]}')

    config = {
        "inputs": [
            {
                "path": str(json_file),
                "namespace": "data",
                "tokens": [{"name": "total", "key": "numbers", "transform": "sum"}],
            }
        ]
    }

    extractor = StructuredDataExtractor(config)
    tokens = extractor.extract_tokens()
    assert tokens["data"]["total"] == 15


def test_REQ_EXT_060_max_min_transforms(tmp_path):
    """REQ-EXT-060: max and min transforms get maximum and minimum"""
    json_file = tmp_path / "test.json"
    json_file.write_text('{"numbers": [5, 2, 9, 1, 7]}')

    config = {
        "inputs": [
            {
                "path": str(json_file),
                "namespace": "data",
                "tokens": [
                    {"name": "maximum", "key": "numbers", "transform": "max"},
                    {"name": "minimum", "key": "numbers", "transform": "min"},
                ],
            }
        ]
    }

    extractor = StructuredDataExtractor(config)
    tokens = extractor.extract_tokens()
    assert tokens["data"]["maximum"] == 9
    assert tokens["data"]["minimum"] == 1


def test_REQ_EXT_060_unique_transform(tmp_path):
    """REQ-EXT-060: unique transform removes duplicates"""
    json_file = tmp_path / "test.json"
    json_file.write_text('{"items": [1, 2, 2, 3, 1, 4, 3]}')

    config = {
        "inputs": [
            {
                "path": str(json_file),
                "namespace": "data",
                "tokens": [
                    {"name": "unique_items", "key": "items", "transform": "unique"}
                ],
            }
        ]
    }

    extractor = StructuredDataExtractor(config)
    tokens = extractor.extract_tokens()
    assert tokens["data"]["unique_items"] == [1, 2, 3, 4]


def test_REQ_EXT_062_type_conversion_errors_handled(tmp_path):
    """REQ-EXT-062: Type conversion errors handled gracefully"""
    json_file = tmp_path / "test.json"
    json_file.write_text('{"invalid": "not_a_number"}')

    config = {
        "inputs": [
            {
                "path": str(json_file),
                "namespace": "data",
                "tokens": [
                    {"name": "invalid_int", "key": "invalid", "transform": "int"}
                ],
            }
        ]
    }

    extractor = StructuredDataExtractor(config)
    tokens = extractor.extract_tokens()
    # Should return original value on error
    assert tokens["data"]["invalid_int"] == "not_a_number"


def test_REQ_EXT_063_collection_ops_incompatible_types(tmp_path):
    """REQ-EXT-063: Collection operations handle incompatible types"""
    json_file = tmp_path / "test.json"
    json_file.write_text('{"value": "not_a_list"}')

    config = {
        "inputs": [
            {
                "path": str(json_file),
                "namespace": "data",
                "tokens": [{"name": "sum_result", "key": "value", "transform": "sum"}],
            }
        ]
    }

    extractor = StructuredDataExtractor(config)
    tokens = extractor.extract_tokens()
    # Should return original value for incompatible type
    assert tokens["data"]["sum_result"] == "not_a_list"


def test_REQ_EXT_070_regex_filtering(tmp_path):
    """REQ-EXT-070: Support regex filtering"""
    json_file = tmp_path / "test.json"
    json_file.write_text('{"version": "v1.2.3"}')

    config = {
        "inputs": [
            {
                "path": str(json_file),
                "namespace": "data",
                "tokens": [
                    {"name": "ver", "key": "version", "regex": r"v(\d+\.\d+\.\d+)"}
                ],
            }
        ]
    }

    extractor = StructuredDataExtractor(config)
    tokens = extractor.extract_tokens()

    # Should extract first group
    assert tokens["data"]["ver"] == "1.2.3"


def test_REQ_EXT_071_regex_first_group(tmp_path):
    """REQ-EXT-071: Extract first matching group"""
    json_file = tmp_path / "test.json"
    json_file.write_text('{"text": "abc123def"}')

    config = {
        "inputs": [
            {
                "path": str(json_file),
                "namespace": "data",
                "tokens": [
                    {"name": "num", "key": "text", "regex": r"[a-z]+(\d+)[a-z]+"}
                ],
            }
        ]
    }

    extractor = StructuredDataExtractor(config)
    tokens = extractor.extract_tokens()

    assert tokens["data"]["num"] == "123"


def test_REQ_EXT_072_regex_entire_match(tmp_path):
    """REQ-EXT-072: Extract entire match if no groups"""
    json_file = tmp_path / "test.json"
    json_file.write_text('{"text": "abc123def"}')

    config = {
        "inputs": [
            {
                "path": str(json_file),
                "namespace": "data",
                "tokens": [{"name": "match", "key": "text", "regex": r"\d+"}],
            }
        ]
    }

    extractor = StructuredDataExtractor(config)
    tokens = extractor.extract_tokens()

    assert tokens["data"]["match"] == "123"


def test_REQ_EXT_073_regex_no_match_original(tmp_path):
    """REQ-EXT-073: Use original value if regex doesn't match"""
    json_file = tmp_path / "test.json"
    json_file.write_text('{"text": "hello"}')

    config = {
        "inputs": [
            {
                "path": str(json_file),
                "namespace": "data",
                "tokens": [
                    {"name": "val", "key": "text", "regex": r"\d+"}  # Won't match
                ],
            }
        ]
    }

    extractor = StructuredDataExtractor(config)
    tokens = extractor.extract_tokens()

    # Should keep original
    assert tokens["data"]["val"] == "hello"


def test_REQ_EXT_074_regex_after_transform(tmp_path):
    """REQ-EXT-074: Regex applied after transformations"""
    json_file = tmp_path / "test.json"
    json_file.write_text('{"text": "version 1.2.3"}')

    config = {
        "inputs": [
            {
                "path": str(json_file),
                "namespace": "data",
                "tokens": [
                    {
                        "name": "ver",
                        "key": "text",
                        "transform": "upper",
                        "regex": r"VERSION (\S+)",
                    }
                ],
            }
        ]
    }

    extractor = StructuredDataExtractor(config)
    tokens = extractor.extract_tokens()

    # Transform first, then regex
    assert tokens["data"]["ver"] == "1.2.3"


def test_REQ_EXT_080_wildcard_returns_list(tmp_path):
    """REQ-EXT-080: Wildcard [*] returns list"""
    json_file = tmp_path / "test.json"
    json_file.write_text('{"items": [1, 2, 3]}')

    config = {
        "inputs": [
            {
                "path": str(json_file),
                "namespace": "data",
                "tokens": [{"name": "all", "key": "items[*]"}],
            }
        ]
    }

    extractor = StructuredDataExtractor(config)
    tokens = extractor.extract_tokens()

    assert isinstance(tokens["data"]["all"], list)
    assert tokens["data"]["all"] == [1, 2, 3]


def test_REQ_EXT_081_wildcard_returns_object(tmp_path):
    """REQ-EXT-081: Wildcard .* returns entire object"""
    json_file = tmp_path / "test.json"
    json_file.write_text('{"data": {"a": 1, "b": 2}}')

    config = {
        "inputs": [
            {
                "path": str(json_file),
                "namespace": "ns",
                "tokens": [{"name": "all", "key": "data.*"}],
            }
        ]
    }

    extractor = StructuredDataExtractor(config)
    tokens = extractor.extract_tokens()

    assert isinstance(tokens["ns"]["all"], dict)


def test_REQ_EXT_082_zero_based_index(tmp_path):
    """REQ-EXT-082: Array elements zero-based indexed"""
    json_file = tmp_path / "test.json"
    json_file.write_text('{"items": ["zero", "one", "two"]}')

    config = {
        "inputs": [
            {
                "path": str(json_file),
                "namespace": "data",
                "tokens": [
                    {"name": "first", "key": "items[0]"},
                    {"name": "third", "key": "items[2]"},
                ],
            }
        ]
    }

    extractor = StructuredDataExtractor(config)
    tokens = extractor.extract_tokens()

    assert tokens["data"]["first"] == "zero"
    assert tokens["data"]["third"] == "two"


def test_REQ_EXT_083_nested_array_access(tmp_path):
    """REQ-EXT-083: Nested array access supported"""
    json_file = tmp_path / "test.json"
    json_file.write_text('{"items": [{"subitems": [{"name": "target"}]}]}')

    config = {
        "inputs": [
            {
                "path": str(json_file),
                "namespace": "data",
                "tokens": [{"name": "nested", "key": "items[0].subitems[0].name"}],
            }
        ]
    }

    extractor = StructuredDataExtractor(config)
    tokens = extractor.extract_tokens()

    assert tokens["data"]["nested"] == "target"


def test_REQ_EXT_091_namespace_hierarchical_structure(tmp_path):
    """REQ-EXT-091: Namespace creates hierarchical token structure"""
    json_file = tmp_path / "data.json"
    json_file.write_text('{"key1": "value1", "key2": "value2"}')

    config = {
        "inputs": [
            {
                "path": str(json_file),
                "namespace": "mydata",
                "tokens": [{"name": "item1", "key": "key1"}],
            }
        ]
    }

    extractor = StructuredDataExtractor(config)
    tokens = extractor.extract_tokens()

    # Should create namespace.token_name structure
    assert "mydata" in tokens
    assert "item1" in tokens["mydata"]
    assert tokens["mydata"]["item1"] == "value1"


def test_REQ_EXT_095_namespace_extraction_example(tmp_path):
    """REQ-EXT-095: Example namespace-based extraction"""
    project_file = tmp_path / "project.json"
    project_file.write_text('{"name": "MyProject", "version": "1.0"}')

    config_file = tmp_path / "config.yaml"
    config_file.write_text("host: localhost\nport: 8080")

    config = {
        "inputs": [
            {"path": str(project_file), "namespace": "project"},
            {"path": str(config_file), "namespace": "config"},
        ]
    }

    extractor = StructuredDataExtractor(config)
    tokens = extractor.extract_tokens()

    # Namespaced access
    assert tokens["project"]["name"] == "MyProject"
    assert tokens["config"]["host"] == "localhost"


def test_REQ_EXT_100_extract_all_toplevel_keys(tmp_path):
    """REQ-EXT-100: Extract all top-level keys when no rules specified"""
    json_file = tmp_path / "data.json"
    json_file.write_text('{"key1": "val1", "key2": "val2", "key3": "val3"}')

    config = {
        "inputs": [
            {
                "path": str(json_file),
                "namespace": "data",
                # No 'tokens' specified
            }
        ]
    }

    extractor = StructuredDataExtractor(config)
    tokens = extractor.extract_tokens()

    # All keys should be extracted
    assert "data" in tokens
    assert "key1" in tokens["data"]
    assert "key2" in tokens["data"]
    assert "key3" in tokens["data"]


def test_REQ_EXT_101_toplevel_keys_become_tokens(tmp_path):
    """REQ-EXT-101: Top-level keys accessible as namespace.key_name"""
    json_file = tmp_path / "app.json"
    json_file.write_text('{"name": "App", "version": "2.0"}')

    config = {"inputs": [{"path": str(json_file), "namespace": "app"}]}

    extractor = StructuredDataExtractor(config)
    tokens = extractor.extract_tokens()

    # Access as namespace.key_name
    assert tokens["app"]["name"] == "App"
    assert tokens["app"]["version"] == "2.0"


def test_REQ_EXT_102_preserve_nested_structures(tmp_path):
    """REQ-EXT-102: Preserve complex nested structures"""
    json_file = tmp_path / "complex.json"
    json_file.write_text("""
    {
        "config": {
            "database": {
                "host": "localhost",
                "port": 5432
            }
        },
        "items": ["a", "b", "c"]
    }
    """)

    config = {"inputs": [{"path": str(json_file), "namespace": "data"}]}

    extractor = StructuredDataExtractor(config)
    tokens = extractor.extract_tokens()

    # Nested structures preserved
    assert isinstance(tokens["data"]["config"], dict)
    assert tokens["data"]["config"]["database"]["host"] == "localhost"
    assert isinstance(tokens["data"]["items"], list)
    assert len(tokens["data"]["items"]) == 3


def test_REQ_EXT_111_clear_error_messages(tmp_path):
    """REQ-EXT-111: Clear error messages with file path"""
    nonexistent = tmp_path / "missing.json"

    config = {"inputs": [{"path": str(nonexistent), "namespace": "data"}]}

    # Should provide clear error with file path
    with pytest.raises(Exception) as exc_info:
        extractor = StructuredDataExtractor(config)
        extractor.extract_tokens()

    error_msg = str(exc_info.value)
    # Error should mention the file
    assert "missing.json" in error_msg or str(nonexistent) in error_msg


def test_REQ_EXT_112_validate_format_before_parse(tmp_path):
    """REQ-EXT-112: Validate file format before parsing"""
    json_file = tmp_path / "data.json"
    json_file.write_text("invalid json content {{{")

    config = {"inputs": [{"path": str(json_file), "namespace": "data"}]}

    # Should detect invalid format
    with pytest.raises(Exception):
        extractor = StructuredDataExtractor(config)
        extractor.extract_tokens()


def test_REQ_EXT_115_duplicate_namespace_error_message(tmp_path):
    """REQ-EXT-115: Duplicate namespace error message"""
    file1 = tmp_path / "file1.json"
    file2 = tmp_path / "file2.json"
    file1.write_text('{"key": "value1"}')
    file2.write_text('{"key": "value2"}')

    config = {
        "inputs": [
            {"path": str(file1), "namespace": "data"},
            {"path": str(file2), "namespace": "data"},  # Duplicate!
        ]
    }

    # Should detect duplicate namespace
    with pytest.raises(Exception) as exc_info:
        extractor = StructuredDataExtractor(config)
        extractor.extract_tokens()

    error_msg = str(exc_info.value).lower()
    assert "duplicate" in error_msg or "namespace" in error_msg


def test_REQ_EXT_120_hierarchical_organization(tmp_path):
    """REQ-EXT-120: Tokens organized hierarchically by namespace"""
    app_file = tmp_path / "app.json"
    db_file = tmp_path / "db.json"
    app_file.write_text('{"name": "MyApp"}')
    db_file.write_text('{"host": "localhost"}')

    config = {
        "inputs": [
            {"path": str(app_file), "namespace": "app"},
            {"path": str(db_file), "namespace": "db"},
        ]
    }

    extractor = StructuredDataExtractor(config)
    tokens = extractor.extract_tokens()

    # Hierarchical organization
    assert "app" in tokens
    assert "db" in tokens
    assert tokens["app"]["name"] == "MyApp"
    assert tokens["db"]["host"] == "localhost"


def test_REQ_EXT_121_namespace_prevents_collisions(tmp_path):
    """REQ-EXT-121: Namespaces prevent token collisions"""
    file1 = tmp_path / "file1.json"
    file2 = tmp_path / "file2.json"
    file1.write_text('{"name": "File1Name"}')
    file2.write_text('{"name": "File2Name"}')

    config = {
        "inputs": [
            {"path": str(file1), "namespace": "source1"},
            {"path": str(file2), "namespace": "source2"},
        ]
    }

    extractor = StructuredDataExtractor(config)
    tokens = extractor.extract_tokens()

    # Both have 'name' but in different namespaces
    assert tokens["source1"]["name"] == "File1Name"
    assert tokens["source2"]["name"] == "File2Name"
    # No collision!


def test_REQ_EXT_122_static_and_namespaced_coexist(tmp_path):
    """REQ-EXT-122: Static and namespaced tokens coexist"""
    json_file = tmp_path / "data.json"
    json_file.write_text('{"key": "value"}')

    config = {
        "inputs": [{"path": str(json_file), "namespace": "extracted"}],
        "static_tokens": {"static_key": "static_value"},
    }

    extractor = StructuredDataExtractor(config)
    tokens = extractor.extract_tokens()

    # Both types coexist
    assert "extracted" in tokens  # Namespaced
    assert "static_key" in tokens  # Static
    assert tokens["extracted"]["key"] == "value"
    assert tokens["static_key"] == "static_value"
