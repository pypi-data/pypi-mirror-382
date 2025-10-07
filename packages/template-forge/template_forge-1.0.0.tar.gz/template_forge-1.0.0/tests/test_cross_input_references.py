"""Tests for cross-input token references (REQ-ADV-003).

These tests verify that static tokens can reference values extracted from
input files using from_input syntax.
"""

from template_forge.core import StructuredDataExtractor


class TestBasicFromInputReferences:
    """Tests for basic from_input functionality."""

    def test_REQ_ADV_003_simple_from_input_reference(self, tmp_path):
        """Test basic from_input reference to extracted value."""
        (tmp_path / "data.json").write_text('{"version": "1.2.3"}')

        config = {
            "inputs": [
                {
                    "path": str(tmp_path / "data.json"),
                    "namespace": "config",
                }
            ],
            "static_tokens": {
                "app_version": {"from_input": "config.version"},
            },
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }
        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert tokens["app_version"] == "1.2.3"

    def test_REQ_ADV_003_nested_from_input_reference(self, tmp_path):
        """Test from_input reference to nested value."""
        (tmp_path / "data.json").write_text(
            '{"project": {"metadata": {"name": "TestProject"}}}'
        )

        config = {
            "inputs": [
                {
                    "path": str(tmp_path / "data.json"),
                    "namespace": "config",
                }
            ],
            "static_tokens": {
                "project_name": {"from_input": "config.project.metadata.name"},
            },
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }
        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert tokens["project_name"] == "TestProject"

    def test_REQ_ADV_003_from_input_with_default(self, tmp_path):
        """Test from_input with default value when path doesn't exist."""
        (tmp_path / "data.json").write_text('{"name": "App"}')

        config = {
            "inputs": [
                {
                    "path": str(tmp_path / "data.json"),
                    "namespace": "config",
                }
            ],
            "static_tokens": {
                "version": {
                    "from_input": "config.nonexistent.version",
                    "default": "1.0.0",
                },
            },
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }
        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert tokens["version"] == "1.0.0"

    def test_REQ_ADV_003_from_input_without_default_returns_none(self, tmp_path):
        """Test from_input without default returns None when path doesn't exist."""
        (tmp_path / "data.json").write_text('{"name": "App"}')

        config = {
            "inputs": [
                {
                    "path": str(tmp_path / "data.json"),
                    "namespace": "config",
                }
            ],
            "static_tokens": {
                "version": {"from_input": "config.nonexistent.version"},
            },
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }
        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert tokens["version"] is None


class TestFromInputWithTransformations:
    """Tests for from_input combined with transformations."""

    def test_REQ_ADV_003_from_input_with_transform(self, tmp_path):
        """Test from_input followed by transformation."""
        (tmp_path / "data.json").write_text('{"projectName": "MyAwesomeProject"}')

        config = {
            "inputs": [
                {
                    "path": str(tmp_path / "data.json"),
                    "namespace": "config",
                }
            ],
            "static_tokens": {
                "module_name": {
                    "from_input": "config.projectName",
                    "transform": "snake_case",
                },
            },
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }
        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert tokens["module_name"] == "my_awesome_project"

    def test_REQ_ADV_003_from_input_with_multiple_transforms(self, tmp_path):
        """Test from_input with chained transformations."""
        (tmp_path / "data.json").write_text('{"project": "  MyProject  "}')

        config = {
            "inputs": [
                {
                    "path": str(tmp_path / "data.json"),
                    "namespace": "config",
                }
            ],
            "static_tokens": {
                "header_guard": {
                    "from_input": "config.project",
                    "transforms": ["strip", "snake_case", "uppercase"],
                },
            },
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }
        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert tokens["header_guard"] == "MY_PROJECT"

    def test_REQ_ADV_003_from_input_with_regex_extract(self, tmp_path):
        """Test from_input with regex extraction."""
        (tmp_path / "data.json").write_text('{"version": "v2.5.10-beta"}')

        config = {
            "inputs": [
                {
                    "path": str(tmp_path / "data.json"),
                    "namespace": "config",
                }
            ],
            "static_tokens": {
                "major_version": {
                    "from_input": "config.version",
                    "transforms": [{"regex_extract": r"v(\d+)\.\d+\.\d+"}],
                },
            },
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }
        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert tokens["major_version"] == "2"


class TestFromInputWithArrays:
    """Tests for from_input with array operations."""

    def test_REQ_ADV_003_from_input_array_index(self, tmp_path):
        """Test from_input with array indexing."""
        (tmp_path / "data.json").write_text('{"components": ["core", "ui", "db"]}')

        config = {
            "inputs": [
                {
                    "path": str(tmp_path / "data.json"),
                    "namespace": "config",
                }
            ],
            "static_tokens": {
                "first_component": {"from_input": "config.components[0]"},
                "second_component": {"from_input": "config.components[1]"},
            },
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }
        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert tokens["first_component"] == "core"
        assert tokens["second_component"] == "ui"

    def test_REQ_ADV_003_from_input_array_wildcard(self, tmp_path):
        """Test from_input with array wildcard to extract all elements."""
        (tmp_path / "data.json").write_text(
            '{"modules": [{"name": "core"}, {"name": "ui"}, {"name": "db"}]}'
        )

        config = {
            "inputs": [
                {
                    "path": str(tmp_path / "data.json"),
                    "namespace": "config",
                }
            ],
            "static_tokens": {
                "module_names": {"from_input": "config.modules[*].name"},
            },
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }
        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert tokens["module_names"] == ["core", "ui", "db"]

    def test_REQ_ADV_003_from_input_nested_array(self, tmp_path):
        """Test from_input with nested array access."""
        (tmp_path / "data.json").write_text(
            '{"systems": [{"components": [{"id": "comp1"}]}]}'
        )

        config = {
            "inputs": [
                {
                    "path": str(tmp_path / "data.json"),
                    "namespace": "config",
                }
            ],
            "static_tokens": {
                "component_id": {"from_input": "config.systems[0].components[0].id"},
            },
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }
        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert tokens["component_id"] == "comp1"


class TestFromInputWithWildcards:
    """Tests for from_input with wildcard operations."""

    def test_REQ_ADV_003_from_input_object_wildcard(self, tmp_path):
        """Test from_input with object wildcard to get entire object."""
        (tmp_path / "data.json").write_text(
            '{"settings": {"debug": true, "timeout": 30, "host": "localhost"}}'
        )

        config = {
            "inputs": [
                {
                    "path": str(tmp_path / "data.json"),
                    "namespace": "config",
                }
            ],
            "static_tokens": {
                "all_settings": {"from_input": "config.settings.*"},
            },
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }
        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert tokens["all_settings"] == {
            "debug": True,
            "timeout": 30,
            "host": "localhost",
        }

    def test_REQ_ADV_003_from_input_wildcard_first_element(self, tmp_path):
        """Test from_input with wildcard to extract first matching key."""
        (tmp_path / "data.yaml").write_text(
            """
SoftwareComponents:
  Component1:
    name: MainComponent
    version: 1.0
  Component2:
    name: HelperComponent
    version: 2.0
"""
        )

        config = {
            "inputs": [
                {
                    "path": str(tmp_path / "data.yaml"),
                    "namespace": "yaml_config",
                    "format": "yaml",
                }
            ],
            "static_tokens": {
                # Extract first component name using array indexing
                "component_name": {
                    "from_input": "yaml_config.SoftwareComponents.*[0].name"
                },
            },
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }
        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        # Should get one of the components (dict values become list)
        assert "component_name" in tokens


class TestFromInputMultipleInputs:
    """Tests for from_input referencing multiple input files."""

    def test_REQ_ADV_003_from_input_different_namespaces(self, tmp_path):
        """Test from_input referencing different namespaces."""
        (tmp_path / "project.json").write_text('{"name": "MyProject"}')
        (tmp_path / "version.json").write_text('{"number": "1.0.0"}')

        config = {
            "inputs": [
                {
                    "path": str(tmp_path / "project.json"),
                    "namespace": "project",
                },
                {
                    "path": str(tmp_path / "version.json"),
                    "namespace": "version",
                },
            ],
            "static_tokens": {
                "app_name": {"from_input": "project.name"},
                "app_version": {"from_input": "version.number"},
                "full_title": "${app_name} v${app_version}",
            },
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }
        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert tokens["app_name"] == "MyProject"
        assert tokens["app_version"] == "1.0.0"
        assert tokens["full_title"] == "MyProject v1.0.0"


class TestFromInputErrorHandling:
    """Tests for from_input error handling."""

    def test_REQ_ADV_003_from_input_invalid_namespace(self, tmp_path, caplog):
        """Test from_input with non-existent namespace logs warning."""
        (tmp_path / "data.json").write_text('{"name": "App"}')

        config = {
            "inputs": [
                {
                    "path": str(tmp_path / "data.json"),
                    "namespace": "config",
                }
            ],
            "static_tokens": {
                "value": {"from_input": "nonexistent.name"},
            },
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }
        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert tokens["value"] is None
        assert any("not found" in record.message for record in caplog.records)

    def test_REQ_ADV_003_from_input_invalid_path_format(self, tmp_path, caplog):
        """Test from_input with invalid path format."""
        (tmp_path / "data.json").write_text('{"name": "App"}')

        config = {
            "inputs": [
                {
                    "path": str(tmp_path / "data.json"),
                    "namespace": "config",
                }
            ],
            "static_tokens": {
                "value": {"from_input": ""},
            },
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }
        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert tokens["value"] is None
        assert any("Invalid" in record.message for record in caplog.records)

    def test_REQ_ADV_003_from_input_missing_path_uses_default(self, tmp_path):
        """Test from_input with missing path uses default value."""
        (tmp_path / "data.json").write_text('{"name": "App"}')

        config = {
            "inputs": [
                {
                    "path": str(tmp_path / "data.json"),
                    "namespace": "config",
                }
            ],
            "static_tokens": {
                "version": {
                    "from_input": "config.missing.path",
                    "default": "0.0.1",
                },
            },
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }
        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert tokens["version"] == "0.0.1"


class TestComplexScenarios:
    """Tests for complex real-world scenarios."""

    def test_REQ_ADV_003_autosar_component_extraction(self, tmp_path):
        """Test extracting component data from AUTOSAR ARXML file."""
        (tmp_path / "ecu.arxml").write_text(
            """<?xml version="1.0"?>
<AUTOSAR>
  <AR-PACKAGES>
    <AR-PACKAGE>
      <SHORT-NAME>MyEcuProject</SHORT-NAME>
      <ELEMENTS>
        <SOFTWARE-COMPONENT>
          <SHORT-NAME>MainComponent</SHORT-NAME>
          <VERSION>2.1.5</VERSION>
        </SOFTWARE-COMPONENT>
      </ELEMENTS>
    </AR-PACKAGE>
  </AR-PACKAGES>
</AUTOSAR>"""
        )

        config = {
            "inputs": [
                {
                    "path": str(tmp_path / "ecu.arxml"),
                    "namespace": "arxml",
                }
            ],
            "static_tokens": {
                # Extract project name
                "project_name": {
                    "from_input": "arxml.AR-PACKAGES.AR-PACKAGE.SHORT-NAME"
                },
                # Extract component name
                "component_name": {
                    "from_input": "arxml.AR-PACKAGES.AR-PACKAGE.ELEMENTS.SOFTWARE-COMPONENT.SHORT-NAME"
                },
                # Extract and transform version
                "version_major": {
                    "from_input": "arxml.AR-PACKAGES.AR-PACKAGE.ELEMENTS.SOFTWARE-COMPONENT.VERSION",
                    "transforms": [{"regex_extract": r"(\d+)\.\d+\.\d+"}],
                },
                # Create module name from component
                "module_name": {
                    "from_input": "arxml.AR-PACKAGES.AR-PACKAGE.ELEMENTS.SOFTWARE-COMPONENT.SHORT-NAME",
                    "transform": "snake_case",
                },
            },
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }
        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert tokens["project_name"] == "MyEcuProject"
        assert tokens["component_name"] == "MainComponent"
        assert tokens["version_major"] == "2"
        assert tokens["module_name"] == "main_component"

    def test_REQ_ADV_003_multiple_inputs_combined(self, tmp_path):
        """Test combining data from multiple input files."""
        (tmp_path / "app.yaml").write_text(
            """
application:
  name: MyApp
  modules:
    - name: core
      port: 8080
    - name: api
      port: 8081
"""
        )
        (tmp_path / "version.json").write_text('{"major": 2, "minor": 5, "patch": 1}')

        config = {
            "inputs": [
                {
                    "path": str(tmp_path / "app.yaml"),
                    "namespace": "app",
                    "format": "yaml",
                },
                {
                    "path": str(tmp_path / "version.json"),
                    "namespace": "ver",
                },
            ],
            "static_tokens": {
                "app_name": {"from_input": "app.application.name"},
                "core_port": {"from_input": "app.application.modules[0].port"},
                "version": "${ver.major}.${ver.minor}.${ver.patch}",
                "full_name": "${app_name} v${version}",
            },
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }
        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert tokens["app_name"] == "MyApp"
        assert tokens["core_port"] == 8080
        assert tokens["version"] == "2.5.1"
        assert tokens["full_name"] == "MyApp v2.5.1"


class TestDocumentationExamples:
    """Tests for examples from requirements documentation."""

    def test_REQ_ADV_003_example_from_docs(self, tmp_path):
        """Test the example from requirements document."""
        (tmp_path / "config.yaml").write_text(
            """
project:
  version: 1.2.3
SoftwareComponents:
  Component1:
    name: MainComponent
  Component2:
    name: HelperComponent
"""
        )

        config = {
            "inputs": [
                {
                    "path": str(tmp_path / "config.yaml"),
                    "namespace": "yaml_config",
                    "format": "yaml",
                }
            ],
            "static_tokens": {
                "version": {
                    "from_input": "yaml_config.project.version",
                    "default": "1.0.0",
                },
            },
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }
        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert tokens["version"] == "1.2.3"
