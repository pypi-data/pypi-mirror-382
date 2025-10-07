#!/usr/bin/env python3
"""Template processing module for Template Forge.

This module handles Jinja2 template processing with custom filters,
content preservation, conditional generation, and diff display.
"""

import difflib
import importlib
import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from jinja2 import DictLoader, Environment, FileSystemLoader, StrictUndefined

from .preservation import PreservationHandler


class TemplateProcessor:
    """Process Jinja2 templates with extracted tokens and content preservation."""

    def __init__(self, config: Dict[str, Any], tokens: Dict[str, Any]):
        """Initialize the template processor.

        Args:
            config: Configuration dictionary from YAML file
            tokens: Dictionary of extracted tokens
        """
        self.config = config
        self.tokens = tokens
        self.logger = logging.getLogger(__name__)
        self.preservation_handler = PreservationHandler()
        self.config_dir = Path()  # Default, should be set by caller

        # Setup Jinja2 environment - initialize immediately for backward compatibility
        self._jinja_options = config.get("jinja_options", {})
        self.env: Optional[Environment] = (
            None  # Will be initialized on first access or explicitly
        )
        self._init_jinja_env()  # Initialize now with default config_dir

    def _init_jinja_env(self) -> None:
        """Initialize or reinitialize the Jinja2 environment with proper paths."""
        template_dir = Path(self.config.get("template_dir", "."))

        # Resolve relative to config directory
        if not template_dir.is_absolute():
            template_dir = self.config_dir / template_dir

        # Setup Jinja2 environment
        jinja_options = self._jinja_options

        # Configure undefined behavior: strict_undefined=True raises errors, False allows undefined variables
        env_kwargs = {
            "loader": FileSystemLoader(str(template_dir)),
            "trim_blocks": jinja_options.get("trim_blocks", True),
            "lstrip_blocks": jinja_options.get("lstrip_blocks", True),
            "keep_trailing_newline": jinja_options.get("keep_trailing_newline", True),
        }

        # Only set undefined if strict_undefined is True
        if jinja_options.get("strict_undefined", False):
            env_kwargs["undefined"] = StrictUndefined

        self.env = Environment(**env_kwargs)  # nosec B701 - autoescape intentionally False for code/config generation

        # Always register custom filters
        self._register_custom_filters()

    def _register_custom_filters(self) -> None:
        """Register custom Jinja2 filters.

        Implements: REQ-ADV-005
        """
        assert self.env is not None, (
            "Jinja2 environment must be initialized before registering filters"
        )  # nosec B101 - internal consistency check

        # Register built-in custom filters
        self.env.filters["upper"] = str.upper
        self.env.filters["lower"] = str.lower
        self.env.filters["capitalize"] = str.capitalize
        self.env.filters["snake_case"] = lambda s: re.sub(
            r"(?<!^)(?=[A-Z])", "_", s
        ).lower()
        self.env.filters["camel_case"] = lambda s: "".join(
            word.capitalize() for word in s.split("_")
        )
        self.env.filters["pascal_case"] = lambda s: "".join(
            word.capitalize() for word in s.replace("-", "_").split("_")
        )
        self.env.filters["kebab_case"] = lambda s: re.sub(
            r"(?<!^)(?=[A-Z])", "-", s
        ).lower()

        # Custom Python-compatible JSON filter
        def python_json(obj: Any) -> str:
            """Convert object to Python-compatible JSON string."""
            json_str = json.dumps(obj, separators=(",", ": "), ensure_ascii=False)
            # Convert JavaScript boolean values to Python boolean values
            json_str = (
                json_str.replace("true", "True")
                .replace("false", "False")
                .replace("null", "None")
            )
            return json_str

        self.env.filters["pyjson"] = python_json

        # Load custom filters from configuration (REQ-ADV-005)
        custom_filters_config = self.config.get("custom_filters", [])
        if custom_filters_config:
            self._load_custom_filters(custom_filters_config)

    def _load_custom_filters(self, custom_filters_config: List[Dict[str, Any]]) -> None:
        """Load custom Jinja2 filters from external modules.

        Args:
            custom_filters_config: List of filter configuration dictionaries

        Implements: REQ-ADV-005
        """
        assert self.env is not None, (
            "Jinja2 environment must be initialized before loading filters"
        )  # nosec B101 - internal consistency check

        for filter_config in custom_filters_config:
            if not isinstance(filter_config, dict):
                self.logger.warning(
                    f"Invalid custom filter configuration: {filter_config} (expected dict)"
                )
                continue

            module_name = filter_config.get("module")
            if not module_name:
                self.logger.warning("Custom filter config missing 'module' key")
                continue

            filters = filter_config.get("filters", [])
            if not filters:
                self.logger.warning(f"No filters specified for module '{module_name}'")
                continue

            # Try to import the module
            try:
                module = importlib.import_module(module_name)
            except ImportError as e:
                self.logger.error(
                    f"Failed to import custom filter module '{module_name}': {e}"
                )
                continue
            except Exception as e:
                self.logger.error(
                    f"Error importing custom filter module '{module_name}': {e}"
                )
                continue

            # Load each filter from the module
            for filter_spec in filters:
                # Filter can be a string (function name) or dict (with rename)
                if isinstance(filter_spec, str):
                    function_name = filter_spec
                    filter_name = filter_spec
                elif isinstance(filter_spec, dict):
                    # Support rename: {old_name: new_name}
                    if len(filter_spec) != 1:
                        self.logger.warning(
                            f"Invalid filter spec in module '{module_name}': {filter_spec}"
                        )
                        continue
                    filter_name, function_name = next(iter(filter_spec.items()))
                else:
                    self.logger.warning(
                        f"Invalid filter spec in module '{module_name}': {filter_spec}"
                    )
                    continue

                # Get the filter function from the module
                if not hasattr(module, function_name):
                    self.logger.error(
                        f"Function '{function_name}' not found in module '{module_name}'"
                    )
                    continue

                filter_func = getattr(module, function_name)

                # Verify it's callable
                if not callable(filter_func):
                    self.logger.error(
                        f"'{function_name}' in module '{module_name}' is not callable"
                    )
                    continue

                # Register the filter
                self.env.filters[filter_name] = filter_func
                self.logger.info(
                    f"Registered custom filter '{filter_name}' from {module_name}.{function_name}"
                )

    def process_templates(self, dry_run: bool = False, show_diff: bool = False) -> None:
        """Process all templates defined in configuration.

        Args:
            dry_run: If True, preview operations without writing files (REQ-CLI-030-036)
            show_diff: If True, show diffs for existing files (REQ-CLI-050-058)
        """
        # Initialize Jinja environment if not already done
        if self.env is None:
            self._init_jinja_env()

        # Check if templates are explicitly defined or need auto-discovery
        if "templates" in self.config:
            templates = self.config["templates"]
        elif "template_dir" in self.config:
            # Auto-discover templates from template_dir
            templates = self._discover_templates()
            if not templates:
                self.logger.warning(
                    f"No .j2 templates found in directory: {self.config['template_dir']}"
                )
                return
        else:
            self.logger.error("No templates defined in configuration")
            return

        strict_mode = self.config.get("jinja_options", {}).get(
            "strict_undefined", False
        )

        for template_config in templates:
            try:
                self._process_single_template(
                    template_config, dry_run=dry_run, show_diff=show_diff
                )
            except Exception as e:
                # Log error but continue processing other templates (REQ-TPL-014/015/073)
                self.logger.error(f"Error processing template: {e}")
                # In strict mode, re-raise to fail fast
                if strict_mode:
                    raise
                continue

    def _discover_templates(self) -> List[Dict[str, Any]]:
        """Auto-discover .j2 templates from template_dir.

        Returns:
            List of template configurations for discovered templates.
        """
        template_dir = Path(self.config["template_dir"])
        # Resolve relative to config directory
        if not template_dir.is_absolute():
            template_dir = self.config_dir / template_dir

        output_dir = Path(self.config.get("output_dir", "output"))
        if not output_dir.is_absolute():
            output_dir = self.config_dir / output_dir

        templates = []
        for template_path in sorted(template_dir.rglob("*.j2")):
            # Get relative path from template_dir
            relative_path = template_path.relative_to(template_dir)

            # Generate output path by removing .j2 extension and placing in output_dir
            output_relative = relative_path.with_suffix("")
            if relative_path.suffix == ".j2" and relative_path.stem.endswith(".j2"):
                # Handle double extensions like .txt.j2
                output_relative = relative_path.with_suffix("").with_suffix("")

            output_path = output_dir / output_relative

            templates.append(
                {"template": str(relative_path), "output": str(output_path)}
            )

        self.logger.info(
            f"Auto-discovered {len(templates)} templates from {template_dir}"
        )
        return templates

    def _process_single_template(
        self,
        template_config: Dict[str, Any],
        dry_run: bool = False,
        show_diff: bool = False,
    ) -> None:
        """Process a single template with content preservation support.

        Args:
            template_config: Configuration for a single template
            dry_run: If True, preview without writing files
            show_diff: If True, show diff for existing files
        """
        template_name = template_config["template"]
        output_path = Path(template_config["output"])

        # REQ-TPL-130-138: Conditional template generation
        # Check if template has a 'when' condition
        when_condition = template_config.get("when")
        if when_condition:
            try:
                # Use Jinja2 to evaluate condition with tokens
                # Create a simple environment for condition evaluation
                condition_env = Environment(loader=DictLoader({}))  # nosec B701 - autoescape intentionally False for condition evaluation
                condition_template = condition_env.from_string(
                    f"{{% if {when_condition} %}}true{{% endif %}}"
                )

                # Merge global tokens with template-specific tokens for evaluation
                template_tokens = self.tokens.copy()
                if "tokens" in template_config:
                    template_tokens.update(template_config["tokens"])

                condition_result = condition_template.render(**template_tokens)

                if condition_result != "true":
                    self.logger.debug(
                        f"Skipping template '{template_name}' (condition '{when_condition}' not met)"
                    )
                    return  # Skip this template
            except Exception as e:
                self.logger.warning(
                    f"Failed to evaluate condition '{when_condition}' for template '{template_name}': {e}"
                )
                self.logger.warning(
                    f"Skipping template '{template_name}' due to condition evaluation error"
                )
                return  # Skip on error to be safe

        try:
            # Extract preserved content from existing file (if it exists)
            preserved_blocks = self.preservation_handler.extract_preserved_content(
                output_path
            )

            # Load template
            assert self.env is not None, (
                "Jinja2 environment must be initialized before processing templates"
            )  # nosec B101 - internal consistency check
            template = self.env.get_template(template_name)

            # Merge global tokens with template-specific tokens
            template_tokens = self.tokens.copy()
            if "tokens" in template_config:
                template_tokens.update(template_config["tokens"])

            # Render template
            template_output = template.render(**template_tokens)

            # Inject preserved content back into the output
            if preserved_blocks:
                final_content = self.preservation_handler.inject_preserved_content(
                    template_output, preserved_blocks
                )
                if not dry_run:
                    self.logger.info(
                        f"Preserved {len(preserved_blocks)} content blocks in {output_path}"
                    )
            else:
                final_content = template_output

            # Handle dry-run mode (REQ-CLI-031-033)
            if dry_run:
                file_size = len(final_content.encode("utf-8"))
                if output_path.exists():
                    print(
                        f"[DRY RUN] Would modify: {output_path} ({file_size:,} bytes)"
                    )
                else:
                    print(
                        f"[DRY RUN] Would create: {output_path} ({file_size:,} bytes)"
                    )

                if show_diff and output_path.exists():
                    self._show_diff(output_path, final_content)
                return

            # Handle diff mode (REQ-CLI-050-058)
            if show_diff and output_path.exists():
                self._show_diff(output_path, final_content)

            # Create output directory if it doesn't exist
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Write output
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(final_content)

            self.logger.info(f"Generated: {output_path}")

        except Exception as e:
            self.logger.error(f"Template error for '{template_name}': {e}")
            raise  # Re-raise the exception for proper error handling

    def _show_diff(self, file_path: Path, new_content: str) -> None:
        """Show unified diff between existing file and new content (REQ-CLI-050-058)."""
        try:
            with open(file_path, encoding="utf-8") as f:
                old_content = f.read()

            old_lines = old_content.splitlines(keepends=True)
            new_lines = new_content.splitlines(keepends=True)

            diff = difflib.unified_diff(
                old_lines,
                new_lines,
                fromfile=f"{file_path} (existing)",
                tofile=f"{file_path} (new)",
                lineterm="",
            )

            print(f"\n{'=' * 60}")
            print(f"Diff for {file_path}:")
            print("=" * 60)

            additions = 0
            deletions = 0

            for line in diff:
                if line.startswith("+++") or line.startswith("---"):
                    print(line)
                elif line.startswith("@@"):
                    print(f"\033[96m{line}\033[0m")  # Cyan
                elif line.startswith("+"):
                    print(f"\033[92m{line}\033[0m")  # Green
                    additions += 1
                elif line.startswith("-"):
                    print(f"\033[91m{line}\033[0m")  # Red
                    deletions += 1
                else:
                    print(line)

            print(f"\n{additions} additions(+), {deletions} deletions(-)")
            print("=" * 60 + "\n")

        except Exception as e:
            self.logger.warning(f"Could not show diff for {file_path}: {e}")

    def _finalize_content(
        self,
        template_output: str,
        output_path: Path,
        preserved_blocks: Dict[str, str],
    ) -> str:
        """Inject preserved content and finalize output.

        Args:
            template_output: Raw template output
            output_path: Target output file path
            preserved_blocks: Preserved code blocks by identifier

        Returns:
            Final content with preserved blocks injected
        """
        if preserved_blocks:
            final_content = self.preservation_handler.inject_preserved_content(
                template_output, preserved_blocks
            )
            self.logger.info(
                f"Preserved {len(preserved_blocks)} content blocks in {output_path}"
            )
        else:
            final_content = template_output

        return final_content
