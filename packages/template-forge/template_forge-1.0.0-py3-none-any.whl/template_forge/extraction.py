#!/usr/bin/env python3
"""Data extraction module for Template Forge.

This module handles extracting tokens from structured data files (JSON, YAML, XML, ARXML).
Supports glob patterns, wildcards, transformations, and multiple file merge strategies.
"""

import json
import logging
import os
import re
import xml.etree.ElementTree as StdET  # nosec B405 - only for type annotations
from datetime import datetime
from pathlib import Path
from typing import Any, ClassVar, Dict, List, Match, Optional, Tuple, Union

import defusedxml.ElementTree as ET  # nosec B405 - using defusedxml for safe XML parsing
import yaml

from .utils import deep_merge, flatten_array


class StructuredDataExtractor:
    """Extract tokens from structured data files (JSON, YAML, XML, ARXML).

    This class provides a unified interface for extracting tokens from various
    structured data formats using configurable key paths and transformations.

    Attributes:
        SUPPORTED_FORMATS: Mapping of file extensions to format identifiers.
        config: Configuration dictionary containing extraction rules.
        logger: Logger instance for this extractor.

    Example:
        >>> config = {
        ...     'inputs': [{
        ...         'path': 'data.json',
        ...         'tokens': [{'name': 'version', 'key': 'app.version'}]
        ...     }]
        ... }
        >>> extractor = StructuredDataExtractor(config)
        >>> tokens = extractor.extract_tokens()
    """

    # Supported file formats and their handlers
    SUPPORTED_FORMATS: ClassVar[Dict[str, str]] = {
        ".json": "json",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".xml": "xml",
        ".arxml": "arxml",  # AUTOSAR XML
    }

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize the extractor with configuration.

        Args:
            config: Configuration dictionary containing input files and token definitions.
                   Must include 'inputs' list and optionally 'static_tokens' dict.

        Raises:
            ValueError: If configuration is invalid or missing required fields.
        """
        if not isinstance(config, dict):
            raise ValueError("Configuration must be a dictionary")

        self.config = config
        self.logger = logging.getLogger(__name__)
        # Store config_dir for resolving relative file paths
        self.config_dir = Path.cwd()  # Default to current working directory

    def extract_tokens(self) -> Dict[str, Any]:
        """Extract all tokens from configured input files and static tokens.

        Processes all input files defined in the configuration and extracts tokens
        according to the specified key paths. All tokens from input files are organized
        under their namespace to prevent collisions (REQ-EXT-090-095).

        Returns:
            Dictionary mapping token names to their extracted values.
            Input file tokens are organized as {namespace: {token_name: value}}
            Static tokens are available at the root level.

        Raises:
            FileNotFoundError: If an input file cannot be found.
            ValueError: If file format is not supported or namespaces are duplicated.
        """
        tokens: Dict[str, Any] = {}
        namespaces_seen = set()

        # Process input files first to make their tokens available for static_tokens
        if "inputs" in self.config:
            for input_config in self.config["inputs"]:
                # Validate namespace is provided (REQ-CFG-020, REQ-EXT-094)
                if "namespace" not in input_config:
                    file_path = input_config.get("path", "unknown")
                    raise ValueError(
                        f"Missing required 'namespace' field for input file: {file_path}\n"
                        f"Each input must specify a unique namespace to prevent token collisions.\n"
                        f"Example: namespace: 'project' or namespace: 'database'"
                    )

                namespace = input_config["namespace"]

                # Validate namespace uniqueness (REQ-EXT-094, REQ-EXT-114)
                if namespace in namespaces_seen:
                    file_path = input_config.get("path", "unknown")
                    raise ValueError(
                        f"Duplicate namespace '{namespace}' found in configuration\n"
                        f"  File: {file_path}\n"
                        f"  Solution: Use unique namespaces for each input file"
                    )

                namespaces_seen.add(namespace)

                # Extract tokens from this file
                file_tokens = self._extract_from_file(input_config)

                # REQ-ADV-006: Handle 'list' strategy - special case
                # If file_tokens contains the special "__list__" key, unwrap it
                if "__list__" in file_tokens and len(file_tokens) == 1:
                    # This is a list strategy result
                    tokens[namespace] = file_tokens["__list__"]
                    self.logger.debug(
                        f"Added list of {len(file_tokens['__list__'])} items "
                        f"under namespace '{namespace}'"
                    )
                else:
                    # Organize under namespace (REQ-EXT-090, REQ-EXT-091)
                    if namespace in tokens:
                        self.logger.warning(
                            f"Namespace '{namespace}' conflicts with existing token. "
                            f"Input tokens will override."
                        )

                    tokens[namespace] = file_tokens
                    self.logger.debug(
                        f"Added {len(file_tokens)} tokens under namespace '{namespace}'"
                    )

        # Process static tokens after inputs (so they can reference extracted tokens)
        # Implements REQ-ADV-002: Derived/Computed Tokens
        if "static_tokens" in self.config:
            static_tokens = self.config["static_tokens"]
            if isinstance(static_tokens, dict):
                processed_static = self._process_static_tokens(static_tokens, tokens)
                tokens.update(processed_static)
                self.logger.debug(
                    f"Added static tokens: {list(processed_static.keys())}"
                )

        self.logger.debug(f"Total token namespaces: {list(tokens.keys())}")
        return tokens

    def _resolve_file_path(
        self, path_pattern: str, match_strategy: str = "first"
    ) -> Union[Path, List[Path]]:
        """Resolve a file path that may contain glob patterns.

        Args:
            path_pattern: File path or glob pattern (e.g., 'autosar/*.arxml')
            match_strategy: Strategy for multiple matches:
                - 'first': Use first matching file (default)
                - 'error_if_multiple': Raise error if multiple files match
                - 'all': Return all matching files (for merge strategies)
                - 'list': Return all matching files (for list strategy)

        Returns:
            Resolved Path object(s):
            - For 'first', 'error_if_multiple': Single Path
            - For 'all', 'list': List[Path] of all matching files

        Raises:
            FileNotFoundError: If no files match the pattern
            ValueError: If multiple files match and strategy is 'error_if_multiple'

        Implements: REQ-ADV-001, REQ-ADV-006
        """
        # Resolve pattern relative to config directory
        pattern_path = Path(path_pattern)
        if not pattern_path.is_absolute():
            # Make pattern relative to config directory
            pattern_path = self.config_dir / pattern_path

        # Check if path contains glob patterns
        if any(char in str(path_pattern) for char in ["*", "?", "[", "]"]):
            # Use Path.glob to find matching files
            # Need to separate the base directory from the pattern
            parts = str(pattern_path).split("*", 1)
            if parts:
                # Find the base directory (part before the first glob)
                base_str = parts[0].rstrip("/\\")

                # If base_str is empty or the original had a trailing separator,
                # it's a directory; otherwise, get the parent directory
                base_path_obj = Path(base_str) if base_str else self.config_dir
                if parts[0].endswith(("/", "\\")):
                    # Original ended with separator, so base_str is the directory
                    base_path = base_path_obj
                elif base_path_obj.exists() and base_path_obj.is_dir():
                    # It exists and is a directory
                    base_path = base_path_obj
                else:
                    # Assume it's a file path component, get parent
                    base_path = base_path_obj.parent if base_str else self.config_dir

                # Get the relative pattern from the base
                try:
                    rel_pattern = str(pattern_path.relative_to(base_path))
                except ValueError:
                    # If relative_to fails, use the full pattern
                    rel_pattern = str(pattern_path)

                # Use rglob if ** is in pattern, otherwise use glob
                if "**" in rel_pattern:
                    matching_files = sorted(
                        str(p) for p in base_path.rglob(rel_pattern.replace("**/", ""))
                    )
                else:
                    matching_files = sorted(str(p) for p in base_path.glob(rel_pattern))
            else:
                matching_files = []

            if not matching_files:
                raise FileNotFoundError(
                    f"No files found matching pattern: {path_pattern}\n"
                    f"  Glob patterns supported: *, **, ?, [...]\n"
                    f"  Example: 'autosar/*.arxml', 'config/**/*.yaml'\n"
                    f"  Searched in: {self.config_dir}"
                )

            if len(matching_files) > 1:
                if match_strategy == "error_if_multiple":
                    raise ValueError(
                        f"Multiple files match pattern '{path_pattern}':\n"
                        + "\n".join(f"  - {f}" for f in matching_files)
                        + "\n\nSpecify match: 'first' to use first file, "
                        "or provide exact filename."
                    )

                # REQ-ADV-006: Return all files for 'all' and 'list' strategies
                if match_strategy in ["all", "list"]:
                    resolved_paths = [Path(f) for f in matching_files]
                    self.logger.debug(
                        f"Resolved glob pattern '{path_pattern}' to {len(resolved_paths)} files"
                    )
                    return resolved_paths

                self.logger.info(
                    f"Multiple files match '{path_pattern}'. Using first: {matching_files[0]}"
                )

            # For 'first' strategy or single match
            if match_strategy in ["all", "list"] and len(matching_files) == 1:
                # Return as list even for single file to maintain consistent return type
                return [Path(matching_files[0])]

            resolved_path = Path(matching_files[0])
            self.logger.debug(
                f"Resolved glob pattern '{path_pattern}' to: {resolved_path}"
            )
            return resolved_path
        else:
            # Not a glob pattern, resolve relative to config dir
            if not pattern_path.is_absolute():
                pattern_path = self.config_dir / path_pattern

            # Return as list for 'all' and 'list' strategies
            if match_strategy in ["all", "list"]:
                return [Path(pattern_path)]

            return Path(pattern_path)

    def _apply_transformation(self, value: str, transform: str) -> str:
        """Apply a single transformation to a string value.

        Args:
            value: The string value to transform
            transform: The transformation name (snake_case, camel_case, etc.)

        Returns:
            Transformed string value

        Implements: REQ-ADV-002
        """
        if not isinstance(value, str):
            self.logger.warning(
                f"Transformation '{transform}' expects string, got {type(value).__name__}"
            )
            return str(value)

        # Case transformations
        if transform in ("lowercase", "lower"):
            return value.lower()
        elif transform in ("uppercase", "upper"):
            return value.upper()
        elif transform == "snake_case":
            # Convert CamelCase or spaces to snake_case
            s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", value)
            s2 = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1)
            return re.sub(r"[\s-]+", "_", s2).lower()
        elif transform == "camel_case":
            # Convert snake_case, kebab-case, spaces, or PascalCase to camelCase
            # First, convert any existing CamelCase/PascalCase to snake_case
            if not re.search(r"[\s_-]", value):
                # No obvious delimiters, might be CamelCase/PascalCase
                s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", value)
                value = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1)

            components = re.split(r"[\s_-]+", value)
            if not components:
                return value
            result = components[0].lower()
            for component in components[1:]:
                if component:  # Skip empty strings
                    result += component[0].upper() + component[1:].lower()
            return result
        elif transform == "pascal_case":
            # Convert to PascalCase
            components = re.split(r"[\s_-]+", value)
            result = ""
            for component in components:
                if component:  # Skip empty strings
                    result += component[0].upper() + component[1:].lower()
            return result
        elif transform == "kebab_case":
            # Convert to kebab-case
            s1 = re.sub("(.)([A-Z][a-z]+)", r"\1-\2", value)
            s2 = re.sub("([a-z0-9])([A-Z])", r"\1-\2", s1)
            return re.sub(r"[\s_]+", "-", s2).lower()
        elif transform == "strip":
            return value.strip()
        else:
            self.logger.warning(f"Unknown transformation: {transform}")
            return value

    def _resolve_token_reference(self, value: str, all_tokens: Dict[str, Any]) -> str:
        """Resolve ${token_name} and context variable references in a string value.

        Supports:
        - ${token_name} or ${namespace.token_name} - token references
        - ${ENV.VAR_NAME} - environment variables
        - ${CWD} - current working directory (absolute path)
        - ${CWD.basename} - current working directory name only
        - ${CONFIG_DIR} - configuration file directory
        - ${TIMESTAMP} - current ISO timestamp
        - ${DATE} - current date (YYYY-MM-DD)

        Args:
            value: String potentially containing ${...} references
            all_tokens: Dictionary of all available tokens

        Returns:
            String with all references resolved

        Implements: REQ-ADV-002, REQ-ADV-004
        """
        # Pattern matches ${token_name} or ${namespace.token_name}
        pattern = r"\$\{([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)\}"

        def replace_reference(match: Match[str]) -> str:
            token_path = match.group(1)

            # Handle ${ENV.VAR_NAME} - environment variables
            if token_path.startswith("ENV."):
                var_name = token_path[4:]  # Remove "ENV." prefix
                if var_name in os.environ:
                    return os.environ[var_name]
                else:
                    self.logger.warning(
                        f"Environment variable '{var_name}' referenced but not set"
                    )
                    return match.group(0)  # Return original if not found

            # Handle ${CWD} - current working directory
            if token_path == "CWD":  # noqa: S105 # nosec B105 - context variable name, not a password
                return str(Path.cwd())

            # Handle ${CWD.basename} - current working directory name
            if token_path == "CWD.basename":  # noqa: S105 # nosec B105 - context variable name, not a password
                return Path.cwd().name

            # Handle ${CONFIG_DIR} - configuration file directory
            if token_path == "CONFIG_DIR":  # noqa: S105 # nosec B105 - context variable name, not a password
                return str(self.config_dir)

            # Handle ${TIMESTAMP} - current ISO timestamp
            if token_path == "TIMESTAMP":  # noqa: S105 # nosec B105 - context variable name, not a password
                return datetime.now().isoformat()

            # Handle ${DATE} - current date
            if token_path == "DATE":  # noqa: S105 # nosec B105 - context variable name, not a password
                return datetime.now().strftime("%Y-%m-%d")

            # Handle normal token references
            parts = token_path.split(".")

            # Navigate through nested dictionary
            current = all_tokens
            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    self.logger.warning(
                        f"Token reference '${{{token_path}}}' not found in available tokens"
                    )
                    return match.group(0)  # Return original if not found

            return str(current)

        return re.sub(pattern, replace_reference, value)

    def _extract_from_input_path(
        self, input_path: str, all_tokens: Dict[str, Any], default: Any = None
    ) -> Any:
        """Extract value from tokens using namespace.key path.

        Args:
            input_path: Path like "namespace.key.path" or "namespace.array[*].field"
            all_tokens: All available tokens dictionary
            default: Default value if extraction fails

        Returns:
            Extracted value or default

        Implements: REQ-ADV-003
        """
        # Validate path is not empty
        if not input_path or not input_path.strip():
            self.logger.warning(
                f"Invalid from_input path '{input_path}': must include namespace"
            )
            return default

        # Split into namespace and key path
        parts = input_path.split(".", 1)
        namespace = parts[0]
        key_path = parts[1] if len(parts) > 1 else "."

        # Check if namespace exists
        if namespace not in all_tokens:
            self.logger.warning(
                f"Namespace '{namespace}' not found in from_input path '{input_path}'"
            )
            return default

        namespace_data = all_tokens[namespace]

        # Use _extract_from_dict to navigate the path
        try:
            result = self._extract_from_dict(namespace_data, key_path)
            if result is None:
                if default is not None:
                    self.logger.debug(
                        f"Path '{input_path}' returned None, using default: {default}"
                    )
                    return default
                self.logger.warning(f"Could not extract value from path '{input_path}'")
                return default
            return result
        except Exception as e:
            self.logger.warning(f"Error extracting from_input path '{input_path}': {e}")
            return default

    def _process_derived_token(
        self, token_name: str, token_def: Any, all_tokens: Dict[str, Any]
    ) -> Any:
        """Process a derived/computed token definition.

        Args:
            token_name: Name of the token being processed
            token_def: Token definition (can be simple value or dict with transforms)
            all_tokens: All available tokens for reference resolution

        Returns:
            Computed token value after applying transformations

        Implements: REQ-ADV-002, REQ-ADV-003, REQ-ADV-004
        """
        # Simple value - just return as-is (but resolve references if string)
        if not isinstance(token_def, dict):
            if isinstance(token_def, str):
                return self._resolve_token_reference(token_def, all_tokens)
            return token_def

        # Handle from_input: extract value from input data (REQ-ADV-003)
        if "from_input" in token_def:
            input_path = token_def["from_input"]
            default = token_def.get("default", None)
            value = self._extract_from_input_path(input_path, all_tokens, default)
            # After extracting from input, still apply transforms if present
            token_def = dict(token_def)  # Make a copy
            token_def["value"] = value
            # Continue to process transforms below

        # Complex token definition with value and transformations
        if "value" not in token_def:
            # If no 'value' key, treat the whole dict as a static nested dict
            # but still process nested values recursively
            processed_dict = {}
            for key, val in token_def.items():
                # Recursively process each value in the dict
                if isinstance(val, str):
                    processed_dict[key] = self._resolve_token_reference(val, all_tokens)
                elif isinstance(val, dict):
                    processed_dict[key] = self._process_derived_token(
                        f"{token_name}.{key}", val, all_tokens
                    )
                else:
                    processed_dict[key] = val
            return processed_dict

        value = token_def["value"]

        # Check for required environment variables (REQ-ADV-004)
        if token_def.get("required", False):
            if isinstance(value, str):
                # Check if value references an environment variable
                env_pattern = r"\$\{ENV\.([a-zA-Z_][a-zA-Z0-9_]*)\}"
                env_match = re.search(env_pattern, value)
                if env_match:
                    env_var = env_match.group(1)
                    if env_var not in os.environ:
                        raise ValueError(
                            f"Token '{token_name}': required environment variable '{env_var}' is not set"
                        )
                if env_match:
                    env_var = env_match.group(1)
                    if env_var not in os.environ:
                        raise ValueError(
                            f"Token '{token_name}': required environment variable '{env_var}' is not set"
                        )

        # Resolve token references in the value
        if isinstance(value, str):
            value = self._resolve_token_reference(value, all_tokens)

        # Apply single transformation
        if "transform" in token_def:
            transform = token_def["transform"]
            if not isinstance(value, str):
                self.logger.warning(
                    f"Token '{token_name}': transform expects string value, got {type(value).__name__}"
                )
                value = str(value)
            value = self._apply_transformation(value, transform)

        # Apply multiple transformations in order
        if "transforms" in token_def:
            transforms = token_def["transforms"]
            if not isinstance(transforms, list):
                self.logger.warning(
                    f"Token '{token_name}': transforms must be a list, got {type(transforms).__name__}"
                )
                return value

            for transform_def in transforms:
                if isinstance(transform_def, str):
                    # Simple transformation name
                    if isinstance(value, str):
                        value = self._apply_transformation(value, transform_def)
                elif isinstance(transform_def, dict):
                    # Complex transformation (regex_extract, regex_replace)
                    if "regex_extract" in transform_def:
                        pattern = transform_def["regex_extract"]
                        if isinstance(value, str):
                            match = re.search(pattern, value)
                            if match:
                                value = (
                                    match.group(1)
                                    if match.lastindex
                                    else match.group(0)
                                )
                            else:
                                self.logger.warning(
                                    f"Token '{token_name}': regex_extract pattern '{pattern}' did not match"
                                )
                    elif "regex_replace" in transform_def:
                        pattern = transform_def["regex_replace"].get("pattern", "")
                        replacement = transform_def["regex_replace"].get(
                            "replacement", ""
                        )
                        if isinstance(value, str):
                            value = re.sub(pattern, replacement, value)
                    else:
                        self.logger.warning(
                            f"Token '{token_name}': Unknown transformation type: {transform_def}"
                        )

        return value

    def _process_static_tokens(
        self, static_tokens_config: Dict[str, Any], all_tokens: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process static tokens, resolving references and applying transformations.

        Args:
            static_tokens_config: Static tokens from configuration
            all_tokens: All available tokens (for reference resolution)

        Returns:
            Processed static tokens dictionary

        Implements: REQ-ADV-002, REQ-ADV-004
        """
        processed = {}

        # Process static tokens, making each processed token available for reference
        # by subsequent tokens. This allows static tokens to reference other static tokens.
        for token_name, token_def in static_tokens_config.items():
            try:
                # Process this token using currently available tokens
                processed_value = self._process_derived_token(
                    token_name, token_def, all_tokens
                )
                processed[token_name] = processed_value

                # Add this processed token to all_tokens so it can be referenced
                # by subsequent static tokens
                all_tokens[token_name] = processed_value

            except ValueError as e:
                # Re-raise ValueError (e.g., required environment variable not set)
                self.logger.error(f"Error processing static token '{token_name}': {e}")
                raise
            except Exception as e:
                self.logger.error(f"Error processing static token '{token_name}': {e}")
                # Keep original value on error
                processed[token_name] = token_def
                all_tokens[token_name] = token_def

        return processed

    def _extract_from_file(self, input_config: Dict[str, Any]) -> Dict[str, Any]:
        """Extract tokens from a single input file or multiple files (REQ-ADV-006).

        If no token extraction rules are specified, all top-level keys are extracted
        (REQ-EXT-100-102).

        Supports glob patterns in file paths (REQ-ADV-001).

        REQ-ADV-006: Supports multiple match strategies:
        - 'first': Extract from first matching file (default)
        - 'all': Merge data from all matching files
        - 'list': Create array with data from all matching files
        - 'error_if_multiple': Fail if multiple files match
        """
        # Resolve file path (may contain glob patterns)
        path_pattern = input_config["path"]
        match_strategy = input_config.get("match", "first")

        resolved_paths = self._resolve_file_path(path_pattern, match_strategy)

        # Handle single vs multiple file strategies
        if match_strategy in ["all", "list"]:
            # Multiple file strategies
            if not isinstance(resolved_paths, list):
                # Should never happen due to _resolve_file_path logic, but handle gracefully
                resolved_paths = [resolved_paths]

            if match_strategy == "list":
                # Extract from each file and return as list
                return self._extract_from_files_as_list(resolved_paths, input_config)
            else:  # match_strategy == "all"
                # Merge data from all files
                merge_strategy = input_config.get("merge_strategy", "deep")
                return self._extract_and_merge_files(
                    resolved_paths, input_config, merge_strategy
                )
        else:
            # Single file strategies ('first' or 'error_if_multiple')
            file_path = (
                resolved_paths
                if isinstance(resolved_paths, Path)
                else resolved_paths[0]
            )

            # Check if resolved file exists
            if not file_path.exists():
                self.logger.error(f"Input file not found: {file_path}")
                raise FileNotFoundError(f"Input file not found: {file_path}")

            return self._extract_from_single_file(file_path, input_config)

    def _extract_from_single_file(
        self, file_path: Path, input_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract tokens from a single file.

        Helper method for _extract_from_file to handle single file extraction.
        """
        # Determine format from extension or explicit override
        format_type = input_config.get("format")
        if not format_type:
            file_ext = file_path.suffix.lower()
            if file_ext not in self.SUPPORTED_FORMATS:
                supported_formats = ", ".join(self.SUPPORTED_FORMATS.keys())
                self.logger.error(
                    f"Unsupported file format: {file_ext}. Supported formats: {supported_formats}"
                )
                raise ValueError(
                    f"Unsupported file format: {file_ext}. Supported formats: {supported_formats}"
                )
            format_type = self.SUPPORTED_FORMATS[file_ext]

        self.logger.info(f"Processing {format_type.upper()} file: {file_path}")

        try:
            # Load file data
            data = self._load_file(file_path, format_type)

            # Extract tokens
            tokens = {}

            # Check if token extraction rules are specified
            if input_config.get("tokens"):
                # Extract specific tokens based on rules
                for token_config in input_config["tokens"]:
                    token_name = token_config["name"]
                    key_path = token_config["key"]

                    # Extract value based on format
                    if format_type in ["json", "yaml"]:
                        value = self._extract_from_dict(data, key_path)
                    elif format_type in ["xml", "arxml"]:
                        value = self._extract_from_xml(data, key_path)
                    else:
                        value = None

                    # Apply transform if specified (BEFORE regex)
                    if value is not None and "transform" in token_config:
                        value = self._apply_transform(value, token_config["transform"])

                    # Apply regex filter if specified
                    if value is not None and "regex" in token_config:
                        regex_result = self._apply_regex_filter(
                            value, token_config["regex"]
                        )
                        if regex_result is not None:
                            value = regex_result

                    # Apply filter if specified (for arrays)
                    if value is not None and "filter" in token_config:
                        value = self._apply_filter(value, token_config["filter"])

                    # Apply flatten if specified (for nested arrays)
                    if value is not None and token_config.get("flatten", False):
                        value = flatten_array(value)  # Use the flatten_array from utils

                    # Use default value if extraction failed
                    if value is None and "default" in token_config:
                        value = token_config["default"]

                    if value is not None:
                        tokens[token_name] = value
                        self.logger.debug(f"Extracted token '{token_name}': {value}")
                    else:
                        self.logger.warning(
                            f"Could not extract token '{token_name}' from key '{key_path}'"
                        )
            else:
                # No tokens specified - extract all top-level keys (REQ-EXT-100-102)
                if format_type in ["json", "yaml"]:
                    if isinstance(data, dict):
                        tokens = data
                        self.logger.debug(
                            f"Extracted all top-level keys: {list(tokens.keys())}"
                        )
                    else:
                        self.logger.warning(
                            f"File {file_path} does not contain a dictionary at root level. "
                            f"Cannot extract top-level keys."
                        )
                elif format_type in ["xml", "arxml"]:
                    # For XML, extract all child elements as tokens
                    for child in data:
                        key = child.tag
                        # Handle namespaces in XML tags
                        if "}" in key:
                            key = key.split("}")[-1]

                        if child.text and child.text.strip():
                            tokens[key] = child.text.strip()
                        else:
                            # Complex element - convert to dict
                            tokens[key] = self._xml_to_dict(child)

                    self.logger.debug(
                        f"Extracted all child elements: {list(tokens.keys())}"
                    )

            return tokens

        except Exception as e:
            self.logger.error(f"Error loading file {file_path}: {e}")
            raise RuntimeError(f"Error loading file {file_path}: {e}") from e

    def _extract_from_files_as_list(
        self, file_paths: List[Path], input_config: Dict[str, Any]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Extract from multiple files and return as list.

        Implements REQ-ADV-006: 'list' strategy.
        Returns a special structure where the namespace contains a list
        of all extracted data from matching files.
        """
        extracted_data_list = []

        for file_path in file_paths:
            if not file_path.exists():
                self.logger.warning(f"Input file not found: {file_path}, skipping")
                continue

            try:
                file_data = self._extract_from_single_file(file_path, input_config)
                extracted_data_list.append(file_data)
                self.logger.debug(f"Extracted data from {file_path}")
            except Exception as e:
                self.logger.warning(f"Failed to extract from {file_path}: {e}")
                continue

        # Return as a special list token - templates can iterate over this
        # The namespace will contain a list instead of a dict
        if not extracted_data_list:
            self.logger.warning("No data extracted from any matching files")
            return {}

        self.logger.info(
            f"Extracted data from {len(extracted_data_list)} files as list"
        )
        # Return the list directly - it will be accessible in templates
        # as namespace[index] or via iteration
        return {"__list__": extracted_data_list}

    def _extract_and_merge_files(
        self, file_paths: List[Path], input_config: Dict[str, Any], merge_strategy: str
    ) -> Dict[str, Any]:
        """Extract and merge data from multiple files.

        Implements REQ-ADV-006: 'all' strategy with merge strategies.

        Args:
            file_paths: List of file paths to process
            input_config: Input configuration
            merge_strategy: 'deep' for recursive merge, 'shallow' for top-level only
        """
        merged_tokens: Dict[str, Any] = {}

        for file_path in file_paths:
            if not file_path.exists():
                self.logger.warning(f"Input file not found: {file_path}, skipping")
                continue

            try:
                file_data = self._extract_from_single_file(file_path, input_config)

                if merge_strategy == "deep":
                    merged_tokens = deep_merge(
                        merged_tokens, file_data
                    )  # Use deep_merge from utils
                else:  # shallow merge
                    merged_tokens.update(file_data)

                self.logger.debug(f"Merged data from {file_path}")
            except Exception as e:
                self.logger.warning(f"Failed to extract from {file_path}: {e}")
                continue

        if not merged_tokens:
            self.logger.warning("No data extracted from any matching files")
        else:
            self.logger.info(
                f"Merged data from {len(file_paths)} files using '{merge_strategy}' strategy"
            )

        return merged_tokens

    def _load_file(self, file_path: Path, format_type: str) -> Any:
        """Load and parse a file based on its format."""
        try:
            with open(file_path, encoding="utf-8") as f:
                if format_type == "json":
                    return json.load(f)
                elif format_type == "yaml":
                    return yaml.safe_load(f)
                elif format_type in ["xml", "arxml"]:
                    return ET.parse(f).getroot()
        except Exception as e:
            raise Exception(f"Failed to parse {format_type.upper()} file: {e}") from e

    def _extract_from_dict(self, data: Dict[str, Any], key_path: str) -> Any:
        """Extract value from dictionary using enhanced dot notation key path.

        Supports:
        - Simple paths: "user.name"
        - Array indexing: "users[0].name"
        - Array slicing: "users[1:3]"
        - Array wildcards: "users[*].name" (extract from all items)
        - Object wildcards: "config.*" (return entire object)
        - Root access: "." (return entire data)
        """
        # If key is just a dot, return the whole data
        if key_path == ".":
            return data

        # Handle object wildcards like "config.*"
        if key_path.endswith(".*"):
            # Get everything before the wildcard
            base_path = key_path[:-2]  # Remove ".*"
            if not base_path:
                # Just ".*" - return the entire data
                return data
            # Navigate to the object and return it
            current = data
            for part in base_path.split("."):
                if not part:
                    continue
                current = self._extract_single_part(current, part)
                if current is None:
                    return None
            return current

        # Handle array wildcards like "modules[*].name"
        if "[*]" in key_path:
            return self._extract_with_wildcard(data, key_path)

        # Split the path and process each part
        keys = key_path.split(".")
        current = data

        for key in keys:
            if not key:  # Skip empty parts
                continue

            # Handle legacy format like "items.[1]"
            if key.startswith("[") and key.endswith("]"):
                # Legacy array indexing format
                try:
                    index = int(key[1:-1])
                    if isinstance(current, (list, tuple)) and 0 <= index < len(current):
                        current = current[index]
                    else:
                        return None
                except (ValueError, IndexError):
                    return None
            else:
                current = self._extract_single_part(current, key)
                if current is None:
                    return None

        return current

    def _extract_with_wildcard(self, data: Dict[str, Any], key_path: str) -> Any:
        """Handle wildcard extraction like 'modules[*].name'."""
        parts = key_path.split("[*]")
        base_path = parts[0]
        remaining_path = parts[1].lstrip(".") if len(parts) > 1 and parts[1] else None

        # Get the array using the base path
        current = data
        if base_path:
            for part in base_path.split("."):
                if not part:
                    continue
                current = self._extract_single_part(current, part)
                if current is None:
                    return None

        # If current is not a list, return None
        if not isinstance(current, list):
            return None

        # If there's a remaining path, apply it to each element
        if remaining_path:
            results = []
            for item in current:
                if item is not None:
                    result = self._extract_from_dict(item, remaining_path)
                    if result is not None:
                        results.append(result)
            return results if results else None

        return current

    def _extract_single_part(self, current: Any, part: str) -> Any:
        """Extract a single part of the path, handling arrays and objects."""
        import re

        # Check for array notation
        array_pattern = r"^([^\[]+)\[([^\]]+)\]$"
        match = re.match(array_pattern, part)

        if match:
            # Handle array access
            array_name = match.group(1)
            index_expr = match.group(2)

            # First get the array
            if isinstance(current, dict):
                array_obj = self._get_dict_value(current, array_name)
            else:
                array_obj = current

            if not isinstance(array_obj, (list, tuple)):
                return None

            # Handle different index expressions
            if ":" in index_expr:
                # Slicing (e.g., "1:3", ":2", "1:")
                return self._slice_array(array_obj, index_expr)
            else:
                # Simple indexing
                try:
                    index = int(index_expr)
                    return array_obj[index] if 0 <= index < len(array_obj) else None
                except (ValueError, IndexError):
                    return None
        else:
            # Handle regular key access
            if isinstance(current, dict):
                return self._get_dict_value(current, part)
            elif isinstance(current, list):
                # Extract key from all objects in array
                results = []
                for item in current:
                    if isinstance(item, dict):
                        value = self._get_dict_value(item, part)
                        if value is not None:
                            results.append(value)
                return results if results else None
            else:
                return None

    def _slice_array(
        self, array: Union[List[Any], Tuple[Any, ...]], slice_expr: str
    ) -> List[Any]:
        """Handle array slicing expressions like '1:3', ':2', '1:'."""
        parts = slice_expr.split(":")
        start = int(parts[0]) if parts[0] else None
        end = int(parts[1]) if len(parts) > 1 and parts[1] else None

        try:
            result = array[start:end]
            return list(result) if isinstance(result, tuple) else result
        except (ValueError, TypeError):
            return []

    def _get_dict_value(self, data: Dict[str, Any], key: str) -> Any:
        """Get value from dictionary with case-insensitive matching."""
        # Try exact match first
        if key in data:
            return data[key]

        # Try case-insensitive match
        for k, v in data.items():
            if k.lower() == key.lower():
                return v

        return None

    def _extract_from_xml(self, root: StdET.Element, key_path: str) -> Any:
        """Extract value from XML using dot notation key path."""

        def strip_namespace(tag: str) -> str:
            """Remove namespace from XML tag."""
            if "}" in tag:
                return tag.split("}")[-1]
            return tag

        keys = key_path.split(".")
        current = root

        # Skip root element name if it matches first key
        if keys and strip_namespace(root.tag).lower() == keys[0].lower():
            keys = keys[1:]

        for i, key in enumerate(keys):
            if key.startswith("@"):
                # Extract attribute
                attr_name = key[1:]
                return current.get(attr_name)

            # Handle wildcard
            if key == "*":
                # Extract all child elements
                if i == len(keys) - 1:
                    # Last key is wildcard - return list of all children
                    result: List[Union[str, Dict[str, Any]]] = []
                    for child in current:
                        # Try to get text, otherwise convert to dict
                        if child.text and child.text.strip() and not list(child):
                            result.append(child.text.strip())
                        else:
                            result.append(self._xml_to_dict(child))
                    return result if result else None
                else:
                    # Wildcard in the middle - not yet supported
                    return None

            # Handle array indexing: element[0], element[1], element[*]
            array_index = None
            is_wildcard_array = False
            if "[" in key and key.endswith("]"):
                base_key, index_part = key[:-1].split("[", 1)
                if index_part == "*":
                    is_wildcard_array = True
                else:
                    try:
                        array_index = int(index_part)
                    except ValueError:
                        return None
                key = base_key

            # Find all matching child elements (case-insensitive, namespace-aware)
            matches = []
            for child in current:
                child_tag = strip_namespace(child.tag).lower()
                if child_tag == key.lower():
                    matches.append(child)

            if not matches:
                return None

            # Handle array wildcard [*]

            if is_wildcard_array:
                wildcard_result: List[Union[str, Dict[str, Any]]] = []
                for child in matches:
                    if child.text and child.text.strip() and not list(child):
                        wildcard_result.append(child.text.strip())
                    else:
                        wildcard_result.append(self._xml_to_dict(child))
                return (
                    wildcard_result if wildcard_result else None
                )  # Handle array indexing
            if array_index is not None:
                if array_index >= len(matches):
                    return None
                current = matches[array_index]
            else:
                # No index - just take the first match
                current = matches[0]

        # Return text content of the element
        return current.text if current.text else None

    def _xml_to_dict(self, element: StdET.Element) -> Dict[str, Any]:
        """Convert XML element to dictionary structure.

        Implements REQ-EXT-035: Convert XML structure to dictionary with:
        - 'text': Element text content (if present)
        - '@attributeName': Attribute values (if present)
        - 'childName': Nested child elements (if present)
        """
        result: Dict[str, Any] = {}

        # Add attributes with @ prefix
        if element.attrib:
            for key, value in element.attrib.items():
                result[f"@{key}"] = value

        # Add text content if present
        if element.text and element.text.strip():
            result["text"] = element.text.strip()

        # Add child elements
        for child in element:
            key = child.tag
            # Handle namespaces
            if "}" in key:
                key = key.split("}")[-1]

            # Convert child to dict
            child_value = self._xml_to_dict(child)

            # If child only has text, use the text directly
            if len(child_value) == 1 and "text" in child_value:
                child_value = child_value["text"]

            # Handle multiple children with same tag name (REQ-EXT-037)
            if key in result:
                # Convert to list if not already
                if not isinstance(result[key], list):
                    result[key] = [result[key]]
                result[key].append(child_value)
            else:
                result[key] = child_value

        return result

    def _apply_regex_filter(
        self, value: str, pattern: str
    ) -> Optional[Union[str, Tuple[str, ...]]]:
        """Apply regex filter to extract specific parts of the value."""
        try:
            match = re.search(pattern, str(value))
            if match:
                groups = match.groups()
                if len(groups) == 0:
                    return match.group(0)  # Return full match if no groups
                elif len(groups) == 1:
                    return groups[0]  # Return single group
                else:
                    return groups  # Return tuple of groups
            return None
        except re.error as e:
            self.logger.error(f"Invalid regex pattern '{pattern}': {e}")
            return value

    def _apply_transform(self, value: Any, transform: str) -> Any:
        """Apply transformation to the extracted value."""
        try:
            # String transforms - only apply if value is a string or can be converted
            if transform in ["upper", "lower", "title", "capitalize", "strip"]:
                if not isinstance(value, str):
                    # Don't transform non-strings
                    return value
                if transform == "upper":
                    return value.upper()
                elif transform == "lower":
                    return value.lower()
                elif transform == "title":
                    return value.title()
                elif transform == "capitalize":
                    return value.capitalize()
                elif transform == "strip":
                    return value.strip()
            elif transform == "int":
                return int(value)
            elif transform == "float":
                return float(value)
            elif transform == "bool":
                return str(value).lower() in ["true", "1", "yes", "on"]
            elif transform == "snake_case":
                return re.sub(r"(?<!^)(?=[A-Z])", "_", str(value)).lower()
            elif transform == "camel_case":
                return "".join(word.capitalize() for word in str(value).split("_"))
            elif transform == "len":
                return len(value) if hasattr(value, "__len__") else 0
            elif transform == "any":
                return any(value) if isinstance(value, (list, tuple)) else bool(value)
            elif transform == "all":
                return all(value) if isinstance(value, (list, tuple)) else bool(value)
            elif transform == "sum":
                return sum(value) if isinstance(value, (list, tuple)) else value
            elif transform == "max":
                return (
                    max(value) if isinstance(value, (list, tuple)) and value else value
                )
            elif transform == "min":
                return (
                    min(value) if isinstance(value, (list, tuple)) and value else value
                )
            elif transform == "unique":
                return (
                    list(dict.fromkeys(value))
                    if isinstance(value, (list, tuple))
                    else value
                )
            else:
                self.logger.warning(f"Unknown transform: {transform}")
                return value
        except (ValueError, TypeError) as e:
            self.logger.warning(
                f"Transform '{transform}' failed for value '{value}': {e}"
            )
            return value

    def _apply_filter(self, value: Any, filter_pattern: str) -> Any:
        """Apply regex filter to array elements."""
        import re

        if not isinstance(value, (list, tuple)):
            # Apply filter to single value
            if re.search(filter_pattern, str(value)):
                return value
            else:
                return None

        # Apply filter to array elements
        filtered = []
        for item in value:
            if re.search(filter_pattern, str(item)):
                filtered.append(item)

        return filtered if filtered else None
