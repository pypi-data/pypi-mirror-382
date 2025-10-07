#!/usr/bin/env python3
"""Core classes for Template Forge.

This module contains the main classes for extracting tokens from structured data
and processing Jinja2 templates with comprehensive type safety and error handling.
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional, Protocol, Set

import yaml

from .extraction import StructuredDataExtractor
from .hooks import HookExecutor
from .preservation import PreservationHandler
from .processing import TemplateProcessor

# Re-export for backward compatibility
__all__ = [
    "HookExecutor",
    "PreservationHandler",
    "StructuredDataExtractor",
    "TemplateForge",
    "TemplateProcessor",
    "TokenExtractor",
]


class TokenExtractor(Protocol):
    """Protocol for token extraction from different data sources."""

    def extract_tokens(self) -> Dict[str, Any]:
        """Extract tokens from the data source.

        Returns:
            Dictionary mapping token names to their extracted values.
        """
        ...


class TemplateForge:
    """Main class for orchestrating template generation from structured data."""

    def __init__(self, config_file: Path):
        """Initialize Template Forge with configuration file.

        Args:
            config_file: Path to YAML configuration file
        """
        self.config_file = config_file
        self.logger = logging.getLogger(__name__)
        self.config = self._load_config()

    def _process_includes(
        self,
        config: Dict[str, Any],
        config_path: Path,
        _visited: Optional[Set[Path]] = None,
    ) -> Dict[str, Any]:
        """Process 'includes' directive in configuration.

        Implements REQ-CFG-100-110: Configuration file inclusion and merging.

        Args:
            config: Configuration dictionary to process
            config_path: Path to the configuration file (for resolving relative paths)
            _visited: Set of already visited files (for circular detection)

        Returns:
            Merged configuration dictionary

        Raises:
            FileNotFoundError: If an included file doesn't exist (REQ-CFG-107)
            ValueError: If circular includes detected (REQ-CFG-105)
        """
        if _visited is None:
            _visited = set()

        # Track this file to detect circular includes
        config_path_abs = config_path.resolve()
        if config_path_abs in _visited:
            raise ValueError(
                f"Circular include detected: {config_path_abs} has already been included"
            )
        _visited.add(config_path_abs)

        # Check if this config has includes
        if "includes" not in config:
            return config

        includes = config.pop("includes")  # Remove from config after reading

        # Support both single file and list of files (REQ-CFG-101)
        if isinstance(includes, str):
            includes = [includes]

        # Process each included file
        merged_config: Dict[str, Any] = {}
        for include_path_str in includes:
            # Resolve path relative to containing file (REQ-CFG-103)
            include_path = config_path.parent / include_path_str

            if not include_path.exists():
                raise FileNotFoundError(
                    f"Included configuration file not found: {include_path}\n"
                    f"  Referenced from: {config_path}\n"
                    f"  Include path: {include_path_str}"
                )

            self.logger.debug(f"Loading included configuration: {include_path}")

            # Load included file
            try:
                with open(include_path, encoding="utf-8") as f:
                    included_config = yaml.safe_load(f)

                if not isinstance(included_config, dict):
                    raise ValueError(
                        f"Included file {include_path} must contain a dictionary"
                    )

                # Recursively process nested includes (REQ-CFG-104)
                included_config = self._process_includes(
                    included_config, include_path, _visited
                )

                # Merge included config (REQ-CFG-102)
                merged_config = self._merge_configs(merged_config, included_config)

            except yaml.YAMLError as e:
                raise ValueError(
                    f"Invalid YAML in included file {include_path}: {e}"
                ) from e

        # Finally merge the main config (main config takes precedence)
        merged_config = self._merge_configs(merged_config, config)

        return merged_config

    def _merge_configs(
        self, base: Dict[str, Any], overlay: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Merge two configuration dictionaries.

        Implements REQ-CFG-102: Merge rules for included configurations.
        - static_tokens: Deep merge dictionaries
        - inputs, templates: Append lists
        - Other keys: Overlay value takes precedence

        Args:
            base: Base configuration
            overlay: Configuration to merge on top

        Returns:
            Merged configuration
        """
        result = base.copy()

        for key, value in overlay.items():
            if key not in result:
                # New key, just add it
                result[key] = value
            elif key == "static_tokens":
                # Deep merge static tokens (REQ-CFG-102)
                if isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = self._deep_merge_dicts(result[key], value)
                else:
                    result[key] = value
            elif key in ("inputs", "templates"):
                # Append lists (REQ-CFG-102)
                if isinstance(result[key], list) and isinstance(value, list):
                    result[key] = result[key] + value
                else:
                    result[key] = value
            else:
                # Other keys: overlay takes precedence
                result[key] = value

        return result

    def _deep_merge_dicts(
        self, base: Dict[str, Any], overlay: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Deep merge two dictionaries.

        Args:
            base: Base dictionary
            overlay: Dictionary to merge on top

        Returns:
            Merged dictionary
        """
        result = base.copy()

        for key, value in overlay.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                # Recursively merge nested dicts
                result[key] = self._deep_merge_dicts(result[key], value)
            else:
                # Overlay value takes precedence
                result[key] = value

        return result

    def _load_config(self) -> Dict[str, Any]:
        """Load and validate configuration from YAML file.

        Validates REQ-CFG-011-014: Configuration must define at least one data extraction
        mechanism (inputs or static_tokens) AND at least one output generation mechanism
        (templates or template_dir).

        Processes includes before validation (REQ-CFG-109).
        """
        try:
            with open(self.config_file, encoding="utf-8") as f:
                config = yaml.safe_load(f)

            if not isinstance(config, dict):
                raise ValueError("Configuration must be a dictionary")

            # Process includes before validation (REQ-CFG-100-109)
            config = self._process_includes(config, self.config_file)

            # Validate data extraction requirement (REQ-CFG-011)
            has_data_source = ("inputs" in config and config["inputs"]) or (
                "static_tokens" in config and config["static_tokens"]
            )

            if not has_data_source:
                raise ValueError(
                    "Configuration must define at least one data extraction mechanism:\n"
                    "  - 'inputs': To extract data from external files (JSON, YAML, XML, ARXML)\n"
                    "  - 'static_tokens': To provide static key-value pairs\n"
                    "At least one of these sections must be present and non-empty."
                )

            # Validate output generation requirement (REQ-CFG-012)
            has_output_target = ("templates" in config and config["templates"]) or (
                "template_dir" in config and config["template_dir"]
            )

            if not has_output_target:
                raise ValueError(
                    "Configuration must define at least one output generation mechanism:\n"
                    "  - 'templates': Explicit list of templates to process\n"
                    "  - 'template_dir': Directory containing template files to discover\n"
                    "At least one of these sections must be present and non-empty."
                )

            return config

        except Exception as e:
            self.logger.error(f"Error loading configuration: {e}")
            raise RuntimeError(f"Error loading configuration: {e}") from e

    def run(
        self, dry_run: bool = False, show_diff: bool = False, no_hooks: bool = False
    ) -> None:
        """Run the complete template generation process.

        Args:
            dry_run: If True, preview operations without writing files
            show_diff: If True, show diffs of changes (works with or without dry_run)
            no_hooks: If True, skip post-generation hooks (REQ-AUT-090)
        """
        mode_msg = []
        if dry_run:
            mode_msg.append("DRY RUN MODE")
        if show_diff:
            mode_msg.append("DIFF PREVIEW")
        if no_hooks:
            mode_msg.append("HOOKS DISABLED")

        mode_str = f" [{', '.join(mode_msg)}]" if mode_msg else ""
        self.logger.info(
            f"Starting template generation{mode_str} with config: {self.config_file}"
        )

        # Extract tokens from input files
        extractor = StructuredDataExtractor(self.config)
        extractor.config_dir = self.config_file.parent  # Set config directory
        tokens = extractor.extract_tokens()
        self.logger.debug(f"Extracted tokens: {list(tokens.keys())}")

        # Process templates
        processor = TemplateProcessor(self.config, tokens)
        processor.config_dir = self.config_file.parent  # Set config directory
        processor._init_jinja_env()  # Reinitialize with correct config_dir
        processor.process_templates(dry_run=dry_run, show_diff=show_diff)

        # Execute post-generation hooks (REQ-AUT-010-011, REQ-AUT-090)
        # Only execute if template generation succeeded and hooks not disabled
        if not no_hooks:
            hook_executor = HookExecutor(self.config, tokens, self.config_file)
            hooks_success = hook_executor.execute_post_generate_hooks(dry_run=dry_run)

            if not hooks_success:
                self.logger.warning("Some post-generation hooks failed")

        completion_msg = (
            "Template generation preview completed"
            if dry_run
            else "Template generation completed"
        )
        self.logger.info(completion_msg)
