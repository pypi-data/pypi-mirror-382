"""Tests for REQ-ADV-006: Multiple File Input Strategies

This module tests the ability to handle multiple files matching a glob pattern
with different strategies: 'first', 'all' (merge), 'error_if_multiple', and 'list'.
"""

import json
import logging

import pytest
import yaml

from template_forge.core import StructuredDataExtractor


class TestFirstStrategy:
    """Test the 'first' strategy (default) - use first matching file."""

    def test_REQ_ADV_006_first_strategy_default(self, tmp_path, caplog):
        """REQ-ADV-006: Default strategy should use first matching file."""
        caplog.set_level(logging.DEBUG)

        # Create multiple matching files
        input_dir = tmp_path / "inputs"
        input_dir.mkdir()

        (input_dir / "config1.json").write_text(
            json.dumps({"name": "first", "value": 100})
        )
        (input_dir / "config2.json").write_text(
            json.dumps({"name": "second", "value": 200})
        )

        config = {
            "inputs": [
                {
                    "path": str(input_dir / "*.json"),
                    "namespace": "config",
                    # No match specified - should default to 'first'
                }
            ],
            "templates": [],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        # Should use first file
        assert tokens["config"]["name"] == "first"
        assert tokens["config"]["value"] == 100

    def test_REQ_ADV_006_first_strategy_explicit(self, tmp_path):
        """REQ-ADV-006: Explicit 'first' strategy should use first file."""
        input_dir = tmp_path / "inputs"
        input_dir.mkdir()

        (input_dir / "a.yaml").write_text(yaml.dump({"priority": 1}))
        (input_dir / "b.yaml").write_text(yaml.dump({"priority": 2}))
        (input_dir / "c.yaml").write_text(yaml.dump({"priority": 3}))

        config = {
            "inputs": [
                {
                    "path": str(input_dir / "*.yaml"),
                    "namespace": "data",
                    "match": "first",
                }
            ],
            "templates": [],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert tokens["data"]["priority"] == 1


class TestErrorIfMultipleStrategy:
    """Test 'error_if_multiple' strategy - fail if more than one match."""

    def test_REQ_ADV_006_error_if_multiple_fails(self, tmp_path):
        """REQ-ADV-006: Should raise error when multiple files match."""
        input_dir = tmp_path / "configs"
        input_dir.mkdir()

        (input_dir / "main1.json").write_text(json.dumps({"id": 1}))
        (input_dir / "main2.json").write_text(json.dumps({"id": 2}))

        config = {
            "inputs": [
                {
                    "path": str(input_dir / "main*.json"),
                    "namespace": "main",
                    "match": "error_if_multiple",
                }
            ],
            "templates": [],
        }

        with pytest.raises(ValueError, match="Multiple files match"):
            extractor = StructuredDataExtractor(config)
            extractor.extract_tokens()

    def test_REQ_ADV_006_error_if_multiple_accepts_single(self, tmp_path):
        """REQ-ADV-006: Should succeed when only one file matches."""
        input_dir = tmp_path / "configs"
        input_dir.mkdir()

        (input_dir / "main.json").write_text(json.dumps({"id": 42}))

        config = {
            "inputs": [
                {
                    "path": str(input_dir / "main*.json"),
                    "namespace": "main",
                    "match": "error_if_multiple",
                }
            ],
            "templates": [],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        assert tokens["main"]["id"] == 42


class TestAllStrategyShallowMerge:
    """Test 'all' strategy with shallow merge."""

    def test_REQ_ADV_006_all_strategy_shallow_merge(self, tmp_path):
        """REQ-ADV-006: Should merge all files with shallow strategy."""
        modules_dir = tmp_path / "modules"
        modules_dir.mkdir()

        (modules_dir / "module1.json").write_text(
            json.dumps({"name": "Module1", "version": "1.0"})
        )
        (modules_dir / "module2.json").write_text(
            json.dumps({"description": "Second module", "version": "2.0"})
        )

        config = {
            "inputs": [
                {
                    "path": str(modules_dir / "*.json"),
                    "namespace": "modules",
                    "match": "all",
                    "merge_strategy": "shallow",
                }
            ],
            "templates": [],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        # Shallow merge: later values overwrite
        assert tokens["modules"]["name"] == "Module1"
        assert tokens["modules"]["description"] == "Second module"
        assert tokens["modules"]["version"] == "2.0"  # Last one wins

    def test_REQ_ADV_006_all_strategy_default_to_deep(self, tmp_path):
        """REQ-ADV-006: Should default to deep merge if no merge_strategy."""
        modules_dir = tmp_path / "modules"
        modules_dir.mkdir()

        (modules_dir / "a.json").write_text(
            json.dumps({"config": {"host": "localhost", "port": 8080}})
        )
        (modules_dir / "b.json").write_text(
            json.dumps({"config": {"port": 9090, "timeout": 30}})
        )

        config = {
            "inputs": [
                {
                    "path": str(modules_dir / "*.json"),
                    "namespace": "settings",
                    "match": "all",
                    # No merge_strategy - should default to 'deep'
                }
            ],
            "templates": [],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        # Deep merge: nested dicts are merged
        assert tokens["settings"]["config"]["host"] == "localhost"
        assert tokens["settings"]["config"]["port"] == 9090  # Updated
        assert tokens["settings"]["config"]["timeout"] == 30  # Added


class TestListStrategy:
    """Test 'list' strategy - create array of all extracted data."""

    def test_REQ_ADV_006_list_strategy_creates_array(self, tmp_path):
        """REQ-ADV-006: List strategy should create array of all file data."""
        components_dir = tmp_path / "components"
        components_dir.mkdir()

        (components_dir / "comp1.yaml").write_text(
            yaml.dump({"name": "Component1", "type": "Service"})
        )
        (components_dir / "comp2.yaml").write_text(
            yaml.dump({"name": "Component2", "type": "Worker"})
        )
        (components_dir / "comp3.yaml").write_text(
            yaml.dump({"name": "Component3", "type": "API"})
        )

        config = {
            "inputs": [
                {
                    "path": str(components_dir / "*.yaml"),
                    "namespace": "components",
                    "match": "list",
                }
            ],
            "templates": [],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        # Namespace should contain a list
        assert isinstance(tokens["components"], list)
        assert len(tokens["components"]) == 3

        # Verify content
        names = [comp["name"] for comp in tokens["components"]]
        assert "Component1" in names
        assert "Component2" in names
        assert "Component3" in names

    def test_REQ_ADV_006_list_strategy_single_file(self, tmp_path):
        """REQ-ADV-006: List strategy should work with single matching file."""
        data_dir = tmp_path / "data"
        data_dir.mkdir()

        (data_dir / "single.json").write_text(json.dumps({"name": "Single"}))

        config = {
            "inputs": [
                {
                    "path": str(data_dir / "*.json"),
                    "namespace": "items",
                    "match": "list",
                }
            ],
            "templates": [],
        }

        extractor = StructuredDataExtractor(config)
        tokens = extractor.extract_tokens()

        # Should still be a list, even with one item
        assert isinstance(tokens["items"], list)
        assert len(tokens["items"]) == 1
        assert tokens["items"][0]["name"] == "Single"
