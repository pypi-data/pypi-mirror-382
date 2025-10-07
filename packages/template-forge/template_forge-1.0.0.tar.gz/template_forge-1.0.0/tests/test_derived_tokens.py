"""Tests for derived/computed tokens (REQ-ADV-002).

These tests verify that static tokens can reference other tokens and
apply transformations to compute their values.
"""

from template_forge.core import StructuredDataExtractor


class TestTokenReferences:
    """Tests for ${token_name} reference resolution."""

    def test_REQ_ADV_002_simple_token_reference(self, tmp_path):
        """Test referencing another token using ${token_name} syntax."""
        (tmp_path / "data.json").write_text('{"project": "MyProject"}')

        config = {
            "inputs": [
                {
                    "path": str(tmp_path / "data.json"),
                    "namespace": "config",
                }
            ],
            "static_tokens": {
                "project_name": "${config.project}",
            },
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }
        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert "project_name" in tokens
        assert tokens["project_name"] == "MyProject"

    def test_REQ_ADV_002_nested_token_reference(self, tmp_path):
        """Test referencing nested tokens."""
        (tmp_path / "data.json").write_text(
            '{"app": {"name": "TestApp", "version": "1.0"}}'
        )

        config = {
            "inputs": [
                {
                    "path": str(tmp_path / "data.json"),
                    "namespace": "config",
                }
            ],
            "static_tokens": {
                "app_name": "${config.app.name}",
                "app_version": "${config.app.version}",
            },
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }
        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert tokens["app_name"] == "TestApp"
        assert tokens["app_version"] == "1.0"

    def test_REQ_ADV_002_reference_to_static_token(self):
        """Test referencing another static token."""
        config = {
            "static_tokens": {
                "base_name": "MyApp",
                "full_name": "${base_name} Pro",
            },
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }
        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert tokens["base_name"] == "MyApp"
        assert tokens["full_name"] == "MyApp Pro"

    def test_REQ_ADV_002_missing_reference_warning(self, caplog):
        """Test that missing token references generate warnings."""
        config = {
            "static_tokens": {
                "name": "${nonexistent.token}",
            },
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }
        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        # Should keep original value if reference not found
        assert tokens["name"] == "${nonexistent.token}"
        assert any("not found" in record.message for record in caplog.records)

    def test_REQ_ADV_002_multiple_references_in_value(self):
        """Test multiple token references in a single value."""
        config = {
            "static_tokens": {
                "first": "Hello",
                "second": "World",
                "combined": "${first} ${second}!",
            },
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }
        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert tokens["combined"] == "Hello World!"


class TestCaseTransformations:
    """Tests for case transformation."""

    def test_REQ_ADV_002_lowercase_transform(self):
        """Test lowercase transformation."""
        config = {
            "static_tokens": {
                "name": "MyProject",
                "lower_name": {"value": "${name}", "transform": "lowercase"},
            },
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }
        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert tokens["lower_name"] == "myproject"

    def test_REQ_ADV_002_uppercase_transform(self):
        """Test uppercase transformation."""
        config = {
            "static_tokens": {
                "name": "MyProject",
                "upper_name": {"value": "${name}", "transform": "uppercase"},
            },
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }
        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert tokens["upper_name"] == "MYPROJECT"

    def test_REQ_ADV_002_snake_case_transform(self):
        """Test snake_case transformation."""
        config = {
            "static_tokens": {
                "camel_name": "MyProjectName",
                "snake_name": {"value": "${camel_name}", "transform": "snake_case"},
            },
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }
        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert tokens["snake_name"] == "my_project_name"

    def test_REQ_ADV_002_camel_case_transform(self):
        """Test camelCase transformation."""
        config = {
            "static_tokens": {
                "snake_name": "my_project_name",
                "camel_name": {"value": "${snake_name}", "transform": "camel_case"},
            },
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }
        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert tokens["camel_name"] == "myProjectName"

    def test_REQ_ADV_002_pascal_case_transform(self):
        """Test PascalCase transformation."""
        config = {
            "static_tokens": {
                "snake_name": "my_project_name",
                "pascal_name": {"value": "${snake_name}", "transform": "pascal_case"},
            },
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }
        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert tokens["pascal_name"] == "MyProjectName"

    def test_REQ_ADV_002_kebab_case_transform(self):
        """Test kebab-case transformation."""
        config = {
            "static_tokens": {
                "camel_name": "MyProjectName",
                "kebab_name": {"value": "${camel_name}", "transform": "kebab_case"},
            },
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }
        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert tokens["kebab_name"] == "my-project-name"

    def test_REQ_ADV_002_strip_transform(self):
        """Test strip transformation."""
        config = {
            "static_tokens": {
                "name": "  MyProject  ",
                "clean_name": {"value": "${name}", "transform": "strip"},
            },
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }
        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert tokens["clean_name"] == "MyProject"


class TestChainedTransformations:
    """Tests for chaining multiple transformations."""

    def test_REQ_ADV_002_multiple_transforms_in_order(self):
        """Test applying multiple transformations in sequence."""
        config = {
            "static_tokens": {
                "name": "  MyProjectName  ",
                "processed": {
                    "value": "${name}",
                    "transforms": ["strip", "snake_case", "uppercase"],
                },
            },
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }
        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        # Should apply: strip -> "MyProjectName" -> snake_case -> "my_project_name" -> uppercase -> "MY_PROJECT_NAME"
        assert tokens["processed"] == "MY_PROJECT_NAME"

    def test_REQ_ADV_002_complex_transformation_chain(self):
        """Test complex transformation chain."""
        config = {
            "static_tokens": {
                "base": "hello world project",
                "result": {
                    "value": "${base}",
                    "transforms": ["pascal_case", "snake_case"],
                },
            },
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }
        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        # "hello world project" -> PascalCase -> "HelloWorldProject" -> snake_case -> "hello_world_project"
        assert tokens["result"] == "hello_world_project"


class TestRegexTransformations:
    """Tests for regex-based transformations."""

    def test_REQ_ADV_002_regex_extract(self):
        """Test regex extraction transformation."""
        config = {
            "static_tokens": {
                "full_version": "v1.2.3-beta",
                "major_version": {
                    "value": "${full_version}",
                    "transforms": [{"regex_extract": r"v(\d+)\.\d+\.\d+"}],
                },
            },
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }
        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert tokens["major_version"] == "1"

    def test_REQ_ADV_002_regex_extract_no_group(self):
        """Test regex extraction without capture group."""
        config = {
            "static_tokens": {
                "text": "Error: Something went wrong",
                "error_part": {
                    "value": "${text}",
                    "transforms": [{"regex_extract": r"Error: \w+"}],
                },
            },
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }
        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert tokens["error_part"] == "Error: Something"

    def test_REQ_ADV_002_regex_replace(self):
        """Test regex replacement transformation."""
        config = {
            "static_tokens": {
                "name": "MyProjectHIABC",
                "clean_name": {
                    "value": "${name}",
                    "transforms": [
                        {
                            "regex_replace": {
                                "pattern": r"(HI[ABC])",
                                "replacement": r"_\1",
                            }
                        }
                    ],
                },
            },
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }
        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert tokens["clean_name"] == "MyProject_HIABC"

    def test_REQ_ADV_002_regex_extract_no_match_warning(self, caplog):
        """Test that non-matching regex generates warning."""
        config = {
            "static_tokens": {
                "text": "no version here",
                "version": {
                    "value": "${text}",
                    "transforms": [{"regex_extract": r"v(\d+\.\d+\.\d+)"}],
                },
            },
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }
        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        # Should keep original value and log warning
        assert tokens["version"] == "no version here"
        assert any("did not match" in record.message for record in caplog.records)


class TestComplexScenarios:
    """Tests for complex real-world scenarios."""

    def test_REQ_ADV_002_autosar_component_naming(self, tmp_path):
        """Test deriving component names from ARXML data."""
        (tmp_path / "ecu.arxml").write_text(
            '<?xml version="1.0"?>'
            "<AUTOSAR><AR-PACKAGES><AR-PACKAGE>"
            "<SHORT-NAME>MyEcuProject</SHORT-NAME>"
            "</AR-PACKAGE></AR-PACKAGES></AUTOSAR>"
        )

        config = {
            "inputs": [
                {
                    "path": str(tmp_path / "ecu.arxml"),
                    "namespace": "arxml",
                    "tokens": [
                        {
                            "name": "project_name",
                            "key": "AR-PACKAGES.AR-PACKAGE.SHORT-NAME",
                        }
                    ],
                }
            ],
            "static_tokens": {
                # Derive component prefix from project name
                "component_prefix": {
                    "value": "${arxml.project_name}",
                    "transform": "snake_case",
                },
                # Create header guard
                "header_guard": {
                    "value": "${arxml.project_name}",
                    "transforms": ["snake_case", "uppercase"],
                },
                # Create module name
                "module_name": {
                    "value": "${arxml.project_name}",
                    "transforms": ["camel_case"],
                },
            },
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }
        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert tokens["component_prefix"] == "my_ecu_project"
        assert tokens["header_guard"] == "MY_ECU_PROJECT"
        assert tokens["module_name"] == "myEcuProject"

    def test_REQ_ADV_002_version_extraction_and_formatting(self):
        """Test extracting and formatting version numbers."""
        config = {
            "static_tokens": {
                "full_version": "v2.5.10-alpha+build.123",
                "major": {
                    "value": "${full_version}",
                    "transforms": [{"regex_extract": r"v(\d+)\.\d+\.\d+"}],
                },
                "minor": {
                    "value": "${full_version}",
                    "transforms": [{"regex_extract": r"v\d+\.(\d+)\.\d+"}],
                },
                "patch": {
                    "value": "${full_version}",
                    "transforms": [{"regex_extract": r"v\d+\.\d+\.(\d+)"}],
                },
                "version_string": "Version ${major}.${minor}.${patch}",
            },
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }
        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert tokens["major"] == "2"
        assert tokens["minor"] == "5"
        assert tokens["patch"] == "10"
        assert tokens["version_string"] == "Version 2.5.10"

    def test_REQ_ADV_002_path_manipulation(self, tmp_path):
        """Test manipulating file paths."""
        (tmp_path / "config.json").write_text('{"workspace": "/home/user/my_project"}')

        config = {
            "inputs": [
                {
                    "path": str(tmp_path / "config.json"),
                    "namespace": "config",
                }
            ],
            "static_tokens": {
                # Extract project name from path
                "project_name": {
                    "value": "${config.workspace}",
                    "transforms": [{"regex_extract": r"([^/\\]+)$"}],
                },
                # Convert to various naming conventions
                "project_snake": {
                    "value": "${project_name}",
                    "transform": "snake_case",
                },
                "project_camel": {
                    "value": "${project_name}",
                    "transform": "camel_case",
                },
            },
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }
        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert tokens["project_name"] == "my_project"
        assert tokens["project_snake"] == "my_project"
        assert tokens["project_camel"] == "myProject"


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_REQ_ADV_002_non_string_value_with_transform(self, caplog):
        """Test transformation on non-string value logs warning."""
        config = {
            "static_tokens": {
                "number": 123,
                "transformed": {"value": 123, "transform": "uppercase"},
            },
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }
        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        # Should convert to string and log warning
        assert tokens["transformed"] == "123"
        assert any("expects string" in record.message for record in caplog.records)

    def test_REQ_ADV_002_unknown_transformation(self, caplog):
        """Test unknown transformation logs warning."""
        config = {
            "static_tokens": {
                "name": "test",
                "result": {"value": "${name}", "transform": "unknown_transform"},
            },
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }
        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        # Should keep original value
        assert tokens["result"] == "test"
        assert any(
            "Unknown transformation" in record.message for record in caplog.records
        )

    def test_REQ_ADV_002_transforms_not_list_warning(self, caplog):
        """Test non-list transforms value logs warning."""
        config = {
            "static_tokens": {
                "name": "test",
                "result": {"value": "${name}", "transforms": "not_a_list"},
            },
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }
        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        # Should keep original value
        assert tokens["result"] == "test"
        assert any("must be a list" in record.message for record in caplog.records)

    def test_REQ_ADV_002_dict_without_value_key(self):
        """Test dict without 'value' key is treated as nested dict."""
        config = {
            "static_tokens": {
                "nested": {
                    "key1": "value1",
                    "key2": "value2",
                },
            },
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }
        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        # Should treat as regular nested dictionary
        assert tokens["nested"]["key1"] == "value1"
        assert tokens["nested"]["key2"] == "value2"

    def test_REQ_ADV_002_empty_string_value(self):
        """Test empty string values are handled correctly."""
        config = {
            "static_tokens": {
                "empty": "",
                "transformed": {"value": "", "transform": "uppercase"},
            },
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }
        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert tokens["empty"] == ""
        assert tokens["transformed"] == ""


class TestDocumentationExamples:
    """Tests for examples from requirements documentation."""

    def test_REQ_ADV_002_example_from_docs(self):
        """Test the example from requirements document."""
        config = {
            "static_tokens": {
                "workspace_name": "MyWorkspace",
                "project_dir": "${workspace_name}",
                "module_name": {
                    "value": "${workspace_name}",
                    "transform": "snake_case",
                },
            },
            "templates": [{"template": "t.j2", "output": "o.txt"}],
        }
        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert tokens["project_dir"] == "MyWorkspace"
        assert tokens["module_name"] == "my_workspace"
